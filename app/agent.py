import json
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, AIMessage

from conf.env import LLM, LLM_API_KEY, LLM_BASE_URL
from app.facts import get_fact_from_db, add_llm_fact
from app.schema import Fact


TOOLS = [get_fact_from_db, add_llm_fact]


def _get_llm() -> ChatOpenAI:
    llm = ChatOpenAI(
        api_key=LLM_API_KEY, base_url=LLM_BASE_URL, model=LLM, temperature=0.7
    )
    return llm.bind_tools(TOOLS)


def create_agent_state_graph(known_facts: str, user_id: int):
    def generate_fact(state: MessagesState):
        system_message = SystemMessage(
            content=(
                f"""You are a helpful assistant that provides interesting facts to users. The facts can be in either of two categories -- 'happy' or 'sad'.
                If the user asks for a fact from the database, use the tool 'get_fact_from_db' to retrieve a fact from the specified category.
                If there are no facts in that category in the database, generate one yourself, save that to the database using the 'add_llm_fact', and then pass it to the user.
                If the user requests you to generate a fact yourself, use the tool 'add_llm_fact' to add the fact to the database before you pass it to the user.
                Do not make up facts on your own. Keep the facts short, within 1 or 2 sentences. Do not tell users facts that they have already been told.
                Make sure to use the tools provided to you to get or add facts.
                Always ensure that the facts you provide are relevant to the requested category.

                All the tools require a user_id parameter to identify the user making the request. The user_id is: {user_id}

                Here are some facts that have already been provided to the user:
                {known_facts}
                """
            )
        )
        llm = _get_llm()
        return {"messages": [llm.invoke([system_message] + state["messages"])]}

    def format_fact(state: MessagesState):
        """Final node that extracts fact data from tool messages and returns the JSON."""

        messages = state["messages"]

        # Look for ToolMessage in the conversation that contains the fact data
        for msg in reversed(messages):
            # Check if it's a ToolMessage with the right name
            if hasattr(msg, "name") and msg.name in [
                "get_fact_from_db",
                "add_llm_fact",
            ]:
                try:
                    # Validate that it's proper JSON and contains fact data
                    fact_data = json.loads(msg.content)
                    # Validate it can be parsed as a Fact
                    Fact(**fact_data)
                    # Return the JSON string as AIMessage content
                    return {"messages": [AIMessage(content=msg.content)]}
                except (json.JSONDecodeError, Exception):
                    # If parsing fails, continue looking
                    continue

        # Fallback: if no tool message found, return error as JSON
        # This happens when the LLM fails to make a proper tool call
        error_fact = {
            "fact_id": -1,
            "fact_text": "Error: The AI assistant failed to retrieve a fact. Please try again.",
        }
        return {"messages": [AIMessage(content=json.dumps(error_fact))]}

    def should_continue(state: MessagesState):
        """Route to tools if there are tool calls, otherwise to format_fact."""
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "format_fact"

    graph = StateGraph(MessagesState)
    graph.add_node("generate_fact", generate_fact)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_node("format_fact", format_fact)

    graph.add_edge(START, "generate_fact")
    graph.add_conditional_edges(
        "generate_fact", should_continue, ["tools", "format_fact"]
    )
    graph.add_edge("tools", "generate_fact")
    graph.add_edge("format_fact", END)

    return graph.compile()
