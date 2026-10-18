import type { Review } from "../types";
import RatingStars from "./RatingStars";
import { formatDate } from "./format";

interface Props {
  reviews: Review[];
  onDelete: (id: string) => void;
}

export default function ReviewList({ reviews, onDelete }: Props) {
  if (reviews.length === 0) return <p className="muted">No reviews yet. Be the first!</p>;
  return (
    <ul className="reviews">
      {reviews.map((r) => (
        <li key={r.id} className="card review">
          <div className="review-head">
            <strong>{r.author}</strong>
            <RatingStars value={r.rating} />
            <span className="muted small">{formatDate(r.created_at)}</span>
            <button type="button" className="btn-link danger" onClick={() => onDelete(r.id)}>
              Delete
            </button>
          </div>
          {r.comment && <p>{r.comment}</p>}
        </li>
      ))}
    </ul>
  );
}
