# Refactor Log

## 2026-11-19 — Fix: Pydantic validation failure on agent output

**Symptom:** `OperationsAnswer` validation failed with `Field required` errors on
`key_metrics`, `operational_insights`, `proposed_actions`, `draft_messages`, plus a
`float_parsing` error on `key_metrics[].value`. The LLM emitted invented keys
(`metric`, `insight`, `message_draft`, `draft_follow_up_message`).

**Root cause:**
1. `output_type=OperationsAnswer` (plain) → pydantic-ai ToolOutput mode: the model
   emits free-form tool-call arguments with no schema constraint at generation time.
2. Instructions referenced a nonexistent tool `draft_follow_up_message` and used
   `message_draft` ambiguously; the model echoed them as JSON keys. Sub-field names
   were never specified in the prompt.

**Fix (`agent.py`):**
- Instructions: removed the fake tool reference, stated `message_draft` is an
  `action_type` value, listed exact sub-field keys per list, and required
  `key_metrics[].value` to be numeric.
- `retries=2` added as a safety net — pydantic-ai feeds validation errors back to
  the model for self-correction.
- `NativeOutput(OperationsAnswer)` was verified working (grammar-constrained
  decoding) but reverted: `to_web`'s built-in UI renders native output as a raw
  JSON text bubble, while `ToolOutput` renders the `final_result` tool call as a
  collapsible card. ToolOutput kept for UI quality; residual validation risk is
  mitigated by the corrected instructions + retries, not eliminated.

**Verified:** `test_agent.py` produces schema-valid output in ToolOutput mode,
including the originally failing cancelled-shipment scenario; tools unaffected.

## 2026-11-20 — Fix: ImportError after flat `agent.py` → `agent/` package split

**Symptom:** `ImportError: cannot import name 'create_agent_deps' from 'agent.agent'`
on uvicorn startup (`web_chat.py`).

**Root cause:** incomplete package split. `create_agent_deps` moved to
`agent/agent_get_tools.py`, which itself imported nonexistent modules
`.models`, `.api`, `.utils`. `agent/__init__.py` was left empty, so nothing
imported the tools module — meaning tool registration via
`@shipping_agent.tool` decorators never ran (agent would have served with 0
tools) and `test_agent.py`'s `from agent import ...` also broke.

**Fix:**
- `agent/agent_get_tools.py`: imports repointed to existing modules
  (`from .agent import shipping_agent, ShippingAgentDeps, to_json` +
  `from api_client import ShippingAPIError, ShippingAPIClient`).
- `agent/__init__.py`: re-exports `shipping_agent` + `create_agent_deps`
  (guarantees tools register whenever the package is imported).
- `web_chat.py`: imports `create_agent_deps` from `agent.agent_get_tools`.

**Verified:** `import web_chat` succeeds, `from agent import ...` works for
`test_agent.py`, all 4 tools registered, `create_agent_deps()` builds deps.

**Note:** `agent/agent.py` and `agent_get_tools.py` still import root-level
`api_client`/`models` — works while the server runs from the project root.
If the package is ever used outside this directory, move those modules into
the package (the originally planned `.api`/`.models`/`.utils` split).

## 2026-11-20 — Fix: Agent ignores `final_result` and repeats greeting after tool call

**Symptom:** When the agent called tools returning large lists (e.g.,
`get_delayed_shipments` with 17 shipments), the model responded with a generic
greeting instead of calling `final_result`. PydanticAI retried 4 times and
crashed with `UnexpectedModelBehavior: Exceeded maximum output retries`.

**Root cause:**
1. Ollama's active context window for `gemma4:12b` was capped at `4096` tokens.
2. The system prompt + 9 tool schemas consumed ~2030 tokens.
3. `get_delayed_shipments` returned ~7194 chars (~2200 tokens) because `to_json`
   used `indent=2` and included all fields.
4. Total tokens exceeded 4096, so Ollama silently dropped the user's question
   and the tool result, leaving only the system prompt. The model defaulted to
   a greeting. Retries kept failing because the massive tool result stayed in
   the history.

**Fix:**
- `agent/agent.py`: Rewrote `to_json` to use compact separators, recursively
  remove `null` values, and truncate lists > 25 items with a truncation notice.
  Cleaned up `instructions` to match the actually registered read-only tools.
- `agent/agent_get_tools.py`: Added missing `to_json` to `get_management_report`.
- Ollama: Created `Modelfile` with `PARAMETER num_ctx 8192` and ran
  `ollama create gemma4:12b -f Modelfile` to double the context window.

**Verified:** `run_sync("ما الشحنات المتأخرة...")` now returns a valid
`OperationsAnswer` via `final_result` on the first attempt.

## 2026-11-20 — Fix: Conversational text bubbles appear before `final_result` in web UI

**Symptom:** In `to_web()` chat, the model emitted 3+ conversational text bubbles
(a Markdown summary of the data, then apologies like "أعتذر عن الخطأ التقني...")
before finally calling `final_result`. The structured card appeared only at the
bottom after wasted retries.

**Root cause:**
1. `output_type=OperationsAnswer` (plain `AutoOutputSchema`) left the final call
   unconstrained; after receiving a large tool result, `gemma4:12b` preferred
   writing the report as plain `content` text instead of a `final_result` call.
2. Ollama's `/v1` adapter does not strictly enforce tool-choice, so plain text
   was allowed at the output step.
3. Instructions banned only *raw JSON* as text — implicitly inviting a readable
   Markdown text answer — and said nothing about empty `content`. On each
   `no_output` retry the model apologized *as text* again, so all retries were
   consumed by text bubbles.

**Fix (`agent/agent.py`):**
- `output_type=ToolOutput(OperationsAnswer, name="final_result", description=...)`
  with an explicit Arabic description stating it is the only way to finish.
- `model_settings` gained `temperature: 0.0` to reduce preamble improvisation.
- Instructions rewritten: new top-priority section forbids ANY plain text
  (no summary, explanation, apology, or Markdown — `content` must stay empty);
  every response must be a tool call only (`get_*` or `final_result`); after a
  data tool result, call `final_result` immediately; on validation errors,
  correct args silently instead of apologizing; ambiguous questions go inside
  `final_result.answer`.

**Verified:** Live runs against Ollama for "ما الشحنات المتأخرة؟" and
"ما هي حالة الشحنة SHP-1020؟": tool calls were `get_delayed_shipments` /
`get_shipment_by_id` → `final_result`, `TEXT PARTS: []` (zero), output is a
valid `OperationsAnswer`. `import web_chat` still OK.

**Residual note:** A prompt-based guarantee is not absolute — if `gemma4:12b`
ever emits a text part anyway, `to_web()` will stream it. A hard guarantee
would require filtering `TextPart` events in a custom UI layer (not done, kept
as future option).
