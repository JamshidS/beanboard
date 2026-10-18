import type { Review } from "../types";

export type ReviewSortKey = "newest" | "oldest" | "highest" | "lowest" | "author";

export const REVIEW_SORT_OPTIONS: { value: ReviewSortKey; label: string }[] = [
  { value: "newest", label: "Newest first" },
  { value: "oldest", label: "Oldest first" },
  { value: "highest", label: "Highest rating" },
  { value: "lowest", label: "Lowest rating" },
  { value: "author", label: "Author A\u2013Z" },
];

const time = (r: Review) => new Date(r.created_at).getTime() || 0;
const byId = (a: Review, b: Review) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
const newestFirst = (a: Review, b: Review) => time(b) - time(a) || byId(a, b);

/** Returns a sorted copy; never mutates the input. */
export function sortReviews(reviews: Review[], key: ReviewSortKey): Review[] {
  const out = [...reviews];
  switch (key) {
    case "newest":
      return out.sort((a, b) => time(b) - time(a) || byId(a, b));
    case "oldest":
      return out.sort((a, b) => time(a) - time(b) || byId(a, b));
    case "highest":
      return out.sort((a, b) => b.rating - a.rating || newestFirst(a, b));
    case "lowest":
      return out.sort((a, b) => a.rating - b.rating || newestFirst(a, b));
    case "author":
      return out.sort(
        (a, b) =>
          a.author.localeCompare(b.author, undefined, { sensitivity: "base" }) || newestFirst(a, b),
      );
  }
}
