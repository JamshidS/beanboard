import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getLeaderboard, listBeans } from "../api";
import type { Bean, BeanScore, Roast } from "../types";
import AddBeanForm from "../components/AddBeanForm";
import BeanCard from "../components/BeanCard";
import RatingStars from "../components/RatingStars";

const FILTERS: { label: string; value: Roast | undefined }[] = [
  { label: "All", value: undefined },
  { label: "Light", value: "light" },
  { label: "Medium", value: "medium" },
  { label: "Dark", value: "dark" },
];

export default function BeansPage() {
  const [roast, setRoast] = useState<Roast | undefined>(undefined);
  const [beans, setBeans] = useState<Bean[] | null>(null);
  const [top, setTop] = useState<BeanScore[]>([]);
  const [error, setError] = useState<string | null>(null);

  const loadBeans = useCallback(() => {
    listBeans(roast)
      .then((data) => {
        setBeans(data);
        setError(null);
      })
      .catch((e: Error) => setError(e.message));
  }, [roast]);

  useEffect(loadBeans, [loadBeans]);

  useEffect(() => {
    getLeaderboard(3)
      .then(setTop)
      .catch(() => setTop([]));
  }, []);

  return (
    <>
      <section>
        <h2>Top rated</h2>
        <div className="top-strip">
          {top.map((s, i) => (
            <Link key={s.bean_id} to={`/beans/${s.bean_id}`} className="card top-card">
              <span className="rank">#{i + 1}</span>
              <div>
                <strong>{s.name}</strong>
                <div className="top-meta">
                  <RatingStars value={s.average_rating} />
                  <span className="muted small">
                    {s.average_rating?.toFixed(1) ?? "-"} ({s.review_count})
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      <section>
        <div className="toolbar">
          <h2>All beans</h2>
          <div className="chips">
            {FILTERS.map((f) => (
              <button
                key={f.label}
                type="button"
                className={f.value === roast ? "chip active" : "chip"}
                onClick={() => setRoast(f.value)}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>
        {error && <p className="status error">{error}</p>}
        {!error && beans === null && <p className="status">Loading beans...</p>}
        {beans && beans.length === 0 && <p className="status">No beans match this roast.</p>}
        {beans && (
          <div className="grid">
            {beans.map((b) => (
              <BeanCard key={b.id} bean={b} />
            ))}
          </div>
        )}
      </section>

      <AddBeanForm onCreated={loadBeans} />
    </>
  );
}
