# gto_calculator.py (updated with user input and BB call range)
import numpy as np
import pandas as pd
from hand_equity import get_all_hands
from utils import expand_hand, get_combinations
import argparse

# Load precomputed equity table
equity_df = pd.read_csv('equity_table.csv')
equity_dict = {(row['hand1'], row['hand2']): row['equity'] for _, row in equity_df.iterrows()}
equity_dict.update({(h2, h1): 1 - equity for (h1, h2), equity in equity_dict.items()})

def get_equity(hand1, hand2):
    """Get precomputed equity of hand1 vs hand2."""
    return equity_dict.get((hand1, hand2), 0.5)  # Default to 0.5 if not found

def calculate_push_fold_gto(effective_stack, sb_pos=True):
    """
    Calculate GTO push/fold ranges for a given stack size.
    effective_stack: Stack size in big blinds (e.g., 10)
    sb_pos: True if Small Blind, False if Big Blind
    Returns: (sb_push_freq, bb_call_freq) - Dictionaries of hand:push/call_frequency
    """
    # Simplified assumptions
    sb = 0.5  # Small blind
    bb = 1.0  # Big blind
    pot = sb + bb  # Initial pot before action

    # Get all possible hands
    hands = get_all_hands()
    
    # Initialize strategies (push frequency for SB, call frequency for BB)
    sb_push_freq = {hand: 0.5 for hand in hands}  # Start with 50% push frequency
    bb_call_freq = {hand: 0.5 for hand in hands}  # Start with 50% call frequency

    # Iterative method to approximate Nash equilibrium
    iterations = 100  # Increased for better convergence
    learning_rate = 0.01  # Reduced for finer adjustments
    for _ in range(iterations):
        # Calculate BB's counter-strategy (best response to SB's push range)
        new_bb_call_freq = {}
        for bb_hand in hands:
            bb_ev_call = 0
            bb_ev_fold = 0
            for sb_hand in hands:
                push_prob = sb_push_freq[sb_hand]
                if push_prob == 0:
                    continue
                equity = get_equity(bb_hand, sb_hand)
                ev_win = (effective_stack + pot) * equity
                ev_lose = -effective_stack * (1 - equity)
                bb_ev_call += push_prob * (ev_win + ev_lose) * get_combinations(sb_hand)
                bb_ev_fold += push_prob * (-bb) * get_combinations(sb_hand)
            if bb_ev_call > bb_ev_fold:
                new_bb_call_freq[bb_hand] = min(1.0, bb_call_freq[bb_hand] + learning_rate)
            else:
                new_bb_call_freq[bb_hand] = max(0.0, bb_call_freq[bb_hand] - learning_rate)

        # Calculate SB's counter-strategy (best response to BB's call range)
        new_sb_push_freq = {}
        for sb_hand in hands:
            sb_ev_push = 0
            sb_ev_fold = 0
            for bb_hand in hands:
                call_prob = bb_call_freq[bb_hand]
                equity = get_equity(sb_hand, bb_hand)
                ev_fold = pot * (1 - call_prob)
                ev_call_win = (effective_stack + pot) * equity * call_prob
                ev_call_lose = -effective_stack * (1 - equity) * call_prob
                sb_ev_push += (ev_fold + ev_call_win + ev_call_lose) * get_combinations(bb_hand)
                sb_ev_fold += -sb * get_combinations(bb_hand)
            if sb_ev_push > sb_ev_fold:
                new_sb_push_freq[sb_hand] = min(1.0, sb_push_freq[sb_hand] + learning_rate)
            else:
                new_sb_push_freq[sb_hand] = max(0.0, sb_push_freq[sb_hand] - learning_rate)

        sb_push_freq = new_sb_push_freq
        bb_call_freq = new_bb_call_freq

    return sb_push_freq, bb_call_freq

def main():
    parser = argparse.ArgumentParser(description="Poker GTO Push/Fold Calculator")
    parser.add_argument('--stack', type=float, default=10, help="Effective stack size in big blinds")
    parser.add_argument('--position', choices=['sb', 'bb'], default='sb', help="Position: sb (Small Blind) or bb (Big Blind)")
    args = parser.parse_args()

    sb_pos = args.position == 'sb'
    sb_strategy, bb_strategy = calculate_push_fold_gto(args.stack)

    # SB Push Strategy
    df_sb = pd.DataFrame.from_dict(sb_strategy, orient='index', columns=['Push Frequency'])
    df_sb = df_sb.sort_values(by='Push Frequency', ascending=False)
    print(f"SB Push GTO Strategy for {args.stack} BB:")
    print(df_sb.head(10))
    df_sb.to_csv(f"sb_push_strategy_{args.stack}bb.csv")

    # BB Call Strategy
    df_bb = pd.DataFrame.from_dict(bb_strategy, orient='index', columns=['Call Frequency'])
    df_bb = df_bb.sort_values(by='Call Frequency', ascending=False)
    print(f"\nBB Call GTO Strategy for {args.stack} BB:")
    print(df_bb.head(10))
    df_bb.to_csv(f"bb_call_strategy_{args.stack}bb.csv")

if __name__ == "__main__":
    main()