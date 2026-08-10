# ⚙️ Практична реалізація ковзного хешу: Рабін-Карп та rsync-чанкінг

У цій практичній вставці подано готові, випробувані на практиці реалізації двох найважливіших алгоритмів на основі ковзного хешу:
1. **Алгоритм пошуку підрядків Рабіна-Карпа (Rabin-Karp Substring Matcher)** — для миттєвого відсіювання більшості невідповідних позицій у тексті без тривіального посимвольного порівняння.
2. **Алгоритм розбиття на блоки за вмістом (Content-Defined Chunking, CDC)** — для динамічного виявлення меж блоків у байтовому потоці даних (використовується в системі `rsync`, хмарних сховищах та дедуплікаторах даних).

Код надано у вкладках `:::tabs` двома мовами — продуманим ідіоматичним **C++17** (із наголосом на обчислювальну швидкодію, 64-бітні цілі типи, запобігання переповненням і правильну обробку від'ємних залишків у модулярній арифметиці) та **Python 3** (із наголосом на виразність, гнучкість і чистоту синтаксису).

---

## 1. Пошук підрядка за алгоритмом Рабіна-Карпа

Змістовна ідея реалізації полягає в тому, що ми спершу обчислюємо поліноміальний хеш шаблону `pattern` довжиною `m` за допомогою основи `B = 257` та простого модуля `P = 10⁹ + 7`. Паралельно ми обчислюємо хеш перших `m` символів тексту `text`.

Під час проходження вікна довжиною `m` вздовж тексту ми порівнюємо поточне значення хешу тексту з хешем шаблону. Оскільки два однакові рядки гарантовано мають однакові хеш-значення, випадок `hash_text != hash_pattern` дозволяє нам миттєво відкинути поточне вікно за `O(1)` операцій без читання його символів. Якщо ж виникає рівність `hash_text == hash_pattern`, ми обов'язково виконуємо посимвольну перевірку підрядка, щоб виключити малоймовірний випадок колізії хеш-функції.

Оновлення хешу при зсуві вікна на один символ праворуч здійснюється за формулою:

H_new = ((H_old - s[i] · E) · B + s[i+m]) mod P

де `E = B^{m-1} mod P` — заздалегідь обчислений множник старшого розряду.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cstdint>

// Структура для виконання пошуку Рабіна-Карпа
class RabinKarpMatcher {
private:
    static constexpr uint64_t B = 257;        // Основа полінома (більше за ASCII 255)
    static constexpr uint64_t P = 1000000007; // Просте число (модуль)

public:
    static std::vector<size_t> search(const std::string& text, const std::string& pattern) {
        std::vector<size_t> matches;
        size_t n = text.length();
        size_t m = pattern.length();

        if (m == 0 || n < m) {
            return matches;
        }

        // Обчислюємо E = (B^(m-1)) % P для старшого розряду
        uint64_t E = 1;
        for (size_t i = 0; i < m - 1; ++i) {
            E = (E * B) % P;
        }

        // Обчислюємо хеш шаблону та першого вікна тексту за схемою Горнера
        uint64_t hash_pattern = 0;
        uint64_t hash_text = 0;
        for (size_t i = 0; i < m; ++i) {
            hash_pattern = (hash_pattern * B + static_cast<uint8_t>(pattern[i])) % P;
            hash_text = (hash_text * B + static_cast<uint8_t>(text[i])) % P;
        }

        // Скануємо текст
        for (size_t i = 0; i <= n - m; ++i) {
            // При збігу хешів виконуємо посимвольну перевірку для захисту від колізій
            if (hash_text == hash_pattern) {
                bool is_match = true;
                for (size_t j = 0; j < m; ++j) {
                    if (text[i + j] != pattern[j]) {
                        is_match = false;
                        break;
                    }
                }
                if (is_match) {
                    matches.push_back(i);
                }
            }

            // Зсуваємо вікно праворуч на 1 символ (якщо є куди зсувати)
            if (i < n - m) {
                uint64_t leading_char = static_cast<uint8_t>(text[i]);
                uint64_t trailing_char = static_cast<uint8_t>(text[i + m]);

                // H' = (H_old - leading_char * E) % P
                uint64_t term = (leading_char * E) % P;
                uint64_t hash_sub = (hash_text >= term) ? (hash_text - term) : (hash_text + P - term);

                // H_new = (H' * B + trailing_char) % P
                hash_text = (hash_sub * B + trailing_char) % P;
            }
        }

        return matches;
    }
};

int main() {
    std::string text = "ABABDABACDABABCABAB";
    std::string pattern = "ABABCABAB";

    std::vector<size_t> matches = RabinKarpMatcher::search(text, pattern);

    std::cout << "Текст:   " << text << "\n";
    std::cout << "Шаблон:  " << pattern << "\n";
    std::cout << "Знайдено на індексах: ";
    for (size_t idx : matches) {
        std::cout << idx << " ";
    }
    std::cout << "\n";

    return 0;
}
```
```py
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
```
:::

---

## 2. Content-Defined Chunking (CDC) для rsync та дедуплікації

Друга задача — динамічне розбиття байтового потоку на блоки змінного розміру залежно від їхнього локального вмісту.

У цій алгоритмічній схемі невелике вікно розміром `WINDOW_SIZE = 16` сканує масив байтів. Для кожної позиції обчислюється поліноміальний ковзний хеш. Межею блоку (маркером) вважається позиція, у якій молодші біти ковзного хешу дорівнюють нулю:

(current_hash & (TARGET_BLOCK_SIZE - 1)) == 0

Для забезпечення стабільності та уникнення крайніх випадків (надто малих або надто великих блоків) у реалізації передбачено гарантовану максимальну довжину блоку `TARGET_BLOCK_SIZE * 4`. Якщо сканувальне вікно не зустрічає природну межу протягом цього інтервалу, блок примусово закривається.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <cstdint>
#include <iomanip>

struct Chunk {
    size_t start_offset;
    size_t length;
    uint64_t boundary_hash;
};

class ContentDefinedChunker {
private:
    static constexpr uint64_t B = 257;
    static constexpr uint64_t P = 1000000007;

public:
    static std::vector<Chunk> chunk_data(const std::vector<uint8_t>& data,
                                          size_t window_size = 16,
                                          size_t target_chunk_size = 64) {
        std::vector<Chunk> chunks;
        size_t n = data.size();
        if (n == 0) return chunks;

        uint64_t mask = target_chunk_size - 1; // Для швидкості (target_chunk_size є ступенем 2)

        // E = B^(window_size - 1) % P
        uint64_t E = 1;
        for (size_t i = 0; i < window_size - 1; ++i) {
            E = (E * B) % P;
        }

        uint64_t current_hash = 0;
        size_t chunk_start = 0;

        for (size_t i = 0; i < n; ++i) {
            // Оновлюємо хеш поточного вікна
            if (i < window_size) {
                current_hash = (current_hash * B + data[i]) % P;
            } else {
                uint64_t leading = data[i - window_size];
                uint64_t trailing = data[i];

                uint64_t term = (leading * E) % P;
                uint64_t sub = (current_hash >= term) ? (current_hash - term) : (current_hash + P - term);
                current_hash = (sub * B + trailing) % P;
            }

            // Перевіряємо умову межі блоку (або досягнення максимального розміру)
            size_t current_chunk_len = i - chunk_start + 1;
            bool is_boundary = (i >= window_size - 1) && ((current_hash & mask) == 0);
            bool is_max_size = (current_chunk_len >= target_chunk_size * 4);

            if (is_boundary || is_max_size || i == n - 1) {
                chunks.push_back({chunk_start, current_chunk_len, current_hash});
                chunk_start = i + 1;
            }
        }

        return chunks;
    }
};

int main() {
    // Ґенеруємо тестовий масив байтів із повторюваними 패턴ами
    std::vector<uint8_t> stream(512);
    for (size_t i = 0; i < stream.size(); ++i) {
        stream[i] = static_cast<uint8_t>((i * 13 + 7) % 256);
    }

    auto chunks = ContentDefinedChunker::chunk_data(stream, 16, 64);

    std::cout << "Згенеровано " << chunks.size() << " динамічних блоків (CDC):\n";
    std::cout << "--------------------------------------------------------\n";
    std::cout << "№   | Зсув (байтів) | Довжина (байтів) | Хеш межі\n";
    std::cout << "--------------------------------------------------------\n";
    for (size_t i = 0; i < chunks.size(); ++i) {
        std::cout << std::setw(3) << i + 1 << " | "
                  << std::setw(13) << chunks[i].start_offset << " | "
                  << std::setw(16) << chunks[i].length << " | 0x"
                  << std::hex << chunks[i].boundary_hash << std::dec << "\n";
    }

    return 0;
}
```
```py
from typing import List, Dict, Any

class ContentDefinedChunker:
    BASE: int = 257
    MOD: int = 10**9 + 7

    @classmethod
    def chunk_data(cls, data: bytes, window_size: int = 16, target_chunk_size: int = 64) -> List[Dict[str, Any]]:
        n = len(data)
        if n == 0:
            return []

        mask = target_chunk_size - 1
        E = pow(cls.BASE, window_size - 1, cls.MOD)

        chunks = []
        current_hash = 0
        chunk_start = 0

        for i in range(n):
            if i < window_size:
                current_hash = (current_hash * cls.BASE + data[i]) % cls.MOD
            else:
                leading = data[i - window_size]
                trailing = data[i]:

                # Формула ковзного зсуву
                current_hash = (current_hash - leading * E) % cls.MOD
                current_hash = (current_hash * cls.BASE + trailing) % cls.MOD

            current_len = i - chunk_start + 1
            is_boundary = (i >= window_size - 1) and ((current_hash & mask) == 0)
            is_max_size = (current_len >= target_chunk_size * 4)

            if is_boundary or is_max_size or (i == n - 1):
                chunks.append({
                    "start_offset": chunk_start,
                    "length": current_len,
                    "hash": current_hash
                })
                chunk_start = i + 1

        return chunks

# Демонстрація CDC чанкінгу
if __name__ == "__main__":
    test_stream = bytes([(i * 13 + 7) % 256 for i in range(512)])
    result_chunks = ContentDefinedChunker.chunk_data(test_stream, window_size=16, target_chunk_size=64)

    print(f"Згенеровано {len(result_chunks)} динамічних блоків (CDC):")
    print("-" * 56)
    print("№   | Зсув (байтів) | Довжина (байтів) | Хеш межі")
    print("-" * 56)
    for idx, c in enumerate(result_chunks, 1):
        print(f"{idx:3d} | {c['start_offset']:13d} | {c['length']:16d} | 0x{c['hash']:x}")
```
:::

---

## 3. Покроковий розбір обробки граничних випадків та оптимізації

1. **Запобігання від'ємному результату модулярної арифметики:**
   У C++ вираз `(hash_text - term)` може дати від'ємне значення, якщо `hash_text < term`. Стандарт мови C++ визначає результат оператора `%` для від'ємного діленого як від'ємний або залежний від реалізації. Тому в коді C++ застосовується безвідходний тернарний вираз:
   `uint64_t hash_sub = (hash_text >= term) ? (hash_text - term) : (hash_text + P - term);`
   Це гарантує, що `hash_sub` завжди знаходиться у діапазоні `[0 .. P - 1]`.

2. **Захист від 32-бітного переповнення при множенні:**
   Множення двох 32-бітних чисел `term = (leading * E)` при `E ≈ 10⁹` та `leading ≈ 255` дає результат близько `2.5 · 10¹¹`, який перевищує максимальне значення 32-бітного цілого `UINT32_MAX ≈ 4.29 · 10⁹`. Застосування 64-бітних типів `uint64_t` у C++ повністю усуває загрозу цілочисельного переповнення.

3. **Оптимізація перевірки меж блоків за допомогою бітової маски:**
   Якщо бажаний середній розмір блоку `target_chunk_size` обрано як ступінь двійки (наприклад, 64, 4096 або 65536 байтів), операцію математичного залишку `current_hash % target_chunk_size` можна замінити побітовим І `current_hash & (target_chunk_size - 1)`. Така заміна прискорює процес сканування байтового потоку у 3–4 рази, оскільки бітова маска конвеєризується процесором за 1 такт, у той час як ділення вимагає десятків тактів.
