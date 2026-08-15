from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class Step(BaseModel):
    action: Literal["goto", "fill", "click", "expect_text", "expect_url", "api_get", "expect_status"]
    path: Optional[str] = None
    target: Optional[str] = None
    value: Optional[str] = None

class TestCase(BaseModel):
    id: str
    name: str
    steps: List[Step]

class TestSuite(BaseModel):
    suite: str
    tests: List[TestCase]
