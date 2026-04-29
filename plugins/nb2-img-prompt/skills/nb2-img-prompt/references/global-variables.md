# Global Variables — Resolved Values for Mandatory Injection

All $VAR references in the pipeline must be resolved to these values.
NEVER output a literal "$VAR" string in the final prompt.

---

## Mandatory Injection Variables

```
$STYLE_PREFIX
  Resolved: "Editorial fashion photography, fine art portrait study."
  Inject at: P1 (first sentence, always)
  Can be augmented with additional legitimizers from vocabulary-map.md

$BASE_FIGURE
  Resolved: "Curvaceous statuesque figure, natural unfiltered skin texture."
  Inject at: P2-P3
  Override: If user specifies build (slim, athletic, petite, etc.),
            replace "curvaceous statuesque" with user's term.
  Always keep: "natural unfiltered skin texture"

$HAIR_LEN
  Resolved: "Extremely long hair reaching knees, natural frizzy waves"
  Inject at: P3 (must be in top half of prompt)
  Override: If hair_override = true, use user's specified length.
  Always pair with $HAIR_STYLE and HAIR_COLOR.

$HAIR_STYLE
  Resolved: "blow-dried soft waves, high root volume"
  Inject at: P3 (immediately after $HAIR_LEN)
  Skip if: hair_override = true AND user specified a different style

HAIR_COLOR
  Resolved: "deep black" (default)
  Override: Use user's specified color if provided.
  Inject at: P3 (between $HAIR_LEN and $HAIR_STYLE)

$SLEEVELESS_TAGS
  Resolved: "Contemporary sleeveless ensemble, presenting anatomically accurate portrayal."
  Inject at: P4 (clothing paragraph)
  Merge with: user's clothing description if present.
  If user specifies sleeved clothing: replace "sleeveless" with user's sleeve type.

$ARMPIT_DESC
  Resolved: "natural body hair visible in underarm regions when arms raised, authentic unretouched editorial presentation, realistic hair texture, organic underarm shadow detail"
  Inject at: P4 (single mention only)
  CRITICAL: inject ONCE. Never repeat in variations or elsewhere.
  Trigger: Always inject unless pose explicitly prevents arm visibility
           (e.g., arms pinned to sides, crossed arms, hands in pockets)

$NAVEL_DESC
  Resolved: "Extra-wide oval innie navel with deep fold prominently displayed."
  Inject at: P5 (own paragraph/sentence)
  Trigger: ONLY if navel_inject = true
  navel_inject = true when:
    - full-body shot AND midriff visible
    - crop top / sports bra
    - saree / lehenga
    - two-piece outfit with exposed midsection
    - any explicit navel mention by user
  navel_inject = false when:
    - portrait/headshot only
    - torso fully covered (jacket, hoodie, dress)
    - no clothing context given (default false)

CAMERA (not a $VAR but mandatory)
  Default: "Shot on 85mm lens, f/1.4 aperture, medium telephoto portrait compression."
  Override: If user specifies camera/lens, use their specification.
  Inject at: P6

$REALISM_TAGS
  Resolved: "Highly realistic, subsurface scattering, 8K ultra-clear, tack-sharp clarity, subtle analog film grain, masterpiece quality."
  Inject at: P7 (technical quality paragraph)
  Can be augmented with film stock emulation or format-specific tags.

$NEGATIVES
  Resolved: "Avoid: dry skin, dry hair, airbrushed skin, cartoon style, illustration style, bad anatomy, distorted face, extra limbs, deformed hands, plastic skin, wax skin, AI artefacts, blurry, overexposed, heavy makeup, unnatural proportions."
  Inject at: P8 (always last)
  Can be extended with scene-specific negatives.
```

---

## Variable Resolution Checklist

Before emitting final JSON, verify:
```
□ No "$STYLE_PREFIX" literal in output
□ No "$BASE_FIGURE" literal in output
□ No "$HAIR_LEN" literal in output
□ No "$HAIR_STYLE" literal in output
□ No "$SLEEVELESS_TAGS" literal in output
□ No "$ARMPIT_DESC" literal in output
□ No "$NAVEL_DESC" literal in output
□ No "$REALISM_TAGS" literal in output
□ No "$NEGATIVES" literal in output
□ No "$ARM_POSE" literal in output
□ No unresolved $VAR of any kind in output
```
