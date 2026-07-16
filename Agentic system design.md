
# Single vs mulit-agent systems

- Single systems 
    Clear specialized tasks with multiple sequential steps

- Multi-agent systems
    - Multiple parallel tasks
    - Specialized work 
    - Long running loops

# Architecture components

## 1. Model layer
    - Task-aware model choice
    - Structured output constraint for API contracts
    - What happens when the model fails(or gives invalid output), what is the fallback?

## 2. Tool 
    - Clear name and description
    - I/O contracts
    - Permission boundaries
    - Timeout/error retry-behaviour

## 3. Memory & state
    - Episodic(state)
    - Long-term
    - Low-latency graph memory in app state DBs - postgres, dynamoDB, Redis
    - Knowledge retrival - Qdrant, milvus etc.
    - Long term memory - S3-like cheaper memory storage
    - Context window optimization

## 4. Orchestration
    Actual app system-design 
    - Chat window
    - Agent framework choice ( LangGraph/CrewAI/MAF )
    - Orchestration ( Temporal/RabbitMQ+Celery )
    - Logging & tracing
    - Evaluation

## 5. Evaluation
    Trace-level evaluation
    - Tool selection & arguments
    - Hallucination
    - Invalid format
    - Policy compliance
    - Regression testing after changing each component(prompt/LLM/tools/workflow)
    - Try to create ground truths

## 6. Approval and policy control
    - Sending email/refund issue/deleting data/financial transaction
    - Policy checks & RBAC controls & permission boundaries


# Production quality parameters

## 1. Reliability
    - Decomposition
    - Retries based on retryable & non-retryable errors - timeouts, malformed outputs, rate limits, provider errors, degraded quality
    - Fallbacks
    - Validation & monitoring
    - 
## 2. Cost and latency
    - Task-aware model selection/routing
    - Model output constraint
    - Caching - tool calls, results, policy lookups, table content
    - Stream always

## 3. Context and RAG
    - Each sources' freshness, latency, trust, privacy
    - Summarizations instead of whole history

## 4. Observability, security and privacy
    - Tracing all LLM I/O, arch metrics, tool calls, retries, eval, user feedback, cost
    - Only send data reqd. for operations
    - PII & sensitive data handling