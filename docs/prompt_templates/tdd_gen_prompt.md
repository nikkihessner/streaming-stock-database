Generate pytest tests for the function <FUNCTION_NAME>.

Use the design contract exactly as written in <DESIGN_DOC_NAME>.

Contract scope:
- Purpose: <1-line purpose or “use doc verbatim”>
- Mathematical definition: <formula or “use doc verbatim”>
- Invariants:
  - <list or “use doc verbatim”>
- Failure semantics:
  - <list or “use doc verbatim”>

Repo specifics:
- Import path: <FULL PYTHON IMPORT PATH>
- Function signature: <EXACT SIGNATURE>
- Test location: <PATH TO TEST FILE>

Constraints:
- Write exactly <N> tests per invariant.
- Tests must encode invariants, not implementation details.
- Use library-provided testing helpers where appropriate
  (e.g., pandas.testing.assert_*).
- Do not add new behavior, features, or assumptions.
- Do not rename functions, arguments, or outputs.
- Do not introduce fixtures unless explicitly requested.

Edge policy:
- Input types allowed: <e.g., pd.Series only>
- Index alignment policy: <raise | align | ignore>
- NaN / inf policy: <propagate | error | mask>
- Output naming requirements: <exact name or “none”>

Return:
- Only the test code.
- No explanations.