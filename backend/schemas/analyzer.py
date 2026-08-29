from pydantic import BaseModel
from typing import Optional


class AnalyzeRequest(BaseModel):
    file_listing: str
    tech_hints:   str = ""


class ToolSuggestion(BaseModel):
    category: str
    tools:    list[str]
    reason:   str


class AnalyzeResponse(BaseModel):
    stack_summary:   list[str]
    conventions:     list[str]
    tool_suggestions: list[ToolSuggestion]
