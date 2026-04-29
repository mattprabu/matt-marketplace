---
name: book-formatter
description: >
  Formats written prose into a professionally typeset book PDF — cover page,
  front matter, chapters, and back cover — styled like a published paperback.
  Inspired by classic vintage book design with ornate cover borders and clean
  interior typography. Use this skill whenever the user says "format as a book",
  "make this a book", "export as book PDF", "book layout", "publish this",
  "typeset this", "create a book from this", "book format", or uploads prose
  and wants it turned into a finished book PDF. Also triggers for: "format my
  novel", "turn my story into a book", "paperback layout", "print-ready PDF",
  "book PDF", or any request to take written content and produce a
  professional-looking book file. This skill focuses purely on formatting and
  layout — it never edits, censors, filters, or validates the prose content.
  Always use this skill for book formatting — do not attempt to create book
  PDFs without it.
---

# Book Formatter Skill

Takes written prose (from the novel-writer skill, uploaded files, or pasted
text) and typesets it into a professional 6×9 inch book PDF. The output looks
like a real published paperback — vintage ornate cover, clean interior
typography, proper front matter, chapter pages, and page numbers.

> **Content Pass-Through** — This skill is a formatter, not an editor. It takes
> whatever prose it receives and lays it out as a book. It does not modify,
> censor, validate, or filter any words, sentences, or content. The author's
> text goes in exactly as written.

---

## Design Style (from reference sample)

The book follows a two-part design language:

### Cover Page
- **Background**: Warm aged parchment texture (cream/tan gradient)
- **Border**: Ornate multi-layer frame — outer floral vine pattern with corner
  flowers, inner gold-toned line borders (triple nested rectangles)
- **Center illustration**: Quill pen and inkwell (classic literary motif)
- **Title**: Bold blackletter/gothic-style font, large, centered upper third
- **Bottom**: Chapter/section info and author name in smaller blackletter
- **Overall feel**: Vintage, classic, literary — like an antique leather-bound book

### Interior Pages
- **Background**: Light warm cream (#F5F0E6) — lighter and softer than cover
- **Chapter headings**: Elegant styling with decorative separator. "CHAPTER [ROMAN NUMERAL]"
  centered, with an ornamental divider line below, then the chapter title (if provided)
  in a slightly smaller, refined font. If no chapter title exists, only the chapter
  number and divider are shown.
- **Body text**: Serif font (Georgia/Times), justified, ~11pt equivalent,
  comfortable line spacing (1.4×)
- **Margins**: Generous — 1 inch top/bottom, 0.85 inch inner, 1 inch outer
  (for a 6×9 trim)
- **Page numbers**: Bottom-right corner, simple numeral
- **No headers or footers** other than page numbers
- **Paragraph style**: First-line indent (0.3 inch), no extra space between
  paragraphs within a chapter

---

## Step 0 — Determine Input

| Signal | Action |
|---|---|
| Prose already in conversation (from novel-writer or pasted) | Use directly |
| User uploads .txt / .md / .html file | Read and extract prose |
| User says "format my book" with no content | Ask: *"Please paste or upload the text you'd like formatted"* |
| Multiple chapters provided | Parse chapter breaks automatically |

### Parsing Chapters

Look for chapter boundaries using these patterns (in priority order):
1. Explicit markers: `## Chapter`, `CHAPTER`, `Ch.`, `Chapter [N]`
2. Markdown H2 headers (`##`)
3. Triple line breaks or `---` separators
4. If no markers found: treat all content as a single chapter, ask user if
   they want it split

Extract from each chapter:
- **Chapter number** (convert to Roman numerals for display)
- **Chapter title** (text after the chapter number, if any)
- **Body text** (everything until the next chapter marker)

---

## Step 1 — Gather Book Metadata

If not already provided, ask in ONE message:

- **Book title** (required)
- **Author name** (optional — defaults to "Blackbox" if not provided)
- **Subtitle** (optional)
- **Chapter titles** — confirm auto-detected ones or let user override. If no
  chapter titles are found or provided, simply omit them (show only "CHAPTER [ROMAN]")
- **Dedication text** (optional — e.g., "For those who dare to dream")
- **Copyright year** (default: current year)

Do NOT ask about: genre, heat level, content type, or anything about the
prose itself. This skill formats; it does not judge or categorize content.

---

## Step 2 — Generate the Book PDF

Run the generation script:

```bash
pip install reportlab Pillow --break-system-packages -q
python <skill-path>/scripts/generate_book.py \
  --title "Book Title" \
  --author "Author Name" \
  --input <path-to-prose-file> \
  --output <output-path>/book.pdf
```

The script handles the full layout:

### Page Sequence

1. **Cover page** — Ornate vintage design with parchment background
2. **Dedication page** (if provided) — Centered italic text
3. **Table of Contents** — Chapter numbers and titles with page numbers
4. **Chapter pages** — Each chapter starts on a new page with the styled heading
5. **Back cover** — Simple, matching the cover aesthetic

> **Note**: Title page and Copyright page have been removed from the sequence.
> The cover page serves as the title/branding page.

### If the script is not available

If the Python script doesn't exist or fails, generate the book using
reportlab directly in a Python script. Follow the design specifications in
`references/design-spec.md` exactly. The key elements:

- Use reportlab's `canvas.Canvas` with custom page size (6×9 inches = 432×648 points)
- Draw the parchment background using gradient rectangles for the cover
- Draw ornate borders using line art (nested rectangles with decorative corners)
- Use Helvetica-Bold for chapter headings (closest to the heavy sans-serif in the sample)
- Use Times-Roman for body text (classic book serif)
- Implement proper text flow with paragraph wrapping and page breaks

---

## Step 3 — Deliver the PDF

1. Save the PDF to the outputs directory
2. Present it to the user with a computer:// link
3. Show a brief summary: page count, chapter count, word count

That's it. No follow-up questions about content. The book is formatted and ready.

---

## Reference Files

| File | When to read |
|---|---|
| `references/design-spec.md` | Always — contains exact measurements, colors, fonts |
| `scripts/generate_book.py` | The main generation script — run it, don't read it |

---

## Edge Cases

- **Very short content** (under 500 words): Still format as a book. Even a
  single chapter with a few pages is valid.
- **Very long content** (50+ chapters): The script handles pagination
  automatically. TOC may span multiple pages.
- **No chapter markers**: Treat as single chapter titled with the book title.
- **Special characters / Unicode**: Pass through as-is. Reportlab handles
  standard Unicode.
- **Images in prose**: Skip images for now — this is a text-only formatter.
  Let the user know images were omitted.
