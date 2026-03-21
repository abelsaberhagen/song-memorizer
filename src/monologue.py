import voice_to_text

file_path = 'src/lyrics.txt'
content = ''

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")

unwanted_chars = ['.', ',', '!', '?']

monologue = content


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

