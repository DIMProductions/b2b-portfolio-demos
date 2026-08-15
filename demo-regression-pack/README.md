# Regression Pack Demo (YAML-driven Fixed Runner)

This repository demonstrates a highly maintainable automated E2E test suite. 
Instead of writing fragile UI test code, human QA testers write strict YAML test specifications. 
Our fixed Python Runner consumes this YAML and reliably executes Playwright actions using a Page Object Model (POM), producing rich enterprise-grade reports.

## 5-Minute Overview: Data Flow

```text
YAML Test Spec (Excel/Spreadsheet Equivalent)
        ↓
    Validation (Pydantic Schema)
        ↓
   Fixed Runner (Playwright + Pytest)
        ↓
  ┌─────────────┐
  │             │
 PASS        FAIL (with Screenshot)
  │             │
  └──────┬──────┘
         ↓
  Enterprise Output
  - junit.xml
  - report.html (self-contained)
  - failure screenshots / traces
  - CI/CD pipeline integration
```

## Self-Contained Demo
This repository includes a tiny bundled Web App (`src/dummy_app.py`) so tests run locally without relying on external internet connectivity or volatile third-party websites.

## How to Run

1. Start the target app and run tests:
```bash
docker-compose up --build
```
2. Check `output/` for `junit.xml`, `report.html`, and failure screenshots.

## Acceptance Criteria
See [docs/acceptance_criteria.md](docs/acceptance_criteria.md) for the mechanical definition of done.
