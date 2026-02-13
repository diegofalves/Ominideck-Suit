# SQL Rules for OTM Support

## Objective

Produce safe, auditable, and domain-aware SQL for OTM support tasks.

## Mandatory rules

- Always qualify table names with schema when known (example: `GLOGOWNER.SHIPMENT`).
- Prefer explicit joins (`INNER JOIN`, `LEFT JOIN`) over implicit join syntax.
- Never use `SELECT *` in final answers.
- Include a domain filter when table supports domain scoping.
- Keep read-only behavior for support queries (`SELECT` only, unless user explicitly requests DML).
- Return query plus short validation checklist.

## Domain filter guidance

- Prefer `DOMAIN_NAME = '<DOMAIN>'` when the column exists.
- If domain is encoded in GID, use a safe expression and state assumption.
- If domain strategy is unknown, ask for confirmation before final query.

## Performance guardrails

- Limit result sets during exploration (`FETCH FIRST 200 ROWS ONLY` or equivalent).
- Filter by indexed identifiers first (`*_GID`, `*_XID`, reference qualifiers).
- Avoid function-wrapping indexed columns in predicates when possible.
- For heavy joins, start with CTEs and inspect row counts per step.

## Output contract for assistant

- `Goal`: one sentence
- `Assumptions`: bullet list
- `Query`: final SQL
- `Validation`: quick checks (expected row volume, key null checks, duplicates)
