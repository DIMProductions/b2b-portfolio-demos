# Acceptance Criteria (検収条件)

## PASS Conditions
1. **Schema Validation**: The runner MUST validate `test_spec.yaml` against a strict Pydantic schema before execution. Any undefined actions (e.g., `action: hack`) MUST be rejected immediately.
2. **Execution Match**: The number of executed test cases in the output MUST exactly match the number of test cases defined in the YAML file.
3. **Enterprise Reporting**: The test run MUST produce a standard `junit.xml` reflecting accurate PASS/FAIL states.
4. **Failure Traceability**: If a test fails, a screenshot OR trace file MUST be generated automatically in `output/screenshots/`.
5. **Idempotency**: Running the same YAML spec against the same target environment MUST yield identical action sequences.
6. **CI/CD Parity**: The CI configuration (`.github/workflows/playwright.yml`) MUST use the exact same fixed runner used locally.

## Out of Scope (除外事項)
* **Code Generation**: The runner DOES NOT generate arbitrary Python code from YAML (which creates security risks and unmaintainable code). It dynamically parses and executes a fixed set of safe actions.
* **Complex Logic in YAML**: Branching (`if/else`) or loops within the YAML test spec are not supported. Tests must be declarative and linear.
* **Target Environment Provisioning**: The provisioning of the staging/production database state is assumed to be handled outside this module.
