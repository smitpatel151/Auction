words = list()


def permute(word, result):
    global words

    if len(word) == 0:
        words.append(result)

    for i in range(len(word)):
        char = word[i]
        leftPart = word[0:i]
        rightPart = word[i + 1:]
        remainWord = leftPart + rightPart
        permute(remainWord, result + char)


permute("SMIT", "")
print(words)