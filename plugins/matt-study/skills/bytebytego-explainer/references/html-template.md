# HTML Template for ByteByteGo-Style Explainer

Use this as the base for every output. Replace all [PLACEHOLDERS].

---

## Full boilerplate (updated — includes all validated components)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[TOPIC TITLE] — ByteByteGo Style</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {
  --brand: #E50914;
  --accent: #F5A623;
  --bg: #0a0a0a;
  --bg2: #111111;
  --bg3: #1a1a1a;
  --bg4: #222222;
  --border: rgba(255,255,255,0.08);
  --border-mid: rgba(255,255,255,0.14);
  --text: #F0EEE9;
  --text2: #A09E98;
  --text3: #6B6966;
  --green: #22C55E;
  --blue: #3B82F6;
  --purple: #A855F7;
  --amber: #F59E0B;
  --teal: #14B8A6;
  --red: #EF4444;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: 'DM Sans', sans-serif; line-height: 1.7; font-size: 15px; }
.page { max-width: 780px; margin: 0 auto; padding: 48px 24px 80px; }

/* ── Hero ── */
.hero { border-left: 4px solid var(--brand); padding: 32px 28px; background: var(--bg2); border-radius: 4px; margin-bottom: 40px; }
.hero-tag { font-size: 11px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--brand); margin-bottom: 12px; }
.hero h1 { font-size: 28px; font-weight: 700; line-height: 1.25; margin-bottom: 14px; color: var(--text); }
.hero p { color: var(--text2); font-size: 15px; max-width: 600px; }
.hero-meta { display: flex; gap: 20px; margin-top: 20px; flex-wrap: wrap; }
.hero-meta span { font-size: 12px; color: var(--text3); font-family: 'DM Mono', monospace; }
.hero-meta strong { color: var(--text2); }

/* ── Table of Contents ── */
.toc { background: var(--bg2); border: 1px solid var(--border); border-radius: 6px; padding: 24px 28px; margin-bottom: 48px; }
.toc h3 { font-size: 12px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text3); margin-bottom: 16px; }
.toc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 24px; }
.toc-item { display: flex; align-items: center; gap: 10px; font-size: 13px; color: var(--text2); }
.toc-num { font-family: 'DM Mono', monospace; font-size: 11px; color: var(--brand); min-width: 20px; }

/* ── Section ── */
.section { margin-bottom: 56px; }
.section-header { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; }
.section-badge { background: var(--brand); color: white; font-size: 11px; font-weight: 700; width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-family: 'DM Mono', monospace; }
.section h2 { font-size: 20px; font-weight: 700; color: var(--text); }
.section p { color: var(--text2); margin-bottom: 14px; font-size: 15px; }
.section p strong { color: var(--text); }

/* ── Divider ── */
.divider { border: none; border-top: 1px solid var(--border); margin: 48px 0; }

/* ── Stat cards ── */
.stat-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 24px 0; }
.stat-card { background: var(--bg3); border: 1px solid var(--border); border-radius: 6px; padding: 18px 16px; text-align: center; }
.stat-val { font-size: 22px; font-weight: 700; color: var(--text); font-family: 'DM Mono', monospace; }
.stat-val span { color: var(--brand); }
.stat-label { font-size: 11px; color: var(--text3); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.08em; }

/* ── Amber callout ── */
.callout { border-left: 3px solid var(--accent); background: rgba(245,166,35,0.07); padding: 16px 20px; border-radius: 0 6px 6px 0; margin: 20px 0; }
.callout-label { font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent); margin-bottom: 6px; }
.callout p { color: var(--text2); font-size: 14px; margin: 0; line-height: 1.6; }
.callout p strong { color: var(--accent); }

/* ── Comparison table ── */
.compare-table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 13px; }
.compare-table th { text-align: left; padding: 10px 14px; background: var(--bg3); color: var(--text3);
                    font-weight: 500; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em;
                    border-bottom: 1px solid var(--border); }
.compare-table td { padding: 10px 14px; border-bottom: 1px solid var(--border); color: var(--text2); vertical-align: top; line-height: 1.5; }
.compare-table td:first-child { color: var(--text); font-weight: 600; }
.compare-table tr:last-child td { border-bottom: none; }

/* ── Badges / Tags ── */
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; font-family: 'DM Mono', monospace; }
.badge-green { background: rgba(34,197,94,0.12); color: var(--green); }
.badge-red   { background: rgba(239,68,68,0.12); color: var(--red); }
.badge-blue  { background: rgba(59,130,246,0.12); color: var(--blue); }
.badge-amber { background: rgba(245,158,11,0.12); color: var(--amber); }
.badge-purple{ background: rgba(168,85,247,0.12); color: var(--purple); }

/* ── Pill list (tech tags) ── */
.pill-list { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0; }
.pill { background: var(--bg3); border: 1px solid var(--border); border-radius: 4px; padding: 5px 12px; font-size: 12px; color: var(--text2); font-family: 'DM Mono', monospace; }

/* ── Priority stack ── */
.priority-stack { display: flex; flex-direction: column; gap: 8px; margin: 20px 0; }
.priority-item { display: flex; align-items: center; gap: 12px; background: var(--bg3);
                 border: 1px solid var(--border); border-radius: 8px; padding: 12px 16px; }
.priority-rank { font-size: 11px; font-weight: 700; color: var(--text3); width: 24px; font-family: 'DM Mono', monospace; }
.priority-bar { height: 4px; border-radius: 2px; flex-shrink: 0; }
.priority-info .label { font-size: 13px; font-weight: 600; color: var(--text); }
.priority-info .sub { font-size: 12px; color: var(--text3); margin-top: 2px; }

/* ── Outro ── */
.outro { border-left: 3px solid var(--teal); background: rgba(20,184,166,0.07); padding: 24px 28px; border-radius: 0 6px 6px 0; margin-top: 48px; }
.outro-label { font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--teal); margin-bottom: 10px; }
.outro p { color: var(--text2); font-size: 15px; }

@media (max-width: 600px) {
  .stat-row { grid-template-columns: 1fr 1fr; }
  .toc-grid { grid-template-columns: 1fr; }
  .hero h1 { font-size: 22px; }
}
</style>
</head>
<body>
<div class="page">

  <!-- HERO -->
  <div class="hero">
    <div class="hero-tag">ByteByteGo · [Category]</div>
    <h1>[TITLE LINE 1]<br>[TITLE LINE 2 — optional]</h1>
    <p>[1–2 sentence hook. Sharp contrast or bold question. What makes this topic interesting/hard?]</p>
    <div class="hero-meta">
      <span><strong>[N]</strong> [unit — e.g. pages / topics / patterns]</span>
      <span><strong>[N]</strong> [another stat]</span>
      <span><strong>[N]</strong> [another stat]</span>
    </div>
  </div>

  <!-- TABLE OF CONTENTS -->
  <div class="toc">
    <h3>In This Issue</h3>
    <div class="toc-grid">
      <div class="toc-item"><span class="toc-num">01</span>[Sub-topic 1]</div>
      <div class="toc-item"><span class="toc-num">02</span>[Sub-topic 2]</div>
      <div class="toc-item"><span class="toc-num">03</span>[Sub-topic 3]</div>
      <div class="toc-item"><span class="toc-num">04</span>[Sub-topic 4]</div>
      <div class="toc-item"><span class="toc-num">05</span>[Sub-topic 5]</div>
      <div class="toc-item"><span class="toc-num">06</span>[Sub-topic 6]</div>
    </div>
  </div>

  <!-- SECTION 1 -->
  <div class="section">
    <div class="section-header">
      <div class="section-badge">01</div>
      <h2>[Section 1 title — 5–8 words]</h2>
    </div>
    <p>[Analogy paragraph — familiar mental model first]</p>
    <p>[Technical detail paragraph — with <strong>bolded key term</strong>]</p>

    <!-- SVG diagram — always inline with background + border-radius -->
    <svg viewBox="0 0 680 [H]" xmlns="http://www.w3.org/2000/svg"
         style="width:100%;margin:24px 0;display:block;background:#111;border-radius:8px;">
      <defs>
        <marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="rgba(255,255,255,0.3)"/>
        </marker>
      </defs>
      <!-- diagram content -->
    </svg>

    <div class="callout">
      <div class="callout-label">Key Insight</div>
      <p>[1–2 sentence insight that makes this section click]</p>
    </div>
  </div>

  <hr class="divider">

  <!-- SECTION 2 — comparison table example -->
  <div class="section">
    <div class="section-header">
      <div class="section-badge">02</div>
      <h2>[Section 2 title]</h2>
    </div>
    <p>[Hook + analogy]</p>

    <table class="compare-table">
      <thead>
        <tr><th>[Col 1]</th><th>[Col 2]</th><th>[Col 3]</th><th>[Col 4]</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>[Item A]</td>
          <td>[detail]</td>
          <td><span class="badge badge-blue">[tag]</span></td>
          <td>[trade-off]</td>
        </tr>
      </tbody>
    </table>
  </div>

  <hr class="divider">

  <!-- SECTION 3 — stat cards example -->
  <div class="section">
    <div class="section-header">
      <div class="section-badge">03</div>
      <h2>[Section 3 title]</h2>
    </div>
    <p>[Hook + analogy]</p>

    <div class="stat-row">
      <div class="stat-card">
        <div class="stat-val">[N]<span>[unit]</span></div>
        <div class="stat-label">[what this measures]</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">[N]<span>[unit]</span></div>
        <div class="stat-label">[what this measures]</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">[N]<span>[unit]</span></div>
        <div class="stat-label">[what this measures]</div>
      </div>
    </div>
  </div>

  <hr class="divider">

  <!-- REPEAT SECTIONS following the same pattern -->

  <!-- OUTRO -->
  <div class="outro">
    <div class="outro-label">Over to you</div>
    <p>[Engagement question relating to the reader's own systems or decisions]</p>
  </div>

</div>
</body>
</html>
```

---

## Component snippets

### 2-column stat row (for 2 metrics)
```html
<div class="stat-row" style="grid-template-columns: repeat(2, 1fr);">
  ...
</div>
```

### Inline code style
```html
<code style="background:var(--bg3);border:1px solid var(--border);padding:1px 6px;border-radius:4px;font-family:'DM Mono',monospace;font-size:0.85em;color:var(--text);">GET /segment/42</code>
```

### Two-column layout (text + diagram side by side)
```html
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;align-items:start;margin:24px 0;">
  <div>
    <p>[text content]</p>
  </div>
  <svg viewBox="0 0 300 200" style="width:100%;background:#111;border-radius:8px;">
    <!-- mini diagram -->
  </svg>
</div>
```

### Pill list
```html
<div class="pill-list">
  <span class="pill">Redis</span>
  <span class="pill">Kafka</span>
  <span class="pill">PostgreSQL</span>
  <span class="pill">gRPC</span>
</div>
```

### Priority stack
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
</div>
```
