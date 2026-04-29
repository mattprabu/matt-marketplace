# ByteByteGo Diagram Patterns

All diagrams use the dark theme. viewBox="0 0 680 H". DM Sans font.
SVGs are always rendered inline with: `style="width:100%;margin:24px 0;display:block;background:#111;border-radius:8px;"`

---

## When to use which pattern

| Situation | Pattern |
|-----------|---------|
| Services talking to each other | Flow diagram (SVG) |
| A → B → C pipeline | Flow diagram (SVG) |
| A vs B vs C comparison | Comparison table (HTML) |
| 2–4 key metrics / numbers | Stat cards (HTML) |
| Important insight / caveat | Amber callout box (HTML) |
| Things inside things | Structural/containment diagram (SVG) |
| Priority or ranking | Priority stack list (HTML) |
| Decision logic (if/else) | Decision flow diagram (SVG) |
| Problem → Solution pairs | Two-row grid diagram (SVG) |

---

## Standard arrow marker (include in every SVG with arrows)

```svg
<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="rgba(255,255,255,0.3)"/>
  </marker>
</defs>
```

Use on lines: `marker-end="url(#arr)"`

---

## Pattern 1: Flow diagram (SVG)

Use for request lifecycles, data pipelines, auth flows, encoding chains.

Node colors by role:
- Input/client nodes: amber `rgba(245,158,11,0.12)` / `stroke rgba(245,158,11,0.35)`
- Processing nodes: blue `rgba(59,130,246,0.12)` / `stroke rgba(59,130,246,0.35)`
- Core/origin nodes: red `rgba(229,9,20,0.12)` / `stroke rgba(229,9,20,0.35)`
- Output/CDN nodes: green `rgba(34,197,94,0.12)` / `stroke rgba(34,197,94,0.35)`
- Storage nodes: purple `rgba(168,85,247,0.12)` / `stroke rgba(168,85,247,0.35)`

Node sizing:
- Single-line: width=110–140, height=44, rx=8
- Two-line: width=110–140, height=56, rx=8
- Container box: larger rect, dashed border, label at top

Text:
- Title: font-size="12" font-weight="600" — use node's accent color
- Subtitle: font-size="10" — #A09E98

Arrow style:
- Solid arrow: stroke=rgba(255,255,255,0.15), stroke-width="1", marker-end="url(#arr)"
- Dashed arrow: stroke-dasharray="4 3"
- Label above arrow: font-size="9" font-family="DM Mono" fill="#6B6966"

Layout rules:
- Left-to-right OR top-to-bottom — never diagonal primary flow
- 30–40px gap between nodes
- Safe area: x=20 to x=660, y=20 to y=(H-20)
- Max 5–6 nodes per diagram

---

## Pattern 2: Problem/Solution two-row grid (SVG)

Use when showing N problems with their corresponding solutions.
This is the validated pattern from the cache failure diagram.

Structure:
- Row 1 (y≈20): Problem nodes — each colored by problem type
- Separator label (y≈125): "SOLUTIONS" text in var(--text3)
- Row 2 (y≈148): Solution nodes — all in green rgba(34,197,94,0.07)
- Connecting vertical arrows between each problem and its solution

```svg
<svg viewBox="0 0 680 220" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;margin:24px 0;display:block;background:#111;border-radius:8px;">
  <defs>
    <marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="rgba(255,255,255,0.3)"/>
    </marker>
  </defs>

  <!-- Problem row (4 problems, evenly spaced) -->
  <rect x="20"  y="20" width="145" height="64" rx="6" fill="rgba(239,68,68,0.1)"   stroke="rgba(239,68,68,0.35)"   stroke-width="0.8"/>
  <text x="92"  y="46" text-anchor="middle" font-family="DM Sans" font-size="12" font-weight="600" fill="#EF4444">[Problem 1]</text>
  <text x="92"  y="64" text-anchor="middle" font-family="DM Sans" font-size="10" fill="#A09E98">[subtitle line 1]</text>
  <text x="92"  y="78" text-anchor="middle" font-family="DM Sans" font-size="10" fill="#A09E98">[subtitle line 2]</text>

  <!-- ... repeat for problems 2, 3, 4 at x=185, x=350, x=515 -->

  <!-- SOLUTIONS label -->
  <text x="340" y="130" text-anchor="middle" font-family="DM Sans" font-size="11" fill="#6B6966" letter-spacing="0.08em">SOLUTIONS</text>

  <!-- Solution row -->
  <rect x="20"  y="148" width="145" height="54" rx="6" fill="rgba(34,197,94,0.07)" stroke="rgba(34,197,94,0.25)" stroke-width="0.8"/>
  <text x="92"  y="170" text-anchor="middle" font-family="DM Sans" font-size="10" fill="#22C55E">[Fix line 1]</text>
  <text x="92"  y="188" text-anchor="middle" font-family="DM Sans" font-size="10" fill="#A09E98">[Fix line 2]</text>

  <!-- ... repeat for solutions 2, 3, 4 -->

  <!-- Connecting arrows (problem bottom → solution top) -->
  <line x1="92" y1="85" x2="92" y2="145" stroke="rgba(255,255,255,0.15)" stroke-width="1" marker-end="url(#arr)"/>
  <!-- ... repeat for others -->
</svg>
```

Node x positions for 4 columns (width=145, gap=20):
- Col 1: x=20,  center=92
- Col 2: x=185, center=257
- Col 3: x=350, center=422
- Col 4: x=515, center=587

---

## Pattern 3: Stat cards (HTML)

Use when you have 2–4 concrete numbers to highlight.

```html
<div class="stat-row">
  <div class="stat-card">
    <div class="stat-val">25<span>ms</span></div>
    <div class="stat-label">Median write latency</div>
  </div>
  <div class="stat-card">
    <div class="stat-val">65<span>M</span></div>
    <div class="stat-label">Peak concurrent streams</div>
  </div>
  <div class="stat-card">
    <div class="stat-val">4.5<span>x</span></div>
    <div class="stat-label">Throughput improvement</div>
  </div>
</div>
```

---

## Pattern 4: Amber callout box (HTML)

Two variants — with and without explicit label:

### With label (preferred for strong emphasis):
```html
<div class="callout">
  <div class="callout-label">Key Insight</div>
  <p>Hot keys drive 80% of cache queries. Never set an expiration on them — stale is infinitely better than a database stampede at 3am.</p>
</div>
```

### Classic inline bold:
```html
<div class="callout">
  <p><strong>Key insight:</strong> The URL for the PUT matches the GET URL exactly. Simple storage + retrieval — the intelligence is in what happens when both pipelines disagree.</p>
</div>
```

---

## Pattern 5: Comparison table (HTML)

Use for CPU vs GPU vs TPU style, or comparing 3–4 options side by side.

```html
<table class="compare-table">
  <thead>
    <tr>
      <th>Protocol</th>
      <th>Best For</th>
      <th>Transport</th>
      <th>Trade-off</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>REST</td>
      <td>Public APIs, CRUD</td>
      <td><span class="badge badge-blue">HTTP/1.1</span></td>
      <td>Simple but chatty — N+1 fetches</td>
    </tr>
    <tr>
      <td>gRPC</td>
      <td>Internal microservices</td>
      <td><span class="badge badge-green">HTTP/2</span></td>
      <td>Fast + typed but no browser native</td>
    </tr>
  </tbody>
</table>
```

---

## Pattern 6: Structural/containment diagram (SVG)

Use for "things inside things": VPC/subnet, CDN layers, storage stack.

Nesting convention:
- Outer container: large rect, rx=12, lightest fill, dashed or semi-transparent border
- Inner regions: medium rect, rx=7, slightly darker fill, solid border
- Label at top-left inside the container

---

## Pattern 7: Priority stack (HTML)

Use when ranking items by importance or showing degradation tiers.

```html
<div class="priority-stack">
  <div class="priority-item">
    <div class="priority-rank">P1</div>
    <div class="priority-bar" style="width:80px;background:#22C55E;"></div>
    <div class="priority-info">
      <div class="label">Origin writes</div>
      <div class="sub">Failure = broken stream for all viewers</div>
    </div>
  </div>
  <div class="priority-item">
    <div class="priority-rank">P2</div>
    <div class="priority-bar" style="width:55px;background:#F59E0B;"></div>
    <div class="priority-info">
      <div class="label">Live edge reads</div>
      <div class="sub">Failure = buffering for majority of clients</div>
    </div>
  </div>
  <div class="priority-item">
    <div class="priority-rank">P3</div>
    <div class="priority-bar" style="width:30px;background:#EF4444;"></div>
    <div class="priority-info">
      <div class="label">DVR reads</div>
      <div class="sub">Failure = only affects viewers rewinding</div>
    </div>
  </div>
</div>
```

---

## SVG text rules

- All text: `font-family="DM Sans"`
- Node title: `font-size="12" font-weight="600"` — use node's accent color
- Node subtitle: `font-size="10"` — fill="#A09E98"
- Section label: `font-size="11"` — fill="#6B6966" letter-spacing="0.08em"
- Arrow label: `font-size="9" font-family="DM Mono"` — fill="#6B6966"
- `text-anchor="middle"` for centered node text
- `dominant-baseline="central"` for vertical centering on single-line text

## viewBox height calculation

After placing all elements:
1. Find the bottom-most element: max(y + height)
2. Add 30px padding
3. Set that as H in `viewBox="0 0 680 H"`

Never guess — always compute from actual element positions.

## Safe area
- x range: 20 to 660
- y range: 20 to (H-20)
- Minimum node spacing: 20px gap between adjacent nodes
