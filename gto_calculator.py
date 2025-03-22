# gto_calculator.py
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
    return equity_dict.get((hand1, hand2), 0.5)

def calculate_push_fold_gto(effective_stack, sb_pos=True):
    sb = 0.5
    bb = 1.0
    pot = sb + bb

    hands = get_all_hands()
    
    sb_push_freq = {hand: 0.5 for hand in hands}
    bb_call_freq = {hand: 0.5 for hand in hands}
    sb_push_ev = {hand: 0.0 for hand in hands}  # EV of pushing
    bb_call_ev = {hand: 0.0 for hand in hands}  # EV of calling

    iterations = 200  # Increased iterations
    learning_rate = 0.005  # Reduced learning rate
    for _ in range(iterations):
        # BB's counter-strategy
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
                bb_ev_fold += push_prob * 0 * get_combinations(sb_hand)  # Fixed: BB has already posted the BB
            bb_call_ev[bb_hand] = bb_ev_call  # Store EV of calling
            if bb_ev_call > bb_ev_fold:
                new_bb_call_freq[bb_hand] = min(1.0, bb_call_freq[bb_hand] + learning_rate)
            else:
                new_bb_call_freq[bb_hand] = max(0.0, bb_call_freq[bb_hand] - learning_rate)

        # SB's counter-strategy
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
            sb_push_ev[sb_hand] = sb_ev_push  # Store EV of pushing
            if sb_ev_push > sb_ev_fold:
                new_sb_push_freq[sb_hand] = min(1.0, sb_push_freq[sb_hand] + learning_rate)
            else:
                new_sb_push_freq[sb_hand] = max(0.0, sb_push_freq[sb_hand] - learning_rate)

        sb_push_freq = new_sb_push_freq
        bb_call_freq = new_bb_call_freq

    return sb_push_freq, bb_call_freq, sb_push_ev, bb_call_ev

def main():
    parser = argparse.ArgumentParser(description="Poker GTO Push/Fold Calculator")
    parser.add_argument('--stack', type=float, default=10, help="Effective stack size in big blinds")
    parser.add_argument('--position', choices=['sb', 'bb'], default='sb', help="Position: sb or bb")
    args = parser.parse_args()

    sb_pos = args.position == 'sb'
    sb_strategy, bb_strategy, sb_push_ev, bb_call_ev = calculate_push_fold_gto(args.stack)

    # SB Push Strategy
    df_sb = pd.DataFrame({
        'Push Frequency': sb_strategy,
        'Push EV': sb_push_ev
    })
    df_sb = df_sb.sort_values(by='Push Frequency', ascending=False)
    print(f"SB Push GTO Strategy for {args.stack} BB:")
    print(df_sb.head(10))
    df_sb.to_csv(f"sb_push_strategy_{args.stack}bb.csv")

    # BB Call Strategy
    df_bb = pd.DataFrame({
        'Call Frequency': bb_strategy,
        'Call EV': bb_call_ev
    })
    df_bb = df_bb.sort_values(by='Call Frequency', ascending=False)
    print(f"\nBB Call GTO Strategy for {args.stack} BB:")
    print(df_bb.head(10))
    df_bb.to_csv(f"bb_call_strategy_{args.stack}bb.csv")

if __name__ == "__main__":
    main()