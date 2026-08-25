# Редактор у терміналі

<preknowlist>
- [TTY і termios](root:sys-unix/tty-and-termios) — лінійна дисципліна ядра, канонічний і небуферизований режими, прапорці введення й виведення.
- [Керуючі послідовності термінала](root:sys-unix/terminal-escape-sequences) — протокол керування дисплеєм: ESC [, позиціонування курсора, стирання рядків, кольори.
- [Ширина символу в комірках](root:sys-unix/wcwidth-and-cell-width) — відмінність між байтами, кодовими точками та шириною знака на сітці моноширинного термінала.
- [Стандартні потоки](root:sys-unix/standard-streams) — дескриптори `STDIN_FILENO` та `STDOUT_FILENO`, небуферизований ввід-вивід.
- [Сигнали](root:sys-unix/signal-model) — асинхронні повідомлення ядра, перехоплення `SIGWINCH` при зміні геометрії вікна.
- [ncurses](root:sys-unix/ncurses) — концепція віртуального екрана та порівняння буферів для мінімізації трафіку.
</preknowlist>

Коли стандартна консольна утиліта на кшталт `cat` або `grep` читає дані зі стандартного вводу, ядро операційної системи бере на себе всю попередню обробку: воно накопичує байти в буфері до натискання Enter, локально малює кожен введений символ назад на екран (echo), обробляє Backspace для стирання помилок і надсилає процесу сигнал `SIGINT` при натисканні комбінації Ctrl+C. Для утиліти командного рядка така поведінка зручна, але для повноекранного текстового редактора — такого як `vi`, `vim`, `nano`, `micro` чи мінімалістичного `kilo` — вона фатальна.

Повноекранному редактору потрібен безпосередній контроль над кожним натисканням клавіші в ту саму мить, коли палець торкається клавіатури. Якщо користувач натискає стрілку вправо або комбінацію Ctrl+S для збереження файлу, програма не може чекати на символ нового рядка, не повинна дозволяти ядру вбивати процес сигналом переривання і зобов'язана самостійно вирішувати, які саме пікселі чи символи мають змінитися на склі термінала.

Історичний шлях від простих рядкових інструментів до сучасних екранних редакторів показує еволюцію взаємодії людини з терміналом ([від ed до Vim](root:sys-unix/terminal-text-editor/hist-line-to-screen-editors.md) — народження модального режиму в `vi`, розробка Emacs та поява відкритих клонів).

![Порівняння канонічного та сирого режимів TTY](/root/sys/sys-unix/terminal-text-editor/img/raw-mode-termios.svg)

*Канонічний режим TTY приховує потік введення за буфером ядра, тоді як сирий режим передає кожен байт безпосередньо в Event Loop редактора.*

## Анатомія сирого режиму: маніпуляція термінальною лінією

За замовчуванням псевдотермінал або послідовна лінія функціонують у так званому **канонічному режимі** (Canonical Mode). Усередині ядра Linux цим керує драйвер лінійної дисципліни `N_TTY`. У ньому діють три базові правила: введення віддається процесу лише після надходження символу переведення рядка (`\n`), кожен введений символ негайно відсилається назад у вихідний потік термінала (локальне відлуння), а керуючі символи перехоплюються для генерації сигналів або редагування поточного рядка.

Щоб текстовий редактор міг працювати, термінальну лінію необхідно перевести в **сирий режим** (Raw Mode). Це здійснюється модифікацією структури `struct termios` через системні виклики `tcgetattr` та `tcsetattr`.

Повний перелік прапорців та їхніх бітових масок описано в довіднику інтерфейсу ([протокол керуючих послідовностей та прапорців termios](root:sys-unix/terminal-text-editor/api-editor-terminal-sequences.md) — системні структури `termios`, коди клавіш та інструкції ANSI).

Переведення вимагає скидання конкретних бітових масок у чотирьох полях конфігурації:

1. **Локальні прапорці (`c_lflag`):**
   - `ECHO` — вимикає локальне відлуння. Без цього кожне натискання клавіші одразу друкувалося б на екрані там, де стоїть фізичний курсор, руйнуючи інтерфейс редактора.
   - `ICANON` — вимикає канонічний режим. Виклик `read()` перестає чекати на Enter і повертає байти негайно, по мірі їх надходження від клавіатури.
   - `ISIG` — вимикає генерацію сигналів `SIGINT` (Ctrl+C), `SIGTSTP` (Ctrl+Z) та `SIGQUIT` (`Ctrl+\`). Тепер ці комбінації надходять у процес як звичайні числові байти (`0x03`, `0x1A`, `0x1C`), дозволяючи призначити їх на команди редактора (наприклад, скасування операції або вихід).
   - `IEXTEN` — вимикає розширену обробку вводу, зокрема спеціальну поведінку Ctrl+V (літеральне введення наступного символу) та Ctrl+O.

2. **Вхідні прапорці (`c_iflag`):**
   - `IXON` — вимикає програмне керування потоком даних XON/XOFF. За замовчуванням комбінація Ctrl+S призупиняє передачу даних на термінал до натискання Ctrl+Q. Вимкнення цього прапорця звільняє Ctrl+S для класичної операції збереження документа.
   - `ICRNL` — вимикає автоматичну трансляцію символу повернення каретки `\r` (ASCII 13) у новий рядок `\n` (ASCII 10). Після цього редактор отримує чистий байт `13` при натисканні Enter.
   - `BRKINT`, `INPCK`, `ISTRIP` — вимикають надсилання сигналу при розриві зв'язку (Break), апаратну перевірку парності та скидання восьмого біта байта. Скидання `ISTRIP` критично важливе для збереження всіх 8 бітів у кодуваннях UTF-8.

3. **Вихідні прапорці (`c_oflag`):**
   - `OPOST` — вимикає постобробку виведення. У канонічному режимі ядро автоматично додає повернення каретки `\r` до кожного байта `\n`. Після вимкнення `OPOST` передача `\n` переміщує курсор лише на один рядок вниз, залишаючи його в тій самій колонці. Редактор бере керування курсором на себе і для переходу на початок нового рядка зобов'язаний явно надсилати `\r\n`.

4. **Керуючі символи та таймаути (`c_cc`):**
   Масив `c_cc` містить два вирішальні параметри для регулювання поведінки блокування у виклику `read()`: `VMIN` та `VTIME`.
   - `c_cc[VMIN] = 0; c_cc[VTIME] = 1;` — налаштовує неблокуюче читання з таймаутом у 100 мілісекунд (1/10 секунди). Якщо протягом цього інтервалу користувач не натиснув жодної клавіші, `read()` повертає `0`. Це дозволяє циклу подій редактора періодично перевіряти фонові зміни або оновлювати статусний рядок без мертвого блокування процесу.

:::tabs
```c
#include <termios.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>

static struct termios orig_termios;

static void disable_raw_mode(void) {
    // TCSAFLUSH застосовує зміни після вичитування всіх переданих байтів
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios);
}

void enable_raw_mode(void) {
    if (tcgetattr(STDIN_FILENO, &orig_termios) == -1) {
        perror("tcgetattr");
        exit(EXIT_FAILURE);
    }
    // Відновлення термінала навіть при виклику exit()
    atexit(disable_raw_mode);

    struct termios raw = orig_termios;
    raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
    raw.c_oflag &= ~(OPOST);
    raw.c_cflag |= (CS8);
    raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
    raw.c_cc[VMIN] = 0;
    raw.c_cc[VTIME] = 1; // таймаут 100 мс

    if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) == -1) {
        perror("tcsetattr");
        exit(EXIT_FAILURE);
    }
}
```
```cpp
#include <termios.h>
#include <unistd.h>
#include <iostream>
#include <stdexcept>

class RawTerminalGuard {
public:
    RawTerminalGuard() {
        if (tcgetattr(STDIN_FILENO, &orig_termios_) == -1) {
            throw std::runtime_error("Помилка читання конфігурації TTY через tcgetattr");
        }

        struct termios raw = orig_termios_;
        raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
        raw.c_oflag &= ~(OPOST);
        raw.c_cflag |= (CS8);
        raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
        raw.c_cc[VMIN] = 0;
        raw.c_cc[VTIME] = 1;

        if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) == -1) {
            throw std::runtime_error("Помилка активації Raw Mode через tcsetattr");
        }
    }

    ~RawTerminalGuard() noexcept {
        tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios_);
    }

    RawTerminalGuard(const RawTerminalGuard&) = delete;
    RawTerminalGuard& operator=(const RawTerminalGuard&) = delete;

private:
    struct termios orig_termios_{};
};
```
:::

> 🔧 **Навіщо це.** Якщо програма впаде або завершиться без відновлення початкового стану `termios`, термінал залишиться в сирому режимі: введені користувачем команди шелу не відображатимуться на екрані, а натискання Enter не переводитиме рядок. Команда відновлення наосліп `stty sane` або `reset` скидає параметри термінальної лінії назад у робочий канонічний стан.

![Архітектура циклу обробки подій](/root/sys/sys-unix/terminal-text-editor/img/editor-event-loop.svg)

*Архітектура циклу подій редактора: байтовий потік перетворюється на команди, мутує стан тексту та візуалізується через подвійну буферизацію.*

## Цикл обробки подій та парсер Escape-послідовностей

Серцем будь-якого редактора є **цикл обробки подій** (Event Loop). Його структура складається з трьох послідовних кроків:
1. Очікування та зчитування чергового байта або послідовності з дескриптора `STDIN_FILENO`.
2. Тлумачення коду клавіші, розпізнавання керуючих послідовностей та передача керування диспетчеру дій.
3. Модифікація внутрішнього буфера документа та повне або диференційне перемальовування видимого вікна.

### Проблема клавіші Escape

У терміналі звичайні ASCII-символи з кодами від `32` до `126` представляють самі себе. Керуючі комбінації з модифікатором `Ctrl` відображаються на перші 26 кодів таблиці ASCII: натискання `Ctrl+A` надсилає байт `1` (`'a' & 0x1f`), `Ctrl+B` — байт `2`, і так далі.

Головна складність виникає з навігаційними та функціональними клавішами (стрілки, PageUp, PageDown, Home, End, Delete, F1–F12). Термінал не має для них окремих апаратних кодів у таблиці ASCII. Натомість він передає їх як багатобайтові послідовності, що починаються з байта `ESC` (`0x1B` або 27 у десятковій системі), за яким слідує префікс CSI (Control Sequence Introducer, зазвичай символ `[`):
- Стрілка вгору: `\x1b[A` (три байти: `0x1B`, `0x5B`, `0x41`)
- Стрілка вниз: `\x1b[B`
- Стрілка вправо: `\x1b[C`
- Стрілка вліво: `\x1b[D`
- Page Up: `\x1b[5~` (чотири байти: `0x1B`, `0x5B`, `0x35`, `0x7E`)
- Delete: `\x1b[3~`

Звідси виникає неоднозначність: коли системний виклик `read()` повертає байт `\x1b`, програма не знає наперед, чи користувач натиснув одиночну клавішу `Escape` (наприклад, щоб вийти з режиму вставки у `vi`), чи це перший байт трибайтової послідовності натискання стрілки.

Розв'язання полягає в таймаутному дочитуванні наступних байтів. Якщо після отримання `\x1b` наступні виклики `read()` із коротким інтервалом очікування не повертають нових даних, вважається, що було натиснуто окрему клавішу `Escape`. Якщо ж у буфері негайно з'являється `[` або `O`, запускається скінченний автомат розбору CSI-послідовності.

:::tabs
```c
enum EditorKey {
    KEY_ARROW_LEFT = 1000,
    KEY_ARROW_RIGHT,
    KEY_ARROW_UP,
    KEY_ARROW_DOWN,
    KEY_DEL,
    KEY_HOME,
    KEY_END,
    KEY_PAGE_UP,
    KEY_PAGE_DOWN
};

int editor_read_key(void) {
    int nread;
    char c;
    while ((nread = read(STDIN_FILENO, &c, 1)) != 1) {
        if (nread == -1 && errno != EAGAIN && errno != EINTR) {
            perror("read");
            exit(EXIT_FAILURE);
        }
    }

    if (c == '\x1b') {
        char seq[3];
        // Якщо протягом таймауту наступний байт не надійшов — це одиночний Escape
        if (read(STDIN_FILENO, &seq[0], 1) != 1) return '\x1b';
        if (read(STDIN_FILENO, &seq[1], 1) != 1) return '\x1b';

        if (seq[0] == '[') {
            if (seq[1] >= '0' && seq[1] <= '9') {
                if (read(STDIN_FILENO, &seq[2], 1) != 1) return '\x1b';
                if (seq[2] == '~') {
                    switch (seq[1]) {
                        case '1': return KEY_HOME;
                        case '3': return KEY_DEL;
                        case '4': return KEY_END;
                        case '5': return KEY_PAGE_UP;
                        case '6': return KEY_PAGE_DOWN;
                        case '7': return KEY_HOME;
                        case '8': return KEY_END;
                    }
                }
            } else {
                switch (seq[1]) {
                    case 'A': return KEY_ARROW_UP;
                    case 'B': return KEY_ARROW_DOWN;
                    case 'C': return KEY_ARROW_RIGHT;
                    case 'D': return KEY_ARROW_LEFT;
                    case 'H': return KEY_HOME;
                    case 'F': return KEY_END;
                }
            }
        } else if (seq[0] == 'O') {
            switch (seq[1]) {
                case 'H': return KEY_HOME;
                case 'F': return KEY_END;
            }
        }
        return '\x1b';
    }
    return (unsigned char)c;
}
```
```cpp
#include <unistd.h>
#include <cerrno>
#include <optional>
#include <stdexcept>

enum class KeyCode : int {
    ArrowLeft = 1000,
    ArrowRight,
    ArrowUp,
    ArrowDown,
    Delete,
    Home,
    End,
    PageUp,
    PageDown,
    Escape = 27
};

class KeyDecoder {
public:
    static int read_key() {
        char c{0};
        while (true) {
            const ssize_t bytes_read = ::read(STDIN_FILENO, &c, 1);
            if (bytes_read == 1) break;
            if (bytes_read == -1 && errno != EAGAIN && errno != EINTR) {
                throw std::runtime_error("Помилка читання дескриптора STDIN_FILENO");
            }
        }

        if (c != '\x1b') {
            return static_cast<unsigned char>(c);
        }

        char seq[3]{};
        if (::read(STDIN_FILENO, &seq[0], 1) != 1) return static_cast<int>(KeyCode::Escape);
        if (::read(STDIN_FILENO, &seq[1], 1) != 1) return static_cast<int>(KeyCode::Escape);

        if (seq[0] == '[') {
            if (seq[1] >= '0' && seq[1] <= '9') {
                if (::read(STDIN_FILENO, &seq[2], 1) != 1) return static_cast<int>(KeyCode::Escape);
                if (seq[2] == '~') {
                    switch (seq[1]) {
                        case '1': return static_cast<int>(KeyCode::Home);
                        case '3': return static_cast<int>(KeyCode::Delete);
                        case '4': return static_cast<int>(KeyCode::End);
                        case '5': return static_cast<int>(KeyCode::PageUp);
                        case '6': return static_cast<int>(KeyCode::PageDown);
                        case '7': return static_cast<int>(KeyCode::Home);
                        case '8': return static_cast<int>(KeyCode::End);
                        default: break;
                    }
                }
            } else {
                switch (seq[1]) {
                    case 'A': return static_cast<int>(KeyCode::ArrowUp);
                    case 'B': return static_cast<int>(KeyCode::ArrowDown);
                    case 'C': return static_cast<int>(KeyCode::ArrowRight);
                    case 'D': return static_cast<int>(KeyCode::ArrowLeft);
                    case 'H': return static_cast<int>(KeyCode::Home);
                    case 'F': return static_cast<int>(KeyCode::End);
                    default: break;
                }
            }
        } else if (seq[0] == 'O') {
            switch (seq[1]) {
                case 'H': return static_cast<int>(KeyCode::Home);
                case 'F': return static_cast<int>(KeyCode::End);
                default: break;
            }
        }
        return static_cast<int>(KeyCode::Escape);
    }
};
```
:::

![Структури даних для буферів тексту](/root/sys/sys-unix/terminal-text-editor/img/text-buffer-structures.svg)

*Порівняння чотирьох фундаментальних моделей організації тексту: від простого масиву рядків до Gap Buffer, Piece Table та збалансованого дерева Rope.*

## Структури даних для зберігання та редагування тексту

Спосіб представлення тексту в оперативній пам'яті визначає продуктивність вставки символів, споживання пам'яті, швидкість прокрутки та простоту реалізації операцій скасування змін (Undo/Redo).

### 1. Простий масив рядків (Array of Lines)

Найбільш прямолінійна модель: документ зберігається як динамічний масив покажчиків на рядки (наприклад, `std::vector<std::string>` або `char**`).
- **Переваги:** доступ до довільного рядка за номером коштує `O(1)`, відображення на екран тривіальне.
- **Недоліки:** вставка символу всередину довгого рядка вимагає зсуву пам'яті та `realloc` за час `O(L)`, де `L` — довжина рядка. Вставка нового рядка посеред файлу вимагає зсуву масиву покажчиків за час `O(N)`, де `N` — кількість рядків у документі.
- **Застосування:** навчальні та компактні редактори (Kilo, Micro, Nano).

### 2. Буфер з проміжком (Gap Buffer)

Текст зберігається в одному суцільному блоці пам'яті, всередині якого розміщено штучний вільний простір («проміжок», Gap). Початок проміжку завжди синхронізований із поточною позицією курсора редагування.
- **Вставка символу:** символ просто записується в першу позицію проміжку, початок проміжку зсувається на 1 праворуч, а його розмір зменшується. Це операція `O(1)`.
- **Видалення символу (Backspace):** розмір проміжку збільшується на 1 ліворуч — також `O(1)`.
- **Переміщення курсора:** якщо курсор рухається в інше місце документа, текст між старою і новою позиціями копіюється через проміжок за допомогою `memmove` (`O(K)`, де `K` — дистанція переміщення). Оскільки користувач зазвичай друкує багато символів підряд в одному місці, накладні витрати на переміщення проміжку амортизуються.
- **Переповнення:** коли розмір проміжку досягає нуля, виділяється новий більший буфер і проміжок розширюється.
- **Застосування:** Emacs.

:::tabs
```c
#include <stdlib.h>
#include <string.h>

struct GapBuffer {
    char *buffer;
    size_t capacity;
    size_t gap_start;
    size_t gap_end;
};

void gap_init(struct GapBuffer *gb, size_t initial_cap) {
    gb->capacity = initial_cap ? initial_cap : 64;
    gb->buffer = malloc(gb->capacity);
    gb->gap_start = 0;
    gb->gap_end = gb->capacity;
}

void gap_insert_char(struct GapBuffer *gb, char c) {
    if (gb->gap_start == gb->gap_end) {
        // Розширення проміжку при вичерпанні вільного місця
        size_t new_cap = gb->capacity * 2;
        char *new_buf = malloc(new_cap);
        size_t post_gap_len = gb->capacity - gb->gap_end;
        size_t new_gap_end = new_cap - post_gap_len;

        memcpy(new_buf, gb->buffer, gb->gap_start);
        memcpy(new_buf + new_gap_end, gb->buffer + gb->gap_end, post_gap_len);

        free(gb->buffer);
        gb->buffer = new_buf;
        gb->gap_end = new_gap_end;
        gb->capacity = new_cap;
    }
    gb->buffer[gb->gap_start++] = c;
}

void gap_move_cursor(struct GapBuffer *gb, size_t new_pos) {
    if (new_pos < gb->gap_start) {
        size_t delta = gb->gap_start - new_pos;
        memmove(gb->buffer + gb->gap_end - delta, gb->buffer + new_pos, delta);
        gb->gap_start -= delta;
        gb->gap_end -= delta;
    } else if (new_pos > gb->gap_start) {
        size_t delta = new_pos - gb->gap_start;
        memmove(gb->buffer + gb->gap_start, gb->buffer + gb->gap_end, delta);
        gb->gap_start += delta;
        gb->gap_end += delta;
    }
}
```
```cpp
#include <vector>
#include <string>
#include <algorithm>
#include <cstring>

class GapBuffer {
public:
    explicit GapBuffer(size_t initial_capacity = 64)
        : buffer_(std::max<size_t>(initial_capacity, 16)),
          gap_start_(0),
          gap_end_(buffer_.size()) {}

    void insert(char c) {
        if (gap_start_ == gap_end_) {
            grow();
        }
        buffer_[gap_start_++] = c;
    }

    void move_cursor(size_t new_pos) {
        if (new_pos < gap_start_) {
            const size_t delta = gap_start_ - new_pos;
            std::memmove(&buffer_[gap_end_ - delta], &buffer_[new_pos], delta);
            gap_start_ -= delta;
            gap_end_ -= delta;
        } else if (new_pos > gap_start_) {
            const size_t delta = new_pos - gap_start_;
            std::memmove(&buffer_[gap_start_], &buffer_[gap_end_], delta);
            gap_start_ += delta;
            gap_end_ += delta;
        }
    }

    [[nodiscard]] size_t size() const noexcept {
        return buffer_.size() - (gap_end_ - gap_start_);
    }

private:
    std::vector<char> buffer_;
    size_t gap_start_;
    size_t gap_end_;

    void grow() {
        const size_t old_cap = buffer_.size();
        const size_t new_cap = old_cap * 2;
        const size_t post_gap_len = old_cap - gap_end_;
        const size_t new_gap_end = new_cap - post_gap_len;

        std::vector<char> new_buffer(new_cap);
        std::memcpy(new_buffer.data(), buffer_.data(), gap_start_);
        std::memcpy(new_buffer.data() + new_gap_end, buffer_.data() + gap_end_, post_gap_len);

        buffer_ = std::move(new_buffer);
        gap_end_ = new_gap_end;
    }
};
```
:::

### 3. Таблиця фрагментів (Piece Table)

Текст розділяється на два незмінних (immutable) буфери:
- **Original Buffer:** файл, завантажений з диска (часто через `mmap` у режимі read-only). Цей буфер ніколи не змінюється.
- **Append Buffer:** буфер, куди послідовно дописуються всі нові символи, введені користувачем.

Сам документ представляє собою список або дерево дескрипторів (Pieces). Кожен дескриптор містить три поля: посилання на буфер (Original або Append), початкове зміщення в цьому буфері та довжину фрагмента. Вставка тексту розбиває один дескриптор на два і вставляє між ними новий фрагмент, що вказує на щойно додані байти в Append Buffer.
- **Головна перевага:** миттєве завантаження файлів будь-якого розміру без копіювання, мінімальні витрати пам'яті при редагуванні та природна підтримка нескінченної історії скасувань (Undo/Redo): стан документа — це просто знімок списку дескрипторів.
- **Застосування:** AbiWord, Visual Studio Code, сучасні рушії редагування.

### 4. Мотузка (Rope)

Збалансоване двійкове дерево (на основі AVL або B-дерева), листками якого є короткі незмінні рядки тексту. Кожен внутрішній вузол зберігає вагу — сумарну довжину символів у його лівому піддереві.
- **Операції:** вставка та видалення зводяться до розщеплення (split) та злиття (concat) дерев за час `O(log N)`. Ідеально підходить для паралельної обробки великих файлів (гігабайти тексту) та асинхронного синтаксичного аналізу.
- **Застосування:** Kakoune, Xi-editor, Helix.

### Порівняння складності операцій

| Структура даних | Вставка в курсор | Видалення | Довільний доступ | Масштабування на 1 ГБ | Реалізація Undo/Redo |
|---|---|---|---|---|---|
| **Масив рядків** | `O(L)` (зсув рядка) | `O(L)` | `O(1)` за номером рядка | Погане (копіювання масиву) | Повна копія рядка/буфера |
| **Gap Buffer** | `O(1)` (амортизовано) | `O(1)` | `O(1)` з поправкою на Gap | Середнє (єдиний буфер) | Збереження дельт змін |
| **Piece Table** | `O(log P)` (P — фрагменти) | `O(log P)` | `O(log P)` | Ідеальне (`mmap` без копіювання) | Тривіальне (знімок списку Piece) |
| **Rope (Дерево)** | `O(log N)` | `O(log N)` | `O(log N)` | Відмінне | Знімки кореневих вузлів дерева |

![Відображення буфера на фізичний екран через Viewport](/root/sys/sys-unix/terminal-text-editor/img/screen-render-viewport.svg)

*Проєкція буфера тексту на фізичний екран: зміщення рядків і стовпчиків формують видимий зріз документа за один системний виклик write().*

## Оптимізований рендеринг: подвійна буферизація та синхронізація

Найбільш поширена помилка при самостійній розробці екранних програм — пряме надсилання кожного символу або керуючої команди у вихідний потік термінала через окремі виклики `printf()` або `write()`.

Такий підхід породжує дві критичні проблеми:
1. **Мерехтіння екрана (Flicker):** емулятор термінала встигає відмалювати проміжний стан екрана (наприклад, порожнє поле після команди очищення `\x1b[2J`), перш ніж програма надішле оновлений текст. Око сприймає це як неприємне стробоскопічне блимання.
2. **Накладні витрати на системні виклики:** кожен окремий виклик `write()` вимагає перемикання контексту між простором користувача та ядром (User Space ↔ Kernel Space). Виведення кадру з 2000 комірок поодинці сповільнює рендеринг у сотні разів.

### Подвійна буферизація в пам'яті

Щоб рендеринг був миттєвим і плавним, редактор застосовує подвійну буферизацію: весь кадр екрана разом із керуючими послідовностями збирається в оперативній пам'яті в єдиний динамічний акумулюючий буфер (Append Buffer / `abuf`). Коли кадр повністю сформовано, він надсилається в термінал **рівно одним системним викликом `write(STDOUT_FILENO, buf, len)`**.

Схема формування кадру включає п'ять обов'язкових кроків:
1. **Приховати курсор (`\x1b[?25l`):** поки малюються рядки, курсор не повинен хаотично стрибати по екрану.
2. **Перемістити курсор у початок (`\x1b[H`):** замість повільного і мерехтливого очищення всього екрана `\x1b[2J`, редактор просто повертає курсор у позицію `(1, 1)` і переписує наявний текст новим.
3. **Відобразити видимі рядки з очищенням залишків (`\x1b[K`):** після виведення кожного рядка тексту надсилається команда `\x1b[K` (*Erase in Line*), яка стирає старі символи від кінця нового рядка до правого краю вікна. Це усуває сміття від попереднього кадру без очищення всього екрана.
4. **Позиціонувати курсор (`\x1b[row;colH`):** обчислити екранні координати курсора з урахуванням прокрутки (Viewport) і встановити його у відповідну клітинку.
5. **Показати курсор (`\x1b[?25h`):** відновити видимість курсора після завершення збирання кадру.

Практичну роботу цієї моделі можна перевірити на компактному прикладі повного циклу редактора ([реалізація мінімального рушія термінального редактора](root:sys-unix/terminal-text-editor/proj-terminal-raw-editor.md) — робочий код на C та C++ з альтернативним екраном і подвійною буферизацією).

### Робота з альтернативним екраном (Alternate Screen Buffer)

Професійний редактор не повинен затирати історію команд шелу, з якого його запустили. Термінали стандарту ANSI/xterm підтримують два окремих екранних буфери: основний та альтернативний.
- Вхід у редактор: надсилання послідовності `\x1b[?1049h` перемикає термінал на чистий альтернативний буфер.
- Вихід із редактора: надсилання послідовності `\x1b[?1049l` повертає користувача в основний буфер, миттєво відновлюючи попередній вигляд командного рядка зі збереженням усієї історії прокрутки.

## Обробка системних подій і динамічна перебудова (SIGWINCH)

Геометрія термінала не є статичною: користувач може будь-якої миті змінити розмір вікна емулятора мишею або розбити екран у мультиплексорі `tmux`.

Коли розмір вікна змінюється, ядро операційної системи надсилає процесу, що володіє терміналом, асинхронний сигнал **`SIGWINCH`** (*Window Change*).

### Отримання актуального розміру через ioctl

Для отримання поточної кількості рядків і колонок використовується системний виклик `ioctl` із командою `TIOCGWINSZ` (Terminal I/O Control Get Window Size):

:::tabs
```c
#include <sys/ioctl.h>
#include <unistd.h>

int get_window_size(int *rows, int *cols) {
    struct winsize ws;
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == -1 || ws.ws_col == 0) {
        return -1;
    }
    *cols = ws.ws_col;
    *rows = ws.ws_row;
    return 0;
}
```
```cpp
#include <sys/ioctl.h>
#include <unistd.h>
#include <optional>

struct WindowDimensions {
    int rows{0};
    int cols{0};
};

std::optional<WindowDimensions> get_window_size() noexcept {
    struct winsize ws{};
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == -1 || ws.ws_col == 0) {
        return std::nullopt;
    }
    return WindowDimensions{.rows = ws.ws_row, .cols = ws.ws_col};
}
```
:::

### Запасний спосіб через Cursor Position Report

На рідкісних або вбудованих термінальних лініях виклик `ioctl(TIOCGWINSZ)` може повернути помилку або нульовий розмір. У такому випадку редактор застосовує обхідний маневр:
1. Переміщує курсор у крайній правий нижній кут завідомо великими координатами: `\x1b[999C\x1b[999B` (999 позицій вправо і 999 позицій вниз). Термінал затисне координати на своєму реальному максимумі.
2. Надсилає запит звіту про позицію курсора: `\x1b[6n` (*Device Status Report / CPR*).
3. Зчитує з дескриптора `STDIN_FILENO` відповідь термінала у форматі `\x1b[<rows>;<cols>R` і парсить фактичні розміри вікна за допомогою `sscanf`.

### Безпечна модель обробки сигналів

Обробник сигналу `SIGWINCH` виконується асинхронно в контексті переривання, тому всередині нього заборонено викликати небезпечні функції (`malloc`, `printf`, важкий рендеринг). Правильний патерн проектування полягає у виставленні атомарного прапорця:

:::tabs
```c
#include <signal.h>

static volatile sig_atomic_t resize_pending = 0;

static void handle_sigwinch(int sig) {
    (void)sig;
    resize_pending = 1;
}

// В основному циклі Event Loop:
void check_and_apply_resize(void) {
    if (resize_pending) {
        resize_pending = 0;
        get_window_size(&E.screen_rows, &E.screen_cols);
        editor_refresh_screen();
    }
}
```
```cpp
#include <csignal>
#include <atomic>

class WindowResizeManager {
public:
    static void init() {
        struct sigaction sa{};
        sa.sa_handler = &WindowResizeManager::signal_handler;
        sigemptyset(&sa.sa_mask);
        sa.sa_flags = SA_RESTART;
        sigaction(SIGWINCH, &sa, nullptr);
    }

    [[nodiscard]] static bool is_resize_requested() noexcept {
        return resize_pending_.exchange(false, std::memory_order_relaxed);
    }

private:
    static inline std::atomic<bool> resize_pending_{false};

    static void signal_handler(int) noexcept {
        resize_pending_.store(true, std::memory_order_relaxed);
    }
};
```
:::

Коли в основному циклі виявляється піднятий прапорець `resize_pending`, редактор оновлює розміри в'юпорту, коригує діапазон прокрутки (`row_offset`, `col_offset`) під новий розмір матриці та виконує повне перемальовування екрана. Текстовий редактор плавно адаптується до нових меж вікна без втрати курсора та пошкодження буферів.
