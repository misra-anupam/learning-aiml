# CrewAI

Works in situations where multi-agent collaboration based analysis/research/generation is required, 
i.e. problems which are a bit more open-ended and not exactly a software.
Situations where multi-agent systems shine:
    - Specialized agents required
    - Parallel workflows
    - Long running tasks
    - Review/generation loops


CrewAI does not have a concept of isolated thread_id like LangGraph.
Two users questions can overwrite the flow's state and cause havoc.

A flow is similar to an execution object, needed to be loaded in each separate query and the memory be supplied.


# llm

This is similar to AzureChatOpenAI. Just returns the LLM object

# Agent

This is like LLM + Chain; A combination of system prompt and other info. Similar to ReAct agent.
LLM + Prompt + Tools


# Task

This is new. Think of it like a chain in a graph.

# Crew

This is new. Think of it like a node, where multiple tasks(chains) are combined.
Each chain = Agent X Task

# Flow

This is like the entire Agent StateGraph with nodes.
It has @router which does conditional routing

# Process

Very different.
    - sequential
    - hierarchical -> Requires manager_agent which does task delegation, coordination, output review
This is not conditional flows.

# Guardrails

Very different. Checks/validates outputs in flows.
Instead of separate node to validate, this adds a validation and automatic retries.

# Memory

Very different.
Short-term, long-term and entity based.