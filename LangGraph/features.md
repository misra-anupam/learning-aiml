# Phase 1

    - Core execution & control flow
    - Persistence
    - Multi-session handling

# Phase 2
    - Memory
    - Observability
    - HITL
    - Reliability & safety


# All features
## 1. Core execution & control flow
    - Interrupts (human-in-the-loop pause/resume)
    - Time travel (replay/fork from any checkpoint)
    - Streaming (token-level + node-level state updates)
    - Retryable errors for LLM calls / tool calls (with backoff policy)
    - Parallel/fan-out node execution (e.g. concurrent specialist lookups)

## 2. Memory
    - Short-term memory (thread-scoped conversation state, via checkpointer)
    - Long-term persona-based memory (cross-session, per-customer facts/preferences)
    - Memory write policy (what gets persisted vs discarded, and when)
    - Memory retrieval/injection strategy (how past memory gets pulled into a new session's context)

## 3. Persistence
    - Checkpointing (Postgres-backed, thread-level)
    - Store for long-term memory (separate from checkpointer — LangGraph's BaseStore or your own Qdrant/Postgres layer)
    - State schema versioning/migration (so old checkpoints don't break when you change SupportState)

## 4. Observability
    - Tracing (full execution trace: node inputs/outputs, tool calls, latencies)
    - Evaluation (offline: trajectory scoring, tool-call correctness, task completion rate)
    - Online evaluation / production monitoring (drift, failure-rate alerts, not just one-off eval runs)
    - Cost tracking (token usage + $ per ticket, per node)

## 5. Reliability & safety
    - Retryable errors for LLM/tool calls (already listed — this is the right instinct)
    - Fallback models (cheaper/faster model on repeated failure, escalate to stronger model on low confidence)
    - Rate limiting / backpressure (Celery/Redis queue depth-aware throttling)
    - Idempotency keys (prevent duplicate refunds/cancellations on retry)
    - Guardrails / output validation (structured output schema enforcement before acting on tool results)

## 6. Human-in-the-loop
    - HITL approval gates (already listed)
    - HITL edit-and-resume (human edits agent's proposed action before it executes, not just approve/reject)
    - Escalation queue management (priority, SLA timers — ties into your Celery stack)

## 7. Multi-tenancy & scale (platform-specific, since this is your "production platform" piece)
    - Per-customer thread isolation
    - Concurrent session handling (many tickets in flight)
    - Graph versioning (deploy a new graph definition without breaking in-flight checkpointed threads)

