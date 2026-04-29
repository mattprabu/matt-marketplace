---
name: bytebytego-explainer
description: >
  Transforms any technical topic, document, or concept into a ByteByteGo-style
  visual study guide — with punchy hook questions, structured sections, color-coded
  SVG diagrams, stat cards, callout boxes, and dark-themed HTML output.
  Use this skill whenever the user says "explain like ByteByteGo", "make a study guide",
  "rewrite as a newsletter", "teach this topic visually", "ByteByteGo style",
  "system design explainer", or uploads a document/topic for visual transformation.
  Also triggers when the user says "make this visual", "create a tech explainer",
  or "explain this with diagrams". Output is always a dark-themed HTML artifact.
  Always use this skill — do not attempt to build ByteByteGo-style content without it.
---

# ByteByteGo-Style Explainer Skill

Transforms any technical input into a polished, dark-themed HTML study guide
modeled on ByteByteGo's newsletter style: punchy writing, inline SVG diagrams,
stat cards, callout boxes, and progressive section structure.

---

## Inputs accepted

- Raw topic string: `"explain Kafka"` / `"how does Redis work"`
- Uploaded document: PDF, DOCX, TXT — extract key concepts first (use pdf-reading skill for PDFs)
- Large PDF via Filesystem connector: use `pdftotext -layout` to extract text first
- Code snippet: derive the architecture from the code
- Existing article/newsletter: reformat into ByteByteGo style

---

## Transformation pipeline

Follow these steps in order for every request:

### Step 1 — Analyze the input

Extract:
- Core concept (1 sentence)
- 3–6 sub-topics to cover (these become sections)
- Key relationships, flows, or comparisons that need diagrams
- Any stats, numbers, or performance metrics (these become stat cards)
- The "aha moment" — what insight makes this topic click

For large documents (PDF, 100+ pages):
- Run `pdfinfo` to get page count and metadata
- Run `pdftotext -layout` to extract full text
- Scan table of contents / headings to pick the 5-6 most impactful topics
- Don't try to cover everything — pick the sections that generate the most insight

### Step 2 — Plan the structure

Map content to ByteByteGo's section format:
```
Hero → Table of Contents → Section 1 → Section 2 → ... → "Over to you" outro
```

Each section contains:
- H2 heading with a section number badge
- 2–3 short paragraphs (2–3 sentences each, active voice)
- One diagram OR one stat row OR one comparison table OR one callout box
- Never more than one diagram per section

### Step 3 — Write ByteByteGo-style prose

Follow these rules strictly. Read `references/writing-style.md` for full guidance.

Quick rules:
- Lead every section with an analogy or a sharp contrast
- Bold the key term on first use: `<strong>term</strong>`
- 2–3 sentences per paragraph max
- Active voice, present tense
- End the last section with "Over to you:" question

### Step 4 — Generate diagrams

For each section needing a diagram, pick the right type from `references/diagram-patterns.md`.

Quick decision:
- Flow between services → Flow diagram (SVG)
- Comparison of architectures/options → Comparison table (HTML)
- Numbers/performance metrics → Stat cards (3-column grid)
- Important caveat or insight → Callout box (amber left border)
- Things inside other things → Structural/containment diagram (SVG)
- Problem → Solution pairs → Two-row SVG grid (problems top, solutions bottom, arrows connecting)
- Ranked list / degradation tiers → Priority stack (HTML)

All diagrams use the dark theme color palette defined below.

### Step 5 — Render as dark HTML artifact

Use the HTML template in `references/html-template.md`.

Key requirements:
- Dark background: `#0a0a0a`
- Brand red accent: `#E50914`
- Hero: red left-border + background fill `#111111`, includes hero-meta stats bar
- TOC: 2-column grid layout with monospace numbered items
- Section numbers: red circle badges (26×26px)
- Horizontal `<hr class="divider">` between every section
- All SVGs: `width:100%` inline, `background:#111`, `border-radius:8px`
- Stat cards in 3-column grid
- Amber callout boxes for key insights
- Pill tags for technology lists
- Outro: teal left-border callout

---

## Dark theme color palette

Use these consistently across all diagrams and UI:

```
--brand:   #E50914   (Netflix red — brand accent, section numbers, borders)
--accent:  #F5A623   (amber — callout boxes, warnings)
--bg:      #0a0a0a   (page background)
--bg2:     #111111   (diagram/card background)
--bg3:     #1a1a1a   (inner card fills)
--border:  rgba(255,255,255,0.08)
--text:    #F0EEE9   (primary text)
--text2:   #A09E98   (secondary text, paragraph body)
--text3:   #6B6966   (muted labels)
--green:   #22C55E   (success, valid, CDN)
--blue:    #3B82F6   (services, APIs)
--purple:  #A855F7   (databases, storage)
--amber:   #F59E0B   (encoders, warnings)
--teal:    #14B8A6   (outro, engagement)
--red:     #EF4444   (errors, failures)
```

For SVG nodes, use semi-transparent fills:
```
rgba(59,130,246,0.12)  + stroke rgba(59,130,246,0.35)  → blue nodes
rgba(34,197,94,0.12)   + stroke rgba(34,197,94,0.35)   → green nodes
rgba(229,9,20,0.12)    + stroke rgba(229,9,20,0.35)    → red/origin nodes
rgba(245,158,11,0.12)  + stroke rgba(245,158,11,0.35)  → amber nodes
rgba(168,85,247,0.12)  + stroke rgba(168,85,247,0.35)  → purple nodes
```

---

## ByteByteGo prose rules (quick reference — updated from source analysis)

Full rules in `references/writing-style.md`. Key points:

1. **Title IS the hook** — the body opener is functional, not punchy.
   - Good: "The diagram below shows 4 typical cases where caches can go wrong."
   - Good: "Almost every software engineer has used Git before, but only a handful know how it works."
   - Bad: Repeating the title as a question in the first paragraph.

2. **"The diagram below shows..." is a valid and common opener** — do not suppress it.

3. **Lists over prose** — numbered for sequences, bullets for parallel items.
   Convert any 3+ item explanation into a list.

4. **Analogies are rare** — use only for consumer-facing topics (cookies, VPNs, payments).
   For engineering topics, use plain declarative statements.

5. **🔹 emoji sub-headers** for concept breakdowns (ACID, SOLID, etc.) — not H3 tags.

6. **Paragraphs: 1–4 sentences max.** One-sentence paragraphs are fine.

7. **"Over to you:"** — literal prefix, always. Followed by one specific practical question.
   - Good: "Over to you: Have you met any of these issues in production?"
   - Bad: "What do you think? Share your thoughts below!"

---

## Diagram rules (quick reference)

Full patterns in `references/diagram-patterns.md`. Key points:

- viewBox always `"0 0 680 H"` — compute H from content
- SVGs rendered inline with `style="width:100%;margin:24px 0;display:block;background:#111;border-radius:8px;"`
- Arrow marker: always include `<defs>` with the standard polygon marker
- Font: `font-family="DM Sans"` — 12px for labels, 10–11px for sublabels
- Stroke width: 0.8px for node borders, 1px for arrows
- All text must be readable — no text on opaque fills without contrast check
- Max 6 nodes per diagram — split into multiple SVGs if more needed
- No rotated text ever
- Problem/Solution diagrams: problems row on top, solutions row below, connecting arrows, SOLUTIONS label in between

---

## New components (validated in real output sessions)

### Hero meta bar
Add document stats directly under the hero paragraph:
```html
<div class="hero-meta">
  <span><strong>368</strong> pages</span>
  <span><strong>80+</strong> topics covered</span>
  <span><strong>6</strong> core pillars</span>
</div>
```

### TOC 2-column grid
Use numbered grid instead of a bullet list for multi-topic documents:
```html
<div class="toc-grid">
  <div class="toc-item"><span class="toc-num">01</span>Cache Failure Patterns</div>
  <div class="toc-item"><span class="toc-num">02</span>API Design Landscape</div>
</div>
```

### Pill tag list
Use for technology/tool lists (e.g., frameworks, services):
```html
<div class="pill-list">
  <span class="pill">Redis</span>
  <span class="pill">Kafka</span>
  <span class="pill">PostgreSQL</span>
</div>
```

### Section divider
Add `<hr class="divider">` between every section for visual breathing room.

### Callout with explicit label
Use a label line above the callout text for stronger emphasis:
```html
<div class="callout">
  <div class="callout-label">Key Insight</div>
  <p>Hot keys drive 80% of cache queries. Never set an expiration on them.</p>
</div>
```

---

## Output format

Always produce a single self-contained HTML file with:
- Embedded CSS (no external stylesheet except Google Fonts)
- All SVGs inline with background and border-radius set inline
- No JavaScript required (static content only)
- Works standalone — no server, no CDN dependencies for layout
- Save to `/mnt/user-data/outputs/[topic_name].html`

Structure:
```html
<!-- Google Fonts: DM Sans + DM Mono -->
<style> /* all CSS vars and component styles */ </style>
<div class="page">
  <div class="hero"> ... <div class="hero-meta">...</div> </div>
  <div class="toc"> <div class="toc-grid">...</div> </div>
  <div class="section"> ... </div>
  <hr class="divider">
  <div class="section"> ... </div>
  <hr class="divider">
  <!-- repeat -->
  <div class="outro"> ... </div>
</div>
```

---

## Reference files

- `references/writing-style.md` — full ByteByteGo writing rules with examples
- `references/diagram-patterns.md` — SVG templates for each diagram type including Problem/Solution grid
- `references/html-template.md` — complete HTML/CSS boilerplate with all new components

Read these when you need more detail on a specific aspect.
