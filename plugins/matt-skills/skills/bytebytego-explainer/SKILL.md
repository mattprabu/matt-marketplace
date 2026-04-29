---
name: bytebytego-explainer
description: Transforms any technical topic, document, or concept into a clear, visual ByteByteGo-style explanation. Use when the user wants a system design or technical concept broken down with diagrams and layered depth.
argument-hint: "[topic, concept, or document]"
---

Explain $ARGUMENTS in the ByteByteGo style: layered depth, visual diagrams, and plain language first — then internals.

## Format

### 1. One-line summary
State what it is in one sentence a non-engineer could understand.

### 2. The problem it solves
Why does this exist? What would break without it?

### 3. How it works — simple view
Use an analogy. No jargon.

### 4. How it works — technical view
Step-by-step flow with an ASCII diagram:

```
[Component A] → [Component B] → [Component C]
      ↓                ↓
  [Cache]         [Database]
```

### 5. Key design decisions
3–5 bullets on the non-obvious choices (e.g., why eventual consistency, why a ring buffer, why TCP not UDP).

### 6. Trade-offs
| Benefit | Cost |
|---|---|
| High throughput | Higher memory usage |
| … | … |

### 7. Where you'll see this in the real world
Name 2–3 real systems that use this pattern (e.g., Kafka, Cassandra, Nginx).

## Notes
- Diagrams must be ASCII — no Mermaid or external tools
- Keep each section tight: quality over length
- If $ARGUMENTS is a document/file path, read it first and summarize what needs explaining
