from utils.prompt_helpers import (
    classification_chat_messages,
    extraction_chat_messages,
    summary_chat_messages,
    human_input_chat_messages
)
from models import Classification, StructuredAcordao
from utils.llm_adapter import LLMAdapter


def summarize_acordao(llm: LLMAdapter, acordao: str) -> str:
    """
    Summarizes the acordao
    """
    messages = summary_chat_messages(acordao)
    response = llm.generate(messages)
    return response


def classify_acordao(llm: LLMAdapter, acordao: str) -> Classification:
    """
    Classifies the acordao using a structured output."""
    messages = classification_chat_messages(acordao)
    response = llm.generate_structured(messages, schema=Classification)
    return response


def extract_entities(llm: LLMAdapter, acordao: str) -> StructuredAcordao:
    """
    Extracts entities from the acordao using a structured output.
    """
    messages = extraction_chat_messages(acordao)
    response = llm.generate_structured(messages, schema=StructuredAcordao)
    return response


def qa_acordao(llm: LLMAdapter, acordao: str, question: str, chat_history: list) -> str:
    """
    Performs a question-and-answer task about the acordao with conversation history.
    """
    # Put the acordao as the first message in the chat history
    if len(chat_history) == 0:
        chat_history.extend(human_input_chat_messages(acordao))

    chat_history.append(("user", question))
    response = llm.generate(chat_history)
    chat_history.append(("assistant", response))

    return response
