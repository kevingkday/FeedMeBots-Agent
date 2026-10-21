from typing import Any, Dict, List

SYSTEM_PROMPT = """You are an elite competitive No-Limit Texas Hold'em AI bot competing in the FeedMeBots tournament arena.
Your primary objective is to maximize Expected Value (EV) and win chips over the long run.

RULES & INVARIANTS:
1. You MUST choose an action ONLY from the list of provided legal actions.
2. If you choose "raise", you MUST specify "amount" which is the total Raise-To amount, between minRaiseTo and maxRaiseTo inclusive.
3. If checking is legal and free, prefer check over folding.
4. Output strictly valid JSON matching this schema:
{"action": "fold" | "check" | "call" | "raise", "amount": <integer or null>}
Do not include commentary or markdown outside the JSON object.
"""

def build_prompt(state: Dict[str, Any]) -> str:
    """Formats the sanitized PlayerGameStateV1 into a concise, high-signal LLM prompt."""
    stage = state.get("stage", "unknown").upper()
    hole_cards = state.get("holeCards", [])
    community = state.get("communityCards", [])
    pot = state.get("pot", 0)
    to_call = state.get("toCall", 0)
    hero_seat = state.get("seatIndex", -1)
    big_blind = state.get("bigBlind", 100)
    
    # Identify hero stack
    hero_stack = 0
    for s in state.get("seats", []):
        if s.get("seatIndex") == hero_seat:
            hero_stack = s.get("stack", 0)
            break

    # Format legal actions
    legal_actions = state.get("legalActions", [])
    legal_summary = []
    min_raise = state.get("minRaiseTo")
    max_raise = state.get("maxRaiseTo")
    
    for a in legal_actions:
        act = a.get("action")
        if act == "raise":
            legal_summary.append(f"raise (min: {min_raise}, max: {max_raise})")
        else:
            legal_summary.append(act)

    # Format active players at table
    active_players = []
    for s in state.get("seats", []):
        if s.get("status") == "active":
            is_hero = "(Hero)" if s.get("seatIndex") == hero_seat else ""
            active_players.append(f"Seat {s.get('seatIndex')}{is_hero}: {s.get('name')} (Stack: {s.get('stack')}, Bet: {s.get('bet', 0)})")

    # Format recent history for current street
    history = state.get("actionHistory", [])
    recent_history = [
        f"Seat {h.get('seatIndex')}: {h.get('action')}" + (f" {h.get('amount')}" if h.get("amount") else "")
        for h in history[-8:]
    ]

    prompt_lines = [
        f"STAGE: {stage}",
        f"HERO CARDS: {hole_cards}",
        f"COMMUNITY CARDS: {community if community else 'None (Pre-Flop)'}",
        f"POT: {pot} chips | TO CALL: {to_call} chips | HERO STACK: {hero_stack} chips | BIG BLIND: {big_blind}",
        f"LEGAL ACTIONS: [{', '.join(legal_summary)}]",
        f"PLAYERS IN HAND: {'; '.join(active_players)}",
    ]
    if recent_history:
        prompt_lines.append(f"RECENT ACTIONS: {' -> '.join(recent_history)}")
    
    prompt_lines.append("Choose your action now. Return only valid JSON.")
    return "\n".join(prompt_lines)
