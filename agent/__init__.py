from .agent import shipping_agent
from .agent_get_tools import create_agent_deps
from . import agent_stat_tools, agent_get_tools, agent_function_tool # noqa: F401  (import registers its @shipping_agent.tool functions)
