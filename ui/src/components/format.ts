export const formatPrice = (cents: number) => `$${(cents / 100).toFixed(2)}`;

export const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });

export const splitNotes = (notes: string) =>
  notes
    .split(",")
    .map((n) => n.trim())
    .filter(Boolean);
