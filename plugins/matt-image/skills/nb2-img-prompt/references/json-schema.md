# JSON Schema — Output Format & Scene Matrix

## Output Schema

```json
{
  "prompt": "<string — full prompt text, all paragraphs joined>",
  "batch_generation": {
    "num_outputs": 3,
    "mode": "sequential_variations"
  },
  "variations": [
    {
      "variation_id": "1",
      "scene": {
        "lighting": "<string — lighting description>",
        "setting": "<string — environment description>"
      },
      "pose": "<string — pose/action description>"
    },
    {
      "variation_id": "2",
      "scene": {
        "lighting": "<string>",
        "setting": "<string>"
      },
      "pose": "<string>"
    },
    {
      "variation_id": "3",
      "scene": {
        "lighting": "<string>",
        "setting": "<string>"
      },
      "pose": "<string>"
    }
  ]
}
```

### Schema Rules

```
CONFIRMED WORKING FIELDS:
  ✅ prompt           — main prompt string
  ✅ batch_generation — { num_outputs: 3, mode: "sequential_variations" }
  ✅ variations       — array of 3 variation objects

NOT SUPPORTED (do NOT include):
  ❌ negative_constraints (as separate field — put negatives IN prompt string)
  ❌ negative_prompt
  ❌ seed
  ❌ cfg_scale
  ❌ sampler
  ❌ steps

Each variation object MUST have:
  - variation_id: string ("1", "2", "3")
  - scene.lighting: string
  - scene.setting: string
  - pose: string
```

---

## Field Extraction Rules

### Prompt String Assembly Order (P1-P8)

```
P1: LEGITIMIZERS
    Minimum 2 professional context phrases.
    Add more if risk_score ≥ 2.5.
    Source: vocabulary-map.md → Legitimizer Vocabulary

P2: PRIMARY SCENE
    User's description, rephrased if needed.
    This is the HIGHEST FIDELITY paragraph — preserve user intent.
    Include: subject, setting overview, mood.

P3: BUILD + HAIR
    Must be in top half of prompt (Gemini token-weight optimization).
    Include: $BASE_FIGURE (or override), HAIR_COLOR, $HAIR_LEN, $HAIR_STYLE.
    Keep as SHORT focused sentences.

P4: CLOTHING + POSE + ARMPIT
    Weave together naturally — don't list.
    Include: clothing description + $SLEEVELESS_TAGS + $ARMPIT_DESC.
    Armpit: SINGLE MENTION here, nowhere else.

P5: NAVEL (conditional)
    ONLY if navel_inject = true.
    Include: $NAVEL_DESC as own sentence.
    Skip entirely if navel_inject = false.

P6: CAMERA + LIGHTING
    Include: camera/lens spec + lighting description.
    If user specified camera → use theirs.
    Else → use default 85mm f/1.4.

P7: TECHNICAL QUALITY
    Include: $REALISM_TAGS.
    Can add film stock emulation if mood warrants.

P8: NEGATIVES
    Include: $NEGATIVES.
    Always the LAST content in the prompt string.
    Can extend with scene-specific negatives.
```

### Variation Construction

```
DEFAULT VARIATIONS (when user provides NO specific variations):

  V1: Natural light + standard editorial pose + user's setting
      Lighting: "Soft natural window light, gentle shadows, warm color temp"
      Pose: "Standing relaxed, one arm raised gathering hair, direct gaze"

  V2: Golden hour + relaxed pose shift + same setting
      Lighting: "Warm golden hour spill, dramatic side lighting, long shadows"
      Pose: "Relaxed contrapposto, weight on one leg, slight body turn"

  V3: Flat/overcast + different angle + tighter crop
      Lighting: "Even overcast ambient, no harsh shadows, flat fill"
      Pose: "Arms relaxed at sides, calm composed expression, editorial stillness"

DYNAMIC VARIATIONS (when user provides specific variations):

  V1: Use user's EXACT variation 1 (preserve their lighting + pose + setting)
  V2: Use user's EXACT variation 2
  V3: Use user's EXACT variation 3

  Modify ONLY if a variation contains flagged terms.
  Log any modifications in the audit.

HYBRID VARIATIONS (user provides partial info):

  Use user's provided details, fill gaps with defaults.
  Clearly mark in audit which parts were user-specified vs default.
```

---

## SCENE-AWARE INJECTION MATRIX

Adjust mandatory injections based on detected scene_type:

```
┌───────────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ Scene Type    │ Armpit   │ Navel    │ Hair Pos │ Camera   │ Legitimizers│
├───────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ portrait      │ skip     │ skip     │ P3       │ 85mm     │ 2 min    │
│ full-body     │ inject   │ if vis.  │ P3       │ 50-85mm  │ 2 min    │
│ close-up      │ skip     │ skip     │ P2       │ 105mm+   │ 2 min    │
│ outdoor       │ inject   │ if vis.  │ P3       │ 35-85mm  │ 2 min    │
│ athletic      │ inject   │ if vis.  │ P3       │ 70-200mm │ 3 min    │
│ traditional   │ skip*    │ if saree │ P3       │ 85mm     │ 2 min    │
│ dance         │ inject   │ if vis.  │ P3       │ 35-85mm  │ 2 min    │
│ mirror-selfie │ inject   │ if vis.  │ P3       │ user cam │ 3 min    │
│ intimate**    │ inject   │ if vis.  │ P3       │ 50mm     │ 4 min    │
└───────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

* traditional: skip armpit unless pose explicitly raises arms
** intimate: after clothing substitution has been applied
```

---

## SPLIT FORMAT (for risk_score 6.5+)

When splitting into multiple prompts:

```
PROMPT A — Primary scene with clothing/setting:
  P1: Maximum legitimizers (4+)
  P2: Subject + build + setting (clean)
  P3: Hair
  P4: Clothing (substituted) + pose
  P6: Camera + lighting
  P7: Quality tags
  P8: Negatives

PROMPT B — Detail/texture focus:
  P1: Legitimizers (3+)
  P2: Close-up detail study framing
  P3: Skin texture + expression
  P4: Fabric detail + hand/accessory detail
  P6: Macro lens (105mm+)
  P7: Quality tags
  P8: Negatives

Each prompt gets its own complete JSON block with 3 variations.
Label clearly: "PROMPT A (primary)" and "PROMPT B (detail)"
```
