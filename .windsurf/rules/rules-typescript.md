---
trigger: glob
---

# TS / TSX
- "strict": true. No `any` without a comment.
- One export per file, named exports only.
- camelCase funcs/vars, PascalCase types/components, kebab-case dirs.
- Validate external data with Zod.
- Prefer RO-RO (Receive Object, Return Object) for multi-arg funcs.
- React/Next: server components by default; mark clients with 'use client'.
- Tailwind only (no inline styles). Framer Motion for subtle anims.
- TanStack Query for async data; React Hook Form (+ Zod) for forms.
