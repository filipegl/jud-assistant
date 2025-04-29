from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from ollama import chat
from langchain.prompts import ChatPromptTemplate


class LLMAdapter:
    """
    Adapter for LLMs (Ollama and OpenAI) to provide a unified interface for generating text and structured outputs.
    """
    def __init__(self, provider="ollama", model_name="llama3.2:3b", temperature=0.3, api_key=None):
        if provider == "ollama":
            def llm_ollama(messages: list[dict], format: dict | None = None):
                return chat(
                    messages=messages,
                    model=model_name,
                    format=format,
                    options={
                        "temperature": temperature,
                        "num_ctx": 8192,
                    }
                )
            self.client = llm_ollama
            self.is_ollama = True
        elif provider == "openai":
            if api_key is None:
                raise ValueError("API key required for OpenAI")
            self.client = ChatOpenAI(
                model_name=model_name,
                openai_api_key=api_key,
                temperature=temperature,
            )
            self.is_ollama = False
        else:
            raise ValueError(f"Provider {provider} not supported.")

    def generate(self, messages) -> str:
        """
        Generates a response from the LLM based on the provided messages.
        Args:
            messages (list): List of tuples containing role and message.
        Returns:
            str: The generated response from the LLM.
        """
        if self.is_ollama:
            ollama_messages = [{"role": role, "content": message} for role, message in messages]
            return self.client(messages=ollama_messages).message.content
        else:
            prompt = ChatPromptTemplate.from_messages(messages)
            chain = prompt | self.client
            response = chain.invoke({})
            return response.content

    def generate_structured(self, messages, schema: BaseModel):
        """
        Generates a structured response from the LLM based on the provided messages and schema.
        Args:
            messages (list): List of tuples containing role and message.
            schema (BaseModel): Pydantic model for structured output.
        Returns:
            BaseModel: The structured response from the LLM.
        """
        if self.is_ollama:
            ollama_messages = [{"role": role, "content": message} for role, message in messages]
            response = self.client(messages=ollama_messages, format=schema.model_json_schema()).message.content
            structured_response = schema.model_validate_json(response)
            return structured_response
        else:
            structured_llm = self.client.with_structured_output(schema=schema)
            prompt_template = ChatPromptTemplate.from_messages(messages)
            prompt = prompt_template.invoke({})
            response = structured_llm.invoke(prompt)
            return response
