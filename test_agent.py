import time
from agent.bot import decide

def run_mock_tests():
    print("=" * 60)
    print("RUNNING FEEDMEBOTS AGENT LOCAL SELF-TEST")
    print("=" * 60)

    # Test Case 1: Pre-Flop Premium Hand Facing Big Blind
    mock_preflop = {
        "version": "v1",
        "stage": "preflop",
        "seatIndex": 0,
        "holeCards": ["Ah", "Kd"],
        "communityCards": [],
        "pot": 150,
        "toCall": 100,
        "minRaiseTo": 200,
        "maxRaiseTo": 10000,
        "bigBlind": 100,
        "legalActions": [
            {"action": "fold"},
            {"action": "call"},
            {"action": "raise", "minRaiseTo": 200, "maxRaiseTo": 10000}
        ],
        "seats": [
            {"seatIndex": 0, "name": "Hero", "stack": 9900, "status": "active"},
            {"seatIndex": 1, "name": "Villain1", "stack": 9850, "status": "active"}
        ],
        "actionHistory": []
    }

    print("\n[Test 1] Premium Pre-Flop [Ah, Kd] - Decision:")
    res1 = decide(mock_preflop)
    assert res1["action"] in ["fold", "call", "raise"], f"Invalid action: {res1}"
    print(f"✅ Result: {res1}")

    # Test Case 2: Flop Check or Bet Opportunity
    mock_flop = {
        "version": "v1",
        "stage": "flop",
        "seatIndex": 0,
        "holeCards": ["Kh", "Ks"],
        "communityCards": ["Kd", "7c", "2s"],
        "pot": 400,
        "toCall": 0,
        "minRaiseTo": 100,
        "maxRaiseTo": 9800,
        "bigBlind": 100,
        "legalActions": [
            {"action": "check"},
            {"action": "raise", "minRaiseTo": 100, "maxRaiseTo": 9800}
        ],
        "seats": [
            {"seatIndex": 0, "name": "Hero", "stack": 9800, "status": "active"},
            {"seatIndex": 1, "name": "Villain1", "stack": 9800, "status": "active"}
        ],
        "actionHistory": []
    }

    print("\n[Test 2] Flop Top Set [Kh, Ks] with check available:")
    res2 = decide(mock_flop)
    assert res2["action"] in ["check", "raise"], f"Invalid action: {res2}"
    print(f"✅ Result: {res2}")

    # Test Case 3: Facing All-in with Weak Hand (Testing Fold/Call)
    mock_river_facing_shove = {
        "version": "v1",
        "stage": "river",
        "seatIndex": 0,
        "holeCards": ["7h", "2d"],
        "communityCards": ["As", "Ks", "Qs", "Js", "3d"],
        "pot": 12000,
        "toCall": 5000,
        "minRaiseTo": None,
        "maxRaiseTo": None,
        "bigBlind": 100,
        "legalActions": [
            {"action": "fold"},
            {"action": "call"}
        ],
        "seats": [
            {"seatIndex": 0, "name": "Hero", "stack": 5000, "status": "active"},
            {"seatIndex": 1, "name": "Villain1", "stack": 15000, "status": "active"}
        ],
        "actionHistory": []
    }

    print("\n[Test 3] River Facing Shove with Trash [7h, 2d]:")
    res3 = decide(mock_river_facing_shove)
    assert res3["action"] in ["fold", "call"], f"Invalid action: {res3}"
    print(f"✅ Result: {res3}")

    print("\n🎉 All 3 self-test scenarios completed successfully!")

if __name__ == "__main__":
    run_mock_tests()
