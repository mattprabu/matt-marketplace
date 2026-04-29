#!/usr/bin/env python3
"""
Book Formatter — Generates a professionally typeset 6×9 book PDF.

Produces: cover page, optional dedication, table of contents, chapter pages
with proper typography, and back cover. Default author: Blackbox.

Design: Vintage ornate cover with parchment background + light cream interior
with elegant centered chapter headings and decorative dividers.
"""

import argparse
import math
import random
import re
import sys
from datetime import datetime

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas

# ── Page dimensions ──────────────────────────────────────────────────────
PAGE_W = 6 * inch    # 432pt
PAGE_H = 9 * inch    # 648pt

# ── Colors ───────────────────────────────────────────────────────────────
PARCHMENT_BASE = HexColor("#E8D5A3")
PARCHMENT_DARK = HexColor("#C4A96A")
PARCHMENT_LIGHT = HexColor("#F5ECD0")
PARCHMENT_STAIN = HexColor("#D4BC82")
BORDER_GOLD = HexColor("#8B7335")
COVER_TEXT = HexColor("#1A1A0E")
ACCENT_GOLD = HexColor("#6B5B2E")
ACCENT_LIGHT = HexColor("#A8935A")

INTERIOR_BG = HexColor("#F5F0E6")  # light warm cream
INTERIOR_PARCHMENT = HexColor("#F0E8D4")  # very light warm cream base for interior
INTERIOR_PARCHMENT_EDGE = HexColor("#E5DCCA")  # subtle edge darkening
BODY_TEXT_COLOR = HexColor("#1A1A1A")
HEADING_COLOR = HexColor("#2C2417")  # warm dark brown for chapter headings
CHAPTER_TITLE_COLOR = HexColor("#4A3C2A")  # medium warm brown for chapter titles
CHAPTER_DIVIDER_COLOR = HexColor("#C4A96A")  # gold accent for dividers
PAGE_NUM_COLOR = HexColor("#333333")

# ── Margins (interior) ──────────────────────────────────────────────────
MARGIN_TOP = 72
MARGIN_BOTTOM = 72
MARGIN_INNER = 61
MARGIN_OUTER = 72

# ── Typography ───────────────────────────────────────────────────────────
BODY_FONT = "Times-Roman"
BODY_BOLD = "Times-Bold"
BODY_ITALIC = "Times-Italic"
HEADING_FONT = "Helvetica-Bold"
BODY_SIZE = 11
BODY_LEADING = 15.4
HEADING_SIZE = 22
TITLE_SIZE = 18
PARA_INDENT = 22
PAGE_NUM_SIZE = 10


def roman_numeral(n):
    vals = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    result = ""
    for val, numeral in vals:
        while n >= val:
            result += numeral
            n -= val
    return result


def normalize_source_text(text):
    """Pre-clean prose before parsing.

    - Normalize CRLF/CR line endings to LF (Windows-saved files).
    - Strip markdown bold wrappers around chapter heading lines, e.g.
      ``**Chapter 1: The Spark**`` -> ``Chapter 1: The Spark`` so the
      chapter regex matches.
    - Remove ``(Word count: NNN)`` annotation lines that LLM-generated
      drafts often leave at the end of each chapter.
    """
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip ** or __ wrappers around chapter heading lines
    text = re.sub(
        r'(?im)^\s*(?:\*\*|__)\s*((?:#{1,3}\s*)?(?:CHAPTER|Chapter|chapter)\s+\w+[^\n]*?)\s*(?:\*\*|__)\s*$',
        r'\1',
        text,
    )
    # Remove (Word count: NNN) annotation lines
    text = re.sub(r'(?im)^\s*\(?\s*word\s*count\s*:\s*[\d,]+\s*\)?\s*$\n?', '', text)
    return text


def parse_chapters(text):
    """Parse prose text into chapters."""
    text = normalize_source_text(text)
    pattern = r'(?:^|\n)(?:#{1,3}\s*)?(?:CHAPTER|Chapter|chapter)\s+(\w+)[\ \t:\-—]*([^\n]*)\n'
    splits = list(re.finditer(pattern, text))

    if splits:
        chapters = []
        for i, match in enumerate(splits):
            num_str = match.group(1).strip()
            title = match.group(2).strip()
            try:
                num = int(num_str)
            except ValueError:
                num = i + 1
            start = match.end()
            end = splits[i + 1].start() if i + 1 < len(splits) else len(text)
            body = text[start:end].strip()
            chapters.append({"number": num, "title": title, "body": body})
        return chapters

    h2_pattern = r'(?:^|\n)##\s+([^\n]+)\n'
    h2_splits = list(re.finditer(h2_pattern, text))
    if h2_splits:
        chapters = []
        for i, match in enumerate(h2_splits):
            title = match.group(1).strip()
            start = match.end()
            end = h2_splits[i + 1].start() if i + 1 < len(h2_splits) else len(text)
            body = text[start:end].strip()
            chapters.append({"number": i + 1, "title": title, "body": body})
        return chapters

    sep_pattern = r'\n(?:---+|\n{3,})\n'
    parts = re.split(sep_pattern, text.strip())
    if len(parts) > 1:
        chapters = []
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            lines = part.split("\n", 1)
            if len(lines) == 2 and len(lines[0]) < 80:
                chapters.append({
                    "number": i + 1,
                    "title": lines[0].strip().strip("#").strip(),
                    "body": lines[1].strip()
                })
            else:
                chapters.append({"number": i + 1, "title": "", "body": part})
        return chapters

    return [{"number": 1, "title": "", "body": text.strip()}]


def wrap_text_to_lines(text, font_name, font_size, max_width, c):
    """Word-wrap text using actual font metrics."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip() if current_line else word
        width = c.stringWidth(test_line, font_name, font_size)
        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


# ─────────────────────────────────────────────────────────────────────────
# Cover artwork drawing helpers
# ─────────────────────────────────────────────────────────────────────────

def _draw_leaf(c, x, y, size, angle_deg, filled=True):
    """Draw a single decorative leaf at position, rotated by angle."""
    c.saveState()
    c.translate(x, y)
    c.rotate(angle_deg)
    path = c.beginPath()
    # Leaf shape: pointed oval
    path.moveTo(0, 0)
    path.curveTo(size * 0.4, size * 0.6, size * 0.4, size * 0.9, 0, size)
    path.curveTo(-size * 0.4, size * 0.9, -size * 0.4, size * 0.6, 0, 0)
    c.drawPath(path, fill=1 if filled else 0, stroke=1)
    # Center vein
    c.setLineWidth(0.3)
    c.line(0, size * 0.1, 0, size * 0.85)
    c.restoreState()


def _draw_flower(c, cx, cy, radius, petals=5):
    """Draw a small decorative flower rosette."""
    for i in range(petals):
        angle = (2 * math.pi / petals) * i
        px = cx + math.cos(angle) * radius * 0.5
        py = cy + math.sin(angle) * radius * 0.5
        # Each petal is a small ellipse
        c.saveState()
        c.translate(px, py)
        c.rotate(math.degrees(angle))
        path = c.beginPath()
        r = radius * 0.55
        path.moveTo(0, 0)
        path.curveTo(r * 0.5, r * 0.8, r * 0.3, r, 0, r)
        path.curveTo(-r * 0.3, r, -r * 0.5, r * 0.8, 0, 0)
        c.drawPath(path, fill=1, stroke=1)
        c.restoreState()
    # Center dot
    c.circle(cx, cy, radius * 0.2, fill=1, stroke=0)


def _draw_vine_segment(c, x1, y1, x2, y2, leaf_side=1, num_leaves=3):
    """Draw a vine stem from (x1,y1) to (x2,y2) with leaves along it."""
    # Main stem as a gentle curve
    mx = (x1 + x2) / 2 + leaf_side * 8
    my = (y1 + y2) / 2
    path = c.beginPath()
    path.moveTo(x1, y1)
    path.curveTo(mx, y1 + (y2 - y1) * 0.33,
                 mx, y1 + (y2 - y1) * 0.66,
                 x2, y2)
    c.drawPath(path, fill=0, stroke=1)

    # Leaves along the stem
    for i in range(num_leaves):
        t = (i + 1) / (num_leaves + 1)
        # Position along the line
        lx = x1 + (x2 - x1) * t
        ly = y1 + (y2 - y1) * t
        leaf_angle = 45 * leaf_side + (i % 2) * 30
        _draw_leaf(c, lx + leaf_side * 3, ly, 10 + i * 2, leaf_angle, filled=False)


def _draw_ornate_border(c, page_w, page_h):
    """Draw a rich ornate border with vines, flowers, and nested frames."""
    c.saveState()

    # ── Triple-line inner frame ──
    c.setStrokeColor(BORDER_GOLD)
    c.setLineWidth(2.5)
    c.rect(30, 30, page_w - 60, page_h - 60, fill=0, stroke=1)
    c.setLineWidth(0.5)
    c.rect(38, 38, page_w - 76, page_h - 76, fill=0, stroke=1)
    c.setLineWidth(1.8)
    c.rect(44, 44, page_w - 88, page_h - 88, fill=0, stroke=1)

    # ── Decorative corner pieces ──
    c.setStrokeColor(ACCENT_GOLD)
    c.setFillColor(Color(ACCENT_GOLD.red, ACCENT_GOLD.green, ACCENT_GOLD.blue, 0.4))
    c.setLineWidth(0.7)

    corner_inset = 30
    corners = [
        (corner_inset, corner_inset, 0),
        (page_w - corner_inset, corner_inset, 90),
        (page_w - corner_inset, page_h - corner_inset, 180),
        (corner_inset, page_h - corner_inset, 270),
    ]

    for cx, cy, rot in corners:
        c.saveState()
        c.translate(cx, cy)
        c.rotate(rot)
        # Corner L-bracket with scroll ends
        # Horizontal arm
        path = c.beginPath()
        path.moveTo(0, 0)
        path.lineTo(40, 0)
        path.curveTo(45, 0, 48, 3, 48, 8)
        path.curveTo(48, 13, 44, 16, 40, 14)
        path.curveTo(38, 13, 38, 10, 40, 8)
        c.drawPath(path, fill=0, stroke=1)
        # Vertical arm
        path = c.beginPath()
        path.moveTo(0, 0)
        path.lineTo(0, 40)
        path.curveTo(0, 45, 3, 48, 8, 48)
        path.curveTo(13, 48, 16, 44, 14, 40)
        path.curveTo(13, 38, 10, 38, 8, 40)
        c.drawPath(path, fill=0, stroke=1)
        # Small diamond at corner junction
        path = c.beginPath()
        path.moveTo(0, 8)
        path.lineTo(8, 0)
        path.lineTo(0, -8)
        path.lineTo(-8, 0)
        path.close()
        c.drawPath(path, fill=1, stroke=1)
        # Corner flower
        _draw_flower(c, 0, 0, 8, petals=6)
        c.restoreState()

    # ── Vine decorations along edges ──
    c.setLineWidth(0.6)
    c.setStrokeColor(ACCENT_GOLD)
    c.setFillColor(Color(ACCENT_GOLD.red, ACCENT_GOLD.green, ACCENT_GOLD.blue, 0.3))

    edge_inset = 22
    vine_margin = 65  # stay away from corners

    # Left edge — vine going upward
    num_leaves_side = 8
    seg_h = (page_h - 2 * vine_margin) / num_leaves_side
    for i in range(num_leaves_side):
        by = vine_margin + i * seg_h
        bx = edge_inset
        # Small leaf alternating sides
        side = 1 if i % 2 == 0 else -1
        leaf_size = 9 + (i % 3) * 2
        _draw_leaf(c, bx + side * 2, by + seg_h * 0.5, leaf_size,
                   70 * side, filled=False)
        # Connecting tendril
        path = c.beginPath()
        path.moveTo(bx, by)
        path.curveTo(bx + side * 6, by + seg_h * 0.3,
                     bx + side * 6, by + seg_h * 0.7,
                     bx, by + seg_h)
        c.drawPath(path, fill=0, stroke=1)

    # Right edge — mirror
    for i in range(num_leaves_side):
        by = vine_margin + i * seg_h
        bx = page_w - edge_inset
        side = -1 if i % 2 == 0 else 1
        leaf_size = 9 + (i % 3) * 2
        _draw_leaf(c, bx + side * 2, by + seg_h * 0.5, leaf_size,
                   70 * side, filled=False)
        path = c.beginPath()
        path.moveTo(bx, by)
        path.curveTo(bx + side * 6, by + seg_h * 0.3,
                     bx + side * 6, by + seg_h * 0.7,
                     bx, by + seg_h)
        c.drawPath(path, fill=0, stroke=1)

    # Top edge
    num_leaves_top = 6
    seg_w = (page_w - 2 * vine_margin) / num_leaves_top
    for i in range(num_leaves_top):
        bx = vine_margin + i * seg_w
        by = page_h - edge_inset
        side = 1 if i % 2 == 0 else -1
        leaf_size = 8 + (i % 3) * 2
        _draw_leaf(c, bx + seg_w * 0.5, by + side * 2, leaf_size,
                   90 + 50 * side, filled=False)
        path = c.beginPath()
        path.moveTo(bx, by)
        path.curveTo(bx + seg_w * 0.3, by + side * 6,
                     bx + seg_w * 0.7, by + side * 6,
                     bx + seg_w, by)
        c.drawPath(path, fill=0, stroke=1)

    # Bottom edge
    for i in range(num_leaves_top):
        bx = vine_margin + i * seg_w
        by = edge_inset
        side = -1 if i % 2 == 0 else 1
        leaf_size = 8 + (i % 3) * 2
        _draw_leaf(c, bx + seg_w * 0.5, by + side * 2, leaf_size,
                   90 + 50 * side, filled=False)
        path = c.beginPath()
        path.moveTo(bx, by)
        path.curveTo(bx + seg_w * 0.3, by + side * 6,
                     bx + seg_w * 0.7, by + side * 6,
                     bx + seg_w, by)
        c.drawPath(path, fill=0, stroke=1)

    # ── Midpoint flowers on each edge ──
    _draw_flower(c, page_w / 2, page_h - edge_inset, 10, petals=5)
    _draw_flower(c, page_w / 2, edge_inset, 10, petals=5)
    _draw_flower(c, edge_inset, page_h / 2, 10, petals=5)
    _draw_flower(c, page_w - edge_inset, page_h / 2, 10, petals=5)

    c.restoreState()


def _draw_parchment_bg(c, page_w, page_h):
    """Draw warm aged parchment background with texture."""
    # Base fill
    c.setFillColor(PARCHMENT_BASE)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # Edge darkening — layered gradient
    for i in range(25):
        alpha = 0.015 * (25 - i)
        c.setFillColor(Color(
            PARCHMENT_DARK.red, PARCHMENT_DARK.green,
            PARCHMENT_DARK.blue, alpha))
        inset = i * 2.5
        c.rect(inset, inset, page_w - 2 * inset, page_h - 2 * inset,
               fill=1, stroke=0)

    # Subtle center warmth — very faint ellipse
    c.setFillColor(Color(
        PARCHMENT_LIGHT.red, PARCHMENT_LIGHT.green,
        PARCHMENT_LIGHT.blue, 0.15))
    cx, cy = page_w / 2, page_h / 2
    c.ellipse(cx - 120, cy - 160, cx + 120, cy + 160, fill=1, stroke=0)

    # Paper texture — fine grain
    random.seed(42)
    for _ in range(400):
        x = random.uniform(5, page_w - 5)
        y = random.uniform(5, page_h - 5)
        size = random.uniform(0.5, 3)
        alpha = random.uniform(0.01, 0.05)
        shade = random.uniform(0.5, 0.75)
        c.setFillColor(Color(shade, shade * 0.85, shade * 0.6, alpha))
        c.rect(x, y, size, size * random.uniform(0.5, 2), fill=1, stroke=0)

    # Subtle edge staining
    c.setFillColor(Color(
        PARCHMENT_STAIN.red, PARCHMENT_STAIN.green,
        PARCHMENT_STAIN.blue, 0.08))
    # Top-left stain
    c.ellipse(-20, page_h - 80, 100, page_h + 20, fill=1, stroke=0)
    # Bottom-right stain
    c.ellipse(page_w - 90, -20, page_w + 20, 70, fill=1, stroke=0)


def _draw_quill_inkwell(c, cx, cy, scale=1.0):
    """Draw a detailed quill pen and inkwell illustration."""
    c.saveState()
    c.translate(cx, cy)
    s = scale

    c.setStrokeColor(COVER_TEXT)
    c.setFillColor(COVER_TEXT)
    c.setLineWidth(1.2 * s)

    # ── Inkwell base shadow ──
    c.setFillColor(Color(0.1, 0.1, 0.05, 0.15))
    c.ellipse(-45 * s, -55 * s, 50 * s, -35 * s, fill=1, stroke=0)

    c.setFillColor(COVER_TEXT)
    c.setStrokeColor(COVER_TEXT)

    # ── Inkwell body ──
    c.setLineWidth(1.5 * s)
    # Base ellipse
    c.ellipse(-35 * s, -48 * s, 35 * s, -32 * s, fill=0, stroke=1)

    # Pot walls
    path = c.beginPath()
    path.moveTo(-30 * s, -40 * s)
    path.curveTo(-28 * s, -10 * s, -22 * s, 8 * s, -20 * s, 12 * s)
    path.lineTo(20 * s, 12 * s)
    path.curveTo(22 * s, 8 * s, 28 * s, -10 * s, 30 * s, -40 * s)
    c.drawPath(path, fill=0, stroke=1)

    # Rim — thicker ellipse at top
    c.setLineWidth(2.2 * s)
    c.ellipse(-22 * s, 6 * s, 22 * s, 20 * s, fill=0, stroke=1)

    # Ink surface (dark fill inside rim)
    c.setFillColor(Color(0.1, 0.08, 0.05, 0.8))
    c.ellipse(-18 * s, 9 * s, 18 * s, 17 * s, fill=1, stroke=0)

    c.setFillColor(COVER_TEXT)
    c.setStrokeColor(COVER_TEXT)

    # Pot horizontal bands (decorative rings)
    c.setLineWidth(0.6 * s)
    for band_y in [-15, -25]:
        bw = 26 + band_y * -0.2  # narrower at bottom
        c.ellipse(-bw * s, (band_y - 3) * s, bw * s, (band_y + 3) * s,
                  fill=0, stroke=1)

    # ── Quill shaft ──
    c.setLineWidth(1.3 * s)
    # Shaft from inkwell up-right diagonally
    shaft_bx, shaft_by = 3 * s, 14 * s      # base (in ink)
    shaft_tx, shaft_ty = 85 * s, 130 * s     # tip (top)
    c.line(shaft_bx, shaft_by, shaft_tx, shaft_ty)

    # ── Feather barbs ──
    c.setLineWidth(0.5 * s)
    num_barbs = 14
    for i in range(3, num_barbs):
        t = i / num_barbs
        # Point on shaft
        sx = shaft_bx + (shaft_tx - shaft_bx) * t
        sy = shaft_by + (shaft_ty - shaft_by) * t

        barb_len = (8 + i * 3.5) * s
        # Shaft angle
        shaft_angle = math.atan2(shaft_ty - shaft_by, shaft_tx - shaft_bx)

        # Right barbs — more prominent
        r_angle = shaft_angle + 0.6 + (i * 0.02)
        rex = sx + math.cos(r_angle) * barb_len
        rey = sy + math.sin(r_angle) * barb_len
        path = c.beginPath()
        path.moveTo(sx, sy)
        path.curveTo(
            sx + math.cos(r_angle) * barb_len * 0.4,
            sy + math.sin(r_angle) * barb_len * 0.5,
            rex - math.cos(shaft_angle) * barb_len * 0.15,
            rey - math.sin(shaft_angle) * barb_len * 0.1,
            rex, rey)
        c.drawPath(path, fill=0, stroke=1)

        # Left barbs — shorter
        l_barb_len = barb_len * 0.6
        l_angle = shaft_angle - 0.7 - (i * 0.015)
        lex = sx + math.cos(l_angle) * l_barb_len
        ley = sy + math.sin(l_angle) * l_barb_len
        path = c.beginPath()
        path.moveTo(sx, sy)
        path.curveTo(
            sx + math.cos(l_angle) * l_barb_len * 0.4,
            sy + math.sin(l_angle) * l_barb_len * 0.5,
            lex - math.cos(shaft_angle) * l_barb_len * 0.1,
            ley - math.sin(shaft_angle) * l_barb_len * 0.1,
            lex, ley)
        c.drawPath(path, fill=0, stroke=1)

    # ── Feather tip — filled triangular tuft ──
    c.setLineWidth(0.4 * s)
    tip_len = 25 * s
    for j in range(-3, 4):
        angle_off = j * 0.12
        r_a = math.atan2(shaft_ty - shaft_by, shaft_tx - shaft_bx) + 0.5 + angle_off
        ex = shaft_tx + math.cos(r_a) * tip_len
        ey = shaft_ty + math.sin(r_a) * tip_len
        path = c.beginPath()
        path.moveTo(shaft_tx, shaft_ty)
        path.curveTo(
            shaft_tx + math.cos(r_a) * tip_len * 0.5,
            shaft_ty + math.sin(r_a) * tip_len * 0.6,
            ex, ey, ex, ey)
        c.drawPath(path, fill=0, stroke=1)

    # ── Nib at base ──
    c.setLineWidth(1 * s)
    c.setFillColor(COVER_TEXT)
    path = c.beginPath()
    nib_angle = math.atan2(shaft_ty - shaft_by, shaft_tx - shaft_bx)
    nbx = shaft_bx - math.cos(nib_angle) * 6 * s
    nby = shaft_by - math.sin(nib_angle) * 6 * s
    path.moveTo(shaft_bx, shaft_by)
    perp = nib_angle + math.pi / 2
    path.lineTo(nbx + math.cos(perp) * 3 * s, nby + math.sin(perp) * 3 * s)
    path.lineTo(nbx - math.cos(nib_angle) * 12 * s,
                nby - math.sin(nib_angle) * 12 * s)
    path.lineTo(nbx - math.cos(perp) * 3 * s, nby - math.sin(perp) * 3 * s)
    path.close()
    c.drawPath(path, fill=1, stroke=1)

    # ── Ink flourish curve beneath inkwell ──
    c.setLineWidth(1 * s)
    c.setStrokeColor(COVER_TEXT)
    path = c.beginPath()
    path.moveTo(-40 * s, -52 * s)
    path.curveTo(-55 * s, -72 * s, 0 * s, -80 * s, 40 * s, -58 * s)
    path.curveTo(55 * s, -50 * s, 60 * s, -65 * s, 50 * s, -72 * s)
    c.drawPath(path, fill=0, stroke=1)

    c.restoreState()


def _draw_interior_parchment(c, page_w, page_h):
    """Draw a light warm cream background for interior pages — much lighter than cover."""
    # Base light warm cream fill
    c.setFillColor(INTERIOR_PARCHMENT)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # Very subtle edge darkening (lighter than before)
    for i in range(10):
        alpha = 0.008 * (10 - i)
        c.setFillColor(Color(
            INTERIOR_PARCHMENT_EDGE.red, INTERIOR_PARCHMENT_EDGE.green,
            INTERIOR_PARCHMENT_EDGE.blue, alpha))
        inset = i * 2
        c.rect(inset, inset, page_w - 2 * inset, page_h - 2 * inset,
               fill=1, stroke=0)

    # Very fine, subtle paper grain texture (reduced from before)
    random.seed(99)
    for _ in range(120):
        x = random.uniform(5, page_w - 5)
        y = random.uniform(5, page_h - 5)
        size = random.uniform(0.3, 1.8)
        alpha = random.uniform(0.005, 0.025)
        shade = random.uniform(0.6, 0.8)
        c.setFillColor(Color(shade, shade * 0.9, shade * 0.7, alpha))
        c.rect(x, y, size, size * random.uniform(0.5, 1.5), fill=1, stroke=0)


# ─────────────────────────────────────────────────────────────────────────
# Main generator class
# ─────────────────────────────────────────────────────────────────────────

class BookGenerator:
    def __init__(self, title, author="Blackbox", subtitle="", dedication="",
                 copyright_year=None, output_path="book.pdf"):
        self.title = title
        self.author = author
        self.subtitle = subtitle
        self.dedication = dedication
        self.copyright_year = copyright_year or str(datetime.now().year)
        self.output_path = output_path
        self.chapters = []
        self.current_page = 0

        self.c = canvas.Canvas(output_path, pagesize=(PAGE_W, PAGE_H))
        self.c.setTitle(title)
        self.c.setAuthor(author)

    def draw_cover(self):
        """Draw the front cover page."""
        c = self.c
        _draw_parchment_bg(c, PAGE_W, PAGE_H)
        _draw_ornate_border(c, PAGE_W, PAGE_H)
        _draw_quill_inkwell(c, PAGE_W / 2 - 10, PAGE_H / 2 - 30, scale=1.1)

        # ── Title ──
        c.setFillColor(COVER_TEXT)
        c.setFont(HEADING_FONT, 36)
        title_lines = wrap_text_to_lines(
            self.title.upper(), HEADING_FONT, 36, PAGE_W - 140, c
        )
        title_y = PAGE_H - 120
        for line in title_lines:
            tw = c.stringWidth(line, HEADING_FONT, 36)
            c.drawString((PAGE_W - tw) / 2, title_y, line)
            title_y -= 46

        # ── Bottom: author name ──
        c.setFont(HEADING_FONT, 16)
        aw = c.stringWidth(self.author.upper(), HEADING_FONT, 16)
        c.drawString((PAGE_W - aw) / 2, 75, self.author.upper())

        if self.subtitle:
            c.setFont("Helvetica", 13)
            sw = c.stringWidth(self.subtitle, "Helvetica", 13)
            c.drawString((PAGE_W - sw) / 2, 105, self.subtitle)

        c.showPage()

    def draw_title_page(self):
        c = self.c
        _draw_interior_parchment(c, PAGE_W, PAGE_H)

        c.setFillColor(HEADING_COLOR)
        c.setFont(HEADING_FONT, 30)
        title_lines = wrap_text_to_lines(
            self.title.upper(), HEADING_FONT, 30, PAGE_W - 120, c
        )
        y = PAGE_H - 200
        for line in title_lines:
            tw = c.stringWidth(line, HEADING_FONT, 30)
            c.drawString((PAGE_W - tw) / 2, y, line)
            y -= 38

        if self.subtitle:
            y -= 10
            c.setFont("Helvetica", 16)
            sw = c.stringWidth(self.subtitle, "Helvetica", 16)
            c.drawString((PAGE_W - sw) / 2, y, self.subtitle)

        # Decorative line
        c.setStrokeColor(HexColor("#CCCCCC"))
        c.setLineWidth(0.5)
        c.line(PAGE_W / 2 - 60, PAGE_H / 2, PAGE_W / 2 + 60, PAGE_H / 2)

        c.setFillColor(BODY_TEXT_COLOR)
        c.setFont("Helvetica", 18)
        aw = c.stringWidth(self.author, "Helvetica", 18)
        c.drawString((PAGE_W - aw) / 2, 200, self.author)

        c.showPage()

    def draw_copyright_page(self):
        c = self.c
        _draw_interior_parchment(c, PAGE_W, PAGE_H)

        c.setFillColor(BODY_TEXT_COLOR)
        c.setFont(BODY_FONT, 9)
        lines = [
            f"Copyright © {self.copyright_year} {self.author}",
            "All rights reserved.",
            "",
            "No part of this publication may be reproduced, distributed, or",
            "transmitted in any form or by any means without the prior written",
            "permission of the author.",
            "",
            f"First edition, {self.copyright_year}",
        ]
        y = 280
        for line in lines:
            c.drawString(MARGIN_INNER, y, line)
            y -= 14
        c.showPage()

    def draw_dedication_page(self):
        if not self.dedication:
            return
        c = self.c
        _draw_interior_parchment(c, PAGE_W, PAGE_H)

        c.setFillColor(BODY_TEXT_COLOR)
        c.setFont(BODY_ITALIC, 13)
        lines = wrap_text_to_lines(
            self.dedication, BODY_ITALIC, 13, PAGE_W - 160, c
        )
        total_height = len(lines) * 20
        y = (PAGE_H + total_height) / 2
        for line in lines:
            tw = c.stringWidth(line, BODY_ITALIC, 13)
            c.drawString((PAGE_W - tw) / 2, y, line)
            y -= 20
        c.showPage()

    def draw_toc(self, chapter_pages):
        c = self.c
        _draw_interior_parchment(c, PAGE_W, PAGE_H)

        c.setFillColor(HEADING_COLOR)
        c.setFont(HEADING_FONT, 20)
        tw = c.stringWidth("CONTENTS", HEADING_FONT, 20)
        c.drawString((PAGE_W - tw) / 2, PAGE_H - 100, "CONTENTS")

        c.setFillColor(BODY_TEXT_COLOR)
        y = PAGE_H - 160

        for ch_num, ch_title, pg_num in chapter_pages:
            if y < MARGIN_BOTTOM + 40:
                c.showPage()
                _draw_interior_parchment(c, PAGE_W, PAGE_H)
                c.setFillColor(BODY_TEXT_COLOR)
                y = PAGE_H - 80

            c.setFont(BODY_FONT, 12)
            rom = roman_numeral(ch_num)
            entry = f"Chapter {rom}  —  {ch_title}" if ch_title else f"Chapter {rom}"

            pg_str = str(pg_num)
            pg_width = c.stringWidth(pg_str, BODY_FONT, 12)
            entry_width = c.stringWidth(entry, BODY_FONT, 12)

            c.drawString(MARGIN_INNER, y, entry)
            c.drawString(PAGE_W - MARGIN_OUTER - pg_width, y, pg_str)

            # Dot leaders
            dot_start = MARGIN_INNER + entry_width + 8
            dot_end = PAGE_W - MARGIN_OUTER - pg_width - 8
            dot_w = c.stringWidth(".", BODY_FONT, 12)
            x = dot_start
            while x < dot_end:
                c.drawString(x, y, ".")
                x += dot_w * 2.5

            y -= 28
        c.showPage()

    def _draw_body_text_justified(self, text, x, y, max_width, font, size,
                                   leading, indent=0, first_para_no_indent=False):
        """
        Draw justified body text. Returns the y position after all text is drawn,
        and the page_number (in case new pages were created).
        """
        c = self.c
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if len(paragraphs) <= 1 and "\n" in text:
            # Check if single-newline separated
            candidate = [p.strip() for p in text.split("\n") if p.strip()]
            if len(candidate) > 1:
                paragraphs = candidate

        is_first = first_para_no_indent

        for para_text in paragraphs:
            para_text = para_text.replace("\n", " ").strip()
            if not para_text:
                continue

            c.setFont(font, size)
            p_indent = 0 if is_first else indent
            effective_width = max_width - p_indent

            lines = wrap_text_to_lines(para_text, font, size, effective_width, c)

            for i, line in enumerate(lines):
                if y < MARGIN_BOTTOM + 20:
                    c.showPage()
                    self.current_page += 1
                    y = self._start_body_page()
                    c.setFillColor(BODY_TEXT_COLOR)
                    c.setFont(font, size)

                lx = x + (p_indent if i == 0 else 0)
                line_width = max_width - (p_indent if i == 0 else 0)

                # Justify all lines except the last line of a paragraph
                is_last_line = (i == len(lines) - 1)
                words = line.split()

                if not is_last_line and len(words) > 1:
                    total_word_w = sum(c.stringWidth(w, font, size) for w in words)
                    extra = (line_width - total_word_w) / (len(words) - 1)
                    # Only justify if spacing is reasonable (< 1 em)
                    if extra < size * 0.9 and extra > 0:
                        cx_pos = lx
                        for wi, word in enumerate(words):
                            c.drawString(cx_pos, y, word)
                            cx_pos += c.stringWidth(word, font, size)
                            if wi < len(words) - 1:
                                cx_pos += extra
                    else:
                        c.drawString(lx, y, line)
                else:
                    c.drawString(lx, y, line)

                y -= leading

            is_first = False

        return y

    def _start_body_page(self):
        """Set up a new body page with background and page number. Returns y start."""
        c = self.c
        _draw_interior_parchment(c, PAGE_W, PAGE_H)
        # Page number
        c.setFillColor(PAGE_NUM_COLOR)
        c.setFont(BODY_FONT, PAGE_NUM_SIZE)
        pg_str = str(self.current_page)
        pg_w = c.stringWidth(pg_str, BODY_FONT, PAGE_NUM_SIZE)
        c.drawString(PAGE_W - MARGIN_OUTER - pg_w, 40, pg_str)
        return PAGE_H - MARGIN_TOP

    def _draw_chapter_divider(self, y):
        """Draw a centered decorative divider line with diamond ornament."""
        c = self.c
        cx = PAGE_W / 2
        line_half = 40  # 80pt total width

        # Gold divider line
        c.setStrokeColor(CHAPTER_DIVIDER_COLOR)
        c.setLineWidth(1)
        c.line(cx - line_half, y, cx - 6, y)
        c.line(cx + 6, y, cx + line_half, y)

        # Small diamond in center
        c.setFillColor(CHAPTER_DIVIDER_COLOR)
        path = c.beginPath()
        path.moveTo(cx, y + 4)
        path.lineTo(cx + 4, y)
        path.lineTo(cx, y - 4)
        path.lineTo(cx - 4, y)
        path.close()
        c.drawPath(path, fill=1, stroke=0)

    def draw_chapter(self, chapter, page_number):
        """Draw a chapter. Returns page number after chapter ends."""
        c = self.c
        self.current_page = page_number
        rom = roman_numeral(chapter["number"])
        title = chapter["title"]
        body = chapter["body"]

        text_x = MARGIN_INNER
        text_width = PAGE_W - MARGIN_INNER - MARGIN_OUTER

        # Start chapter page with extra top space
        _draw_interior_parchment(c, PAGE_W, PAGE_H)

        # Page number
        c.setFillColor(PAGE_NUM_COLOR)
        c.setFont(BODY_FONT, PAGE_NUM_SIZE)
        pg_str = str(self.current_page)
        pg_w = c.stringWidth(pg_str, BODY_FONT, PAGE_NUM_SIZE)
        c.drawString(PAGE_W - MARGIN_OUTER - pg_w, 40, pg_str)

        y = PAGE_H - 100  # Extra top margin for chapter opening

        # Chapter marker — centered, warm dark brown
        c.setFillColor(HEADING_COLOR)
        c.setFont(HEADING_FONT, HEADING_SIZE)
        chapter_text = f"CHAPTER {rom}"
        ch_w = c.stringWidth(chapter_text, HEADING_FONT, HEADING_SIZE)
        c.drawString((PAGE_W - ch_w) / 2, y, chapter_text)
        y -= 14

        # Decorative divider
        self._draw_chapter_divider(y)
        y -= 14

        # Chapter title (only if provided)
        if title:
            c.setFillColor(CHAPTER_TITLE_COLOR)
            c.setFont(BODY_ITALIC, TITLE_SIZE)
            # Title Case instead of ALL CAPS for elegance
            title_display = title.title() if title == title.upper() or title == title.lower() else title
            title_lines = wrap_text_to_lines(
                title_display, BODY_ITALIC, TITLE_SIZE, text_width, c
            )
            for tl in title_lines:
                tl_w = c.stringWidth(tl, BODY_ITALIC, TITLE_SIZE)
                c.drawString((PAGE_W - tl_w) / 2, y, tl)
                y -= 24
        y -= 40  # Space before body

        # Body text
        c.setFillColor(BODY_TEXT_COLOR)
        y = self._draw_body_text_justified(
            body, text_x, y, text_width,
            BODY_FONT, BODY_SIZE, BODY_LEADING,
            indent=PARA_INDENT, first_para_no_indent=True
        )

        c.showPage()
        self.current_page += 1
        return self.current_page

    def draw_back_cover(self):
        c = self.c
        _draw_parchment_bg(c, PAGE_W, PAGE_H)

        # Simplified border — triple line frame only
        c.setStrokeColor(BORDER_GOLD)
        c.setLineWidth(2.5)
        c.rect(30, 30, PAGE_W - 60, PAGE_H - 60, fill=0, stroke=1)
        c.setLineWidth(0.5)
        c.rect(38, 38, PAGE_W - 76, PAGE_H - 76, fill=0, stroke=1)
        c.setLineWidth(1.8)
        c.rect(44, 44, PAGE_W - 88, PAGE_H - 88, fill=0, stroke=1)

        # Small scrollwork ornament in center
        cx, cy = PAGE_W / 2, PAGE_H / 2
        c.setStrokeColor(ACCENT_GOLD)
        c.setLineWidth(1)
        path = c.beginPath()
        path.moveTo(cx - 50, cy)
        path.curveTo(cx - 35, cy + 20, cx - 15, cy + 20, cx, cy)
        path.curveTo(cx + 15, cy - 20, cx + 35, cy - 20, cx + 50, cy)
        c.drawPath(path, fill=0, stroke=1)
        # Mirror
        path = c.beginPath()
        path.moveTo(cx - 50, cy)
        path.curveTo(cx - 35, cy - 15, cx - 15, cy - 15, cx, cy)
        path.curveTo(cx + 15, cy + 15, cx + 35, cy + 15, cx + 50, cy)
        c.drawPath(path, fill=0, stroke=1)

        # Author name
        c.setFillColor(COVER_TEXT)
        c.setFont(HEADING_FONT, 14)
        aw = c.stringWidth(self.author.upper(), HEADING_FONT, 14)
        c.drawString((PAGE_W - aw) / 2, 75, self.author.upper())

        c.showPage()

    def generate(self, chapters):
        self.chapters = chapters

        # Cover
        self.draw_cover()
        # Dedication (optional — no title page or copyright page)
        self.draw_dedication_page()

        # Calculate front matter pages (cover + optional dedication)
        front_pages = 1 + (1 if self.dedication else 0)
        toc_pages = max(1, math.ceil(len(chapters) / 18))
        first_chapter_page = front_pages + toc_pages + 1

        # Estimate chapter page numbers for TOC
        chapter_pages_list = []
        current_pg = first_chapter_page
        for ch in chapters:
            chapter_pages_list.append((ch["number"], ch["title"], current_pg))
            word_count = len(ch["body"].split())
            est_pages = max(1, math.ceil(word_count / 350))
            current_pg += est_pages

        # TOC
        self.draw_toc(chapter_pages_list)

        # Chapters
        page_num = first_chapter_page
        for ch in chapters:
            page_num = self.draw_chapter(ch, page_num)

        # Back cover
        self.draw_back_cover()

        self.c.save()

        total_words = sum(len(ch["body"].split()) for ch in chapters)
        print(f"Book generated: {self.output_path}")
        print(f"  Title: {self.title}")
        print(f"  Author: {self.author}")
        print(f"  Chapters: {len(chapters)}")
        print(f"  Total words: {total_words:,}")
        print(f"  Pages: ~{page_num}")

        return {
            "path": self.output_path,
            "chapters": len(chapters),
            "words": total_words,
            "pages": page_num
        }


def main():
    parser = argparse.ArgumentParser(description="Generate a book PDF")
    parser.add_argument("--title", required=True, help="Book title")
    parser.add_argument("--author", default="Blackbox", help="Author name (default: Blackbox)")
    parser.add_argument("--subtitle", default="", help="Book subtitle")
    parser.add_argument("--dedication", default="", help="Dedication text")
    parser.add_argument("--copyright-year", default=None, help="Copyright year")
    parser.add_argument("--input", required=True, help="Path to prose text file")
    parser.add_argument("--output", default="book.pdf", help="Output PDF path")

    args = parser.parse_args()

    # Read input file
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    chapters = parse_chapters(text)

    gen = BookGenerator(
        title=args.title,
        author=args.author,
        subtitle=args.subtitle,
        dedication=args.dedication,
        copyright_year=args.copyright_year,
        output_path=args.output,
    )

    result = gen.generate(chapters)
    return result


if __name__ == "__main__":
    main()
