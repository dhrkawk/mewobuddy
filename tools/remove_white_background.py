"""
Quick background remover for cat videos.

Converts an input video to RGBA and makes pixels matching a target background
color (with tolerance) transparent. Outputs a transparent GIF that QMovie can
display.

Usage:
    python tools/remove_white_background.py input.mp4 output.gif \
        --bg 255 255 255 --tolerance 15 --max-frames 300

Dependencies:
    pip install opencv-python imageio
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import imageio.v2 as imageio
import numpy as np


def remove_background(
    input_path: Path,
    output_path: Path,
    bg_color: tuple[int, int, int] = (255, 255, 255),
    tolerance: int = 15,
    max_frames: int | None = None,
    method: str = "threshold",  # "threshold" | "rembg"
    model: str = "u2net",
    mask_blur: int = 0,
    mask_erode: int = 0,
    mask_dilate: int = 0,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {input_path}")

    supported_models = {"u2net", "u2netp", "u2net_human_seg", "u2net_cloth_seg", "silueta"}
    if method == "rembg" and model not in supported_models:
        raise RuntimeError(f"rembg 모델 '{model}'은 지원하지 않습니다. 사용 가능한 모델: {', '.join(sorted(supported_models))}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    fps = fps if fps and fps > 0 else 24
    frame_duration = 1 / fps

    frames: list[np.ndarray] = []
    frame_idx = 0

    # Convert target background from RGB to BGR (cv2 uses BGR order)
    bg_bgr = np.array([bg_color[2], bg_color[1], bg_color[0]], dtype=np.int16)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

        if method == "rembg":
            try:
                from rembg import new_session, remove as rembg_remove  # type: ignore
            except Exception as exc:
                raise RuntimeError(
                    "rembg import 실패: rembg/onnxruntime가 설치되어 있는지 확인하세요. "
                    "예) pip install rembg onnxruntime"
                ) from exc
            session = new_session(model)
            rgba = rembg_remove(rgba, session=session)  # rembg returns RGBA uint8
            rgba = np.array(rgba, copy=True)  # ensure writable
        else:
            # threshold-based chroma removal
            rgba = rgba.astype(np.int16)
            diff = np.abs(rgba[:, :, :3] - bg_bgr)
            mask = (diff <= tolerance).all(axis=2)
            rgba[:, :, 3] = 255  # default opaque
            rgba[mask, 3] = 0    # make background transparent
            rgba = rgba.astype(np.uint8)

        rgba = _refine_alpha(rgba, blur=mask_blur, erode=mask_erode, dilate=mask_dilate)
        frames.append(rgba)
        frame_idx += 1
        if max_frames is not None and frame_idx >= max_frames:
            break

    cap.release()

    if not frames:
        raise RuntimeError("No frames processed; check the input video.")

    # Save as GIF with transparency; duration is per-frame seconds
    imageio.mimsave(output_path, frames, duration=frame_duration, loop=0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove a solid background color from video and export as transparent GIF.")
    parser.add_argument("input", type=Path, help="Input video file (e.g., MP4)")
    parser.add_argument("output", type=Path, help="Output GIF path")
    parser.add_argument("--bg", type=int, nargs=3, metavar=("R", "G", "B"), default=(255, 255, 255), help="Background color to remove (RGB)")
    parser.add_argument("--tolerance", type=int, default=15, help="Tolerance for color match (0-255). Higher = more aggressive.")
    parser.add_argument("--max-frames", type=int, default=None, help="Limit number of frames for quick tests.")
    parser.add_argument("--method", choices=["threshold", "rembg"], default="threshold", help="Background removal method.")
    parser.add_argument(
        "--model",
        type=str,
        default="u2net",
        choices=["u2net", "u2netp", "u2net_human_seg", "u2net_cloth_seg", "silueta"],
        help="rembg model name",
    )
    parser.add_argument("--mask-blur", type=int, default=0, help="Gaussian blur radius for alpha mask smoothing (odd kernel size will be computed).")
    parser.add_argument("--mask-erode", type=int, default=0, help="Erode iterations on alpha mask (shrinks subject).")
    parser.add_argument("--mask-dilate", type=int, default=0, help="Dilate iterations on alpha mask (expands subject).")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    remove_background(
        args.input,
        args.output,
        bg_color=tuple(args.bg),
        tolerance=args.tolerance,
        max_frames=args.max_frames,
        method=args.method,
        model=args.model,
        mask_blur=args.mask_blur,
        mask_erode=args.mask_erode,
        mask_dilate=args.mask_dilate,
    )
    print(f"Saved transparent GIF to {args.output}")


def _refine_alpha(rgba: np.ndarray, blur: int = 0, erode: int = 0, dilate: int = 0) -> np.ndarray:
    """Optional post-process on alpha channel to reduce jaggies/halos."""
    if rgba.shape[2] < 4:
        return rgba
    if not rgba.flags.writeable:
        rgba = np.array(rgba, copy=True)
    alpha = rgba[:, :, 3]
    # Erode/dilate with 3x3 kernel
    kernel = np.ones((3, 3), np.uint8)
    if erode > 0:
        alpha = cv2.erode(alpha, kernel, iterations=erode)
    if dilate > 0:
        alpha = cv2.dilate(alpha, kernel, iterations=dilate)
    if blur > 0:
        k = max(1, blur * 2 + 1)  # ensure odd
        alpha = cv2.GaussianBlur(alpha, (k, k), 0)
    rgba[:, :, 3] = alpha
    return rgba


if __name__ == "__main__":
    main()
