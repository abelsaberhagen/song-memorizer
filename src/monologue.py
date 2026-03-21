import voice_to_text

unwanted_chars = ['.', ',', '!', '?']

monologue = "I want to go to France"

monologue.lower()
for c in unwanted_chars:
    monologue = monologue.strip(c)
    
monologue_list = monologue.split(' ')


vt = voice_to_text.VoiceToText()

spoken = ''
while not spoken == monologue:
    spoken = vt.transcribe_voice()
    spoken.lower()
    if spoken == monologue:
        print("You completed your training!")

# for word in monologue_list:
#     guess = ''
#     while not guess == word:
#         print("Type in the next word.")
#         guess = input()
#         if guess == word:
#             print("That is correct.")
#         else:
#             print("That is incorrect.")

