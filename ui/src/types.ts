export type Roast = "light" | "medium" | "dark";

export interface Bean {
  id: number;
  name: string;
  roaster: string;
  origin: string;
  roast: Roast;
  price_cents: number;
  flavor_notes: string;
  created_at: string;
}

export interface BeanCreate {
  name: string;
  roaster: string;
  origin: string;
  roast: Roast;
  price_cents: number;
  flavor_notes?: string;
}

export type BeanUpdate = Partial<BeanCreate>;

export interface Review {
  id: string;
  bean_id: number;
  author: string;
  rating: number;
  comment: string;
  created_at: string;
}

export interface ReviewCreate {
  author: string;
  rating: number;
  comment?: string;
}

export interface BeanStats {
  bean_id: number;
  average_rating: number;
  review_count: number;
}

export interface BeanScore {
  bean_id: number;
  name: string;
  roaster: string;
  roast: Roast;
  average_rating: number | null;
  review_count: number;
}

export interface BeanSummary {
  bean: Bean;
  average_rating: number | null;
  review_count: number;
  latest_reviews: Review[];
}
