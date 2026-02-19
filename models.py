"""
Mirrors the object model of redeal's library.
Can be used instead of the redeal library if we don't have redeal in the python environment.
"""
import random
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Iterator, Sequence


class Suit(IntEnum):
    SPADES   = 0
    HEARTS   = 1
    DIAMONDS = 2
    CLUBS    = 3

    def __str__(self) -> str:
        return ["♠", "♥", "♦", "♣"][self.value]

    @property
    def letter(self) -> str:
        return "SHDC"[self.value]


class Rank(IntEnum):
    TWO   = 2
    THREE = 3
    FOUR  = 4
    FIVE  = 5
    SIX   = 6
    SEVEN = 7
    EIGHT = 8
    NINE  = 9
    TEN   = 10
    JACK  = 11
    QUEEN = 12
    KING  = 13
    ACE   = 14

    def __str__(self) -> str:
        if self.value <= 9:
            return str(self.value)
        return {10: "T", 11: "J", 12: "Q", 13: "K", 14: "A"}[self.value]


# HCP for deal constraints
HCP_TABLE: dict[Rank, int] = {
    Rank.ACE: 4, Rank.KING: 3, Rank.QUEEN: 2, Rank.JACK: 1
}

# Controls for future settings
CONTROL_TABLE: dict[Rank, int] = {Rank.ACE: 2, Rank.KING: 1}


@dataclass(frozen=True, order=True)
class Card:
    suit: Suit
    rank: Rank

    def __str__(self) -> str:
        return f"{self.suit}{self.rank}"

    @property
    def hcp(self) -> int:
        return HCP_TABLE.get(self.rank, 0)

    @property
    def control(self) -> int:
        return CONTROL_TABLE.get(self.rank, 0)

    @classmethod
    def from_str(cls, s: str) -> "Card":
        suit_map = {"S": Suit.SPADES, "H": Suit.HEARTS, "D": Suit.DIAMONDS, "C": Suit.CLUBS}
        rank_map = {str(r): r for r in Rank}
        rank_map.update({"T": Rank.TEN, "J": Rank.JACK, "Q": Rank.QUEEN,
                         "K": Rank.KING, "A": Rank.ACE})
        return cls(suit=suit_map[s[0].upper()], rank=rank_map[s[1].upper()])


FULL_DECK: list[Card] = [Card(suit, rank) for suit in Suit for rank in Rank]


class Hand:
    """
        One player's 13-card holding.

        Mirrors the interface exposed by redeal's Hand objects so downstream code
        can be written once and work against both implementations.
    """
    def __init__(self, cards: Sequence[Card]) -> None:
        if len(cards) != 13:
            raise ValueError(f"A hand must contain exactly 13 cards, got {len(cards)}")
        self._cards: tuple[Card, ...] = tuple(sorted(cards, reverse=True))

    def _suit(self, suit: Suit) -> tuple[Card, ...]:
        return tuple(c for c in self._cards if c.suit == suit)

    @property
    def spades(self) -> tuple[Card, ...]: return self._suit(Suit.SPADES)

    @property
    def hearts(self) -> tuple[Card, ...]: return self._suit(Suit.HEARTS)

    @property
    def diamonds(self) -> tuple[Card, ...]: return self._suit(Suit.DIAMONDS)

    @property
    def clubs(self) -> tuple[Card, ...]: return self._suit(Suit.CLUBS)

    def suit(self, s: Suit) -> tuple[Card, ...]:
        return self._suit(s)

    @property
    def hcp(self) -> int:
        return sum(c.hcp for c in self._cards)

    @property
    def controls(self) -> int:
        return sum(c.control for c in self._cards)

    @property
    def shape(self) -> tuple[int, int, int, int]:
        return tuple(len(self._suit(s)) for s in Suit)

    @property
    def hcp_per_suit(self) -> dict[Suit, int]:
        return {s: sum(c.hcp for c in self._suit(s)) for s in Suit}

    def top_cards(self, suit: Suit, n: int = 3) -> int:
        """Count of top-N honours (AKQ by default) in a suit."""
        honour_ranks = sorted(Rank, reverse=True)[:n]
        return sum(1 for c in self._suit(suit) if c.rank in honour_ranks)

    @property
    def losers(self) -> float:
        """Losing Trick Count (LTC)."""
        total = 0.0
        for suit in Suit:
            holding = self._suit(suit)
            length = len(holding)
            if length == 0:
                continue
            tricks_to_count = min(length, 3)
            ranks_in_suit = [c.rank for c in holding]
            losers_in_suit = 0.0
            for critical in [Rank.ACE, Rank.KING, Rank.QUEEN][:tricks_to_count]:
                if critical not in ranks_in_suit:
                    losers_in_suit += 1
            if (
                    Rank.QUEEN in ranks_in_suit
                    and Rank.KING not in ranks_in_suit
                    and Rank.ACE not in ranks_in_suit
            ):
                losers_in_suit += 0.5
            total += losers_in_suit
        return total

    @property
    def zar(self) -> float:
        suit_lengths = sorted(self.shape, reverse=True)
        longest, second_longest, _, shortest = suit_lengths
        distribution = (longest + second_longest) + (longest - shortest)
        return self.hcp + self.controls + distribution

    @property
    def is_balanced(self) -> bool:
        """4-3-3-3, 4-4-3-2, or 5-3-3-2."""
        s = sorted(self.shape, reverse=True)
        return s in ([4, 3, 3, 3], [4, 4, 3, 2], [5, 3, 3, 2])

    @property
    def is_semi_balanced(self) -> bool:
        """Balanced OR 5-4-2-2 / 6-3-2-2."""
        if self.is_balanced:
            return True
        s = sorted(self.shape, reverse=True)
        return s in ([5, 4, 2, 2], [6, 3, 2, 2])

    """
    Display Helpers
    """

    def suit_str(self, suit: Suit) -> str:
        """e.g. 'AKJ92'"""
        cards = self._suit(suit)
        if not cards:
            return "-"
        return "".join(str(c.rank) for c in cards)

    def __str__(self) -> str:
        parts = []
        for suit in Suit:
            parts.append(f"{suit}{self.suit_str(suit)}")
        return " ".join(parts)

    def __repr__(self) -> str:
        return f"Hand({self!s})"

    def __iter__(self) -> Iterator[Card]:
        return iter(self._cards)

    def __len__(self) -> int:
        return len(self._cards)


class Seat(IntEnum):
    NORTH = 0
    EAST  = 1
    SOUTH = 2
    WEST  = 3

    def __str__(self) -> str:
        return self.name.capitalize()

    @property
    def partner(self) -> "Seat":
        return Seat((self.value + 2) % 4)

    @property
    def lho(self) -> "Seat":
        """Left-hand opponent."""
        return Seat((self.value + 1) % 4)

    @property
    def rho(self) -> "Seat":
        """Right-hand opponent."""
        return Seat((self.value + 3) % 4)


class Vulnerability(IntEnum):
    NONE     = 0
    NS       = 1
    EW       = 2
    BOTH     = 3

    def __str__(self) -> str:
        return ["None", "NS", "EW", "Both"][self.value]

    def is_vulnerable(self, seat: Seat) -> bool:
        if self == Vulnerability.NONE:
            return False
        if self == Vulnerability.BOTH:
            return True
        if self == Vulnerability.NS:
            return seat in (Seat.NORTH, Seat.SOUTH)
        return seat in (Seat.EAST, Seat.WEST)


    @classmethod
    def from_board(cls, board_number: int) -> "Vulnerability":
        cycle = [
            cls.NONE, cls.NS,   cls.EW,   cls.BOTH,
            cls.NS,   cls.EW,   cls.BOTH, cls.NONE,
            cls.EW,   cls.BOTH, cls.NONE, cls.NS,
            cls.BOTH, cls.NONE, cls.NS,   cls.EW,
        ]
        return cycle[(board_number - 1) % 16]


@dataclass
class Deal:
    """A complete bridge deal — four hands plus metadata."""
    north:   Hand
    east:    Hand
    south:   Hand
    west:    Hand
    dealer:  Seat          = Seat.NORTH
    vuln:    Vulnerability = Vulnerability.NONE
    deal_id: int           = field(default_factory=lambda: random.randint(0, 10**9))

    def hand(self, seat: Seat) -> Hand:
        return [self.north, self.east, self.south, self.west][seat.value]

    def partnership_hcp(self, seat: Seat) -> int:
        """Combined HCP for a seat and its partner."""
        return self.hand(seat).hcp + self.hand(seat.partner).hcp

    def __str__(self) -> str:
        lines = [
            f"Deal #{self.deal_id}  Dealer: {self.dealer}  Vul: {self.vuln}",
            f"  N: {self.north}",
            f"  E: {self.east}",
            f"  S: {self.south}",
            f"  W: {self.west}",
        ]
        return "\n".join(lines)
