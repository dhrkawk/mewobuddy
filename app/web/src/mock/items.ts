import { Item } from "../types";

const placeholder = "assets/placeholders/asset_placeholder.svg";

export const ownedItems: Item[] = [
  {
    id: "skin-1",
    name: "기본",
    image: "media/skins/cute.png",
    status: "owned",
    equipped: true,
    category: "skin",
  },
  {
    id: "skin-2",
    name: "교복",
    image: "media/skins/school.png",
    status: "owned",
    category: "skin",
  },
  {
    id: "motion-1",
    name: "웃음",
    image: placeholder,
    status: "owned",
    equipped: true,
    category: "motion",
  },
  {
    id: "motion-2",
    name: "하트",
    image: placeholder,
    status: "owned",
    category: "motion",
  },
];

export const shopItems: Item[] = [
  {
    id: "skin-shop-1",
    name: "제복",
    price: "₩499",
    image: "media/skins/suit.png",
    status: "locked",
    category: "skin",
  },
  {
    id: "skin-shop-2",
    name: "서큐버스",
    price: "₩299",
    image: "media/skins/devil.png",
    status: "locked",
    category: "skin",
  },
  {
    id: "motion-shop-1",
    name: "깜짝",
    price: "₩199",
    image: "media/motions/laugh.gif",
    status: "locked",
    category: "motion",
  },
];
