import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { deleteReview, getBeanSummary, listReviews, updateBean } from "../api";
import type { BeanSummary, Review } from "../types";
import RatingStars from "../components/RatingStars";
import ReviewForm from "../components/ReviewForm";
import ReviewList from "../components/ReviewList";
import RoastBadge from "../components/RoastBadge";
import { REVIEW_SORT_OPTIONS, ReviewSortKey, sortReviews } from "../components/sortReviews";
import { formatPrice, splitNotes } from "../components/format";

export default function BeanDetailPage() {
  const beanId = Number(useParams().beanId);
  const [summary, setSummary] = useState<BeanSummary | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [price, setPrice] = useState("");
  const [sortKey, setSortKey] = useState<ReviewSortKey>("newest");
  const sortedReviews = useMemo(() => sortReviews(reviews, sortKey), [reviews, sortKey]);

  const load = useCallback(async () => {
    try {
      const [s, r] = await Promise.all([getBeanSummary(beanId), listReviews(beanId)]);
      setSummary(s);
      setReviews(r);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, [beanId]);

  useEffect(() => {
    load();
  }, [load]);

  async function savePrice(e: FormEvent) {
    e.preventDefault();
    try {
      await updateBean(beanId, { price_cents: Math.round(parseFloat(price) * 100) });
      setEditing(false);
      await load();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function remove(id: string) {
    try {
      await deleteReview(id);
      await load();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  const back = (
    <Link to="/" className="back">
      &larr; All beans
    </Link>
  );

  if (error && !summary)
    return (
      <>
        {back}
        <p className="status error">{error}</p>
      </>
    );
  if (!summary)
    return (
      <>
        {back}
        <p className="status">Loading...</p>
      </>
    );

  const { bean } = summary;
  return (
    <>
      {back}
      {error && <p className="status error">{error}</p>}
      <section className="card detail-hero">
        <div>
          <RoastBadge roast={bean.roast} />
          <h1>{bean.name}</h1>
          <p className="muted">
            {bean.roaster} &middot; {bean.origin}
          </p>
          <div className="tags">
            {splitNotes(bean.flavor_notes).map((n) => (
              <span key={n} className="tag">
                {n}
              </span>
            ))}
          </div>
          <div className="price-row">
            {editing ? (
              <form onSubmit={savePrice} className="inline-form">
                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  autoFocus
                  required
                />
                <button type="submit" className="btn">
                  Save
                </button>
                <button type="button" className="btn-link" onClick={() => setEditing(false)}>
                  Cancel
                </button>
              </form>
            ) : (
              <>
                <span className="price big">{formatPrice(bean.price_cents)}</span>
                <button
                  type="button"
                  className="btn-link"
                  onClick={() => {
                    setPrice((bean.price_cents / 100).toFixed(2));
                    setEditing(true);
                  }}
                >
                  Edit price
                </button>
              </>
            )}
          </div>
        </div>
        <div className="score">
          <div className="score-num">{summary.average_rating?.toFixed(1) ?? "-"}</div>
          <RatingStars value={summary.average_rating} size="lg" />
          <div className="muted small">
            {summary.review_count} review{summary.review_count === 1 ? "" : "s"}
          </div>
        </div>
      </section>

      <div className="detail-cols">
        <section>
          <div className="toolbar">
            <h2>Reviews</h2>
            {reviews.length > 0 && (
              <label className="sort-control">
                Sort by
                <select value={sortKey} onChange={(e) => setSortKey(e.target.value as ReviewSortKey)}>
                  {REVIEW_SORT_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </label>
            )}
          </div>
          <ReviewList reviews={sortedReviews} onDelete={remove} />
        </section>
        <section>
          <ReviewForm beanId={beanId} onCreated={load} />
        </section>
      </div>
    </>
  );
}
