"""Constants and utilities related to analysts configuration."""

from agents.degen import degen_agent
from agents.daddy import daddy_agent

# Define analyst configuration - single source of truth
ANALYST_CONFIG = {
    "degen": {
        "display_name": "Degen",
        "agent_func": degen_agent,
        "order": 0,
    },
    "daddy": {
        "display_name": "Dad",
        "agent_func": dad_agent,
        "order": 1,
    }
}

# Derive ANALYST_ORDER from ANALYST_CONFIG for backwards compatibility
ANALYST_ORDER = [(config["display_name"], key) for key, config in sorted(ANALYST_CONFIG.items(), key=lambda x: x[1]["order"])]


def get_analyst_nodes():
    """Get the mapping of analyst keys to their (node_name, agent_func) tuples."""
    return {key: (f"{key}_agent", config["agent_func"]) for key, config in ANALYST_CONFIG.items()}
