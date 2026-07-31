export const BUCKET_BADGE_CLASS = {
  advanced: "bg-success",
  average: "bg-warning text-dark",
  struggling: "bg-danger",
};

export const TREND_ICON = {
  rising: " ↑",
  falling: " ↓",
  flat: "",
};

// Raw color values for chart libraries (SVG fill/stroke) that can't consume Bootstrap
// utility classes the way BUCKET_BADGE_CLASS's consumers do. Same semantics, different
// representation -- keep both here so they can't drift apart from being scattered.
export const BUCKET_CHART_COLOR = {
  advanced: "var(--bs-success)",
  average: "var(--bs-warning)",
  struggling: "var(--bs-danger)",
};