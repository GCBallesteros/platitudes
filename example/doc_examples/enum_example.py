from enum import Enum

import platitudes as pl


class Fruits(Enum):
    Banana = 0
    Apple = 1
    Kiwi = 2


def fruit_scores(fruit: Fruits):
    match fruit:
        case Fruits.Banana:
            print("Good")
        case Fruits.Apple:
            print("Meh")
        case Fruits.Kiwi:
            print("Super delicious")
        case _:
            raise ValueError("Pyright should be screaming at you")


pl.run(fruit_scores)
