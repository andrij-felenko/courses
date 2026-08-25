# ⚙️ KWIC: два розклади на практиці — від процедурного ланцюга до прихованих рішень

Коли програмну систему проєктують на папері, вона завжди виглядає стрункою. Проблема виникає в день, коли одна з ключових деталей реалізації — внутрішній формат масиву, спосіб вирівнювання рядків у пам'яті або алгоритм індексації — має змінитися під новими вимогами замовника чи обмеженнями заліза. На прикладі класичної задачі побудови покажчика ключових слів у контексті (KWIC — англ. *Key Word In Context*), яку вперше розібрав Девід Парнас у 1972 році, ми побачимо, як виглядають обидва способи декомпозиції у працюючому коді: процедурний ланцюг за блок-схемою та модульний розклад за прихованими рішеннями.

Задача KWIC полягає у наступному: на вхід надходить набір текстових рядків. Для кожного рядка необхідно згенерувати всі можливі циклічні зсуви слів (кожне слово по черзі стає першим словом рядка), упорядкувати всі отримані зсуви за абеткою та надрукувати результат у вигляді зручного для пошуку покажчика.

## Процедурний розклад: конвеєр навколо спільної пам'яті

Перший підхід повторює послідовність дій програми у часі. Робота системи ділиться на чотири послідовні фази: ввід тексту з джерела, генерація зсувів слів, алфавітне сортування отриманих записів та форматований вивід. Оскільки всі ці фази потребують доступу до самих символів і таблиці зсувів, розробник природним чином виносить дані у спільну структуру, яку кожен модуль читає й модифікує напряму.

У цій структурі всі масиви оголені: модулі точно знають, що символи лежать у суцільному буфері `chars`, рядки відокремлюються нуль-термінаторами, а кожен зсув кодується парою цілих чисел — індексом рядка та зміщенням символу від початку рядка.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_CHARS 4096
#define MAX_WORDS 512
#define MAX_SHIFTS 512

/* СПІЛЬНА СТРУКТУРА: усі модулі знають її точну будову */
typedef struct {
    char chars[MAX_CHARS];         /* суцільний масив символів із нуль-термінаторами */
    size_t char_count;
    
    size_t line_starts[MAX_WORDS]; /* індекси початку кожного рядка в chars */
    size_t line_count;
    
    /* Зсув описується парою: (індекс рядка, номер першого слова в зсуві) */
    struct {
        size_t line_idx;
        size_t word_offset;
    } shifts[MAX_SHIFTS];
    size_t shift_count;
} shared_kwic_data_t;

/* Модуль 1: Ввід тексту */
void step_input(shared_kwic_data_t *data, const char **raw_lines, size_t count) {
    data->char_count = 0;
    data->line_count = 0;
    for (size_t i = 0; i < count; i++) {
        data->line_starts[data->line_count++] = data->char_count;
        size_t len = strlen(raw_lines[i]) + 1;
        memcpy(&data->chars[data->char_count], raw_lines[i], len);
        data->char_count += len;
    }
}

/* Модуль 2: Циклічний зсув (знає внутрішнє розташування символів у масиві chars) */
void step_circular_shift(shared_kwic_data_t *data) {
    data->shift_count = 0;
    for (size_t l = 0; l < data->line_count; l++) {
        const char *line = &data->chars[data->line_starts[l]];
        size_t word_idx = 0;
        bool in_word = false;
        
        for (size_t c = 0; line[c] != '\0'; c++) {
            if (line[c] != ' ' && !in_word) {
                in_word = true;
                data->shifts[data->shift_count].line_idx = l;
                data->shifts[data->shift_count].word_offset = c;
                data->shift_count++;
            } else if (line[c] == ' ') {
                in_word = false;
            }
        }
    }
}

/* Модуль 3: Упорядкування (порівнює рядки, рахуючи зміщення напряму в chars) */
static int compare_shifts(const void *a, const void *b, void *user_data) {
    const shared_kwic_data_t *data = (const shared_kwic_data_t *)user_data;
    const size_t *idx_a = (const size_t *)a;
    const size_t *idx_b = (const size_t *)b;
    
    const char *line_a = &data->chars[data->line_starts[data->shifts[*idx_a].line_idx]];
    const char *line_b = &data->chars[data->line_starts[data->shifts[*idx_b].line_idx]];
    
    const char *start_a = line_a + data->shifts[*idx_a].word_offset;
    const char *start_b = line_b + data->shifts[*idx_b].word_offset;
    
    return strcmp(start_a, start_b);
}

void step_alphabetize(shared_kwic_data_t *data, size_t *order) {
    for (size_t i = 0; i < data->shift_count; i++) {
        order[i] = i;
    }
    for (size_t i = 0; i < data->shift_count; i++) {
        for (size_t j = i + 1; j < data->shift_count; j++) {
            if (compare_shifts(&order[i], &order[j], data) > 0) {
                size_t tmp = order[i];
                order[i] = order[j];
                order[j] = tmp;
            }
        }
    }
}

/* Модуль 4: Вивід покажчика */
void step_output(const shared_kwic_data_t *data, const size_t *order) {
    for (size_t i = 0; i < data->shift_count; i++) {
        size_t s = order[i];
        size_t l = data->shifts[s].line_idx;
        size_t offset = data->shifts[s].word_offset;
        const char *line = &data->chars[data->line_starts[l]];
        
        printf("%s", line + offset);
        if (offset > 0) {
            printf(" / ");
            for (size_t k = 0; k < offset; k++) {
                putchar(line[k]);
            }
        }
        putchar('\n');
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>

/* СПІЛЬНА СТРУКТУРА: виставляє представлення масиву й зсувів */
struct SharedKwicData {
    std::string raw_chars;
    std::vector<size_t> line_offsets;
    
    struct ShiftEntry {
        size_t line_index;
        size_t char_offset_in_line;
    };
    std::vector<ShiftEntry> shifts;
};

/* Модуль 1: Ввід */
void step_input(SharedKwicData &data, const std::vector<std::string> &lines) {
    data.raw_chars.clear();
    data.line_offsets.clear();
    for (const auto &ln : lines) {
        data.line_offsets.push_back(data.raw_chars.size());
        data.raw_chars.append(ln);
        data.raw_chars.push_back('\0');
    }
}

/* Модуль 2: Циклічний зсув */
void step_circular_shift(SharedKwicData &data) {
    data.shifts.clear();
    for (size_t l = 0; l < data.line_offsets.size(); ++l) {
        const char *line = &data.raw_chars[data.line_offsets[l]];
        size_t offset = 0;
        bool in_word = false;
        
        while (line[offset] != '\0') {
            if (line[offset] != ' ' && !in_word) {
                in_word = true;
                data.shifts.push_back({l, offset});
            } else if (line[offset] == ' ') {
                in_word = false;
            }
            ++offset;
        }
    }
}

/* Модуль 3: Сортування */
std::vector<size_t> step_alphabetize(const SharedKwicData &data) {
    std::vector<size_t> order(data.shifts.size());
    for (size_t i = 0; i < order.size(); ++i) order[i] = i;
    
    std::sort(order.begin(), order.end(), [&](size_t a, size_t b) {
        const auto &sa = data.shifts[a];
        const auto &sb = data.shifts[b];
        const char *line_a = &data.raw_chars[data.line_offsets[sa.line_index]];
        const char *line_b = &data.raw_chars[data.line_offsets[sb.line_index]];
        std::string_view va(line_a + sa.char_offset_in_line);
        std::string_view vb(line_b + sb.char_offset_in_line);
        return va < vb;
    });
    return order;
}

/* Модуль 4: Вивід */
void step_output(const SharedKwicData &data, const std::vector<size_t> &order) {
    for (size_t idx : order) {
        const auto &s = data.shifts[idx];
        const char *line = &data.raw_chars[data.line_offsets[s.line_index]];
        std::string_view suffix(line + s.char_offset_in_line);
        std::cout << suffix;
        if (s.char_offset_in_line > 0) {
            std::string_view prefix(line, s.char_offset_in_line);
            std::cout << " / " << prefix;
        }
        std::cout << '\n';
    }
}
```
:::

У цій процедурній архітектурі кожен крок напряму залежить від внутрішнього влаштування даних. Модуль вводу записує нуль-термінатори у суцільний масив. Модуль зсувів шукає пробіли, скануючи цей самий масив. Модуль упорядкування викликає `strcmp`, передаючи вказівники у середину спільних буферів. Модуль виводу знає, як саме комбінувати суфікс і префікс рядка. 

Якщо одного дня виявиться, що обсяг тексту перевищує доступну оперативну пам'ять, і символи потрібно зберігати на диску у стиснутому вигляді, виявиться жахлива річ: у системі немає жодного файлу, який можна було б залишити без змін. Доведеться переписати всі чотири модулі, оскільки знання про суцільний буфер пам'яті просочилося у кожен алгоритм.

---

## Розклад за Парнасом: модулі як хранителі таємниць

У другому підході межі модулів проводяться не вздовж стрілок блок-схеми, а навколо конкретних проєктних рішень, що мають шанс змінитися у майбутньому.

Кожен модуль отримує єдину та чітко окреслену таємницю:
1. **Модуль збереження рядків (`LineStorage`)** — його таємницею є фізичний спосіб розміщення символів і рядків у пам'яті (суцільний масив, зв'язний список, сторінковий буфер або стиснутий потік). Назовні він надає лише абстрактний доступ: кількість рядків, довжина рядка та символ за координатами `(рядок, позиція)`.
2. **Модуль циклічних зсувів (`CircularShifts`)** — його таємницею є формула обчислення циклічного зсуву слів. Він не дублює рядки у пам'яті, а створює віртуальну проекцію, надаючи операцію `get_char(shift_idx, pos)`, яка прозоро транслює запит до `LineStorage`.
3. **Модуль упорядкування (`Alphabetizer`)** — його таємницею є конкретний алгоритм сортування (швидке сортування, злиття або сортування вибіркою) та таблиця перестановки індексів. Він порівнює зсуви виключно через інтерфейс `get_char`.
4. **Модуль виводу (`OutputFormatter`)** — його таємницею є формат презентації покажчика (текстовий термінал, JSON, веб-сторінка). Він не знає ні про масиви, ні про алгоритми сортування, отримуючи відсортовані символи через публічний контракт.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* =========================================================================
 * МОДУЛЬ 1: Сховище рядків.
 * ТАЄМНИЦЯ: як саме лежать байти в пам'яті.
 * ========================================================================= */
typedef struct line_storage line_storage_t;

struct line_storage {
    char   *buffer;
    size_t *line_offsets;
    size_t *line_lengths;
    size_t  line_count;
    size_t  capacity_bytes;
};

line_storage_t* line_storage_create(void) {
    line_storage_t *ls = (line_storage_t*)malloc(sizeof(line_storage_t));
    ls->capacity_bytes = 4096;
    ls->buffer = (char*)malloc(ls->capacity_bytes);
    ls->line_offsets = (size_t*)malloc(sizeof(size_t) * 128);
    ls->line_lengths = (size_t*)malloc(sizeof(size_t) * 128);
    ls->line_count = 0;
    return ls;
}

void line_storage_destroy(line_storage_t *ls) {
    if (!ls) return;
    free(ls->buffer);
    free(ls->line_offsets);
    free(ls->line_lengths);
    free(ls);
}

void line_storage_add_line(line_storage_t *ls, const char *line) {
    size_t len = strlen(line);
    size_t offset = (ls->line_count == 0) ? 0 : 
                    (ls->line_offsets[ls->line_count - 1] + ls->line_lengths[ls->line_count - 1]);
    
    memcpy(&ls->buffer[offset], line, len);
    ls->line_offsets[ls->line_count] = offset;
    ls->line_lengths[ls->line_count] = len;
    ls->line_count++;
}

size_t line_storage_line_count(const line_storage_t *ls) {
    return ls->line_count;
}

size_t line_storage_line_length(const line_storage_t *ls, size_t line_idx) {
    return ls->line_lengths[line_idx];
}

char line_storage_get_char(const line_storage_t *ls, size_t line_idx, size_t char_idx) {
    if (char_idx >= ls->line_lengths[line_idx]) return '\0';
    size_t offset = ls->line_offsets[line_idx] + char_idx;
    return ls->buffer[offset];
}

/* =========================================================================
 * МОДУЛЬ 2: Циклічні зсуви.
 * ТАЄМНИЦЯ: формула відображення зсунутого індексу на вихідний символ рядка.
 * ========================================================================= */
typedef struct {
    size_t line_idx;
    size_t start_word_char_idx;
} shift_item_t;

typedef struct {
    const line_storage_t *storage;
    shift_item_t         *shifts;
    size_t                shift_count;
} circular_shifts_t;

circular_shifts_t* circular_shifts_create(const line_storage_t *ls) {
    circular_shifts_t *cs = (circular_shifts_t*)malloc(sizeof(circular_shifts_t));
    cs->storage = ls;
    cs->shifts = (shift_item_t*)malloc(sizeof(shift_item_t) * 512);
    cs->shift_count = 0;
    
    size_t total_lines = line_storage_line_count(ls);
    for (size_t l = 0; l < total_lines; l++) {
        size_t len = line_storage_line_length(ls, l);
        bool in_word = false;
        for (size_t c = 0; c < len; c++) {
            char ch = line_storage_get_char(ls, l, c);
            if (ch != ' ' && !in_word) {
                in_word = true;
                cs->shifts[cs->shift_count].line_idx = l;
                cs->shifts[cs->shift_count].start_word_char_idx = c;
                cs->shift_count++;
            } else if (ch == ' ') {
                in_word = false;
            }
        }
    }
    return cs;
}

void circular_shifts_destroy(circular_shifts_t *cs) {
    if (!cs) return;
    free(cs->shifts);
    free(cs);
}

size_t circular_shifts_count(const circular_shifts_t *cs) {
    return cs->shift_count;
}

char circular_shifts_get_char(const circular_shifts_t *cs, size_t shift_idx, size_t pos) {
    size_t line_idx = cs->shifts[shift_idx].line_idx;
    size_t offset = cs->shifts[shift_idx].start_word_char_idx;
    size_t len = line_storage_line_length(cs->storage, line_idx);
    
    if (pos >= len) return '\0';
    size_t mapped_idx = (offset + pos) % (len + 1);
    if (mapped_idx == len) {
        return ' ';
    }
    return line_storage_get_char(cs->storage, line_idx, mapped_idx);
}

/* =========================================================================
 * МОДУЛЬ 3: Упорядкування.
 * ТАЄМНИЦЯ: алгоритм сортування та індекс перестановки.
 * ========================================================================= */
typedef struct {
    const circular_shifts_t *shifts;
    size_t                  *order;
    size_t                   count;
} alphabetizer_t;

static int shift_cmp(const circular_shifts_t *cs, size_t a, size_t b) {
    size_t pos = 0;
    while (true) {
        char ca = circular_shifts_get_char(cs, a, pos);
        char cb = circular_shifts_get_char(cs, b, pos);
        if (ca != cb) return (unsigned char)ca - (unsigned char)cb;
        if (ca == '\0') return 0;
        pos++;
    }
}

alphabetizer_t* alphabetizer_create(const circular_shifts_t *cs) {
    alphabetizer_t *az = (alphabetizer_t*)malloc(sizeof(alphabetizer_t));
    az->shifts = cs;
    az->count = circular_shifts_count(cs);
    az->order = (size_t*)malloc(sizeof(size_t) * az->count);
    
    for (size_t i = 0; i < az->count; i++) az->order[i] = i;
    
    for (size_t i = 0; i < az->count; i++) {
        for (size_t j = i + 1; j < az->count; j++) {
            if (shift_cmp(cs, az->order[i], az->order[j]) > 0) {
                size_t tmp = az->order[i];
                az->order[i] = az->order[j];
                az->order[j] = tmp;
            }
        }
    }
    return az;
}

void alphabetizer_destroy(alphabetizer_t *az) {
    if (!az) return;
    free(az->order);
    free(az);
}

size_t alphabetizer_get_sorted_shift_index(const alphabetizer_t *az, size_t pos) {
    return az->order[pos];
}

/* =========================================================================
 * МОДУЛЬ 4: Вивід покажчика.
 * ТАЄМНИЦЯ: формат оформлення.
 * ========================================================================= */
void output_print_all(const alphabetizer_t *az, const circular_shifts_t *cs) {
    size_t total = circular_shifts_count(cs);
    for (size_t i = 0; i < total; i++) {
        size_t shift_idx = alphabetizer_get_sorted_shift_index(az, i);
        size_t char_pos = 0;
        while (true) {
            char c = circular_shifts_get_char(cs, shift_idx, char_pos++);
            if (c == '\0') break;
            putchar(c);
        }
        putchar('\n');
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <algorithm>

/* МОДУЛЬ 1: Сховище рядків (Інкапсулює спосіб зберігання) */
class LineStorage {
public:
    void add_line(std::string_view line) {
        offsets_.push_back(buffer_.size());
        lengths_.push_back(line.size());
        buffer_.append(line);
    }

    [[nodiscard]] size_t line_count() const noexcept { return offsets_.size(); }
    [[nodiscard]] size_t line_length(size_t line_idx) const noexcept { return lengths_[line_idx]; }

    [[nodiscard]] char get_char(size_t line_idx, size_t char_idx) const noexcept {
        if (line_idx >= offsets_.size() || char_idx >= lengths_[line_idx]) return '\0';
        return buffer_[offsets_[line_idx] + char_idx];
    }

private:
    std::string buffer_;
    std::vector<size_t> offsets_;
    std::vector<size_t> lengths_;
};

/* МОДУЛЬ 2: Циклічні зсуви (Інкапсулює віртуальне зміщення слів) */
class CircularShifts {
public:
    explicit CircularShifts(const LineStorage &storage) : storage_(storage) {
        for (size_t l = 0; l < storage_.line_count(); ++l) {
            size_t len = storage_.line_length(l);
            bool in_word = false;
            for (size_t c = 0; c < len; ++c) {
                char ch = storage_.get_char(l, c);
                if (ch != ' ' && !in_word) {
                    in_word = true;
                    shifts_.push_back({l, c});
                } else if (ch == ' ') {
                    in_word = false;
                }
            }
        }
    }

    [[nodiscard]] size_t count() const noexcept { return shifts_.size(); }

    [[nodiscard]] char get_char(size_t shift_idx, size_t pos) const noexcept {
        const auto &s = shifts_[shift_idx];
        size_t len = storage_.line_length(s.line_index);
        if (pos >= len) return '\0';
        
        size_t mapped = (s.word_start_char + pos) % (len + 1);
        if (mapped == len) return ' ';
        return storage_.get_char(s.line_index, mapped);
    }

private:
    struct ShiftRef {
        size_t line_index;
        size_t word_start_char;
    };
    const LineStorage &storage_;
    std::vector<ShiftRef> shifts_;
};

/* МОДУЛЬ 3: Упорядкування (Інкапсулює алгоритм сортування) */
class Alphabetizer {
public:
    explicit Alphabetizer(const CircularShifts &shifts) : shifts_(shifts) {
        order_.resize(shifts_.count());
        for (size_t i = 0; i < order_.size(); ++i) order_[i] = i;

        std::sort(order_.begin(), order_.end(), [this](size_t a, size_t b) {
            size_t p = 0;
            while (true) {
                char ca = shifts_.get_char(a, p);
                char cb = shifts_.get_char(b, p);
                if (ca != cb) return ca < cb;
                if (ca == '\0') return false;
                ++p;
            }
        });
    }

    [[nodiscard]] size_t sorted_shift_index(size_t rank) const noexcept {
        return order_[rank];
    }

private:
    const CircularShifts &shifts_;
    std::vector<size_t> order_;
};

/* МОДУЛЬ 4: Вивід */
class OutputFormatter {
public:
    static void print(const Alphabetizer &alpha, const CircularShifts &shifts) {
        for (size_t i = 0; i < shifts.count(); ++i) {
            size_t s_idx = alpha.sorted_shift_index(i);
            size_t pos = 0;
            while (true) {
                char c = shifts.get_char(s_idx, pos++);
                if (c == '\0') break;
                std::cout << c;
            }
            std::cout << '\n';
        }
    }
};
```
:::

---

## Тест на стійкість: змінюємо таємницю

Перевіримо перевагу модульного розкладу за Парнасом практичним інженерним експериментом. Припустимо, що вхідний набір текстів зріс від кількох кілобайтів до гігабайтів, і ми більше не можемо дозволити собі тримати весь текст у суцільному буфері оперативної пам'яті. Тепер кожен рядок зберігається у власному динамічному блоці або підвантажується блоками зі стиснутого файлу.

Погляньмо, що відбувається з обома архітектурами при такій зміні вимог.

### Що ламається у процедурній системі
1. **Спільна структура даних:** Структура `shared_kwic_data_t` втрачає поле `char chars[MAX_CHARS]`. Замість нього з'являється динамічний список або таблиця дескрипторів рядків `char *lines[]`.
2. **Модуль вводу (`step_input`):** Повністю переписується, оскільки копіювання байтів у суцільний буфер більше не працює — тепер потрібно виділяти окремий блок пам'яті під кожен рядок.
3. **Модуль циклічного зсуву (`step_circular_shift`):** Ламається на рівні індексації, бо обчислення вказівника на символ `line_starts[l] + c` у суцільному масиві більше не має фізичного змісту.
4. **Модуль сортування (`step_alphabetize`):** Ламається функція порівняння `compare_shifts`, яка спиралася на пряму арифметику вказівників всередині глобального буфера.
5. **Модуль виводу (`step_output`):** Ламається логіка конкатенації суфікса й префікса, оскільки вона зверталася до байтів суцільного масиву за глобальними індексами.
6. **Радіус ураження:** 100% модулів системи вимагають ручних правок та повторного тестування.

### Що відбувається у системі за Парнасом
1. **Модуль сховища рядків (`line_storage`):** Ми змінюємо виключно внутрішнє тіло `line_storage.c` (або клас `LineStorage`). Замість єдиного буфера ми використовуємо вектор окремих рядків або зчитувач із файлу.
2. **Публічний контракт:** Функції `line_storage_get_char`, `line_storage_line_length` та `line_storage_line_count` зберігають свої точні сигнатури та поведінкові гарантії.
3. **Решта системи:** `circular_shifts.c`, `alphabetizer.c` та `output_formatter.c` **не змінюються взагалі**. Жоден рядок коду в цих файлах не редагується, і вони навіть не потребують перекомпіляції у разі використання динамічного зв'язування.
4. **Радіус ураження:** Рівно 1 модуль. Зміна надійно ізольована за інтерфейсним бар'єром.

---

## Інженерні компроміси та аналіз швидкодії

Хоча модульний розклад Парнаса забезпечує бездоганну змінюваність коду, він вносить компроміси щодо продуктивності, які інженер зобов'язаний розуміти:

1. **Накладні витрати на виклики функцій:** У процедурній версії сортувальник викликає `strcmp` безпосередньо над сирими байтами у пам'яті, що дає змогу процесору задіяти векторні інструкції (SIMD). У модульній версії посимвольне опитування через функцію `get_char` породжує мільйони викликів функцій, що може суттєво уповільнити сортування на великих обсягах даних.
2. **Як це вирішується у сучасному коді:** Замість наївного посимвольного доступу контракт модуля розширюють блоковими запитами (наприклад, `std::string_view` або функція `copy_word_to_buffer`), або застосовують міжмодульну оптимізацію на етапі компонування (LTO — англ. *Link-Time Optimization*), яка автоматично інлайнить прості геттери між різними одиницями трансляції.
3. **Керування життєвим циклом об'єктів:** Модуль `CircularShifts` тримає посилання на `LineStorage`. Якщо сховище буде знищене раніше, ніж зсуви, виникає звернення за мертвою адресою (англ. *dangling pointer / use-after-free*). Дисципліна приховування інформації вимагає чіткого документування життєвого циклу або використання RAII-обгорток (`std::shared_ptr`, `std::unique_ptr`).
