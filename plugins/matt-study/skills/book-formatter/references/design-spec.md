# Book Design Specification

## Page Dimensions

- **Trim size**: 6 × 9 inches (432 × 648 points)
- **Bleed**: None (digital PDF, not print-ready with bleeds)

## Margins (Interior Pages)

- **Top**: 72pt (1 inch)
- **Bottom**: 72pt (1 inch)
- **Inner (gutter)**: 61pt (0.85 inch)
- **Outer**: 72pt (1 inch)
- **Text block**: ~299pt wide × ~504pt tall

## Color Palette

### Cover
- Parchment base: #E8D5A3 (warm aged tan)
- Parchment dark: #C4A96A (shadow/border tone)
- Parchment light: #F5ECD0 (highlight areas)
- Border lines: #8B7335 (gold-brown)
- Text color: #1A1A0E (near-black, warm)
- Accent: #6B5B2E (dark gold for decorative elements)

### Interior
- Page background: #F5F0E6 (light warm cream — lighter than before)
- Interior parchment base: #F0E8D4 (very light warm cream)
- Interior parchment edge: #E5DCCA (subtle edge darkening)
- Body text: #1A1A1A (soft black)
- Chapter heading: #2C2417 (warm dark brown — softer than pure black)
- Chapter title: #4A3C2A (medium warm brown)
- Chapter divider line: #C4A96A (gold accent)
- Page numbers: #333333

## Typography

### Cover
- **Title**: Helvetica-Bold, 36pt, ALL CAPS, centered
  (The sample uses a blackletter/gothic font — Helvetica-Bold is the closest
  available in reportlab's built-in fonts. For a more authentic look, the
  script creates a stylized effect.)
- **Author name**: Helvetica-Bold, 16pt, centered
- **Subtitle/Chapter info**: Helvetica, 14pt, centered

### Interior — Chapter Heading
- **"CHAPTER [ROMAN]"**: Helvetica-Bold, 22pt, ALL CAPS, centered, warm dark brown (#2C2417)
- **Decorative divider**: Centered ornamental line (gold #C4A96A) with small
  diamond or flourish, 1pt stroke, ~80pt wide, placed 14pt below chapter marker
- **Chapter title** (if provided): Times-Italic, 18pt, Title Case, centered,
  medium warm brown (#4A3C2A). If no chapter title is given, omit entirely.
- **Spacing**: 100pt from top to chapter marker, 14pt to divider, 14pt to title
  (if present), 40pt from last heading element to first paragraph

### Interior — Body Text
- **Font**: Times-Roman, 11pt
- **Line spacing**: 15.4pt (1.4× font size)
- **Paragraph indent**: 22pt (first line of each paragraph)
- **Paragraph spacing**: 0pt (no extra space — just indent signals new paragraph)
- **Alignment**: Justified
- **First paragraph after heading**: No indent (drop the indent for the
  opening paragraph of each chapter, as is traditional in book typesetting)

### Interior — Page Numbers
- **Font**: Times-Roman, 10pt
- **Position**: Bottom-right, 72pt from right edge, 40pt from bottom
- **Style**: Plain numeral (no dashes, dots, or "Page" prefix)
- **Start numbering**: From first chapter page (front matter uses Roman
  numerals or no numbers)

## Cover Page Layout (detailed)

The cover is built in layers:

1. **Parchment background**: Full-page gradient from #E8D5A3 (center) to
   #C4A96A (edges), with subtle noise/texture effect created by drawing
   many small semi-transparent rectangles

2. **Outer decorative border**: At 20pt inset from page edge
   - Floral vine pattern along all four sides
   - Corner flower/rosette decorations
   - Drawn using bezier curves and circles

3. **Inner frame lines**: Triple nested rectangles
   - Outer line at 35pt inset, 2pt stroke
   - Middle line at 42pt inset, 0.5pt stroke
   - Inner line at 48pt inset, 1.5pt stroke
   - All in gold-brown (#8B7335)

4. **Title zone**: Upper third of the page (y: 450–580pt)
   - Title text centered horizontally
   - Bold, large, dark

5. **Center illustration zone**: Middle of page (y: 250–420pt)
   - Quill and inkwell drawn with bezier curves
   - Or: decorative ornament/flourish if quill is too complex

6. **Bottom zone**: Lower portion (y: 60–200pt)
   - Chapter/section info
   - Author name

## Front Matter Pages

> **Note**: Title page (old page 2) and Copyright page (old page 3) have been
> removed. The book goes directly from cover → dedication (optional) → TOC → chapters.

### Dedication Page (page 2, optional)
- Text centered both horizontally and vertically
- Font: Times-Italic, 13pt
- No page number

### Table of Contents (page 3 or 2)
- Title: "CONTENTS" — Helvetica-Bold, 20pt, centered
- Entries: Times-Roman, 12pt
  - Left: "Chapter I — The Title"
  - Right: page number
  - Dot leaders connecting title to page number
- Page number: Roman numeral (lowercase)

## Chapter Start Pages

Each chapter begins on a new page (recto/odd preferred, but not required for
digital PDF). The chapter opening has extra whitespace at top:

- **Top margin**: 100pt (larger than normal — gives the heading breathing room)
- **Chapter marker**: "CHAPTER [ROMAN]" in Helvetica-Bold 22pt, centered, warm dark brown
- **Decorative divider**: Centered gold line (~80pt) with diamond ornament, 14pt below marker
- **Chapter title** (optional): Times-Italic 18pt, Title Case, centered, 14pt below divider.
  If no chapter title is provided, skip this element entirely.
- **First paragraph**: Starts 40pt below the last heading element, no first-line indent
- **Subsequent paragraphs**: Normal 22pt first-line indent

## Back Cover

Simple design echoing the cover:
- Same parchment background
- Simplified border (just the triple-line frame, no floral)
- Centered text block with a brief tagline or left blank
- Author name at bottom
