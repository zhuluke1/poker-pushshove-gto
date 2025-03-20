# utils.py
import itertools

def expand_hand(hand):
    """
    Expand a hand notation (e.g., 'AKs') to specific cards.
    Returns a list of card combinations (e.g., ['AsKs', 'AhKh', ...]).
    """
    ranks = '23456789TJQKA'
    suits = 'shdc'
    if hand.endswith('s'):  # Suited
        r1, r2 = hand[0], hand[1]
        return [f"{r1}{s}{r2}{s}" for s in suits]
    elif hand.endswith('o'):  # Offsuit
        r1, r2 = hand[0], hand[1]
        combos = []
        for s1 in suits:
            for s2 in suits:
                if s1 != s2:
                    combos.append(f"{r1}{s1}{r2}{s2}")
        return combos
    else:  # Pair
        r = hand[0]
        return [f"{r}{s1}{r}{s2}" for s1, s2 in itertools.combinations(suits, 2)]

def get_combinations(hand):
    """
    Get the number of combinations for a hand.
    Suited: 4 combos, Offsuit: 12 combos, Pair: 6 combos.
    """
    if hand.endswith('s'):
        return 4
    elif hand.endswith('o'):
        return 12
    else:
        return 6