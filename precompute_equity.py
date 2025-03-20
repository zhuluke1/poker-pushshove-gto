# precompute_equity.py
import pandas as pd
from hand_equity import calculate_equity, get_all_hands
from utils import expand_hand
from multiprocessing import Pool, cpu_count
import itertools
import random
from tqdm import tqdm

def compute_equity_for_matchup(args):
    """Compute the average equity for a single hand matchup with sampling."""
    hand1, hand2 = args
    h1_combos = expand_hand(hand1)
    h2_combos = expand_hand(hand2)
    # Get all possible combo pairs
    all_pairs = [(h1_combo, h2_combo) for h1_combo in h1_combos for h2_combo in h2_combos]
    # Filter out pairs with overlapping cards
    valid_pairs = [(h1_combo, h2_combo) for h1_combo, h2_combo in all_pairs
                   if len(set([h1_combo[:2], h1_combo[2:], h2_combo[:2], h2_combo[2:]])) == 4]
    # Sample up to 10 pairs to reduce computation time
    sample_size = min(10, len(valid_pairs))
    sampled_pairs = random.sample(valid_pairs, sample_size) if valid_pairs else []
    equity_sum = 0
    count = 0
    for h1_combo, h2_combo in sampled_pairs:
        h1_cards = [h1_combo[:2], h1_combo[2:]]
        h2_cards = [h2_combo[:2], h2_combo[2:]]
        equity = calculate_equity(h1_cards, h2_cards)
        equity_sum += equity
        count += 1
    if count > 0:
        avg_equity = equity_sum / count
    else:
        avg_equity = 0.5  # Default if no valid matchups
    return {'hand1': hand1, 'hand2': hand2, 'equity': avg_equity}

def precompute_equity_table():
    hands = get_all_hands()
    matchups = [(hand1, hand2) for i, hand1 in enumerate(hands) for hand2 in hands[i+1:]]
    
    num_processes = cpu_count()
    print(f"Using {num_processes} processes to compute equities for {len(matchups)} matchups...")
    with Pool(processes=num_processes) as pool:
        results = list(tqdm(pool.imap(compute_equity_for_matchup, matchups), total=len(matchups)))
    
    df = pd.DataFrame(results)
    df.to_csv('equity_table.csv', index=False)
    print("Equity table saved to equity_table.csv")

if __name__ == "__main__":
    precompute_equity_table()