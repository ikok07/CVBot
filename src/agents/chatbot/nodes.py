import os

from langchain_core.messages import SystemMessage, BaseMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from opik import track

from src.agents.chatbot.state import State
from src.agents.chatbot.tools import tools
from src.models.agent.suggestion_llm_output import SuggestionLLMOutput
from src.prompts.chatbot_prompt import CHATBOT_SYSTEM_PROMPT
from src.prompts.suggestions_llm_prompt import SUGGESTIONS_LLM_PROMPT

llm = ChatOpenAI(
    model=os.getenv("CHATBOT_MODEL"),
    stream_usage=True
)

llm_with_tools = llm.bind_tools(tools)

suggestions_llm = ChatOpenAI(
    model=os.getenv("QUESTION_SUGGESTIONS_MODEL"),
    stream_usage=True
).with_structured_output(SuggestionLLMOutput)

async def chat_node(old_state: State):
    return Command(
        update={
            "messages": await llm_with_tools.ainvoke(
                [
                    SystemMessage(content=CHATBOT_SYSTEM_PROMPT),
                ] + old_state["messages"]
            )
        }
    )

async def suggestions_generation_node(old_state: State):
    response: SuggestionLLMOutput = await suggestions_llm.ainvoke(
        [
            SystemMessage(content=SUGGESTIONS_LLM_PROMPT)
        ] + old_state["messages"]
    )

    return Command(
        update={
            "question_suggestions": response.suggestions
        }
    )