# NSFW Rules v3 — Context-Aware Engine

## LAYER 1 — SCENE CONTEXT CLASSIFIER

Classify the FULL scene before scanning individual terms.
The context determines how aggressively terms get flagged.

### Classification Rules

```
SAFE (×0.5 multiplier):
  - Outdoor/nature/landscape scenes
  - Professional studio with full lighting rigs mentioned
  - Traditional cultural clothing (saree, kimono, hanbok, ao dai)
  - Sports/fitness with full athletic gear
  - Formal/business attire
  - Group/crowd scenes
  - Food/product photography
  - Architecture/interior design focus

NEUTRAL (×1.0 multiplier):
  - Fashion editorial with standard clothing
  - Beach/pool with standard swimwear
  - Dance/performance context
  - Home/casual environment with everyday clothes
  - Fitness with crop tops / sports bras (standard gym wear)
  - Mirror selfie with casual or athletic clothing
  - Sleepwear / loungewear (non-sheer, full coverage)

ELEVATED (×1.5 multiplier):
  - Explicitly intimate framing language
  - Underwear/lingerie as primary clothing
  - Sheer/see-through as primary fabric descriptor
  - Wet clothing emphasis combined with body focus
  - Bedroom + minimal clothing + body-focused framing
  - Bath/shower scenes with body emphasis
```

### Context Override Rules (NEW v3)
```
If scene contains 3+ SAFE indicators alongside 1 ELEVATED indicator:
  → Downgrade to NEUTRAL (the safe context dominates)

If scene contains professional legitimizers + standard clothing terms:
  → Cap at NEUTRAL even if setting is bedroom/bathroom

If clothing is athletic/sportswear (NOT lingerie/underwear):
  → Cap at NEUTRAL regardless of setting
```

---

## LAYER 2 — MULTI-LEVEL RISK DETECTION

### CHECK A — Hard Block Terms

These are ALWAYS removed regardless of context:

```
HARD BLOCK LIST:
  lingerie, underwear, panties, bra (when sole garment),
  thong, g-string, negligee, corset (when sole garment),
  nude, naked, topless, bottomless, undressing, stripping,
  spread legs, bent over (sexual context), orgasm, arousal,
  genitals, nipple (explicit), breast (explicit exposure),
  bondage, fetish, dominatrix, submissive (sexual),
  lolita, schoolgirl (sexualized), jailbait,
  deepfake, [any real person name for sexual content]
```

### CHECK B — Soft Block Terms + Context Exemption Table

```
SOFT BLOCK TERMS (with weight tiers):

  HIGH WEIGHT (+2.0):
    tan lines, visible underwear line, camel toe,
    wet t-shirt, body oil (sexualized), spread,
    upskirt, downblouse, wardrobe malfunction,
    barely covering, almost revealing

  MEDIUM WEIGHT (+1.0):
    cleavage, décolletage, sideboob, underboob,
    midriff (when combined with suggestive pose),
    skin-tight (when body-emphasizing), low-rise,
    braless, commando, sheer (primary descriptor),
    bedroom eyes, come-hither, seductive gaze

  LOW WEIGHT (+0.5):
    curves, figure, body, skin, flesh,
    tight (clothing), form-fitting, snug,
    bare shoulders, bare legs, bare feet,
    perspiration, glistening, dewy skin,
    plunging neckline, backless, strapless
```

### CONTEXT EXEMPTION TABLE (v3 — EXPANDED)

Terms that score 0.0 and are KEPT when context qualifies:

```
┌──────────────────────┬─────────────────────────────────────┬──────────┐
│ Term                 │ EXEMPT when context includes...     │ Weight   │
├──────────────────────┼─────────────────────────────────────┼──────────┤
│ curves / curvy       │ body type descriptor (not action)   │ LOW→0    │
│ figure               │ body build reference                │ LOW→0    │
│ body                 │ full-body shot / body type          │ LOW→0    │
│ skin                 │ skin tone / skin texture / skincare │ LOW→0    │
│ tight                │ tight jeans / tight dress / fit     │ LOW→0    │
│ form-fitting         │ clothing fit descriptor             │ LOW→0    │
│ bare shoulders       │ sleeveless / off-shoulder tops      │ LOW→0    │
│ bare legs            │ shorts / skirt / dress context      │ LOW→0    │
│ bare feet            │ beach / home / yoga context         │ LOW→0    │
│ perspiration         │ fitness / sports / workout          │ LOW→0    │
│ glistening           │ skin after workout / rain / water   │ LOW→0    │
│ dewy skin            │ skincare / beauty editorial         │ LOW→0    │
│ plunging neckline    │ fashion / dress description         │ LOW→0    │
│ backless             │ dress / gown / formal wear          │ LOW→0    │
│ strapless            │ dress / top / gown description      │ LOW→0    │
│ midriff              │ crop top / saree / athletic wear    │ LOW→0    │
│ cleavage             │ formal dress / fashion editorial    │ MED→0   │
│ low-rise             │ jeans / pants description           │ MED→0   │
│ skin-tight           │ athletic wear / leggings / wetsuit  │ MED→0   │
│ snug                 │ clothing fit (any)                  │ LOW→0    │
│ flesh                │ flesh tone / skin color reference   │ LOW→0    │
│ crop top             │ ANY fashion/athletic context        │ LOW→0    │
│ sports bra           │ ANY fitness/athletic context        │ LOW→0    │
│ bikini               │ beach / pool / swim context         │ MED→0   │
│ swimsuit             │ beach / pool / swim / resort        │ LOW→0    │
│ bodysuit             │ dance / fashion / editorial         │ LOW→0    │
│ leotard              │ dance / gymnastics / ballet         │ LOW→0    │
│ compression shorts   │ athletic / gym / running            │ LOW→0    │
│ tank top             │ ANY casual / athletic context       │ LOW→0    │
│ halter               │ fashion / dress / top description   │ LOW→0    │
│ off-shoulder         │ fashion / top / dress description   │ LOW→0    │
│ tube top             │ casual / summer fashion             │ LOW→0    │
│ bandeau              │ fashion / beach / swim context      │ LOW→0    │
│ romper               │ casual / summer fashion             │ LOW→0    │
│ playsuit             │ casual / summer fashion             │ LOW→0    │
│ shorts (any)         │ ANY context                         │ LOW→0    │
│ mini skirt / miniskirt│ fashion / casual / editorial       │ LOW→0    │
│ décolletage          │ fashion / neckline description      │ MED→0   │
│ sideboob             │ fashion editorial / red carpet      │ MED→LOW │
└──────────────────────┴─────────────────────────────────────┴──────────┘
```

### CHECK C — Semantic Intent Patterns

```
SEMANTIC INTENT PATTERNS (flag the WHOLE phrase, not words):

  "showing off her body"     → INTENT: exhibition framing
  "exposing herself"         → INTENT: exhibition framing
  "barely covered"           → INTENT: near-nudity emphasis
  "clothes falling off"      → INTENT: undressing narrative
  "struggling to contain"    → INTENT: wardrobe malfunction
  "bursting out of"          → INTENT: wardrobe malfunction
  "teasing the viewer"       → INTENT: direct sexual address
  "inviting the viewer"      → INTENT: direct sexual address
  "for your pleasure"        → INTENT: direct sexual address
  "wants you to look"        → INTENT: voyeur framing
  "caught changing"          → INTENT: voyeur framing
  "secretly photographed"    → INTENT: voyeur framing
  "removing her [clothing]"  → INTENT: undressing action
  "pulling down"             → INTENT: undressing action
  "sliding off"              → INTENT: undressing action
```

### CHECK D — Vulnerable Context Patterns

```
VULNERABLE CONTEXT (always flag):
  Any implied minor (school uniform + young, teen, childlike)
  Power-dynamic framing (boss/employee, teacher/student sexual)
  Non-consent language (forced, reluctant, unconscious)
  Intoxication + sexual context
  Hidden camera / surveillance framing
```

### CHECK E — Combination Risk Patterns

```
COMBINATION RISK (weighted additions):

  bedroom + underwear/lingerie          → +2.0
  wet + sheer + body-focus              → +2.0
  bedroom + mirror + minimal clothing   → +1.5
  body oil + posing + minimal clothing  → +1.5
  camera angle (low/upward) + skirt     → +1.5
  tight clothing + wet + body emphasis  → +1.0
  bedroom + alone + posing              → +0.5
  mirror + selfie + athletic wear       → +0.0 (SAFE combo)
  gym + sports bra + workout            → +0.0 (SAFE combo)
  beach + bikini + standing             → +0.0 (SAFE combo)
  dance studio + leotard + movement     → +0.0 (SAFE combo)
```

---

## GATED SUBSTITUTION ENGINE

```
GATED TIERS (based on final_score after context multiplier):

  NONE     (0 - 2.0):   No substitutions. All original words preserved.
  LIGHT    (2.5 - 4.0): Substitute ONLY HIGH-weight non-exempt terms (Tier 1)
  MODERATE (4.5 - 6.0): Substitute ALL non-exempt flagged terms (Tier 1)
  HEAVY    (6.5 - 8.0): Substitute ALL flagged terms (Tier 1-2), consider split
  MAXIMUM  (8.5+):      Aggressive Tier 2-3 on ALL body/clothing terms + split
```

---

## DOUBLE-DIP PREVENTION

```
RULES — check AFTER substitution, BEFORE final assembly:

  □ No more than 2 body-part references in a single sentence
  □ No moisture + body part in same clause
  □ No expression + pose in same clause (when both suggestive)
  □ No camera angle + body part combination in same clause
  □ Maximum 1 fabric-transparency term per prompt
  □ No stacking: body-type + clothing-tightness + pose in same sentence

If violation found → split into separate sentences with legitimizer between.
```

---

## DUAL SCORING — Risk + Fidelity

### Risk Score Thresholds
```
  ✅ 0 - 2.0    → Safe. No action needed.
  ⚠️ 2.5 - 4.0  → Low risk. Light substitution only.
  🔶 4.5 - 6.0  → Moderate. Standard substitution.
  🔴 6.5 - 8.0  → High. Heavy substitution + possible split.
  ⛔ 8.5+       → Very high. Maximum intervention.
```

### Fidelity Score Calculation (v3 — WEIGHTED)
```
Each user visual element gets a WEIGHT based on importance:

  CRITICAL (×3): subject, clothing type, setting
  HIGH     (×2): pose, lighting, expression, hair
  MEDIUM   (×1): camera, mood, background details
  LOW      (×0.5): technical tags, color grading, film grain

Fidelity = (sum of preserved_element × weight) / (sum of all_element × weight) × 100

MINIMUM FIDELITY THRESHOLDS:
  NONE tier:     100% (nothing changed)
  LIGHT tier:    ≥90%
  MODERATE tier: ≥80%
  HEAVY tier:    ≥70%
  MAXIMUM tier:  ≥60%

If fidelity would drop below threshold:
  → Reduce substitution scope on MEDIUM/LOW weight elements first
  → Preserve CRITICAL elements even at cost of higher risk score
  → Log: "Fidelity override: [element] preserved despite flag"
```

---

## 20-POINT VALIDATION CHECKLIST

```
□ 1.  Starts with 2+ professional legitimizers?
□ 2.  No hard-block terms present?
□ 3.  All non-exempt soft-block terms handled per gated tier?
□ 4.  No absolute modifiers (strictly/clearly/explicitly)?
□ 5.  Pose described as action with purpose, not exposure?
□ 6.  Risk score within threshold OR appropriate gating applied?
□ 7.  3+ technical photography terms present?
□ 8.  Armpit mentioned exactly once?
□ 9.  No unresolved $VAR literals?
□ 10. No bracket labels [like this] in prompt string?
□ 11. No semantic intent patterns present?
□ 12. Hair positioned before technical tags?
□ 13. No double-dip violations (body stacking)?
□ 14. No vulnerable context patterns present?
□ 15. Maximum 1 fabric-transparency term used?
□ 16. Expression and pose not in same clause (if both suggestive)?
□ 17. Context exemptions correctly applied? (exempt terms preserved as-is)
□ 18. Fidelity score meets minimum threshold for risk level?
□ 19. No Latin/medical jargon in substitutions?
□ 20. Each substitution produces visual equivalent? (no editorial jargon)
```
