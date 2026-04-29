# Matt's Claude Marketplace

A personal Claude Code plugin marketplace with three practical skills.

## Skills

| Skill | What it does |
|---|---|
| `book-formatter` | Formats raw prose into professional book layout with front matter, headings, and typography |
| `analyze-property` | Deep analysis of a single US residential property — valuation, location, investment snapshot |
| `screen-properties` | Bulk-screens a list of US properties and ranks them by investment potential |
| `nb2-img-prompt` | Generates optimized image prompts for Midjourney, DALL-E, and Stable Diffusion |
| `bytebytego-explainer` | Transforms any technical topic into a ByteByteGo-style visual explanation with diagrams |
| `resume-builder` | Creates, revises, or tailors resumes for specific job postings |

## Install

Add this marketplace to Claude Code:

```
/plugin marketplace add https://raw.githubusercontent.com/mattprabu/matt-marketplace/main/.claude-plugin/marketplace.json
```

Then install the plugin:

```
/plugin install matt-skills
```

## Usage

```
/matt-skills:book-formatter path/to/manuscript.md
/matt-skills:analyze-property 123 Main St, Austin TX 78701
/matt-skills:nb2-img-prompt woman in silk dress at a rooftop garden, golden hour
```
