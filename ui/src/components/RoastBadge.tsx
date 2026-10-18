import type { Roast } from "../types";

export default function RoastBadge({ roast }: { roast: Roast }) {
  return <span className={`badge badge-${roast}`}>{roast}</span>;
}
