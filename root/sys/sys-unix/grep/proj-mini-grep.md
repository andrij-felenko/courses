# ⚙️ Реалізація потокового пошуку: буферизація та алгоритм Боєра-Мура

Створення ефективного пошукового фільтра вимагає вирішення двох фундаментальних задач системного програмування: мінімізації кількості системних викликів вводу-виводу та запобігання зайвому копіюванню даних у пам'яті. Наївна реалізація через функції на кшталт `fgets()` або `std::getline()` виконує динамічне виділення пам'яті на кожен рядок, перевіряє кожен байт двічі (спочатку шукаючи `\n`, а потім скануючи символи шаблоном) і суттєво деградує при обробці терабайтних потоків даних.

Нижче наведено повноцінну реалізацію мінімального потокового фільтра `mini-grep`, який поєднує блокове зчитування через ковзний буфер (англ. *sliding buffer*), алгоритм швидкого пошуку підрядків Боєра-Мура-Горспула (*Boyer-Moore-Horspool*) та принцип нульового копіювання (*zero-copy line slicing*).

---

### Архітектура зсувного буфера та життєвий цикл розривів рядків

Вхідні дані надходять у програму через файловий дескриптор блоками фіксованого розміру по 64 КБ (65536 байтів). Цей розмір обрано навмисно: він кратно узгоджується зі стандартним розміром сторінки пам'яті віртуальної пам'яті Linux (4096 байтів) та відповідає стандартній місткості кільцевого буфера міжпроцесних каналів `pipe`.

Оскільки блок фіксованого розміру розриває потік у довільному місці, символ завершення рядка `\n` може опинитися на будь-якій позиції блоку, а в кінці зчитаного буфера майже завжди залишається незавершений фрагмент рядка.

Механізм ковзного вікна працює за чітким детермінованим циклом:
1. Залишок незавершеного рядка з попередньої ітерації копіюється на початок буфера за допомогою `memmove()`. Ця операція є надзвичайно швидкою, оскільки залишок рядка зазвичай не перевищує кількох сотень байтів і повністю знаходиться у кеші L1 процесора.
2. Системний виклик `read()` доповнює вільний простір буфера новою порцією байтів безпосередньо з файлового дескриптора.
3. Вказівник сканування послідовно рухається по буферу, шукаючи межі рядків за допомогою функції `memchr()`, яка використовує векторизовані SIMD-інструкції процесора.
4. Кожен знайдений рядок передається в алгоритм пошуку як пара `(початок, довжина)` або `std::string_view` без будь-якого виділення пам'яті в динамічній купі (heap).
5. Якщо алгоритм виявляє збіг — рядок негайно передається системному виклику `write(STDOUT_FILENO, ...)`.

---

### Математика та оптимізація алгоритму Боєра-Мура-Горспула

Для пошуку фіксованого підрядка довжиною `M` у тексті довжиною `N` наївний алгоритм виконує `O(N · M)` побайтових порівнянь. Алгоритм Боєра-Мура-Горспула оптимізує цей процес, використовуючи властивості суфіксів та інформацію про символи, які спричинили невідповідність.

Алгоритм будує одновимірну таблицю зсувів за так званим «поганим символом» (Bad Character Shift Table). Таблиця має фіксований розмір 256 елементів — по одному слоту для кожного можливого значення байта `uint8_t`:

```text
Для кожного символу c від 0 до 255:
  shift_table[c] = M

Для кожного індексу i від 0 до M - 2:
  shift_table[pattern[i]] = M - 1 - i
```

Зверніть увагу: останній символ шаблону `pattern[M - 1]` навмисно не включається у другий цикл, щоб величина зсуву для нього залишалася ненульовою, запобігаючи нескінченному зацикленню сканера.

Порівняння тексту з шаблоном виконується **з правого краю шаблону наліво**:
- Сканер вирівнює шаблон відносно поточної позиції в тексті й перевіряє останній символ `pattern[M - 1]`.
- Якщо останній символ збігається, порівняння продовжується для попередніх символів `M - 2`, `M - 3` тощо.
- Якщо стається розбіжність на будь-якій позиції, сканер дивиться на символ тексту, який стояв навпроти правого краю шаблону, бере з таблиці величину зсуву для цього байта і пересуває вказівник тексту вперед.

Якщо символ тексту взагалі відсутній у шаблоні, сканер робить стрибок одразу на всі `M` позицій вперед. Завдяки цьому середня обчислювальна складність становить `O(N / M)`, що забезпечує сублінійну швидкість сканування.

---

### Програмна реалізація мовами C та C++

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <stdbool.h>

#define BUFFER_CAPACITY (64 * 1024)

typedef struct {
    size_t shift_table[256];
    const char *pattern;
    size_t pattern_len;
} HorspoolMatcher;

static void matcher_init(HorspoolMatcher *m, const char *pattern) {
    m->pattern = pattern;
    m->pattern_len = strlen(pattern);
    const size_t len = m->pattern_len;

    for (size_t i = 0; i < 256; ++i) {
        m->shift_table[i] = len;
    }

    if (len > 0) {
        for (size_t i = 0; i < len - 1; ++i) {
            uint8_t byte = (uint8_t)pattern[i];
            m->shift_table[byte] = len - 1 - i;
        }
    }
}

static bool matcher_find(const HorspoolMatcher *m, const char *text, size_t text_len) {
    const size_t p_len = m->pattern_len;
    if (p_len == 0) return true;
    if (text_len < p_len) return false;

    const char *p = m->pattern;
    size_t i = p_len - 1;

    while (i < text_len) {
        size_t k = 0;
        while (k < p_len && p[p_len - 1 - k] == text[i - k]) {
            k++;
        }
        if (k == p_len) {
            return true;
        }
        uint8_t bad_byte = (uint8_t)text[i];
        i += m->shift_table[bad_byte];
    }
    return false;
}

static int process_stream(int fd, const HorspoolMatcher *matcher) {
    char buffer[BUFFER_CAPACITY + 1];
    size_t carryover = 0;
    bool any_match_found = false;

    while (1) {
        ssize_t bytes_read = read(fd, buffer + carryover, BUFFER_CAPACITY - carryover);
        if (bytes_read < 0) {
            perror("read");
            return 2;
        }
        if (bytes_read == 0 && carryover == 0) {
            break;
        }

        size_t total_in_buffer = carryover + (size_t)bytes_read;
        size_t line_start = 0;

        while (line_start < total_in_buffer) {
            char *newline_ptr = memchr(buffer + line_start, '\n', total_in_buffer - line_start);
            if (!newline_ptr) {
                if (bytes_read == 0) {
                    /* Кінець потоку без завершального \n */
                    size_t line_len = total_in_buffer - line_start;
                    if (matcher_find(matcher, buffer + line_start, line_len)) {
                        write(STDOUT_FILENO, buffer + line_start, line_len);
                        write(STDOUT_FILENO, "\n", 1);
                        any_match_found = true;
                    }
                    line_start = total_in_buffer;
                }
                break;
            }

            size_t line_end = (size_t)(newline_ptr - buffer);
            size_t line_len = line_end - line_start;

            if (matcher_find(matcher, buffer + line_start, line_len)) {
                write(STDOUT_FILENO, buffer + line_start, line_len + 1);
                any_match_found = true;
            }

            line_start = line_end + 1;
        }

        carryover = total_in_buffer - line_start;
        if (carryover > 0) {
            memmove(buffer, buffer + line_start, carryover);
        }

        if (carryover == BUFFER_CAPACITY) {
            /* Рядок довший за буфер — скидаємо та продовжуємо */
            if (matcher_find(matcher, buffer, carryover)) {
                write(STDOUT_FILENO, buffer, carryover);
                write(STDOUT_FILENO, "\n", 1);
                any_match_found = true;
            }
            carryover = 0;
        }

        if (bytes_read == 0) {
            break;
        }
    }

    return any_match_found ? 0 : 1;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        const char msg[] = "Використання: mini_grep <шаблон>\n";
        write(STDERR_FILENO, msg, sizeof(msg) - 1);
        return 2;
    }

    HorspoolMatcher matcher;
    matcher_init(&matcher, argv[1]);

    return process_stream(STDIN_FILENO, &matcher);
}
```
```cpp
#include <iostream>
#include <string_view>
#include <array>
#include <vector>
#include <span>
#include <cstdint>
#include <cstring>
#include <unistd.h>

class HorspoolMatcher {
public:
    explicit HorspoolMatcher(std::string_view pattern)
        : pattern_(pattern), pattern_len_(pattern.size()) {
        shift_table_.fill(pattern_len_);

        if (pattern_len_ > 0) {
            for (size_t i = 0; i < pattern_len_ - 1; ++i) {
                auto byte_val = static_cast<uint8_t>(pattern_[i]);
                shift_table_[byte_val] = pattern_len_ - 1 - i;
            }
        }
    }

    [[nodiscard]] bool contains_in(std::string_view text) const noexcept {
        if (pattern_len_ == 0) return true;
        if (text.size() < pattern_len_) return false;

        size_t i = pattern_len_ - 1;
        while (i < text.size()) {
            size_t k = 0;
            while (k < pattern_len_ && pattern_[pattern_len_ - 1 - k] == text[i - k]) {
                ++k;
            }
            if (k == pattern_len_) {
                return true;
            }
            auto bad_byte = static_cast<uint8_t>(text[i]);
            i += shift_table_[bad_byte];
        }
        return false;
    }

private:
    std::string_view pattern_;
    size_t pattern_len_{0};
    std::array<size_t, 256> shift_table_{};
};

class StreamProcessor {
public:
    static constexpr size_t BufferCapacity = 64 * 1024;

    explicit StreamProcessor(const HorspoolMatcher& matcher) noexcept
        : matcher_(matcher) {}

    int process_descriptor(int fd) {
        std::vector<char> buffer(BufferCapacity + 1);
        size_t carryover = 0;
        bool any_match = false;

        while (true) {
            ssize_t bytes_read = ::read(fd, buffer.data() + carryover, BufferCapacity - carryover);
            if (bytes_read < 0) {
                std::perror("read");
                return 2;
            }
            if (bytes_read == 0 && carryover == 0) {
                break;
            }

            size_t total_in_buffer = carryover + static_cast<size_t>(bytes_read);
            size_t line_start = 0;

            while (line_start < total_in_buffer) {
                auto* start_ptr = buffer.data() + line_start;
                size_t remaining = total_in_buffer - line_start;
                auto* newline_ptr = static_cast<char*>(std::memchr(start_ptr, '\n', remaining));

                if (!newline_ptr) {
                    if (bytes_read == 0) {
                        std::string_view last_line(start_ptr, remaining);
                        if (matcher_.contains_in(last_line)) {
                            [[maybe_unused]] auto w1 = ::write(STDOUT_FILENO, last_line.data(), last_line.size());
                            [[maybe_unused]] auto w2 = ::write(STDOUT_FILENO, "\n", 1);
                            any_match = true;
                        }
                        line_start = total_in_buffer;
                    }
                    break;
                }

                size_t line_end = static_cast<size_t>(newline_ptr - buffer.data());
                size_t line_len = line_end - line_start;
                std::string_view line_view(start_ptr, line_len);

                if (matcher_.contains_in(line_view)) {
                    [[maybe_unused]] auto w = ::write(STDOUT_FILENO, start_ptr, line_len + 1);
                    any_match = true;
                }

                line_start = line_end + 1;
            }

            carryover = total_in_buffer - line_start;
            if (carryover > 0) {
                std::memmove(buffer.data(), buffer.data() + line_start, carryover);
            }

            if (carryover == BufferCapacity) {
                std::string_view overflow_line(buffer.data(), carryover);
                if (matcher_.contains_in(overflow_line)) {
                    [[maybe_unused]] auto w1 = ::write(STDOUT_FILENO, overflow_line.data(), overflow_line.size());
                    [[maybe_unused]] auto w2 = ::write(STDOUT_FILENO, "\n", 1);
                    any_match = true;
                }
                carryover = 0;
            }

            if (bytes_read == 0) {
                break;
            }
        }

        return any_match ? 0 : 1;
    }

private:
    const HorspoolMatcher& matcher_;
};

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: mini_grep <шаблон>\n";
        return 2;
    }

    HorspoolMatcher matcher(argv[1]);
    StreamProcessor processor(matcher);
    return processor.process_descriptor(STDIN_FILENO);
}
```
:::

---

### Аналіз крайових випадків, продуктивності та компіляції

1. **Файли без завершального символу переведення рядка:** Якщо останній рядок вхідного потоку не містить символу `\n`, системний виклик `read()` повертає `0` при ненульовому залишку даних у буфері. Умова `bytes_read == 0` виявляє цей крайній стан, зіставляє останній рядок і самостійно дописує символ `\n` у вихідний потік, щоб не зламати форматування термінала або наступного процесу в конвеєрі.
2. **Переповнення одинарного рядка:** Якщо вхідний файл містить монолітний рядок без жодного символу `\n`, довжина якого перевищує розмір буфера (64 КБ), наївні парсери переповнюють пам'ять. Наша реалізація детектує стан `carryover == BUFFER_CAPACITY`, виконує перевірку наявної частини рядка, скидає її у потік і скидає лічильник залишку, продовжуючи нормальну роботу.
3. **Локальність кешу та відсутність динамічних алокацій:** Застосування статичного масиву `buffer` у просторі стека або вектора з фіксованим резервуванням гарантує, що жоден виклик `malloc()` або `free()` не виконується в гарячому циклі сканування. Це виключає блокування на м'ютексах алокатора пам'яті та усуває фрагментацію heap-пам'яті.
4. **Компіляторна оптимізація та векторизація:** При компіляції з прапорцями `-O3 -march=native` компілятори GCC та Clang автоматично розгортають внутрішній цикл порівняння суфіксів і генерують безперехідні інструкції з використанням векторних регістрів, що додатково мінімізує кількість хибних передбачень переходів процесора (branch mispredictions).
5. **Zero-copy абстракція в C++:** Використання `std::string_view` у C++ версії надає безпечний інтерфейс із контролем меж і довжини рядка без створення тимчасових об'єктів `std::string` та виділення динамічної пам'яті.
