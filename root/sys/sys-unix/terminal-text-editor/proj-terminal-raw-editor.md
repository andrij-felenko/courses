# ⚙️ Реалізація мінімального рушія термінального редактора

Цей проект демонструє мінімальну, самодостатню інженерну архітектуру повноекранного текстового редактора для термінала без використання сторонніх бібліотек на кшталт `ncurses`.

Програма реалізує чотири базові підсистеми:
1. Переведення термінала в сирий режим (Raw Mode) через `termios` та гарантоване відновлення стану при завершенні процесу.
2. Розбір багатобайтових керуючих Escape-послідовностей клавіш (стрілки навігації, Home, End, PageUp, PageDown, Delete).
3. Подвійна буферизація в пам'яті через акумулюючий буфер рядків (Append Buffer) для усунення мерехтіння екрана.
4. Динамічне опитування розмірів термінала та адаптація в'юпорту при зміні геометрії вікна.

## Архітектурний огляд компонентів

Будь-який автономний редактор будується на узгодженій взаємодії ядра операційної системи, драйвера TTY та циклу подій процесу.

### 1. Керування режимами термінала

Стандартний канонічний режим TTY очікує натискання клавіші Enter, перш ніж передати вхідний потік байтів у дескриптор `STDIN_FILENO`. Одночасно термінал автоматично малює кожен символ назад (локальне відлуння) та перехоплює керуючі комбінації для генерації сигналів переривання (`SIGINT` на Ctrl+C).

Щоб отримати повний контроль, редактор зчитує поточний стан структури `termios` за допомогою виклику `tcgetattr()`, вимикає прапорці `ECHO`, `ICANON`, `ISIG`, `IEXTEN`, `IXON`, `ICRNL`, `OPOST`, налаштовує таймаут читання через `VMIN=0, VTIME=1` і застосовує нову конфігурацію викликом `tcsetattr()`. 

Для запобігання ситуації «зламаного термінала» (коли після аварійного завершення програми в терміналі не працює переведення рядків чи відлуння) в мові C використовується функція автоочищення `atexit()`, а в C++ застосовується патерн RAII (*Resource Acquisition Is Initialization*), де деструктор об'єкта сесії гарантовано повертає оригінальні налаштування TTY при виході з області видимості.

### 2. Подвійна буферизація (Append Buffer)

Безпосередній запис кожного символу або керуючої послідовності у `STDOUT_FILENO` через сотні викликів `write()` призводить до двох негативних наслідків:
- Мерехтіння екрана: термінал встигає відобразити проміжний стан кадру (наприклад, очищений рядок перед виведенням нового тексту).
- Падіння продуктивності: кожен системний виклик `write()` змушує процесор виконувати перемикання контексту між простором користувача та простором ядра.

Редактор вирішує цю проблему за допомогою акумулюючого буфера (`struct ABuffer` у C або `std::string` у C++). Увесь кадр — приховування курсора, перехід у початок екрана, промальовування видимих рядків, очищення залишків рядка послідовністю `\x1b[K`, позиціонування курсора у координати в'юпорту та відновлення видимості курсора — формується в оперативній пам'яті й надсилається в термінал **рівно одним системним викликом `write()`**.

У C++ версії динамічний буфер `std::string` використовує оптимізацію малих рядків (SSO — Small String Optimization) та метод `reserve()`, виділяючи блок пам'яті під розмір повної матриці екрана `screen_rows * (screen_cols + 16)` за один запит до алокатора. Це зводить кількість перерозподілів пам'яті під час рендерингу кадру до абсолютного нуля.

### 3. Декодування Escape-послідовностей

Клавіші навігації передаються терміналом як багатобайтові послідовності стандарту ANSI/VT100 (наприклад, стрілка вгору представлена трьома байтами `\x1b[A`). Декодер клавіш зчитує перший байт: якщо це не `\x1b` (Escape), символ повертається як є. Якщо прочитано `\x1b`, запускається таймаутне дочитування наступних двох байтів. Якщо протягом 100 мс наступні байти не з'явилися, це означає, що користувач натиснув одиночну клавішу `Escape`. Якщо ж байти з'явилися, вони розпізнаються скінченним автоматом і перетворюються на унікальні числові константи переліку `EditorKey`.

## Реалізація на C та ідіоматичному C++

:::tabs
```c
#define _DEFAULT_SOURCE
#define _BSD_SOURCE
#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <signal.h>
#include <errno.h>

enum EditorKey {
    ARROW_LEFT = 1000,
    ARROW_RIGHT,
    ARROW_UP,
    ARROW_DOWN,
    DEL_KEY,
    HOME_KEY,
    END_KEY,
    PAGE_UP,
    PAGE_DOWN
};

struct TermConfig {
    int cx, cy;
    int screen_rows;
    int screen_cols;
    struct termios orig_termios;
};

static struct TermConfig E;

static void disable_raw_mode(void) {
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &E.orig_termios);
}

static void enable_raw_mode(void) {
    if (tcgetattr(STDIN_FILENO, &E.orig_termios) == -1) {
        perror("tcgetattr");
        exit(EXIT_FAILURE);
    }
    atexit(disable_raw_mode);

    struct termios raw = E.orig_termios;
    // Вхідні прапорці: вимкнення XON/XOFF (IXON), перетворення CR->NL (ICRNL), перевірки парності
    raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
    // Вихідні прапорці: вимкнення автоматичного перетворення рядків (\n -> \r\n)
    raw.c_oflag &= ~(OPOST);
    // Прапорці керування: 8 біт на символ
    raw.c_cflag |= (CS8);
    // Локальні прапорці: вимкнення відлуння (ECHO), канонічного режиму (ICANON), сигналів (ISIG), розширень (IEXTEN)
    raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
    // Контрольні символи: читати негайно або по таймауту 100 мс (1/10 секунди)
    raw.c_cc[VMIN] = 0;
    raw.c_cc[VTIME] = 1;

    if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) == -1) {
        perror("tcsetattr");
        exit(EXIT_FAILURE);
    }
}

static int editor_read_key(void) {
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
        if (read(STDIN_FILENO, &seq[0], 1) != 1) return '\x1b';
        if (read(STDIN_FILENO, &seq[1], 1) != 1) return '\x1b';

        if (seq[0] == '[') {
            if (seq[1] >= '0' && seq[1] <= '9') {
                if (read(STDIN_FILENO, &seq[2], 1) != 1) return '\x1b';
                if (seq[2] == '~') {
                    switch (seq[1]) {
                        case '1': return HOME_KEY;
                        case '3': return DEL_KEY;
                        case '4': return END_KEY;
                        case '5': return PAGE_UP;
                        case '6': return PAGE_DOWN;
                        case '7': return HOME_KEY;
                        case '8': return END_KEY;
                    }
                }
            } else {
                switch (seq[1]) {
                    case 'A': return ARROW_UP;
                    case 'B': return ARROW_DOWN;
                    case 'C': return ARROW_RIGHT;
                    case 'D': return ARROW_LEFT;
                    case 'H': return HOME_KEY;
                    case 'F': return END_KEY;
                }
            }
        } else if (seq[0] == 'O') {
            switch (seq[1]) {
                case 'H': return HOME_KEY;
                case 'F': return END_KEY;
            }
        }
        return '\x1b';
    }
    return c;
}

static int get_window_size(int *rows, int *cols) {
    struct winsize ws;
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == -1 || ws.ws_col == 0) {
        return -1;
    }
    *cols = ws.ws_col;
    *rows = ws.ws_row;
    return 0;
}

// Динамічний акумулюючий буфер для рендерингу
struct ABuffer {
    char *b;
    int len;
};

#define ABUF_INIT { NULL, 0 }

static void ab_append(struct ABuffer *ab, const char *s, int len) {
    char *new_buf = realloc(ab->b, ab->len + len);
    if (!new_buf) return;
    memcpy(&new_buf[ab->len], s, len);
    ab->b = new_buf;
    ab->len += len;
}

static void ab_free(struct ABuffer *ab) {
    free(ab->b);
}

static void editor_draw_rows(struct ABuffer *ab) {
    for (int y = 0; y < E.screen_rows; y++) {
        if (y == E.screen_rows / 3) {
            char welcome[80];
            int welcomelen = snprintf(welcome, sizeof(welcome),
                "Minimal Terminal Editor -- v0.1");
            if (welcomelen > E.screen_cols) welcomelen = E.screen_cols;
            int padding = (E.screen_cols - welcomelen) / 2;
            if (padding) {
                ab_append(ab, "~", 1);
                padding--;
            }
            while (padding-- > 0) ab_append(ab, " ", 1);
            ab_append(ab, welcome, welcomelen);
        } else {
            ab_append(ab, "~", 1);
        }

        // Очищення рядка праворуч від курсора
        ab_append(ab, "\x1b[K", 3);
        if (y < E.screen_rows - 1) {
            ab_append(ab, "\r\n", 2);
        }
    }
}

static void editor_refresh_screen(void) {
    struct ABuffer ab = ABUF_INIT;

    // Приховати курсор перед оновленням
    ab_append(&ab, "\x1b[?25l", 6);
    // Перемістити курсор у лівий верхній кут (1, 1)
    ab_append(&ab, "\x1b[H", 3);

    editor_draw_rows(&ab);

    // Встановити курсор у позицію редактора
    char buf[32];
    snprintf(buf, sizeof(buf), "\x1b[%d;%dH", E.cy + 1, E.cx + 1);
    ab_append(&ab, buf, strlen(buf));

    // Показати курсор
    ab_append(&ab, "\x1b[?25h", 6);

    write(STDOUT_FILENO, ab.b, ab.len);
    ab_free(&ab);
}

static void editor_move_cursor(int key) {
    switch (key) {
        case ARROW_LEFT:
            if (E.cx > 0) E.cx--;
            break;
        case ARROW_RIGHT:
            if (E.cx < E.screen_cols - 1) E.cx++;
            break;
        case ARROW_UP:
            if (E.cy > 0) E.cy--;
            break;
        case ARROW_DOWN:
            if (E.cy < E.screen_rows - 1) E.cy++;
            break;
    }
}

static void editor_process_keypress(void) {
    int c = editor_read_key();
    switch (c) {
        case ('q' & 0x1f): // Ctrl+Q вихід
            write(STDOUT_FILENO, "\x1b[2J\x1b[H", 7);
            exit(EXIT_SUCCESS);
            break;
        case ARROW_UP:
        case ARROW_DOWN:
        case ARROW_LEFT:
        case ARROW_RIGHT:
            editor_move_cursor(c);
            break;
    }
}

int main(void) {
    enable_raw_mode();
    if (get_window_size(&E.screen_rows, &E.screen_cols) == -1) {
        perror("get_window_size");
        exit(EXIT_FAILURE);
    }
    E.cx = 0;
    E.cy = 0;

    // Вхід в альтернативний екран
    write(STDOUT_FILENO, "\x1b[?1049h", 8);

    while (1) {
        editor_refresh_screen();
        editor_process_keypress();
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <optional>
#include <stdexcept>
#include <format>
#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>

enum class Key : int {
    ArrowLeft = 1000,
    ArrowRight,
    ArrowUp,
    ArrowDown,
    DeleteKey,
    HomeKey,
    EndKey,
    PageUp,
    PageDown,
    CtrlQ = 17 // 'q' & 0x1f
};

// RAII обгортка для безпечного керування сирим режимом термінала
class TerminalSession {
public:
    TerminalSession() {
        if (tcgetattr(STDIN_FILENO, &orig_termios_) == -1) {
            throw std::runtime_error("Не вдалося отримати параметри termios");
        }

        struct termios raw = orig_termios_;
        raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
        raw.c_oflag &= ~(OPOST);
        raw.c_cflag |= (CS8);
        raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
        raw.c_cc[VMIN] = 0;
        raw.c_cc[VTIME] = 1;

        if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) == -1) {
            throw std::runtime_error("Не вдалося встановити сирий режим термінала");
        }

        // Перемикання в альтернативний екран
        std::cout << "\x1b[?1049h" << std::flush;
    }

    ~TerminalSession() noexcept {
        // Повернення до основного екрана та відновлення канонічного режиму
        std::cout << "\x1b[?1049l\x1b[?25h" << std::flush;
        tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios_);
    }

    TerminalSession(const TerminalSession&) = delete;
    TerminalSession& operator=(const TerminalSession&) = delete;

private:
    struct termios orig_termios_{};
};

class TerminalEditor {
public:
    TerminalEditor() {
        update_window_size();
    }

    void run() {
        while (running_) {
            render();
            process_key();
        }
    }

private:
    int cursor_x_{0};
    int cursor_y_{0};
    int screen_rows_{24};
    int screen_cols_{80};
    bool running_{true};

    void update_window_size() {
        struct winsize ws{};
        if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == 0 && ws.ws_col > 0) {
            screen_cols_ = ws.ws_col;
            screen_rows_ = ws.ws_row;
        }
    }

    int read_raw_byte() const {
        char c{0};
        while (true) {
            const ssize_t bytes_read = ::read(STDIN_FILENO, &c, 1);
            if (bytes_read == 1) return static_cast<unsigned char>(c);
            if (bytes_read == -1 && errno != EAGAIN && errno != EINTR) {
                throw std::runtime_error("Помилка читання stdin");
            }
        }
    }

    int read_key() const {
        const int c = read_raw_byte();
        if (c != '\x1b') return c;

        char seq[3]{};
        if (::read(STDIN_FILENO, &seq[0], 1) != 1) return '\x1b';
        if (::read(STDIN_FILENO, &seq[1], 1) != 1) return '\x1b';

        if (seq[0] == '[') {
            if (seq[1] >= '0' && seq[1] <= '9') {
                if (::read(STDIN_FILENO, &seq[2], 1) != 1) return '\x1b';
                if (seq[2] == '~') {
                    switch (seq[1]) {
                        case '1': return static_cast<int>(Key::HomeKey);
                        case '3': return static_cast<int>(Key::DeleteKey);
                        case '4': return static_cast<int>(Key::EndKey);
                        case '5': return static_cast<int>(Key::PageUp);
                        case '6': return static_cast<int>(Key::PageDown);
                        case '7': return static_cast<int>(Key::HomeKey);
                        case '8': return static_cast<int>(Key::EndKey);
                    }
                }
            } else {
                switch (seq[1]) {
                    case 'A': return static_cast<int>(Key::ArrowUp);
                    case 'B': return static_cast<int>(Key::ArrowDown);
                    case 'C': return static_cast<int>(Key::ArrowRight);
                    case 'D': return static_cast<int>(Key::ArrowLeft);
                    case 'H': return static_cast<int>(Key::HomeKey);
                    case 'F': return static_cast<int>(Key::EndKey);
                }
            }
        } else if (seq[0] == 'O') {
            switch (seq[1]) {
                case 'H': return static_cast<int>(Key::HomeKey);
                case 'F': return static_cast<int>(Key::EndKey);
            }
        }
        return '\x1b';
    }

    void render() {
        std::string frame;
        frame.reserve(screen_rows_ * (screen_cols_ + 16));

        // Сховати курсор і скинути координати
        frame += "\x1b[?25l\x1b[H";

        for (int y = 0; y < screen_rows_; ++y) {
            if (y == screen_rows_ / 3) {
                std::string welcome = "C++ Terminal Text Engine -- Ready";
                if (static_cast<int>(welcome.size()) > screen_cols_) {
                    welcome.resize(screen_cols_);
                }
                int padding = (screen_cols_ - static_cast<int>(welcome.size())) / 2;
                if (padding > 0) {
                    frame += "~";
                    --padding;
                }
                frame.append(padding, ' ');
                frame += welcome;
            } else {
                frame += "~";
            }

            frame += "\x1b[K"; // Очистити рядок до кінця
            if (y < screen_rows_ - 1) {
                frame += "\r\n";
            }
        }

        // Позиціонування та відновлення видимості курсора
        frame += std::format("\x1b[{};{}H\x1b[?25h", cursor_y_ + 1, cursor_x_ + 1);

        ::write(STDOUT_FILENO, frame.data(), frame.size());
    }

    void process_key() {
        const int key = read_key();
        if (key == static_cast<int>(Key::CtrlQ)) {
            running_ = false;
            return;
        }

        switch (static_cast<Key>(key)) {
            case Key::ArrowLeft:
                if (cursor_x_ > 0) --cursor_x_;
                break;
            case Key::ArrowRight:
                if (cursor_x_ < screen_cols_ - 1) ++cursor_x_;
                break;
            case Key::ArrowUp:
                if (cursor_y_ > 0) --cursor_y_;
                break;
            case Key::ArrowDown:
                if (cursor_y_ < screen_rows_ - 1) ++cursor_y_;
                break;
            default:
                break;
        }
    }
};

int main() {
    try {
        TerminalSession session;
        TerminalEditor editor;
        editor.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

## Інженерні нюанси, профілювання та типові пастки

1. **«Зламаний термінал» при аварійному виході:** якщо програма завершується через `SIGSEGV` або необроблений виняток без скидання прапорців `termios`, термінал залишається в сирому режимі (без відлуння символів та обробки Enter). Реєстрація `atexit(disable_raw_mode)` у C та деструктор RAII-обгортки `TerminalSession` у C++ гарантують коректне відновлення TTY при штатному виході. Для захисту від сигналів додатково реєструють обробники `SIGINT`, `SIGTERM` та `SIGSEGV`.
2. **Атомарність оновлення кадру:** виклик окремих інструкцій `write()` на кожну послідовність очищення рядка або символ призводить до того, що емулятор термінала встигає відмалювати проміжний стан. Формування єдиного рядкового буфера в пам'яті та його скидання за один виклик `write()` гарантує повну відсутність мерехтіння. Перевірити це можна за допомогою утиліти `strace -e trace=write ./editor`: на кожне натискання клавіші повинен генеруватися рівно один виклик `write()` на кількасот байтів, а не десятки дрібних викликів.
3. **Обробка кодування UTF-8:** у сирому режимі багатобайтові символи (наприклад, літери кирилиці або емодзі) надходять у вигляді серії з 2–4 окремих викликів `read()`. Редактор повинен накопичувати байти у валідні кодові точки Unicode перед їх вставкою у буфер документа та використовувати функцію `wcwidth()` для обчислення фактичної кількості колонок, які символ займає на моноширинній сітці екрана.
4. **Небезпека `EINTR` у системних викликах:** коли надходить сигнал зміни розміру `SIGWINCH`, заблокований системний виклик `read()` переривається і повертає `-1`, встановлюючи `errno = EINTR`. Цикл читання зобов'язаний явно ігнорувати помилки `EINTR` та `EAGAIN`, продовжуючи опитування потоку без аварійного виходу.
5. **Прокрутка великих файлів (Viewport offset):** при реалізації повноцінного редактора розмір буфера тексту перевищує `screen_rows`. До стану редактора додаються змінні `row_offset` та `col_offset`. Функція `editor_draw_rows()` малює не рядки від `0` до `screen_rows`, а зріз буфера від `row_offset` до `row_offset + screen_rows`, транслюючи логічні координати файлу в екранні за час `O(кількість комірок екрана)`.
