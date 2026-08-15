# Examples

## Normal case: 5 declarative tests, 5 green

`input/test_spec.yaml` covers four distinct flows purely through YAML — no test code is hand-written per scenario:

| ID | Flow |
|---|---|
| `LOGIN-001` | Login with valid credentials → redirected to `/dashboard` |
| `LOGIN-002` | Login with invalid credentials → inline error message |
| `SEARCH-001` | Product search form → filtered results text |
| `FORM-001` | Contact form submission → confirmation message |
| `API-001` | Direct API call (`GET /api/health`) → status code assertion |

Running `pytest tests/test_runner.py` turns each YAML entry into its own parametrized, independently reported test case.

## Failure case: what a FAIL looks like

`failing_spec_example.yaml` in this folder has one step with a wrong expected value on purpose. Pointing the runner at it (see the comment inside the file) produces:

- `output/junit.xml` — the case reported as `<failure>`, not silently skipped
- `output/screenshots/.../test-failed-1.png` — full-page screenshot at the moment of failure
- `output/screenshots/.../trace.zip` — a Playwright trace (open with `playwright show-trace trace.zip`) showing every action, network call, and DOM state leading up to the failure

This was verified directly: running the runner against a deliberately broken assertion produced exactly those two artifact files, confirming `docs/acceptance_criteria.md` criterion 4 (Failure Traceability) actually holds, not just in theory.
