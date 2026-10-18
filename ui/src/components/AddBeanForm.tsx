import { FormEvent, useState } from "react";
import { createBean } from "../api";
import type { Roast } from "../types";

export default function AddBeanForm({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [roaster, setRoaster] = useState("");
  const [origin, setOrigin] = useState("");
  const [roast, setRoast] = useState<Roast>("medium");
  const [price, setPrice] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await createBean({
        name,
        roaster,
        origin,
        roast,
        price_cents: Math.round(parseFloat(price) * 100),
        flavor_notes: notes,
      });
      setName("");
      setRoaster("");
      setOrigin("");
      setPrice("");
      setNotes("");
      setOpen(false);
      onCreated();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <section className="card add-bean">
      <button type="button" className="btn btn-ghost" onClick={() => setOpen(!open)}>
        {open ? "Close" : "+ Add a bean"}
      </button>
      {open && (
        <form onSubmit={submit} className="form-grid">
          <label>
            Name
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </label>
          <label>
            Roaster
            <input value={roaster} onChange={(e) => setRoaster(e.target.value)} required />
          </label>
          <label>
            Origin
            <input value={origin} onChange={(e) => setOrigin(e.target.value)} required />
          </label>
          <label>
            Roast
            <select value={roast} onChange={(e) => setRoast(e.target.value as Roast)}>
              <option value="light">Light</option>
              <option value="medium">Medium</option>
              <option value="dark">Dark</option>
            </select>
          </label>
          <label>
            Price (USD)
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              required
            />
          </label>
          <label>
            Flavor notes
            <input
              value={notes}
              placeholder="comma, separated, notes"
              onChange={(e) => setNotes(e.target.value)}
            />
          </label>
          <div className="form-actions">
            <button type="submit" className="btn">
              Save bean
            </button>
            {error && <span className="error">{error}</span>}
          </div>
        </form>
      )}
    </section>
  );
}
