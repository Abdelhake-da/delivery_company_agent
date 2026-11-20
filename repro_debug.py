from dotenv import load_dotenv
from agent import create_agent_deps, shipping_agent

load_dotenv()
deps = create_agent_deps()

result = shipping_agent.run_sync(
    "ما الشحنات المتأخرة في جدة حالياً في التسليم",
    deps=deps,
)

print("=" * 30, "ALL MESSAGES", "=" * 30)
for i, m in enumerate(result.all_messages()):
    print(f"--- msg[{i}] {type(m).__name__} ---")
    for part in getattr(m, "parts", []):
        print(f"  part: {type(part).__name__}")
        if hasattr(part, "tool_name"):
            print(f"    tool_name: {part.tool_name}")
        if hasattr(part, "args"):
            a = part.args
            print(f"    args: {a if isinstance(a, str) else str(a)[:500]}")
        if hasattr(part, "content"):
            c = str(part.content)
            print(f"    content: {c[:1500]}")
        if hasattr(part, "model_response_object"):
            pass

print("=" * 30, "FINAL OUTPUT", "=" * 30)
print(result.output.model_dump_json(indent=2, ensure_ascii=False))
