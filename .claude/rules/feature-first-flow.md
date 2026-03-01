---
alwaysApply: true
---

## Feature-first flow: spec before code

**CRITICAL**: For Cliplin to work correctly, **project specifications (feature files, ADRs, TDRs/TS4 and related documentation) are always the single source of truth**. On any user change or request you MUST first consult the specs, update them if needed, and only then touch code.

### 1. Always consult and update specs first

- **Before** modifying code or non-spec files, you MUST look at the existing specs:
  - `.feature` files in `docs/features/`
  - TDRs in `docs/tdrs/` (preferred) and legacy TS4 in `docs/ts4/`
  - ADRs and business docs in `docs/adrs/` and `docs/business/`
  - Any relevant specs from `.cliplin/knowledge/**`
- If the request implies new behavior, changed behavior, or clarifications, you MUST **first update (or create) the corresponding specs**. Propose the spec changes and get user agreement when needed; only after the specs are correct can you proceed to code.
- Even for apparent "pure refactors" that should not change behavior, you MUST confirm that the existing behavior is covered by current specs and that the refactor keeps the system aligned with them. Never introduce behavior that is not specified.

### 2. Then implement strictly to satisfy the specs

- **After** the relevant specs are correct (updated or confirmed), perform refactors or write new code **only to satisfy those specs**. Specs drive what is built; code does not drive the spec.
- If no spec existed for the scope, creating/updating the `.feature` file (and any needed ADR/TDR) is the first step; implementation strictly follows from those specs.

### Summary

- **Spec first, then code — always.** Never change code first or rely on undocumented behavior.
- **All behavior must be specified**: any new or changed behavior must be present in feature files and, when appropriate, ADRs/TDRs.
- Every change must be traceable to explicit specifications; specs are the primary source of truth for *what* and *how* the system should behave.

See also: `docs/business/framework.md` (section "Feature-first flow"), framework ADR (in `.cliplin/knowledge/cliplin-framework/docs/adrs/` or query `business-and-architecture` collection).
