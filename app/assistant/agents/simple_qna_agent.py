from typing import List, Tuple
from langchain.schema.runnable import RunnableMap, RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_openai import ChatOpenAI
from assistant.prompts.simple_qna_prompts import CONDENSE_QUESTION_PROMPT, FINAL_ANSWER_PROMPT
from operator import itemgetter

__all__ = ['_format_chat_history', 'create_chain', 'invoke_chain']

def _format_chat_history(chat_history: List[Tuple[str, str]]) -> str:
    """Format chat history into a string."""
    buffer = ""
    for role, message in chat_history:
        if role == 'user':
            buffer += f"\nHuman: {message}"
        elif role == 'assistant':
            buffer += f"\nAssistant: {message}"
    return buffer.strip()


_inputs = RunnableMap(
    standalone_question=RunnablePassthrough.assign(
        chat_history=lambda x: _format_chat_history(x["chat_history"])
    )
    | CONDENSE_QUESTION_PROMPT
    | ChatOpenAI(temperature=0, model='gpt-4o-mini')
    | StrOutputParser(),
)


_context = {
    "context": itemgetter("standalone_question"),
    "question": lambda x: x["standalone_question"],
}

def create_chain(config):
    return (
        _inputs
        | _context
        | FINAL_ANSWER_PROMPT
        | ChatOpenAI(temperature=config['temperature'], model=config['model'])
        | StrOutputParser()
    )

def invoke_chain(message: str, chat_history: List[Tuple[str, str]], config: dict):
    chain = create_chain(config)
    
    input_data = {
        "question": message,
        "chat_history": chat_history
    }
    
    return chain.invoke(input_data)