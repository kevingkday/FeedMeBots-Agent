"""
Converts FeedMeBots simulator JSON hand exports into instruction fine-tuning datasets (JSONL)
for SFT training on NVIDIA RTX 5080.

Usage:
  # 1. In FeedMeBots monorepo, generate 10,000 tournament hands:
  #    pnpm dev:sim --hands 10000 --bots tag,tag,station,random --export data/hands.json
  #
  # 2. In FeedMeBots-Agent:
  #    python train/prepare_data.py --input ../FeedMeBots/data/hands.json --output data/train.jsonl
"""
import argparse
import json
import os
from agent.prompt import SYSTEM_PROMPT, build_prompt

def extract_training_samples(hands_file: str, output_file: str, min_profit_bb: int = 1):
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    with open(hands_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    hands = data if isinstance(data, list) else data.get("hands", [])
    print(f"Loaded {len(hands)} hands from {hands_file}")

    samples = []
    for hand in hands:
        # Filter for winning bot decisions
        winner_seats = hand.get("winners", [])
        for step in hand.get("decisionSteps", []):
            seat = step.get("seatIndex")
            if seat in winner_seats:
                state = step.get("state")
                chosen_action = step.get("action")
                if not state or not chosen_action:
                    continue
                
                user_content = build_prompt(state)
                assistant_content = json.dumps(chosen_action)

                sample = {
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                        {"role": "assistant", "content": assistant_content}
                    ]
                }
                samples.append(sample)

    with open(output_file, "w", encoding="utf-8") as out:
        for s in samples:
            out.write(json.dumps(s) + "\n")

    print(f"Exported {len(samples)} instruction training pairs to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="../FeedMeBots/data/hands.json", help="Path to simulator exported hands.json")
    parser.add_argument("--output", default="data/train.jsonl", help="Output path for JSONL dataset")
    args = parser.parse_args()
    extract_training_samples(args.input, args.output)
