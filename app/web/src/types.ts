export type Page = "home" | "inventory" | "settings";

export interface Notice {
  id: string;
  title: string;
  content: string;
  createdAt: string;
}

export interface Clip {
  id: string;
  title: string;
  views: string;
  duration: string;
  thumbnail: string;
}

export interface Stream {
  id: string;
  title: string;
  date: string;
  length: string;
}

export interface RadioItem {
  id: string;
  title: string;
  date: string;
  length: string;
}

export interface GoalMetric {
  id: string;
  label: string;
  current: number;
  target: number;
  unit: string;
}

export interface Item {
  id: string;
  name: string;
  image: string;
  price?: string;
  status: "owned" | "locked";
  equipped?: boolean;
  category: "skin" | "motion";
}
