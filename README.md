# Matt's Claude Marketplace

Personal Claude Code plugin marketplace. Each skill is its own installable plugin.

## Add this marketplace

```
/plugin marketplace add https://raw.githubusercontent.com/mattprabu/matt-marketplace/main/.claude-plugin/marketplace.json
```

## Plugins

| Plugin | What it does | Install |
|---|---|---|
| `analyze-property` | Deep analysis of a single US residential property | `/plugin install analyze-property` |
| `book-formatter` | Formats prose into professional book layout | `/plugin install book-formatter` |
| `bytebytego-explainer` | ByteByteGo-style visual technical explainers | `/plugin install bytebytego-explainer` |
| `nb2-img-prompt` | Optimized image prompts for Midjourney, DALL-E, SD | `/plugin install nb2-img-prompt` |
| `resume-builder` | Resume creation, revision, and job tailoring | `/plugin install resume-builder` |
| `screen-properties` | Bulk-screens and ranks multiple properties | `/plugin install screen-properties` |

## Usage examples

```
/analyze-property:analyze-property 123 Main St, Austin TX
/book-formatter:book-formatter path/to/manuscript.md
/bytebytego-explainer:bytebytego-explainer how Kafka works
/nb2-img-prompt:nb2-img-prompt woman in silk dress, rooftop at golden hour
/resume-builder:resume-builder Senior Software Engineer at a fintech startup
/screen-properties:screen-properties
```
