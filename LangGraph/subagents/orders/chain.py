from pathlib import Path
import yaml

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from llm import model
from state import OrderAction, OrderItemIssue, ReturnOption, OrderSelection, ItemSelection

_PROMPTS = yaml.safe_load((Path(__file__).parent / "prompts.yaml").read_text())


def _chain(prompt_key: str, schema, orders=None, items=None):
    cfg = _PROMPTS[prompt_key]
    parser = PydanticOutputParser(pydantic_object=schema)
    format_instructions = parser.get_format_instructions()
    prompt = ChatPromptTemplate.from_messages([
        ("system", cfg["system"]),
        ("human", cfg["human"]),
    ]).partial(format_instructions=format_instructions)
    if orders is not None:
        prompt = prompt.partial(orders=orders)
    if items is not None:
        prompt = prompt.partial(items=items)
    return prompt | model.with_structured_output(schema)