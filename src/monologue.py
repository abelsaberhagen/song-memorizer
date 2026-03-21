unwanted_chars = ['.', ',', '!', '?']

monologue = "Help me please."

for c in unwanted_chars:
    monologue = monologue.strip(c)
    
monologue_list = monologue.split(' ')

for word in monologue_list:
    guess = ''
    while not guess == word:
        print("Type in the next word.")
        guess = input()
        if guess == word:
            print("That is correct.")
        else:
            print("That is incorrect.")
    
print("You completed your training!")
