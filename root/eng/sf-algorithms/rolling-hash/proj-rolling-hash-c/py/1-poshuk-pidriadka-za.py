from typing import List

class RabinKarpMatcher:
    BASE: int = 257
    MOD: int = 10**9 + 7

    @classmethod
    def search(cls, text: str, pattern: str) -> List[int]:
        n, m = len(text), len(pattern)
        if m == 0 or n < m:
            return []

        # Обчислюємо E = (BASE^(m-1)) % MOD
        E = pow(cls.BASE, m - 1, cls.MOD)

        # Первинний хеш шаблону та першого вікна
        hash_pattern = 0
        hash_text = 0
        for i in range(m):
            hash_pattern = (hash_pattern * cls.BASE + ord(pattern[i])) % cls.MOD
            hash_text = (hash_text * cls.BASE + ord(text[i])) % cls.MOD

        matches = []
        for i in range(n - m + 1):
            # Якщо хеші збіглися — посимвольна перевірка
            if hash_text == hash_pattern:
                if text[i : i + m] == pattern:
                    matches.append(i)

            # Зсув вікна праворуч
            if i < n - m:
                leading_char = ord(text[i])
                trailing_char = ord(text[i + m])

                # Формула ковзного оновлення
                hash_text = (hash_text - leading_char * E) % cls.MOD
                hash_text = (hash_text * cls.BASE + trailing_char) % cls.MOD

        return matches

# Демонстрація роботи
if __name__ == "__main__":
    text_data = "ABABDABACDABABCABAB"
    pat_data = "ABABCABAB"
    res = RabinKarpMatcher.search(text_data, pat_data)
    print(f"Текст:   {text_data}")
    print(f"Шаблон:  {pat_data}")
    print(f"Індекси збігів: {res}")
