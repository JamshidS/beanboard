interface Props {
  value: number | null;
  size?: "sm" | "lg";
}

export default function RatingStars({ value, size = "sm" }: Props) {
  const filled = Math.round(value ?? 0);
  return (
    <span
      className={`stars stars-${size}`}
      aria-label={value === null ? "No ratings yet" : `${value} out of 5`}
    >
      {[1, 2, 3, 4, 5].map((n) => (
        <span key={n} className={n <= filled ? "star on" : "star"}>
          &#9733;
        </span>
      ))}
    </span>
  );
}
