import type {
  Bean,
  BeanCreate,
  BeanScore,
  BeanStats,
  BeanSummary,
  BeanUpdate,
  Review,
  ReviewCreate,
  Roast,
} from "./types";

async function parse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      // keep the default message
    }
    throw new Error(message);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

const json = (body: unknown): RequestInit => ({
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export async function listBeans(roast?: Roast): Promise<Bean[]> {
  const params = new URLSearchParams(roast ? { roast } : {});
  const res = await fetch(`/api/catalog/beans?${params}`);
  return parse<Bean[]>(res);
}

export async function getBean(beanId: number): Promise<Bean> {
  const res = await fetch(`/api/catalog/beans/${beanId}`);
  return parse<Bean>(res);
}

export async function createBean(data: BeanCreate): Promise<Bean> {
  const res = await fetch(`/api/catalog/beans`, { method: "POST", ...json(data) });
  return parse<Bean>(res);
}

export async function updateBean(beanId: number, data: BeanUpdate): Promise<Bean> {
  const res = await fetch(`/api/catalog/beans/${beanId}`, { method: "PATCH", ...json(data) });
  return parse<Bean>(res);
}

export async function listReviews(beanId: number): Promise<Review[]> {
  const res = await fetch(`/api/reviews/beans/${beanId}`);
  return parse<Review[]>(res);
}

export async function createReview(beanId: number, data: ReviewCreate): Promise<Review> {
  const res = await fetch(`/api/reviews/beans/${beanId}`, { method: "POST", ...json(data) });
  return parse<Review>(res);
}

export async function deleteReview(reviewId: string): Promise<void> {
  const res = await fetch(`/api/reviews/${reviewId}`, { method: "DELETE" });
  return parse<void>(res);
}

export async function getReviewStats(): Promise<BeanStats[]> {
  const res = await fetch(`/api/reviews/stats`);
  return parse<BeanStats[]>(res);
}

export async function getLeaderboard(limit?: number): Promise<BeanScore[]> {
  const params = new URLSearchParams(limit ? { limit: String(limit) } : {});
  const res = await fetch(`/api/insights/leaderboard?${params}`);
  return parse<BeanScore[]>(res);
}

export async function getBeanSummary(beanId: number): Promise<BeanSummary> {
  const res = await fetch(`/api/insights/beans/${beanId}`);
  return parse<BeanSummary>(res);
}
