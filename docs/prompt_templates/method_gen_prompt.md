Implement the function <FUNCTION_NAME>.

Use the design contract exactly as written in <DESIGN_DOC_NAME>.
Do not reinterpret, simplify, or extend the specification.

Contract scope:
- Purpose: use doc verbatim
- Mathematical definition: use doc verbatim
- Invariants: use doc verbatim
- Failure semantics: use doc verbatim

Context:
- This function is part of <MODULE_NAME>.
- It will be composed with other functions; do not add orchestration logic.
- It must be safe for vectorized pandas usage.

Repo specifics:
- Import path: <FULL IMPORT PATH>
- Function signature: <EXACT SIGNATURE>
- Output name requirement: <e.g. 'delta_velocity'>
- Pandas version assumptions: standard pandas (no experimental APIs)

Constraints:
- Implement only this function.
- Do not modify other functions or files.
- Do not add logging, metrics, or configuration.
- Do not add new parameters.
- Do not change types.
- Do not introduce side effects or mutation of inputs.

Testing:
- The implementation must satisfy the existing pytest tests.
- If a test fails due to ambiguity in the doc, stop and ask for clarification instead of guessing.

Return:
- Only the function implementation code.
- No explanations.