# Ezer — TDD V3.1

## System Architecture

### Tier 1 — Product Library
- One JSON file per insurance product
- Contains: product rules, waiting period definitions, feature list, exclusions, moratorium rules
- Human-curated, verified against policy wording
- Shared across all users of that product
- Never contains user-specific data
- File pattern: `product_library_{insurer}_{product}.json`

### Tier 2 — User Schedule
- One JSON file per policy number
- Contains: SI blocks, waiting period status, declared PEDs, active addons, premium
- Links to Tier 1 via `product_id` field
- Human-curated from issued policy schedule
- File pattern: `user_schedule_{policy_number}_{name}.json`

### Insight Engine
- Reads Tier 1 + Tier 2 at runtime, joins them in memory
- Applies check functions — one per insight type
- Each check function returns zero or more insight objects
- No LLM calls, no database, no external dependencies
- Entry point: `engine/insight_engine.py`

---

## Insight Object Structure

```
{
  category:     string   # ACTIVE_FEATURE / GAP_FEATURE / WAITING_PERIOD / 
                         # PED_WAITING / PED_QUALITY_FLAG / SCHEDULE_INTEGRITY_ERROR /
                         # LEGAL_PROTECTION / ACTION_REQUIRED
  confidence:   string   # 🟢 VERIFIED / 🟡 EXTRACTED / 🔴 EXPERIMENTAL
  type:         string   # ACTION / WARNING / INFO
  priority:     string   # HIGH / MEDIUM / LOW
  title:        string   # Short label
  body:         string   # Plain-language explanation
  draft_letter: string   # Optional — present only on ACTION_REQUIRED insights
}
```

---

## Classification Rules

### Type
- `ACTION` — insight includes a draft letter or requires immediate user action
- `WARNING` — risk or gap, no immediate user action step
- `INFO` — awareness only, no risk

### Priority
- `HIGH` — misunderstanding can cause claim denial or financial loss today
- `MEDIUM` — important gap, fixable at renewal, no immediate downside
- `LOW` — informational only

### Fixed mappings
| Category | Type | Priority |
|----------|------|----------|
| ACTION_REQUIRED | ACTION | HIGH |
| SCHEDULE_INTEGRITY_ERROR | WARNING | HIGH |
| PED_QUALITY_FLAG | WARNING | HIGH |
| PED_WAITING | WARNING | HIGH |
| WAITING_PERIOD (running) | WARNING | HIGH |
| GAP_FEATURE | WARNING | MEDIUM |
| ACTIVE_FEATURE | INFO | LOW |
| LEGAL_PROTECTION | INFO | LOW |

---

## Summary Logic (Heuristic)

### Strength Calculation
```
IF count(type == ACTION) >= 1  → WEAK
ELIF count(type == WARNING, priority == HIGH) >= 1  → MODERATE
ELSE  → STRONG
```

### Next Best Action Derivation
```
IF any ACTION exists:
    pick first HIGH priority ACTION
    strip "Action Required — " prefix
    append "today"
ELSE IF any HIGH priority WARNING exists:
    pick first HIGH priority WARNING
    prefix with "Be aware: "
```

---

## Grouping Logic (Presentation Layer)

- `IMMEDIATE ACTIONS` — all insights where type == ACTION
- `RISKS & WARNINGS` — all insights where type == WARNING
- `COVERAGE & BENEFITS` — all insights where type == INFO
- Sort within each section: HIGH → MEDIUM → LOW
- Empty sections are hidden

---

## Deterministic vs Heuristic

### Deterministic (same input always produces same output)
- All insight generation logic
- All classification (type, priority)
- All draft letter content
- Grouping and ordering

### Heuristic (judgment-based, may be refined)
- Strength calculation (WEAK / MODERATE / STRONG)
- Next Best Action selection and wording
- WARNING insights may include a future `suggested_action` field for better Next Best Action derivation (planned)

---

## Known Gaps / Planned V3.1 Additions
- Policy evolution timeline (waiting period expiry milestones)
- Renewal guidance layer (what to add and when)
- Coverage maturity score
- `suggested_action` field on WARNING insights for better Next Best Action derivation
- FastAPI endpoint wrapping the engine
- Single-policy mode (run for one policy number, not all)

---
*Version: 3.1 Draft*
*Last updated: 2026-04-29*
