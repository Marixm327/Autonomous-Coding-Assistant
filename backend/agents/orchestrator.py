from functools import partial

from langgraph.graph import END, START, StateGraph

from backend.agents.coding.agent import coding_node
from backend.agents.planner.agent import planner_node
from backend.agents.research.agent import research_node
from backend.agents.reviewer.agent import reviewer_node
from backend.agents.state import GraphState
from backend.rag.pipeline import RAGPipeline


def _route_after_review(state: GraphState) -> str:
    if state.review_passed:
        return "end"
    idx = state.current_subtask_index
    if state.subtasks and idx < len(state.subtasks) - 1:
        return "next_subtask"
    return "end"


def _advance_subtask(state: GraphState) -> dict:
    return {"current_subtask_index": state.current_subtask_index + 1}


def build_graph(rag: RAGPipeline) -> StateGraph:
    graph = StateGraph(GraphState)

    graph.add_node("planner", planner_node)
    graph.add_node("research", partial(research_node, rag=rag))
    graph.add_node("coding", coding_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("advance_subtask", _advance_subtask)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "research")
    graph.add_edge("research", "coding")
    graph.add_edge("coding", "reviewer")

    graph.add_conditional_edges(
        "reviewer",
        _route_after_review,
        {"end": END, "next_subtask": "advance_subtask"},
    )
    graph.add_edge("advance_subtask", "research")

    return graph.compile()
