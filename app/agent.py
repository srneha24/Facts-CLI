from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage

from conf.env import LLM
from app.facts import get_fact_from_db, add_llm_fact, add_user_fact


TOOLS = [get_fact_from_db, add_llm_fact, add_user_fact]


def _get_llm() -> ChatOllama:
    llm = ChatOllama(model=LLM, temperature=0.7)
    llm.bind_tools(TOOLS)
    return llm


def create_agent_state_graph(known_facts: str, user_id: int) -> StateGraph:
    def generate_fact(state: MessagesState):
        system_message = SystemMessage(
            content=(
                f"""You are a helpful assistant that provides interesting facts to users. The facts can be in either of two categories -- 'happy' or 'sad'.
                If the user asks for a fact from the database, use the tool 'get_fact_from_db' to retrieve a fact from the specified category.
                If the user requests you to geenrate a fact yourself, use the tool 'add_llm_fact' to add the fact to the database before you pass it to the user.
                Always add the fact to the database before providing it to the user using the 'add_user_fact' tool.
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

    graph = StateGraph()
    graph.add_node("generate_fact", generate_fact)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_edge(START, "generate_fact")
    graph.add_edge("generate_fact", "tools")
    graph.add_edge("tools", "generate_fact")
    graph.add_edge("generate_fact", END)
    return graph
