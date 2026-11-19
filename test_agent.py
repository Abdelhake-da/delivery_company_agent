from dotenv import load_dotenv
from agent import create_agent_deps, shipping_agent
load_dotenv()
deps = create_agent_deps()
result = shipping_agent.run_sync(
    " ما هي حالة الشحنة SHP-1020? ",
    deps=deps,
)
print(result.output.model_dump_json(indent=2))