from typing import Any, Dict, List, Optional
try:
    from rich import print
except ImportError:
    pass

def get_safe_fallback(state: Dict[str, Any], reason: str = "") -> Dict[str, Any]:
    """
    Deterministically selects a legal, zero-risk move if the LLM crashes, times out,
    or generates an invalid action.
    """
    legal_actions = state.get("legalActions", [])
    legal_names = [a.get("action") for a in legal_actions]
    to_call = state.get("toCall", 0)
    big_blind = state.get("bigBlind", 100)
    hole_cards = state.get("holeCards", [])

    if reason:
        print(f"[bold yellow][Fallback Triggered][/bold yellow] {reason}")

    # 1. If check is free, always check
    if "check" in legal_names:
        return {"action": "check"}

    # 2. If to_call is zero or very small (e.g. completing small blind), call
    if "call" in legal_names and to_call <= big_blind:
        return {"action": "call"}

    # 3. Otherwise fold safely
    if "fold" in legal_names:
        return {"action": "fold"}

    # Ultimate fallback to the first legal option
    if legal_names:
        first = legal_names[0]
        if first == "raise":
            return {"action": "raise", "amount": state.get("minRaiseTo", 200)}
        return {"action": first}

    return {"action": "fold"}


def validate_and_sanitize(raw_action: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strictly validates the LLM action against state.legalActions and sizing constraints.
    Returns sanitized action matching FeedMeBotsActionV1 schema.
    """
    legal_actions = state.get("legalActions", [])
    legal_names = [a.get("action") for a in legal_actions]

    action = raw_action.get("action", "").lower().strip()
    amount = raw_action.get("amount")

    if action not in legal_names:
        return get_safe_fallback(
            state, 
            reason=f"LLM proposed '{action}', which is not in legal actions: {legal_names}"
        )

    if action == "raise":
        min_raise = state.get("minRaiseTo")
        max_raise = state.get("maxRaiseTo")

        if min_raise is None or max_raise is None:
            # Raise is not allowed
            return get_safe_fallback(state, reason="Raise attempted but minRaiseTo is missing")

        # Handle missing or invalid amounts
        try:
            amount = int(amount) if amount is not None else min_raise
        except (ValueError, TypeError):
            amount = min_raise

        # Clamp amount strictly between minRaiseTo and maxRaiseTo
        clamped_amount = max(min_raise, min(max_raise, amount))
        return {"action": "raise", "amount": clamped_amount}

    # For fold, check, call -> no amount should be sent
    return {"action": action}
