import { BUCKET_BADGE_CLASS } from "../masteryDisplay";

const NODE_WIDTH = 150;
const NODE_HEIGHT = 56;
const COL_GAP = 32;
const ROW_HEIGHT = 96;

// Depth = how many prerequisite "hops" separate a topic from a topic with no prerequisites.
// Used purely for laying the graph out in rows -- unrelated to the backend's own DAG walk.
function computeDepths(topics) {
  const topicById = new Map(topics.map((t) => [t.id, t]));
  const depthById = new Map();

  function depthOf(topicId, visiting) {
    if (depthById.has(topicId)) return depthById.get(topicId);
    if (visiting.has(topicId)) return 0; // cycle guard: malformed prerequisite data shouldn't recurse forever
    visiting.add(topicId);

    const topic = topicById.get(topicId);
    const prereqDepths = (topic?.prerequisite_ids ?? [])
      .filter((id) => topicById.has(id)) // ignore references to topics that no longer exist
      .map((id) => depthOf(id, visiting));
    const depth = prereqDepths.length ? Math.max(...prereqDepths) + 1 : 0;

    depthById.set(topicId, depth);
    return depth;
  }

  topics.forEach((t) => depthOf(t.id, new Set()));
  return depthById;
}

// Lays out each depth level as a centered row, so a single root sits above its branching children.
function layoutNodes(topics) {
  const depthById = computeDepths(topics);
  const rows = new Map();
  for (const topic of [...topics].sort((a, b) => a.id - b.id)) {
    const depth = depthById.get(topic.id);
    if (!rows.has(depth)) rows.set(depth, []);
    rows.get(depth).push(topic);
  }

  const rowWidth = (count) => count * NODE_WIDTH + (count - 1) * COL_GAP;
  const totalWidth = Math.max(...[...rows.values()].map((row) => rowWidth(row.length)));

  const positionById = new Map();
  for (const [depth, row] of rows) {
    const offsetX = (totalWidth - rowWidth(row.length)) / 2;
    row.forEach((topic, i) => {
      positionById.set(topic.id, { x: offsetX + i * (NODE_WIDTH + COL_GAP), y: depth * ROW_HEIGHT });
    });
  }

  const maxDepth = Math.max(...rows.keys());
  return { positionById, width: totalWidth, height: maxDepth * ROW_HEIGHT + NODE_HEIGHT };
}

function nodeClasses(bucket) {
  const bg = bucket ? BUCKET_BADGE_CLASS[bucket] : "bg-secondary";
  return bg.includes("text-") ? bg : `${bg} text-white`;
}

const LEGEND_ITEMS = [
  { label: "Advanced", swatchClass: "bg-success" },
  { label: "Average", swatchClass: "bg-warning" },
  { label: "Struggling", swatchClass: "bg-danger" },
  { label: "Not yet attempted", swatchClass: "bg-secondary" },
  { label: "Recommended next", swatchClass: "border border-3 border-primary" },
];

function TopicMap({ topics, progressRows, nextTopicId }) {
  if (topics.length === 0) return null;

  const progressByTopic = new Map(progressRows.map((r) => [r.topic_id, r]));
  const { positionById, width, height } = layoutNodes(topics);

  return (
    <div className="card mb-4 shadow-sm">
      <div className="card-body">
        <h2 className="h6 text-muted mb-3">Learning Path</h2>

        <div className="position-relative mb-3" style={{ width, height }}>
          <svg width={width} height={height} className="position-absolute top-0 start-0">
            {topics.flatMap((topic) =>
              topic.prerequisite_ids
                .filter((prereqId) => positionById.has(prereqId))
                .map((prereqId) => {
                  const from = positionById.get(prereqId);
                  const to = positionById.get(topic.id);
                  return (
                    <line
                      key={`${prereqId}-${topic.id}`}
                      x1={from.x + NODE_WIDTH / 2}
                      y1={from.y + NODE_HEIGHT}
                      x2={to.x + NODE_WIDTH / 2}
                      y2={to.y}
                      stroke="var(--bs-border-color)"
                      strokeWidth={2}
                    />
                  );
                }),
            )}
          </svg>

          {topics.map((topic) => {
            const pos = positionById.get(topic.id);
            const progress = progressByTopic.get(topic.id);
            const isNext = topic.id === nextTopicId;
            const title = progress
              ? `${topic.name}: ${Math.round(progress.score * 100)}% (${progress.bucket})`
              : `${topic.name}: not yet attempted`;

            return (
              <div
                key={topic.id}
                title={title}
                className={`position-absolute d-flex align-items-center justify-content-center text-center rounded-3 px-2 ${nodeClasses(progress?.bucket)} ${isNext ? "border border-3 border-primary" : ""}`}
                style={{ left: pos.x, top: pos.y, width: NODE_WIDTH, height: NODE_HEIGHT, fontSize: "0.8rem" }}
              >
                {topic.name}
              </div>
            );
          })}
        </div>

        <div className="d-flex flex-wrap gap-3 small text-muted">
          {LEGEND_ITEMS.map(({ label, swatchClass }) => (
            <span key={label} className="d-inline-flex align-items-center gap-1">
              <span
                className={`d-inline-block rounded-1 ${swatchClass}`}
                style={{ width: "0.9rem", height: "0.9rem" }}
              />
              {label}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

export default TopicMap;