from collections import deque

def ladder_length_python(begin_word: str, end_word: str, word_list: list[str]) -> int:
    dict_set = set(word_list)
    if end_word not in dict_set:
        return 0

    q = deque([(begin_word, 1)])

    while q:
        word, length = q.popleft()
        if word == end_word:
            return length

        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                next_word = word[:i] + c + word[i+1:]
                if next_word in dict_set:
                    dict_set.remove(next_word)
                    q.append((next_word, length + 1))
    return 0
