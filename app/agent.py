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
    def model(state: MessagesState):
        """LLM node (Studio calls this 'model')"""
        system_message = SystemMessage(
            content=f"""You are a helpful assistant that provides interesting facts to users. The facts can be in either of two categories -- 'happy' or 'sad'.
                If the user asks for a fact from the database, use the tool 'get_fact_from_db' to retrieve a fact from the specified category.
                If there are no facts in that category in the database, generate one yourself, save that to the database using the 'add_llm_fact', and then pass it to the user.
                If the user requests you to generate a fact yourself, use the tool 'add_llm_fact' to add the fact to the database before you pass it to the user.
                Do not make up facts on your own. Keep the facts short, within 1 or 2 sentences. Do not tell users facts that they have already been told.
                Make sure to use the tools provided to you to get or add facts.
                Always ensure that the facts you provide are relevant to the requested category.

                Do NOT call tools more than once per request.

                All the tools require a user_id parameter to identify the user making the request. The user_id is: {user_id}

                Here are some facts that have already been provided to the user:
                {known_facts}
                """
        )
        llm = _get_llm()
        output = llm.invoke([system_message] + state["messages"])
        return {"messages": [output]}

    def format_fact(state: MessagesState):
        """Terminal node that extracts the final fact."""
        messages = state["messages"]

        for msg in reversed(messages):
            if hasattr(msg, "name") and msg.name in [
                "get_fact_from_db",
                "add_llm_fact",
            ]:
                try:
                    data = json.loads(msg.content)
                    Fact(**data)  # validate
                    return {"messages": [AIMessage(content=msg.content)]}
                except Exception:
                    continue

        error = {
            "fact_id": -1,
            "fact_text": "Error: The AI assistant failed to retrieve a fact.",
        }
        return {"messages": [AIMessage(content=json.dumps(error))]}

    def route_model(state: MessagesState):
        """Required Studio routing — but with your STOP condition."""
        last = state["messages"][-1]
        if last.tool_calls:
            return "tools"
        return "format_fact"

    def route_tools(_):
        """After tool execution, ALWAYS go back to model once."""
        return "model"

    graph = StateGraph(MessagesState)

    graph.add_node("model", model)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_node("format_fact", format_fact)

    graph.add_edge(START, "model")
    graph.add_conditional_edges("model", route_model)
    graph.add_conditional_edges("tools", route_tools)
    graph.add_edge("format_fact", END)

    return graph.compile()
