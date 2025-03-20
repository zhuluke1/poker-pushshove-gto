import eval7
import itertools

def calculate_equity(hand1, hand2, board=None):
    """
    Calculate equity of hand1 vs hand2 on a given board.
    hand1, hand2: Strings like 'AhKh', '8s8d'
    board: List of board cards, e.g., ['Qs', 'Jd', 'Tc']
    Returns: Equity of hand1 (float between 0 and 1)
    """
    deck = eval7.Deck()
    hand1_cards = [eval7.Card(card) for card in hand1]
    hand2_cards = [eval7.Card(card) for card in hand2]
    for card in hand1_cards + hand2_cards:
        deck.cards.remove(card)
    
    if board:
        board_cards = [eval7.Card(card) for card in board]
        for card in board_cards:
            deck.cards.remove(card)
    else:
        board_cards = []

    # Monte Carlo simulation for equity
    iterations = 1000
    wins = 0
    ties = 0
    for _ in range(iterations):
        deck.shuffle()
        remaining = 5 - len(board_cards) if board_cards else 5
        community = board_cards + deck.deal(remaining)
        hand1_eval = eval7.evaluate(hand1_cards + community)
        hand2_eval = eval7.evaluate(hand2_cards + community)
        if hand1_eval > hand2_eval:
            wins += 1
        elif hand1_eval == hand2_eval:
            ties += 1
    
    equity = (wins + ties / 2) / iterations
    return equity

def get_all_hands():
    """Generate all possible starting hands (169 unique combos)."""
    ranks = '23456789TJQKA'
    suits = 'shdc'
    hands = []
    # Suited hands (e.g., AKs)
    for r1 in ranks:
        for r2 in ranks[ranks.index(r1):]:
            if r1 == r2:
                continue
            hands.append(f"{r1}{r2}s")
    # Offsuit hands (e.g., AKo)
    for r1 in ranks:
        for r2 in ranks[ranks.index(r1)+1:]:
            hands.append(f"{r1}{r2}o")
    # Pairs (e.g., AA)
    for r in ranks:
        hands.append(f"{r}{r}")
    return hands