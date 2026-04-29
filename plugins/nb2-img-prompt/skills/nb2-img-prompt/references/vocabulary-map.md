# Vocabulary Map v3 — Visual-Equivalent Substitutions + Photography Lexicon

## SUBSTITUTION TIERS

Each tier represents increasing distance from the original term.
Always use the LOWEST tier that resolves the flag.

---

## CLOTHING SUBSTITUTIONS

### Underwear / Lingerie → Closest Visual Equivalents

```
TIER 1 (closest visual — minimal coverage shift):
  lingerie set          → fine foundational garments, delicate lace-trimmed structural wear
  bra                   → form-fitting structural bodice, minimalist bralette
  bra + panties         → bralette and high-cut minimal briefs
  lace bra              → lace-trimmed bralette, textured sheer knit bodice
  panties               → minimal coverage briefs, high-cut hip-slung base layer
  thong                 → high-cut minimal pelvic garment, abbreviated base layer
  negligee              → silk slip dress, mid-thigh length, lightweight drape
  corset                → structured boned bustier top, architectural tailoring
  babydoll              → short chemise, lightweight flowing hem
  bodysuit (intimate)   → form-fitting structural bodysuit, seamless cut
  teddy                 → one-piece fitted romper, minimal structure
  garter belt           → [REMOVE — no visual equivalent]
  stockings (intimate)  → sheer hosiery, fine-knit leg covering
  camisole (intimate)   → lightweight spaghetti-strap top, relaxed drape

TIER 2 (athletic reframe, similar silhouette):
  lingerie set          → matching athletic crop top and high-waisted shorts
  bra + panties         → sports bra and compression shorts
  lace bra              → structured bandeau top with textured knit
  negligee              → midi wrap dress, lightweight chiffon
  corset                → fitted peplum top with boning detail
  bodysuit              → performance bodysuit, athletic cut
  teddy                 → romper, relaxed jersey knit
  thong                 → high-cut athletic briefs

TIER 3 (full coverage, different silhouette):
  lingerie set          → two-piece lounge set, ribbed cotton
  bra + panties         → full athletic outfit (tank + leggings)
  negligee              → maxi dress, flowing fabric
  corset                → structured blazer, cinched waist
  bodysuit              → long-sleeve unitard, dance-style
```

### Sheer / Transparent / Wet Fabrics

```
TIER 1:
  see-through           → light-permeable weave, diaphanous fabric
  sheer                 → fine-knit gauzy textile, airy translucent weave
  mesh (body-revealing) → performance mesh panel (athletic)
  transparent           → translucent layered fabric
  barely-there fabric   → ultra-lightweight technical fabric
  wet clothes           → moisture-clinging fabric, damp textile drape
  wet t-shirt           → hydro-adherent fitted top

TIER 2:
  see-through           → layered gauze over fitted base
  sheer                 → matte chiffon overlay
  mesh                  → ventilated athletic panel
  transparent           → frosted organza layer
  wet clothes           → rain-dampened fabric texture
  wet t-shirt           → rain-soaked athletic top

NOTE: Maximum 1 fabric-transparency term per prompt (any tier).
```

### Swimwear (CONTEXT-DEPENDENT)

```
In beach/pool/swim context — these are EXEMPT, use as-is:
  bikini, one-piece, swimsuit, swim shorts, rash guard,
  sarong, cover-up, board shorts, tankini,
  aquatic athletic wear, beach-ready structural garments

In NON-swim context — substitute:
  bikini                → bralette and high-waisted shorts
  string bikini         → minimal-coverage athletic two-piece
  micro bikini          → [REMOVE — Tier 3 substitute: standard bikini]
```

### General Clothing Descriptors (use for precision)

```
COVERAGE / FIT VOCABULARY (always safe):
  form-fitting tailored apparel, body-contouring garments,
  high-tension fabric drape, architectural tailoring,
  structured bodice, tailored silhouette, clean hemline,
  abbreviated flared fabric, high-hemmed lower garment,
  plunging neckline, deep-v tailored top, scooped collar,
  distressed textiles, torn asymmetrical garments,
  mid-thigh tailored cut, hip-slung waistline,
  cinched waist, empire waist, drop waist,
  racerback cut, scoop back, keyhole detail

FABRIC VOCABULARY (always safe):
  ribbed cotton, jersey knit, silk charmeuse,
  matte chiffon, organza, tulle, lace overlay,
  stretch lycra, performance nylon, mesh panel,
  denim, leather, suede, velvet, satin,
  linen, cashmere, wool blend, ponte knit
```

---

## BODY DESCRIPTION SUBSTITUTIONS

```
TIER 1 (closest — anatomical reframe, same visual):
  breasts               → bust, upper body volume, chest architecture
  large breasts          → pronounced volumetric bust, generous upper proportions
  busty                 → voluptuous upper figure, full-figured proportions
  cleavage              → deep sternum shadowing, pronounced v-neck transition
  underboob             → lower bust contour, high-cropped hemline exposure
  sideboob              → lateral bust profile, outer chest contour
  butt / ass            → posterior curves, lower structural volume
  big butt              → voluminous gluteal proportions, generous lower volume
  crotch                → [REMOVE]
  nipples               → [REMOVE]
  groin                 → [REMOVE]
  thighs (sexualized)   → substantial upper leg proportions, robust thigh architecture
  thick thighs          → muscular thigh structure, robust femoral volume
  hips / wide hips      → broad pelvic structure, flared lateral contours
  waist / snatched      → tapered midsection, narrow torso transition
  abs / six pack        → defined abdominal musculature, core definition
  hourglass figure      → balanced proportions, undulating body contours
  skinny / thin         → slender structural form, minimalist anatomical volume
  toned / fit           → athletic musculature, defined anatomical topography

TIER 2 (reframe as build silhouette):
  large breasts          → full figure, generous build
  big butt               → athletic build, pronounced hip curve
  hourglass figure       → balanced proportions, classic silhouette
  thick thighs           → athletic legs, strong lower body
  busty                 → voluptuous classical proportions
  wide hips             → pronounced structural proportions

TIER 3 (abstract away — build type only):
  any explicit body part → reference build type only
  "voluptuous body"      → "statuesque presence"
  "sexy figure"          → "striking silhouette"
  "hot body"             → "aesthetically striking form, symmetrical physique"
  "sexy body"            → "classical human figure, striking proportions"
```

### Skin / Complexion (MOSTLY EXEMPT)

```
These are almost always SAFE — only flag if combined with sexual context:

  ALWAYS EXEMPT (score 0, keep as-is):
    warm skin tone, olive complexion, dark complexion,
    fair skin, freckled, sun-kissed, golden-brown,
    matte skin, luminous skin, natural skin texture,
    unretouched skin, skin imperfections, pores visible,
    goosebumps, body hair, alabaster skin, bronzed skin,
    pale complexion, low-melanin complexion,
    rosy tint, flushed cheeks, natural blushing,
    textured skin, high-specular skin reflection

  FLAG ONLY IN SEXUAL COMBO:
    oiled skin, wet skin, glistening body, sweaty body,
    shiny oiled surface, glossy skin finish
    → Tier 1: "natural sheen" / "post-workout glow" / "dewy finish"
    → Tier 1: "high-specular skin reflection" / "glossy epidermal finish"

  ENVIRONMENTAL CONTEXT (exempt when justified):
    sweaty + gym/workout/sports → EXEMPT ("post-exercise moisture")
    wet skin + rain/pool/beach → EXEMPT ("water-contact skin surface")
    glistening + golden hour → EXEMPT ("specular highlight on skin")
    dirty skin + outdoor/labor → EXEMPT ("environmental particulate texture")
```

### Tan Lines

```
  "visible tan lines"           → "natural skin tone variation" (Tier 1)
  "tan line gradient"           → "sun-kissed complexion gradient" (Tier 1)
  "bikini tan lines"            → "subtle warm-to-cool skin transition" (Tier 2)
  "showing tan lines"           → [REMOVE — exhibition framing] (Tier 2)
```

---

## POSE / ACTION SUBSTITUTIONS

```
TIER 1 (closest visual — reframe intent, keep position):
  "spreading legs"             → "wide-placed feet, open hip posture, extended stance"
  "bending over"               → "anterior torso flexion, leaning forward posture"
  "on all fours"               → "tabletop pose, grounded limb support"
  "straddling"                 → "seated with wide base, open stance"
  "arching back"               → "pronounced lumbar curve, concave dorsal posture"
  "squatting"                  → "deep knee flexion, lowered center of gravity"
  "kneeling"                   → "grounded leg posture, lowered vertical profile"
  "thrusting"                  → [REMOVE]
  "grinding"                   → [REMOVE]
  "touching herself"           → "hand-to-skin contact, self-referential tactile pose"
  "pulling clothing"           → "adjusting garment, smoothing fabric"
  "sexy pose"                  → "dynamic asymmetrical stance, editorial fashion posture"
  "heavy breathing"            → "expanded thoracic cavity, dynamic chest posture"
  "looking over shoulder"      → EXEMPT (standard pose)
  "hand on hip"                → EXEMPT
  "arms crossed"               → EXEMPT
  "seated cross-legged"        → EXEMPT
  "standing contrapposto"      → EXEMPT (art term)
  "hip shift"                  → EXEMPT (fashion pose)

TIER 2 (further reframe — softer position):
  "spreading legs"             → "balanced stance, feet shoulder-width"
  "bending over"               → "slight forward lean, hinged hip position"
  "on all fours"               → "kneeling, upright torso"
  "arching back"               → "upright posture, shoulders back"
  "squatting"                  → "compressed leg posture, athletic squat"
  "touching herself"           → "adjusting hair" / "hand resting on collarbone"
  "sexy pose"                  → "aesthetically calculated positioning"
```

---

## SETTING SUBSTITUTIONS

```
TIER 1 (reframe, same space):
  "bedroom"                    → "private studio space" / "home studio"
  "bed"                        → "daybed" / "studio surface" / "settee"
  "shower"                     → "wet studio environment"
  "bathtub"                    → "spa environment"
  "hotel room"                 → "contemporary interior space"
  "dressing room"              → "fitting room environment"
  "locker room"                → "athletic facility"

TIER 2 (shift space):
  "bedroom"                    → "minimalist interior"
  "bed"                        → "neutral backdrop"
  "shower/bath"                → "water feature environment"
  "hotel room"                 → "architectural interior"

ALWAYS EXEMPT (keep as-is):
  studio, gallery, museum, gym, beach, park, street,
  rooftop, balcony, garden, cafe, restaurant, office,
  library, kitchen, living room, patio, courtyard,
  dance studio, yoga studio, stadium, track, pool deck
```

---

## EXPRESSION SUBSTITUTIONS

```
TIER 1 (closest — preserve emotional energy):
  "seductive look"             → "intense classical gaze, magnetic focal contact"
  "bedroom eyes"               → "relaxed half-lidded gaze, contemplative expression"
  "come-hither"                → "inviting warm expression, magnetic eye contact"
  "sultry"                     → "composed low-energy expression, smoldering calm"
  "orgasmic"                   → [REMOVE]
  "moaning"                    → [REMOVE]
  "biting lip"                 → "dental-labial contact, lower lip tension"
  "licking lips"               → "relaxed jaw posture, slight oral opening"
  "parted lips"                → "relaxed jaw posture, naturally separated lips"
  "heavy breathing"            → "elevated respiratory posture, expanded chest"

TIER 2 (neutral reframe):
  "seductive look"             → "confident direct gaze"
  "bedroom eyes"               → "soft unfocused gaze"
  "biting lip"                 → "slight smile, natural expression"
  "parted lips"                → "natural relaxed mouth"

ALWAYS EXEMPT:
  smiling, laughing, serious, contemplative, pensive,
  joyful, playful, cheerful, candid, relaxed, calm,
  focused, determined, fierce, editorial stillness,
  neutral expression, soft gaze, warm expression,
  intense gaze, eye contact, looking away, downcast eyes
```

---

## PHOTOGRAPHY COMPOSITION LEXICON (NEW v3)

### Legitimizer Vocabulary (use 2+ per prompt)

```
EDITORIAL LEGITIMIZERS:
  "Editorial fashion photography"
  "Fine art portrait study"
  "Contemporary fashion editorial"
  "Professional portrait documentation"
  "High-fashion lookbook shoot"
  "Athletic performance photography"
  "Dance movement documentation"
  "Cultural fashion study"
  "Lifestyle brand photography"
  "Fitness campaign editorial"
  "Resort wear catalog shoot"
  "Streetwear editorial series"
  "Activewear brand campaign"
  "Contemporary portraiture"
  "Fashion week backstage documentation"
  "Athletic brand lookbook"
  "Wellness lifestyle photography"
  "Sportswear campaign photography"

HAUTE COUTURE / HIGH-FASHION LEGITIMIZERS:
  "Haute couture editorial spread"
  "Avant-garde fashion documentation"
  "Vogue-style editorial portrait"
  "Minimalist aesthetic fashion study"
  "Architectural tailoring showcase"
  "Designer lookbook photography"
  "High-end swimwear campaign"
  "Luxury resort editorial"
  "Fashion house campaign imagery"
  "Couture fitting documentation"
```

### Lighting Vocabulary (technical — always safe)

```
NATURAL LIGHT:
  golden hour warmth, blue hour ambient, overcast diffusion,
  dappled shade, reflected fill, window light spill,
  open shade, backlit rim, north-facing soft light,
  afternoon crosslight, dawn glow, twilight ambient

STUDIO LIGHT:
  butterfly/paramount lighting, Rembrandt triangle,
  split lighting, broad lighting, short lighting,
  clamshell setup, beauty dish, strip softbox,
  ring light fill, barn-door controlled spill,
  two-point key+fill, three-point standard setup,
  hair light / kicker, background separation light,
  gobo shadow pattern, scrim diffusion

MOOD LIGHT:
  high-key even, low-key dramatic, chiaroscuro contrast,
  film noir shadows, warm practical lighting,
  cool fluorescent cast, tungsten warmth,
  mixed color temperature, neon accent spill,
  volumetric haze, lens flare accent
```

### Lens & Camera Vocabulary (technical — always safe)

```
FOCAL LENGTH:
  14mm ultra-wide (environmental context)
  24mm wide-angle (environmental portrait)
  35mm standard wide (street / documentary)
  50mm normal (natural perspective)
  85mm short telephoto (classic portrait)
  105mm medium telephoto (tight portrait)
  135mm telephoto (compressed portrait)
  200mm long telephoto (sports / distant)

APERTURE:
  f/1.2 ultra-shallow depth of field
  f/1.4 shallow, creamy bokeh
  f/1.8 gentle separation
  f/2.8 moderate depth, sharp subject
  f/4.0 balanced depth
  f/5.6-8.0 deep focus, environmental

CAMERA FORMAT:
  35mm full-frame, APS-C crop sensor,
  medium format Hasselblad, large format 4×5,
  mirrorless handheld, DSLR tripod-mounted,
  iPhone [model] mobile photography, film camera analog,
  Polaroid instant, disposable camera aesthetic,
  drone aerial, GoPro wide-angle action
```

### Composition Terms (always safe)

```
  rule of thirds placement, center-weighted composition,
  golden ratio spiral, leading lines, frame within frame,
  negative space, symmetrical balance, dynamic diagonal,
  foreground-background layering, selective focus isolation,
  fill the frame, environmental portrait, full-body framing,
  three-quarter crop, head-and-shoulders crop, cowboy shot,
  worm's-eye view, bird's-eye view, eye-level straight-on,
  dutch angle / canted frame, over-the-shoulder framing
```

### Technical Quality Tags (always safe)

```
PHOTOREALISM:
  highly realistic, photorealistic rendering,
  subsurface scattering, physically-based skin rendering,
  8K ultra-resolution, tack-sharp detail,
  subtle film grain, natural color science,
  accurate white balance, correct exposure metering,
  rich shadow detail, highlight recovery,
  natural skin pores, micro-detail rendering,
  organic light falloff, accurate color reproduction,
  analog film emulation (Portra 400 / Kodak Gold / Tri-X),
  digital medium format clarity

RENDER ENGINE ENHANCERS (use sparingly — 1-2 max):
  Unreal Engine 5 render quality, Octane Render finish,
  path-traced global illumination, ray-traced reflections,
  V-Ray material accuracy, ultra-detailed texture,
  hyper-realistic skin shader, volumetric light pass,
  physically-based material rendering
```

### Negative Prompt Terms (always safe)

```
STANDARD NEGATIVES:
  Avoid: dry skin, dry hair, airbrushed skin, cartoon style,
  illustration style, bad anatomy, distorted face,
  extra limbs, deformed hands, plastic skin, wax skin,
  AI artefacts, blurry, overexposed, heavy makeup,
  unnatural proportions, mutation, disfigured,
  low quality, jpeg artifacts, watermark, text overlay,
  cropped awkwardly, bad framing, cluttered background,
  harsh unflattering shadows, color banding
```

---

## BODY ANGLES (flag check)

```
SAFE ANGLES (no flag):
  eye-level, slightly above, head-and-shoulders,
  three-quarter view, profile, full-body straight-on,
  bird's-eye (when environmental), over-the-shoulder

FLAGGED ANGLES (check context):
  low angle looking up     → flag if combined with skirt/dress
  between legs             → always flag
  floor level upward       → flag if body-focused
  extreme close-up body    → flag if non-face
  behind/below (body-focused) → flag

ANGLE EXEMPTIONS:
  low angle + full outfit + outdoor → EXEMPT (power pose, architecture)
  low angle + sports + action → EXEMPT (sports photography standard)
  floor level + dance + movement → EXEMPT (dance documentation)
```
