# ByteByteGo Writing Style Guide

## What ByteByteGo actually sounds like

Reading 300+ real posts, one pattern dominates: ByteByteGo is a **diagram-first publisher**.
The writing exists to set up and explain the diagram — not the other way around.
Text is short, functional, and matter-of-fact. It does NOT try to be clever or literary.

The voice is: a senior engineer narrating a whiteboard walkthrough.
Confident. Sparse. Numbered when sequential. Bulleted when parallel.

---

## The 7 real writing patterns (observed from source)

---

### Pattern 1: Title as the hook — not the intro paragraph

ByteByteGo uses the **title itself** as the engagement hook, often phrased as a question or a
bold claim. The body then opens with a single orienting sentence — not a re-statement of the title.

Real examples from the source:

| Title | Opening sentence |
|-------|-----------------|
| "How Git Commands work" | "Almost every software engineer has used Git before, but only a handful know how it works." |
| "How does a VPN work?" | "A VPN, or Virtual Private Network, is a technology that creates a secure, encrypted connection over a less secure network, such as the public internet." |
| "What does ACID mean?" | Direct → straight into 🔹 sections with no preamble |
| "How can Cache Systems go wrong" | "The diagram below shows 4 typical cases where caches can go wrong and their solutions." |
| "Where do we cache data?" | "Data is cached everywhere, from the front end to the back end!" |

**The rule:** Don't write an intro that re-explains the title. Either deliver a single punchy
statement that earns the reader's trust, or go straight to the numbered list / diagram walkthrough.

---

### Pattern 2: "The diagram below shows..." is a legitimate opener

The skill's existing guide implies you should avoid this. The source proves the opposite.
ByteByteGo regularly opens with a direct pointer to the diagram. This is **not lazy** — it respects
the reader's time and signals: the diagram is the primary content.

Real openers from source:
- "The diagram below shows 4 typical cases where caches can go wrong and their solutions."
- "The diagram below shows the architecture of a notification system..."
- "The diagram below illustrates the typical workflow."
- "The diagram below explains what ACID means in the context of a database transaction."
- "This diagram below shows how the compilation and execution work."

**The rule:** It's fine — even preferred — to open a section by pointing directly to the diagram.
Don't force an analogy paragraph when the diagram speaks for itself.

---

### Pattern 3: Numbered and bulleted lists are the primary structure

ByteByteGo does not write flowing prose. It writes **structured lists**.

Numbered lists for sequential processes (step-by-step):
```
Step 1 - When we turn on the power, BIOS/UEFI firmware is loaded...
Step 2 - BIOS/UEFI detects the devices connected...
Step 3 - Choose a booting device...
```

Numbered lists for enumerated concepts (non-sequential):
```
1. Atomicity — all or nothing
2. Consistency — valid state preserved
3. Isolation — concurrent transactions don't interfere
4. Durability — committed data survives failure
```

Bulleted lists for parallel features/properties:
```
● Live Video Streaming
● DNS
● Market Data Multicast
● IoT
```

**The rule:** If there are 3+ things, use a list. Don't write "There are four things: X, Y, Z, and W.
First, X works by... Second, Y works by..." — just number them.

---

### Pattern 4: Short declarative explainers, not analogies

The existing skill over-emphasizes analogy. Real ByteByteGo uses analogies only occasionally —
mostly for consumer-facing concepts (cookies, VPNs). For engineering topics, it uses
**plain declarative statements**.

Analogy-heavy (consumer topics):
> "Imagine Bob goes to a coffee shop for the first time... A cookie acts as the preference card."
> "HTTP is like a goldfish with no memory — it forgets you instantly!"
> "It's like constantly asking, 'Do you have something new for me?'"

Plain declarative (engineering topics — the majority):
> "Event sourcing changes the programming paradigm from persisting states to persisting events."
> "gRPC uses HTTP/2 for transport, which allows for many improvements over HTTP/1.x."
> "The ACID model used in relational databases is too strict for NoSQL databases."
> "GitOps brought a shift in how software and infrastructure are managed with Git as the central hub."

**The rule:** Analogies are used sparingly, mostly for concepts non-engineers also care about.
For technical architecture content, use clear declarative statements. Don't force an analogy
onto every section.

---

### Pattern 5: Section headers use emoji bullets (🔹) for concept breakdowns

For multi-concept posts (ACID, CAP/BASE/SOLID, sensitive data management), ByteByteGo uses
a 🔹 emoji followed by the concept name as a sub-header, then a short paragraph.

```
🔹 Atomicity
The writes in a transaction are executed all at once and cannot be broken into smaller parts.
If there are faults when executing the transaction, the writes are rolled back.
So atomicity means "all or nothing".

🔹 Consistency
Unlike "consistency" in CAP theorem... here consistency means preserving database invariants.
```

This pattern replaces numbered lists when the concepts are definitional rather than sequential.

**The rule:** Use 🔹 sub-headers when you have 3–6 named concepts to define, each needing
1–3 sentences. Don't use H3 headers for this — use the emoji prefix.

---

### Pattern 6: "Over to you" is literal and consistent

The outro is always:
- Prefixed with exactly: **"Over to you:"**
- Followed by a single specific question
- The question is grounded in real engineering practice

Real examples:
- "Over to you: Have you used event sourcing in production?"
- "Over to you: Have you met any of these issues in production?"
- "Over to you: What's your company's release process look like?"
- "Over to you: Do you know which storage location the 'git tag' command operates on?"
- "Over to you: which directory did you use most frequently?"
- "Over to you: What factors would influence your decision to choose a DR strategy?"

Notice: lowercase after the colon is fine. The question can be very specific (git tag)
or broad (release process). It always invites personal experience — not abstract opinion.

**The rule:** Always end with "Over to you: [specific question about their own experience]".
Never rephrase it as "What do you think?" or "Share your thoughts!" or "Let us know below."

---

### Pattern 7: Paragraph length is 1–4 sentences. Never more.

Real paragraph lengths from the source:

Short (1–2 sentences, very common):
> "Event sourcing changes the programming paradigm from persisting states to persisting events.
> The event store is the source of truth."

Medium (3 sentences):
> "A VPN acts as a tunnel through which the encrypted data goes from one location to another.
> Any external party cannot see the data transferring.
> A VPN works in 4 steps:"

Rare long paragraph (4 sentences, always followed immediately by a list):
> "To become proficient in this standard, you can begin by exploring. Utilize commands such as
> 'cd' for navigation and 'ls' for listing directory contents. Imagine the file system as a tree,
> starting from the root (/). With time, it will become second nature to you."

**The rule:** 1–4 sentences per paragraph, always. When you reach 4 sentences, break or
convert to a list.

---

## Real content structure (multi-format posts)

ByteByteGo uses several repeatable post formats. Recognize which format fits the topic:

### Format A: Diagram Walkthrough (most common)
```
[Title as question or bold claim]
[1–2 sentence setup: "The diagram below shows..."]
[Numbered steps: Step 1..., Step 2..., Step 3...]
[Over to you: [question]]
```
Used for: Git flow, VPN, push notifications, live streaming, QR pay, search engines.

### Format B: Concept Breakdown
```
[Title]
[1-sentence definition of the parent concept]
[Numbered or bulleted list with brief explanation per item]
[Over to you: [question]]
```
Used for: UDP use cases, load balancer use cases, firewall rules, API testing types, memory types.

### Format C: Comparison (A vs B)
```
[Title: "X vs Y"]
[1-sentence framing of the difference]
[Section A header → bullet list of traits]
[Section B header → bullet list of traits]
[1–2 sentence verdict: when to use which]
```
Used for: REST vs GraphQL, polling vs webhooks, Git merge vs rebase, REST vs gRPC.

### Format D: Cheat Sheet / Reference
```
[Title]
[1–2 sentence description of what's inside]
["What's included:" or "Key features:"]
[Bulleted list of items]
[Optional: Over to you]
```
Used for: cloud services cheat sheet, system design cheat sheet, REST API cheat sheet.

### Format E: Definition with 🔹 sections
```
[Title]
[1-sentence overview]
[🔹 Concept A]
[1–3 sentences defining it]
[🔹 Concept B]
[1–3 sentences defining it]
[Over to you: [question]]
```
Used for: ACID, CAP/BASE/SOLID/KISS, configuration management.

---

## Words and phrases to avoid

| Avoid | Use instead |
|-------|-------------|
| "In this article we will discuss..." | Start directly with the definition or diagram reference |
| "Let's explore..." | Just start |
| "It's worth noting that" | Just say it |
| "Leverage" | "Use" |
| "Utilize" | "Use" |
| "Straightforward" | Cut it entirely |
| Passive voice in steps | "The server receives X" not "X is received by the server" |
| Long analogy paragraphs for engineering topics | Plain declarative statements |
| "As we can see in the diagram" | "The diagram shows..." or just describe it |
| Vague openers like "In today's world..." | Specific claim or question |

---

## Numbers and stats

Always use specific numbers when available. ByteByteGo extracts real numbers:
- "Stack Overflow serves all the traffic with only 9 on-premise web servers"
- "The hot keys take up 80% of the queries"
- "4 nines = 99.99% uptime = the service can only be down 8.64 seconds per day"
- "VISA charges a 0.11% assessment, plus a $0.0195 usage fee, for every swipe"

When you have 2+ related numbers, put them in stat cards.
When a number is embedded in an explanation, bold it inline: **9 web servers**, **80%**.

---

## Diagram captions (section labels)

Every diagram section in ByteByteGo uses the title as the implicit caption.
In our HTML output, use the diagram-title class (all lowercase, no period):
- ✅ "cache failure patterns"
- ✅ "push notification system architecture"
- ✅ "git storage locations"
- ❌ "Figure 1: How the Cache System Works"

---

## What the existing style guide got wrong (corrections)

| Old guidance | Reality from source |
|---|---|
| "Lead every section with an analogy" | Analogies are used only for consumer topics (~20% of posts). Most posts open with a plain declarative statement or "The diagram below shows..." |
| "Hook with a question or contrast" | Titles ARE the hook. Body openers are functional, not punchy. |
| "2–3 sentences per paragraph max" | Correct but 4 sentences also appears frequently. 1-sentence paragraphs are also very common. |
| "Bold key terms on first use" | ByteByteGo barely uses bold in body text. It relies on structure (numbered lists, headers) instead. |
| Structure: Hook → Analogy → Technical detail → Diagram | Reality: Title/hook → "diagram below shows" or 1-sentence setup → numbered list or 🔹 sections → Over to you |

---

## Quick checklist before finalizing output

- [ ] Does each section start with either a punchy 1-sentence statement OR "The diagram below shows..."?
- [ ] Is content primarily structured as numbered/bulleted lists rather than flowing prose?
- [ ] Are analogies only used if the topic is consumer-facing or the concept is abstract?
- [ ] Does every post end with exactly "Over to you: [specific question]"?
- [ ] Are paragraphs 1–4 sentences max?
- [ ] Are specific numbers extracted and used (not vague "many" or "most")?
- [ ] Is the writing functional and sparse — no filler phrases, no "let's explore", no "in conclusion"?
