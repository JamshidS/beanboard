import { Link } from "react-router-dom";
import type { Bean } from "../types";
import RoastBadge from "./RoastBadge";
import { formatPrice, splitNotes } from "./format";

export default function BeanCard({ bean }: { bean: Bean }) {
  return (
    <Link to={`/beans/${bean.id}`} className="card bean-card">
      <div className="bean-card-top">
        <RoastBadge roast={bean.roast} />
        <span className="price">{formatPrice(bean.price_cents)}</span>
      </div>
      <h3>{bean.name}</h3>
      <p className="muted">
        {bean.roaster} &middot; {bean.origin}
      </p>
      <div className="tags">
        {splitNotes(bean.flavor_notes).map((note) => (
          <span key={note} className="tag">
            {note}
          </span>
        ))}
      </div>
    </Link>
  );
}
