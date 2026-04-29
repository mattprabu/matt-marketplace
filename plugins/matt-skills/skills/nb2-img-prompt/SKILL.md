---
name: nb2-img-prompt
description: Generates optimized, safety-compliant image prompts for AI image generators (Midjourney, DALL-E, Stable Diffusion). Use when the user wants a detailed prompt from a concept or subject.
argument-hint: "[subject or concept]"
---

Generate a polished, optimized image prompt from the concept in $ARGUMENTS.

## Steps

1. **Expand the concept** — Break the input into four core components:
   - **Subject**: Who or what is the focus (person, object, scene)
   - **Style/Mood**: Visual style, era, artistic influence
   - **Lighting**: Natural, golden hour, studio, neon, etc.
   - **Composition**: Framing, angle, depth of field, background

2. **Write the full prompt** — Combine into a single flowing description. Be specific and visual. Avoid abstract adjectives like "beautiful" or "amazing" — describe what makes it visually striking instead.

3. **Apply safety compliance** — Ensure the prompt:
   - Contains no real person's name or likeness
   - Avoids violent, sexual, or otherwise policy-violating content
   - Uses general descriptors for ethnicity/appearance if needed

4. **Format for each generator**

   **Midjourney:**
   ```
   /imagine [full prompt] --ar 4:5 --style raw --v 6
   ```

   **DALL-E:**
   ```
   [Full prompt written as a natural sentence. Specify style as "photorealistic", "illustration", etc.]
   ```

   **Stable Diffusion:**
   ```
   Positive: [comma-separated keywords]
   Negative: blurry, low quality, watermark, text, deformed
   ```

## Notes
- Default aspect ratio: 4:5 (portrait) unless the concept implies otherwise
- If the concept is vague, ask one clarifying question before generating
- Output all three generator formats unless the user specifies one
