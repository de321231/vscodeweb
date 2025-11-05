# ...existing code...
import random
import time

def read_guess():
    while True:
        s = input("Guess a random number between 1 and 100: ").strip()
        try:
            g = int(s)
        except ValueError:
            print("Invilid input. Please enter a number.")
            continue
        if 1 <= g <= 10:
            return g
        print("Not valid number. Please  ")

def main():
    ziel = random.randint(1, 10)
    guess = read_guess()
    if guess == ziel:
        print("Yout rigt!!")
    else:
        print("WRONG!! The correct number was", ziel, "Try again. But your will be wrong again.")

if __name__ == "__main__":
    main()
