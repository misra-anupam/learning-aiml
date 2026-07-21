# Technical metrics

Task success rate — issue actually resolved (LLM-judge or human-graded)
Tool-call correctness — right tool, right args, valid schema
Intent classification accuracy — precision/recall per category
Groundedness — RAGAS-style faithfulness for RAG-backed answers
Steps per ticket — efficiency; clarification-loop and retry rates
Latency & cost per ticket — end-to-end and per-node
Error/retry recovery rate — LLM/tool failures and how often retries succeed
Gate calibration — false escalation rate (sent to human unnecessarily) vs. false containment rate (resolved automatically when it shouldn't be — the costlier direction)

# Product metrics

Containment rate — % resolved without a human
Durable containment — contained AND not reopened AND CSAT above threshold (raw containment alone is a vanity metric)
CSAT / customer effort score
Escalation rate trend over time
Cost per resolved ticket vs. human baseline
SLA compliance — time to first response / resolution
Repeat contact rate — same customer, same issue, within a window