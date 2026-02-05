from collections import Counter
from cards import Suit

HCP_MAP = {
    "A": 4, "K": 3, "Q": 2, "J": 1
}

class Hand:
    def __init__(self, cards: list[str]):
        if len(cards) != 13:
            raise ValueError("A hand must contain exactly 13 cards")
        self.cards = sorted(cards)

    def hcp(self) -> int:
        return sum(HCP_MAP.get(card[0], 0) for card in self.cards)

    def suit_lengths(self) -> dict[Suit, int]:
        counter = Counter(card[1] for card in self.cards)
        return {s: counter.get(s.value, 0) for s in Suit}

    def shape(self) -> tuple[int, int, int, int]:
        lengths = self.suit_lengths()
        return tuple(sorted(lengths.values(), reverse=True))

    def __repr__(self):
        return f"Hand(hcp={self.hcp()}, cards={self.cards})"

