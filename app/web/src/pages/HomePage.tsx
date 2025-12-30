import { Clip, GoalMetric, Notice, RadioItem } from "../types";
import { Section } from "../components/Section";
import { NoticeCard } from "../components/NoticeCard";
import { ClipCard } from "../components/ClipCard";
import { RadioItemCard } from "../components/RadioItem";
import { GoalBar } from "../components/GoalBar";

interface Props {
  notices: Notice[];
  radioItems: RadioItem[];
  goalMetrics: GoalMetric[];
  hotClips: Clip[];
}

export function HomePage({ notices, radioItems, goalMetrics, hotClips }: Props) {
  return (
    <div className="space-y-6">
      <div className="card px-6 py-5 flex items-center justify-between">
        <div className="text-2xl font-semibold text-slate-900">유후의 비밀 기지</div>
      </div>

      <div className="grid grid-cols-[1.1fr_0.9fr] gap-6">
        <div className="flex flex-col gap-6">
          <Section icon="📢" title="최신 공지사항">
            <div className="flex flex-col gap-3">
              {notices.length === 0 ? (
                <div className="card p-4 text-slate-500">아직 공지가 없습니다.</div>
              ) : (
                notices.map((notice) => <NoticeCard key={notice.id} notice={notice} />)
              )}
            </div>
          </Section>

          <Section icon="🎵" title="다시듣기 / 라디오">
            <div className="flex flex-col gap-2">
              {radioItems.map((item) => (
                <RadioItemCard key={item.id} item={item} />
              ))}
            </div>
          </Section>

          <Section icon="🏁" title="목표 달성 현황">
            <div className="flex flex-col gap-4">
              {goalMetrics.map((metric) => (
                <GoalBar key={metric.id} metric={metric} />
              ))}
            </div>
          </Section>
        </div>

        <div className="flex flex-col gap-4">
          <Section icon="🔥" title="핫클립 (하이라이트)">
            {hotClips.length === 0 ? (
              <div className="card p-10 text-slate-400 text-center">핫클립 썸네일을 추가해주세요.</div>
            ) : (
              <div className="flex flex-col gap-4">
                {hotClips.map((clip) => (
                  <ClipCard key={clip.id} clip={clip} />
                ))}
              </div>
            )}
          </Section>
        </div>
      </div>
    </div>
  );
}
