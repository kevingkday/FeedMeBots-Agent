import time
from typing import Any, Dict
from rich import print
from agent.config import BOT_NAME, OLLAMA_MODEL
from agent.llm import query_ollama
from agent.validator import validate_and_sanitize, get_safe_fallback

def decide(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Core FeedMeBots Architectural Invariant:
    decide(player_game_state) -> action
    """
    stage = state.get("stage", "preflop")
    hole_cards = state.get("holeCards", [])
    pot = state.get("pot", 0)
    to_call = state.get("toCall", 0)

    t_start = time.perf_counter()
    action_result = None
    latency_ms = 0.0
    fallback_used = False

    try:
        llm_out = query_ollama(state)
        raw_action = llm_out["raw"]
        latency_ms = llm_out["latency_ms"]
        action_result = validate_and_sanitize(raw_action, state)
        
        # Check if validator had to override
        if action_result.get("action") != raw_action.get("action"):
            fallback_used = True

    except Exception as e:
        latency_ms = (time.perf_counter() - t_start) * 1000.0
        fallback_used = True
        action_result = get_safe_fallback(state, reason=f"Exception: {e}")

    # Rich logging for developer observation
    act = action_result.get("action")
    amt_str = f" to {action_result.get('amount')}" if "amount" in action_result else ""
    status_tag = "[red][FALLBACK][/red]" if fallback_used else "[green][LLM][/green]"
    
    print(
        f"[bold cyan][{BOT_NAME}][/bold cyan] {status_tag} "
        f"Stage: [magenta]{stage.upper():<7}[/magenta] | "
        f"Cards: [yellow]{hole_cards}[/yellow] | "
        f"Pot: [green]{pot:<5}[/green] | "
        f"ToCall: [red]{to_call:<4}[/red] | "
        f"Action: [bold white]{act.upper()}{amt_str}[/bold white] "
        f"([dim]{latency_ms:.1f}ms[/dim])"
    )

    return action_result
