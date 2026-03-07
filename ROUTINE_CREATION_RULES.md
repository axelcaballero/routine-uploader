# Routine Creation Rules

**Last Updated:** 22 de noviembre de 2025

These rules are CRITICAL for routine creation and must be applied to every routine. Reference this file at the start of every chat session.

---

## Rule 1: Rep Ranges Always Use Maximum Value

When an exercise specifies a rep range (e.g., "4x6-8rep"), ALL normal sets must use the **highest number** in the range.

### ✅ CORRECT
- Spec: `4x6-8rep`
- Output: warmup 12 reps, then **4 sets of 8 reps** (NOT 6, 7, 8, 8)
- Spec: `3x12-15rep`
- Output: warmup 12 reps, then **3 sets of 15 reps** (NOT 12, 13, 14, 15)

### ❌ WRONG
- Spec: `4x6-8rep`
- Output: warmup 12, normal sets 6, 7, 8, 8 ❌ (incrementing is wrong)

**Reference:** manifesto.md line 60: "Utiliza siempre el numero más alto, quedaria en 3 series de 15 repeticiones"

---

## Rule 2: "Duplicar Repeticiones" Doubles Reps Per Set

When an exercise in instructions.md has the note "Duplicar repeticiones", it means the exercise is performed individually per limb (arm or leg). **Multiply both warmup AND normal set reps by 2**.

### ✅ CORRECT
- Spec: `4x12rep` with "Duplicar repeticiones"
- Output: warmup **24 reps** (12 × 2), then 4 sets of **24 reps** (12 × 2)
- Spec: `4x6-8rep` with "Duplicar repeticiones"
- Output: warmup **24 reps** (12 × 2), then 4 sets of **16 reps** (8 × 2 from max value)

### ❌ WRONG
- Adding extra sets instead of doubling reps ❌
- Only doubling normal sets but not warmup ❌
- Incrementing reps ❌

---

## Rule 3: Exercises Requiring "Duplicar Repeticiones"

These exercises MUST have reps doubled for BOTH warmup and normal sets:

**Biceps:**
- 37FCC2BB - Curl Alternado con mancuerna
- FAB6EB2F - Predicador banca Scott con mancuerna individual

**Triceps:**
- None with this flag

**Shoulder:**
- 8293E554 - Elevación frontal con mancuerna (if marked "individual")

**Back:**
- F1E57334 - Jalón mancuerna
- D0C4A899 - Jalón en polea alta

**Legs:**
- 0d2c58fa-8cf3-4e4d-ac1c-c6db5262d972 - Desplantes búlgaros
- B537D09F - Desplantes recorridos con mancuerna
- 6E6EE645 - Desplantes fijos con barra

**Biceps (Individual):**
- 724CDE60 - Concentrado con mancuerna

---

## Rule 4: Warmup Sets

- Non-Core default warmup: **12 reps**
- Non-Core routines include warmup before normal working sets
- Core routines do **not** include warmup sets
- Weight should be lighter than working weight (~40-50%)
- If non-Core exercise has "Duplicar repeticiones": warmup = **24 reps** (12 × 2)

---

## Rule 5: Set Types (Hevy API Official)

Only these 4 set types exist in Hevy API:

1. **warmup** - Preparation sets (always 12 reps standard, 24 if duplicated)
2. **normal** - Working sets
3. **dropset** - Progressive drop in weight
4. **failure** - Push to muscular failure

Do NOT use any other set types.

---

## Rule 6: Rest Seconds Policy

- Non-Core routines: default `rest_seconds` is **60**
- Core routines: use `rest_seconds` **20** for all exercises
- Core routines: use **2 normal series** per exercise (no warmup)
- If exercise description includes **"cluster"** in non-Core routines: use **30** seconds
- If routine title mixes muscle group + Core (e.g., "Espalda + Core"), do **not** apply Core-routine global overrides

---

## Rule 7: Other Exercise Notes

- **"Si dice individual, duplicar repeticiones"** (8293E554): Only apply if spec says "individual"
- **"Agregar 'con triangulo' en notas"** (93A552C6): Add descriptive note to exercise notes field
- **"Agregar 'tras nuca' en notas"** (6A6C31A5): Add descriptive note to exercise notes field
- **"Agregar 'recorrido' en notas"** (B537D09F): Add descriptive note to exercise notes field
- **"Agregar 'fijos' en notas"** (6E6EE645): Add descriptive note to exercise notes field

---

## Application Checklist

Before uploading any routine, verify:

- [ ] All rep ranges use the MAXIMUM value for normal sets
- [ ] Non-Core "Duplicar repeticiones" exercises have doubled warmup reps (24)
- [ ] All "Duplicar repeticiones" exercises have doubled normal set reps
- [ ] Only warmup/normal/dropset/failure set types used
- [ ] Core routines have no warmup sets, use 2 normal series, and `rest_seconds` = 20
- [ ] Non-Core routines keep `rest_seconds` = 60 unless cluster (30)
- [ ] Exercise IDs validated against instructions.md
- [ ] Notes field includes any required descriptive text

---

## Examples

### Example 1: Exercise with Rep Range
**Spec:** Curl de bíceps con barra olímpica - 4x15-20rep 80%

```json
{
  "exercise_template_id": "A5AC6449",
  "sets": [
    {"type": "warmup", "reps": 12},
    {"type": "normal", "reps": 20},
    {"type": "normal", "reps": 20},
    {"type": "normal", "reps": 20},
    {"type": "normal", "reps": 20}
  ]
}
```

### Example 2: Exercise with Duplicar Repeticiones
**Spec:** Concentrado con mancuerna - 4x12rep 80% (with "Duplicar repeticiones")

```json
{
  "exercise_template_id": "724CDE60",
  "sets": [
    {"type": "warmup", "reps": 24},
    {"type": "normal", "reps": 24},
    {"type": "normal", "reps": 24},
    {"type": "normal", "reps": 24},
    {"type": "normal", "reps": 24}
  ]
}
```

### Example 3: Exercise with Rep Range AND Duplicar Repeticiones
**Spec:** Curl Alternado con mancuerna - 4x6-8rep 85%+ (with "Duplicar repeticiones")

```json
{
  "exercise_template_id": "37FCC2BB",
  "sets": [
    {"type": "warmup", "reps": 24},
    {"type": "normal", "reps": 16},
    {"type": "normal", "reps": 16},
    {"type": "normal", "reps": 16},
    {"type": "normal", "reps": 16}
  ]
}
```

---

**IMPORTANT:** Load and review this file at the start of EVERY chat session involving routine creation.
