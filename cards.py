from enum import Enum


class Suit(str, Enum):
    SPADES = "S"
    HEARTS = "H"
    DIAMONDS = "D"
    CLUBS = "C"


RANKS = "23456789TJQKA"

FULL_DECK = [r + s.value for s in Suit for r in RANKS]