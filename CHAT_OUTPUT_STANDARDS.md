# Chat Output Display Standards

**Last Updated:** 22 de noviembre de 2025

This document ensures consistent output formatting across all chat sessions and chat windows.

---

## Rule 1: Always Display Full Output in Chat

When user requests information (next workout, workout duration, etc.), display the **COMPLETE formatted output** directly in the chat window, not a summary.

### ❌ WRONG - Summary Only
```
✅ Next workout: Día 9 – Pierna (6 exercises, clean output displayed here in chat)
```

### ✅ CORRECT - Full Output
```
📅 Routine: Día 9 – Pierna
💪 Total Exercises: 6

Exercises:
  1. Squat (Barbell)
     Reps: 8 × 4 sets
  2. Hack Squat (Machine)
     Reps: 8 × 4 sets
  3. Lunge (Barbell)
     Reps: 24 × 4 sets
  4. Leg Extension (Machine)
     Reps: 15 × 4 sets
  5. Seated Leg Curl (Machine)
     Reps: 20 × 3 sets
  6. Lying Leg Curl (Machine)
     Reps: 12 × 3 sets
```

---

## Rule 2: When to Apply This Rule

Apply this standard to ALL output from scripts:
- `python scripts/next_workout.py`
- `python scripts/workout_duration.py <keyword>`
- Any other query scripts that produce formatted output

---

## Rule 3: Paste Terminal Output Directly

When a terminal command produces formatted output:
1. Run the command in terminal
2. **Copy the FULL output** from the terminal result
3. **Paste it directly into the chat message**
4. Do NOT summarize or truncate

---

## Context

This rule was established because:
- User was seeing summaries in chat but full output only in terminal
- Information gets lost when scrolling terminal or closing sessions
- Chat window is the persistent conversation record
- Full output should always be visible for reference

---

**CRITICAL:** Load and review this file at the start of EVERY new chat session involving workout queries or information requests.
