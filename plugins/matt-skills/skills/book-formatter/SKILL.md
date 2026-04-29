---
name: book-formatter
description: Formats written prose into professional book layout. Use when the user provides raw text, chapters, or a manuscript to format as a publishable book.
argument-hint: "[text or file path]"
---

Format the provided prose into a polished, publication-ready book layout.

## Steps

1. **Parse structure** — Identify chapters, sections, and any existing headings. If none exist, infer logical breaks from content shifts.

2. **Apply front matter** — If the content is a full manuscript, generate or clean up:
   - Title page (Title, Author, Year)
   - Table of Contents with chapter titles and page references

3. **Normalize headings** — Apply a consistent hierarchy:
   - `# Chapter Title` for chapters
   - `## Section` for major sections
   - `### Subsection` for minor sections

4. **Clean typography** — Apply standard book conventions:
   - Replace `--` with em dash (—)
   - Replace straight quotes with smart quotes (" " ' ')
   - Ensure single space after periods
   - Remove double blank lines (max one blank line between paragraphs)

5. **Paragraph formatting** — First paragraph of each chapter/section: no indent. Subsequent paragraphs: indent the first line or use block spacing consistently (pick one style and apply throughout).

6. **Output** — Return the fully formatted text. If the input was a file path, write the output back to a new file named `[original]-formatted.md`.

## Notes
- Preserve all original content — do not rewrite or summarize
- If $ARGUMENTS is a file path, read the file first
- Flag any structural ambiguities (e.g., unclear chapter breaks) before formatting
