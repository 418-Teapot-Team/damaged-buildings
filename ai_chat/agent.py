from langgraph.graph import StateGraph, END, add_messages
from langgraph.types import interrupt
from langgraph.types import Command
import uuid
from langgraph.constants import START
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langgraph.graph import MessagesState, START
import os
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt
from tools import search_knowledge
from pydantic import BaseModel
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
from typing import Sequence
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langchain_core.messages.tool import ToolMessage
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

class AskHuman(BaseModel):
    """Ask the human a question"""
    question: str

class SearchAgent:
    def __init__(self, config, model_name: str = "llama-3.1-8b-instant", tools: list = [{
        "type": "web_search_preview",
        "search_context_size": "low",
    }, AskHuman]):
        # self.model = ChatGroq(
        #     model=model_name,
        #     api_key=os.getenv("GROQ_API_KEY"),
        #     temperature=0.1,
        # )
        self.model = ChatOpenAI(
            model="gpt-4o",
            temperature=0.2,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.tools = tools
        self.model = self.model.bind_tools(self.tools)
        self.graph = self._build_graph()
        self.config = config

    def _should_continue(self, state):
        messages = state["messages"]
        last_message = messages[-1]
        if not last_message.tool_calls:  # If there is no function call, then we finish
            return END
        elif last_message.tool_calls[0]["name"] == "AskHuman":
            return "ask_human"
        else:
            return "action"

    def _call_model(self, state):
        messages = state["messages"]
        response = self.model.invoke(messages)
        return {"messages": [response]}

    def _ask_human(self, state):
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]
        ask = AskHuman.model_validate(state["messages"][-1].tool_calls[0]["args"])
        location = interrupt(ask.question)
        
        # Respond to the AskHuman tool with the answer (you may want to send more details)
        tool_message = [{"tool_call_id": tool_call_id, "type": "tool", "content": location}]
        
        # Now, wait for user to provide input or action
        return {"messages": tool_message}

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", self._call_model)
        workflow.add_node("action", ToolNode(self.tools))
        workflow.add_node("ask_human", self._ask_human)

        workflow.add_edge(START, "agent")

        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            path_map=["ask_human", "action", END],
        )

        workflow.add_edge("action", "agent")

        workflow.add_edge("ask_human", "agent")

        memory = MemorySaver()

        return workflow.compile(checkpointer=memory)

    def get_chat_history(self):
        if "messages" not in self.graph.get_state(self.config).values:
            return [""]
        history = self.graph.get_state(self.config).values["messages"]
        print(history)
        for message in history[::-1]:
            print(message.content)
            print(type(message))
            print(len(message.content) == 0)
            if type(message) is ToolMessage:
                return message.content
            if type(message) is HumanMessage:
                return message.content
            if type(message) is AIMessage and len(message.content) == 0:
                return message.additional_kwargs["tool_calls"]
            else:
                return message.content


if __name__ == "__main__":
    config = {"configurable": {"thread_id": uuid.uuid4()}}
    agent = SearchAgent(config=config)

    # Example of running the workflow with an initial message
    for event in agent.graph.stream(
        {
            "messages": [
                (
                    "user",
                    "Ask the user where they are, then look up the weather there",
                )
            ]
        },
        config,
        stream_mode="values",
    ):
        if "messages" in event:
            event["messages"][-1].pretty_print()

    # Example of providing a response to a tool call (e.g., Command)
    for event in agent.graph.stream(
        Command(resume="san francisco"),  
        config,
        stream_mode="values",
    ):
        if "messages" in event:
            event["messages"][-1].pretty_print()

    print(agent.get_chat_history())
