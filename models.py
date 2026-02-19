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