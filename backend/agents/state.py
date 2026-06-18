from typing import Annotated, Any
from uuid import UUID

from langgraph.graph.message import add_messages
from pydantic import BaseModel


class GraphState(BaseModel):
    """Shared state object passed through the LangGraph node pipeline."""

    repository_id: UUID
    task_type: str  # chat | bug_report | patch | pr | test
    user_query: str

    # Message history managed by LangGraph reducer
    messages: Annotated[list[Any], add_messages] = []

    # Planner output
    subtasks: list[str] = []
    current_subtask_index: int = 0

    # Research output
    retrieved_context: list[dict] = []

    # Coding output
    generated_code: str | None = None
    patch: str | None = None

    # Reviewer output
    review_passed: bool = False
    review_notes: str | None = None

    # Tool results
    test_results: dict | None = None
    pr_url: str | None = None

    # Final answer
    final_answer: str | None = None
    error: str | None = None
