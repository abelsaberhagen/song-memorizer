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

lyrics = content.split('\n')

vt = voice_to_text.VoiceToText()

for line in lyrics:
    for c in unwanted_chars:
         line = line.replace(c, '')
        
    line = line.lower()
    spoken = ''
    while not spoken == line:
        spoken = vt.transcribe_voice()
        spoken = spoken.lower()
        print(line)
        print(spoken)
        if not spoken == line:
            print("That wasn't quite right, try again!")
            

# for word in monologue_list:
#     guess = ''
#     while not guess == word:
#         print("Type in the next word.")
#         guess = input()
#         if guess == word:
#             print("That is correct.")
#         else:
#             print("That is incorrect.")

