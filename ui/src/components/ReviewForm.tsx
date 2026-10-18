import { FormEvent, useState } from "react";
import { createReview } from "../api";

export default function ReviewForm({ beanId, onCreated }: { beanId: number; onCreated: () => void }) {
  const [author, setAuthor] = useState("");
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (rating === 0) {
      setError("Pick a star rating first.");
      return;
    }
    setError(null);
    try {
      await createReview(beanId, { author, rating, comment });
      setAuthor("");
      setRating(0);
      setComment("");
      onCreated();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <form onSubmit={submit} className="card review-form">
      <h3>Leave a review</h3>
      <label>
        Your name
        <input value={author} maxLength={60} onChange={(e) => setAuthor(e.target.value)} required />
      </label>
      <div className="star-picker" role="radiogroup" aria-label="Rating">
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            type="button"
            className={n <= rating ? "star-btn on" : "star-btn"}
            aria-label={`${n} star${n > 1 ? "s" : ""}`}
            onClick={() => setRating(n)}
          >
            &#9733;
          </button>
        ))}
      </div>
      <label>
        Tasting notes
        <textarea rows={3} maxLength={500} value={comment} onChange={(e) => setComment(e.target.value)} />
      </label>
      <div className="form-actions">
        <button type="submit" className="btn">
          Post review
        </button>
        {error && <span className="error">{error}</span>}
      </div>
    </form>
  );
}
