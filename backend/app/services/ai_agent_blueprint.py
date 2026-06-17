from textwrap import dedent


class AiAgentBlueprintService:
    def implementation_notes(self) -> list[str]:
        return [
            "Use LangGraph to model ingestion, retrieval, answer generation, citation validation, and memory persistence nodes.",
            "Store document chunks in PostgreSQL and embeddings in Pinecone, ChromaDB, or pgvector depending on scale and compliance needs.",
            "Keep conversation history in PostgreSQL with tenant, user, session, citations, and token usage fields.",
            "Require citations for answers that reference source documents; reject unsupported claims in regulated workflows.",
        ]

    def langgraph_code(self) -> str:
        return dedent(
            """
            from typing import TypedDict

            from langgraph.graph import END, StateGraph

            class AgentState(TypedDict):
                question: str
                retrieved_context: list[dict]
                answer: str
                citations: list[dict]

            async def retrieve(state: AgentState) -> AgentState:
                state["retrieved_context"] = await retriever.search(state["question"], top_k=6)
                return state

            async def answer(state: AgentState) -> AgentState:
                response = await llm.answer_with_citations(
                    question=state["question"],
                    context=state["retrieved_context"],
                )
                state["answer"] = response.answer
                state["citations"] = response.citations
                return state

            async def persist(state: AgentState) -> AgentState:
                await conversation_repository.save_turn(
                    question=state["question"],
                    answer=state["answer"],
                    citations=state["citations"],
                )
                return state

            graph = StateGraph(AgentState)
            graph.add_node("retrieve", retrieve)
            graph.add_node("answer", answer)
            graph.add_node("persist", persist)
            graph.set_entry_point("retrieve")
            graph.add_edge("retrieve", "answer")
            graph.add_edge("answer", "persist")
            graph.add_edge("persist", END)
            agent = graph.compile()
            """
        ).strip()

