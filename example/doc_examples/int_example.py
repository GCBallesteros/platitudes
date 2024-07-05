import platitudes as pl

def age_guesser(age: int):
    if age  == 42:
      print("You guessed right!")
    else:
      print("Try again!")

pl.run(age_guesser)
