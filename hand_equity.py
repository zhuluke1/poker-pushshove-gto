import eval7
import itertools

def normalize_card(card):
    """
    Properly formats a card string like 'as' or 'td' → 'As', 'Td'
    """
    if len(card) != 2:
        raise ValueError(f"Invalid card format: {card}")
    rank = card[0].upper()
    suit = card[1].lower()
    return rank + suit

def calculate_equity(hand1, hand2, board=None):
    """
    Calculate equity of hand1 vs hand2 on a given board.
    hand1, hand2: List of card strings like ['Ah', 'Kh'], ['8s', '8d']
    board: Optional list of board cards, e.g., ['Qs', 'Jd', 'Tc']
    Returns: Equity of hand1 (float between 0 and 1)
    """
    # Normalize all cards and create eval7.Card objects
    hand1_cards = [eval7.Card(normalize_card(card)) for card in hand1]
    hand2_cards = [eval7.Card(normalize_card(card)) for card in hand2]
    board_cards = [eval7.Card(normalize_card(card)) for card in board] if board else []

    # Check for duplicates
    all_cards = hand1_cards + hand2_cards + board_cards
    if len(set(all_cards)) != len(all_cards):
        raise ValueError("Duplicate cards found between hand1, hand2, or board.")

    # Monte Carlo simulation for equity
    iterations = 1000  # Increased for better accuracy
    wins = 0
    ties = 0

    for _ in range(iterations):
        # Reset the deck for each iteration
        deck = eval7.Deck()
        for card in all_cards:
            deck.cards.remove(card)

        remaining = 5 - len(board_cards)

        if remaining < 0:
            raise ValueError("Too many cards on the board!")

        if len(deck.cards) < remaining:
            print("Deck size before deal:", len(deck.cards))
            print("Trying to deal:", remaining)
            print("hand1:", hand1)
            print("hand2:", hand2)
            print("board:", board)
            raise ValueError("Insufficient cards in deck. Possible duplicate or overlap.")

        deck.shuffle()
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
    hands = []

    # Suited hands (e.g., AKs)
    for i in range(len(ranks)):
        for j in range(i+1, len(ranks)):
            hands.append(f"{ranks[j]}{ranks[i]}s")

    # Offsuit hands (e.g., AKo)
    for i in range(len(ranks)):
        for j in range(i+1, len(ranks)):
            hands.append(f"{ranks[j]}{ranks[i]}o")

    # Pocket pairs (e.g., AA)
    for r in ranks:
        hands.append(f"{r}{r}")

    return hands

# === Test Run ===
if __name__ == "__main__":
    try:
        # Test 1: AA vs KK on 2c 7d 9h (should be ~82-83%)
        equity = calculate_equity(['As', 'Ah'], ['Kd', 'Kh'], board=['2c', '7d', '9h'])
        print(f"Equity of AA vs KK on 2c 7d 9h: {equity:.4f}")

        # Test 2: AKs vs QQ preflop (should be ~46% for AKs)
        equity = calculate_equity(['As', 'Ks'], ['Qh', 'Qd'], board=None)
        print(f"Equity of AKs vs QQ preflop: {equity:.4f}")
    except ValueError as e:
        print("Error:", e)