from dotenv import load_dotenv
from agent.agent import shipping_agent
from agent.agent_get_tools import create_agent_deps

load_dotenv()
deps = create_agent_deps()
app = shipping_agent.to_web(
deps=deps,
)