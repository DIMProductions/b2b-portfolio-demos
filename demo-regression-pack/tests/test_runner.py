import os
import yaml
import pytest
import json
from playwright.sync_api import Page, expect
from src.schema import TestSuite

def load_tests():
    spec_path = os.path.join("input", "test_spec.yaml")
    with open(spec_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    suite = TestSuite(**data) # Pydantic Validation happens here
    return suite.tests

TESTS = load_tests()

@pytest.mark.parametrize("test_case", TESTS, ids=[t.id for t in TESTS])
def test_dynamic_spec(page: Page, test_case):
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
    last_api_response = None

    for step in test_case.steps:
        if step.action == "goto":
            page.goto(f"{base_url}{step.path}")
        elif step.action == "fill":
            page.fill(f"id={step.target}", step.value)
        elif step.action == "click":
            page.click(f"id={step.target}")
        elif step.action == "expect_url":
            expect(page).to_have_url(f"{base_url}{step.value}")
        elif step.action == "expect_text":
            expect(page.locator(f"id={step.target}")).to_have_text(step.value)
        elif step.action == "api_get":
            last_api_response = page.request.get(f"{base_url}{step.path}")
        elif step.action == "expect_status":
            assert last_api_response is not None, "expect_status requires a prior api_get step"
            assert str(last_api_response.status) == step.value
