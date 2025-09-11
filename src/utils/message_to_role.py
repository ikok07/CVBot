from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage

def message_to_role(msg: BaseMessage):
    match msg:
        case _ if isinstance(msg, HumanMessage):
            return "user"
        case _ if isinstance(msg, AIMessage):
            return "assistant"
        case _ if isinstance(msg, ToolMessage):
            return "tool"
        case _:
            return "undefined"