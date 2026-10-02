---
applyTo: "src/models/**,src/validators/**"
description: "Core engine coding standards for data models, CSV validators, and graph parsers."
---

# Core Engine Instructions

## Scope
Apply these instructions when working on data models and validators under `src/models/` and `src/validators/`.

## Stack and Conventions
- Use Python 3.10+, Pydantic v2, and pandas.
- Always validate incoming CSV inputs against schemas before building graph structures.
- Return structured, row-specific error messages with 1-indexed row numbers.
- Maintain referential integrity (no orphaned relations).
- Maintain >90% test coverage for core engine modules.
