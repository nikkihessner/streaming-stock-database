We are co-creating a design document.

Context:
- Project: <PROJECT NAME>
- Module / Area: <MODULE OR PHASE>
- Audience: <me only | collaborators | future contributors>
- This doc may encode proprietary logic — do NOT invent domain rules.

Authority rules:
- I am the source of truth for domain semantics.
- If something is underspecified, STOP and ask.
- Do not infer thresholds, constants, or heuristics unless I explicitly provide them.

What I want from you:
- Help structure the document.
- Help surface hidden assumptions.
- Help translate my intent into precise, testable language.
- Suggest invariants, but do not finalize them without confirmation.

Current state:
- What I know for sure:
  - <bullet list>
- What is undecided / fuzzy:
  - <bullet list>
- What must NOT be decided yet:
  - <bullet list>

Deliverable:
- Produce a draft design doc section with:
  - Clear purpose
  - Explicit definitions
  - Invariants (clearly marked as PROPOSED vs CONFIRMED)
  - Failure semantics
  - Open questions section

Constraints:
- No code unless I ask for it.
- No examples that encode strategy unless I approve.
- Keep math symbolic if constants are unknown.
- Prefer clarity over completeness.

Stop condition:
- If you feel tempted to “fill in the blank,” ask instead.