# ⚙️ Реалізація інтерактивного REPL та асинхронного введення на GNU Readline

Коли консольна утиліта — інтерпретатор мови, клієнт бази даних чи діагностичний агент — працює в інтерактивному режимі, вона стикається з двома взаємопов'язаними завданнями: надати користувачеві зручний інтерфейс введення (з автодоповненням, історією та навігацією) та одночасно реагувати на асинхронні події (мережеві пакети, таймери, сигнали зміни розміру вікна) без блокування потоку.

Нижче наведено побудову двох практичних архітектур: класичного синхронного циклу REPL (англ. *Read-Eval-Print Loop*) з користувацьким контекстним автодоповненням і стійкою історією та повноцінного асинхронного циклу на основі системного виклику `poll()` і колбек-інтерфейсу GNU Readline.

## 1. Синхронний REPL із контекстним автодоповненням

Синхронний підхід підходить для утиліт командного рядка, де процес виконує обчислення виключно у відповідь на введену користувачем команду. Програма послідовно читає рядок, розбирає його синтаксис, виконує дію, друкує результат і повертається до очікування нового рядка.

Головне завдання полягає в тому, щоб налаштувати власне двошарове автодоповнення:
1. Якщо користувач натискає `Tab` на першому слові рядка (`start == 0`), пропонувати перелік доступних команд (наприклад, `SELECT`, `INSERT`, `UPDATE`).
2. Якщо користувач натискає `Tab` після першого слова (`start > 0`), пропонувати контекстні параметри (наприклад, імена таблиць `users`, `accounts`, `orders`).

Для цього призначається користувацький диспетчер `rl_attempted_completion_function`. Змінна `rl_attempted_completion_over = 1` сигналізує бібліотеці, що якщо наш генератор не знайшов жодного збігу, Readline не повинен автоматично перемикатися на стандартне автодоповнення імен файлів у поточній файловій системі.

Генератор автодоповнення працює як скінченний ітератор зі збереженням стану між викликами:
- При першому зверненні передається аргумент `state == 0`. Генератор ініціалізує внутрішній індекс списку (`list_index = 0`), обчислює довжину префікса `len = strlen(text)` і повертає динамічно виділену копію першого знайденого збігу через `strdup()` або `malloc()`.
- При наступних викликах передається `state != 0`. Генератор продовжує пошук із попередньої позиції індексу і повертає черговий збіг.
- Коли список слів вичерпано, генератор повертає `NULL`, що вказує Readline на завершення збору варіантів.

Покрокове простеження введення `SEL` + `Tab` + ` us` + `Tab`:
1. Користувач вводить `SEL` і натискає `Tab`. Позиція `start` дорівнює `0`, `text` дорівнює `"SEL"`. Диспетчер викликає `command_generator`, який повертає єдиний збіг `"SELECT"`. Readline автоматично підставляє слово в буфер і додає пробіл.
2. Користувач дописує `us` і натискає `Tab`. Позиція `start` тепер дорівнює `7`, а `text` дорівнює `"us"`. Диспетчер бачить `start > 0` і запускає `table_generator`, який повертає рядок `"users"`. Рядок стає `SELECT users `.

:::tabs
```c
/* repl_sync.c — Інтерактивний REPL із автодоповненням на C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <readline/readline.h>
#include <readline/history.h>

static const char *const COMMANDS[] = {
    "SELECT", "INSERT", "UPDATE", "DELETE",
    "CREATE", "DROP", "SHOW", "HELP", "EXIT", NULL
};

static const char *const TABLES[] = {
    "users", "accounts", "orders", "audit_log", NULL
};

/* Генератор варіантів команд для першого слова */
static char *command_generator(const char *text, int state) {
    static int list_index, len;
    const char *name;

    if (!state) {
        list_index = 0;
        len = (int)strlen(text);
    }

    while ((name = COMMANDS[list_index++]) != NULL) {
        if (strncasecmp(name, text, len) == 0) {
            return strdup(name);
        }
    }
    return NULL;
}

/* Генератор варіантів імен таблиць для наступних аргументів */
static char *table_generator(const char *text, int state) {
    static int list_index, len;
    const char *name;

    if (!state) {
        list_index = 0;
        len = (int)strlen(text);
    }

    while ((name = TABLES[list_index++]) != NULL) {
        if (strncasecmp(name, text, len) == 0) {
            return strdup(name);
        }
    }
    return NULL;
}

/* Диспетчер автодоповнення: перевіряє позицію слова в буфері */
static char **custom_completion(const char *text, int start, int end) {
    (void)end;
    /* Вимикаємо стандартне доповнення імен файлів при відсутності збігів */
    rl_attempted_completion_over = 1;

    /* Якщо слово на початку рядка — доповнюємо команду */
    if (start == 0) {
        return rl_completion_matches(text, command_generator);
    }

    /* Якщо перед словом уже введено команду — доповнюємо імена таблиць */
    return rl_completion_matches(text, table_generator);
}

/* Обробник сигналу SIGINT (Ctrl+C): скидає поточний рядок без аварійного виходу */
static void handle_sigint(int sig) {
    (void)sig;
    write(1, "\n", 1);
    rl_on_new_line();
    rl_replace_line("", 0);
    rl_redisplay();
}

int main(void) {
    const char *hist_file = ".repl_history";
    struct sigaction sa;
    char *line;

    /* Реєстрація безпечного обробника сигналів переривання */
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_sigint;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGINT, &sa, NULL);

    /* Ініціалізація диспетчера доповнень та імені утиліти для inputrc */
    rl_attempted_completion_function = custom_completion;
    rl_readline_name = "MiniDB";

    /* Завантаження історії з диска */
    read_history(hist_file);

    printf("MiniDB Console (GNU Readline). Введіть HELP або EXIT.\n");

    while ((line = readline("minidb> ")) != NULL) {
        /* Пропуск порожніх рядків без збереження в історію */
        if (*line == '\0') {
            free(line);
            continue;
        }

        /* Додавання змістовного рядка в історію */
        add_history(line);

        if (strcasecmp(line, "EXIT") == 0 || strcasecmp(line, "QUIT") == 0) {
            free(line);
            break;
        }

        if (strcasecmp(line, "HELP") == 0) {
            printf("Доступні команди: SELECT, INSERT, UPDATE, DELETE, SHOW, HELP, EXIT\n");
        } else {
            printf("[Виконано]: %s\n", line);
        }

        free(line);
    }

    /* Персистентне збереження та обрізка файлу історії до 100 записів */
    write_history(hist_file);
    history_truncate_file(hist_file, 100);
    printf("\nСеанс завершено.\n");
    return 0;
}
```
```cpp
// repl_sync.cpp — Інтерактивний REPL із автодоповненням на C++20
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <cstring>
#include <csignal>
#include <unistd.h>
#include <readline/readline.h>
#include <readline/history.h>

namespace minidb {

// RAII обгортка для динамічної пам'яті, виділеної бібліотекою Readline
struct ReadlineDeleter {
    void operator()(char* ptr) const noexcept {
        std::free(ptr);
    }
};
using UniqueString = std::unique_ptr<char, ReadlineDeleter>;

// RAII менеджер персистентної історії команд
class HistoryManager {
public:
    explicit HistoryManager(std::string filename, int max_entries = 100)
        : filename_(std::move(filename)), max_entries_(max_entries) {
        read_history(filename_.c_str());
    }

    ~HistoryManager() {
        write_history(filename_.c_str());
        history_truncate_file(filename_.c_str(), max_entries_);
    }

    HistoryManager(const HistoryManager&) = delete;
    HistoryManager& operator=(const HistoryManager&) = delete;

private:
    std::string filename_;
    int max_entries_;
};

class Completer {
public:
    static constexpr std::string_view COMMANDS[] = {
        "SELECT", "INSERT", "UPDATE", "DELETE",
        "CREATE", "DROP", "SHOW", "HELP", "EXIT"
    };

    static constexpr std::string_view TABLES[] = {
        "users", "accounts", "orders", "audit_log"
    };

    static char* CommandGen(const char* text, int state) {
        static size_t idx = 0;
        static size_t len = 0;

        if (state == 0) {
            idx = 0;
            len = std::strlen(text);
        }

        while (idx < std::size(COMMANDS)) {
            const auto& cmd = COMMANDS[idx++];
            if (cmd.size() >= len && ::strncasecmp(cmd.data(), text, len) == 0) {
                return ::strdup(cmd.data());
            }
        }
        return nullptr;
    }

    static char* TableGen(const char* text, int state) {
        static size_t idx = 0;
        static size_t len = 0;

        if (state == 0) {
            idx = 0;
            len = std::strlen(text);
        }

        while (idx < std::size(TABLES)) {
            const auto& tbl = TABLES[idx++];
            if (tbl.size() >= len && ::strncasecmp(tbl.data(), text, len) == 0) {
                return ::strdup(tbl.data());
            }
        }
        return nullptr;
    }

    static char** Dispatcher(const char* text, int start, int /*end*/) {
        rl_attempted_completion_over = 1;
        if (start == 0) {
            return rl_completion_matches(text, CommandGen);
        }
        return rl_completion_matches(text, TableGen);
    }
};

} // namespace minidb

static void handle_sigint(int /*sig*/) {
    write(1, "\n", 1);
    rl_on_new_line();
    rl_replace_line("", 0);
    rl_redisplay();
}

int main() {
    struct sigaction sa{};
    sa.sa_handler = handle_sigint;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGINT, &sa, nullptr);

    minidb::HistoryManager history{".repl_history", 100};
    rl_attempted_completion_function = minidb::Completer::Dispatcher;
    rl_readline_name = "MiniDB";

    std::cout << "MiniDB Console (GNU Readline C++20). Введіть HELP або EXIT.\n";

    while (true) {
        minidb::UniqueString raw_line{readline("minidb> ")};
        if (!raw_line) {
            break; // Отримано EOF (Ctrl+D)
        }

        std::string_view line{raw_line.get()};
        if (line.empty()) {
            continue;
        }

        add_history(raw_line.get());

        if (line == "EXIT" || line == "exit" || line == "quit") {
            break;
        }

        if (line == "HELP" || line == "help") {
            std::cout << "Доступні команди: SELECT, INSERT, UPDATE, DELETE, SHOW, HELP, EXIT\n";
        } else {
            std::cout << "[Виконано]: " << line << "\n";
        }
    }

    std::cout << "\nСеанс завершено.\n";
    return 0;
}
```
:::

## 2. Асинхронний цикл подій із Readline Callback API

Коли застосунок зобов'язаний паралельно обслуговувати фонові таймери (наприклад, періодичні системні звіти, перевірку стану з'єднань чи оновлення метрик) або слухати вхідні мережеві сокети, синхронний виклик `readline()` паралізує всю архітектуру. Будь-яке блокування потоку у виклику `read()` унеможливлює виконання фонових завдань доти, доки користувач не натисне Enter.

Для вирішення цього протиріччя використовують неблокуючий інтерфейс `rl_callback_handler_install()` разом із системним мультиплексором введення-виведення `poll()` або `epoll()`.

Послідовність виконання асинхронного циклу:
1. `rl_callback_handler_install("async-shell> ", line_handler)` переводить термінал у сирий режим, друкує промпт і зберігає покажчик на колбек завершення рядка.
2. Програма реєструє файловий дескриптор `STDIN_FILENO` (дескриптор `0`) у структурі `struct pollfd` із прапорцем події `POLLIN`.
3. Виклик `poll(&pfd, 1, 500)` переводить процес у стан очікування з фіксованим таймаутом (наприклад, 500 мс).
4. Якщо користувач натиснув клавішу, `poll` повертає значення `> 0` із встановленим прапорцем `POLLIN`. Програма викликає `rl_callback_read_char()`, яка зчитує черговий байт, оновлює стан буфера й миттєво перемальовує змінений екранний рядок.
5. Якщо `poll` завершується за таймаутом, програма виконує фонову роботу (перевіряє таймери чи статус сокетів). Якщо потрібно вивести фонове повідомлення на екран під час набору команди, промпт зберігається викликом `rl_save_prompt()`, після друку повідомлення відновлюється через `rl_restore_prompt()` і перемальовується функцією `rl_forced_update_display()`.

Змінні `g_running` та `g_resized` мають тип `volatile sig_atomic_t`. Це гарантує, що запис у них зсередини обробника сигналу є неподільною операцією, яка не створює стану гонки на рівні пам'яті процесора.

:::tabs
```c
/* repl_async.c — Неблокуючий цикл подій із Readline та poll() на C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <poll.h>
#include <time.h>
#include <readline/readline.h>
#include <readline/history.h>

static volatile sig_atomic_t g_running = 1;
static volatile sig_atomic_t g_resized = 0;

static void handle_signal(int sig) {
    if (sig == SIGINT || sig == SIGTERM) {
        g_running = 0;
    } else if (sig == SIGWINCH) {
        g_resized = 1;
    }
}

/* Колбек, який викликає Readline при натисканні Enter */
static void line_handler(char *line) {
    if (line == NULL) {
        /* EOF (Ctrl+D) */
        g_running = 0;
        return;
    }

    if (*line != '\0') {
        add_history(line);
        if (strcmp(line, "quit") == 0 || strcmp(line, "exit") == 0) {
            g_running = 0;
        } else {
            printf("[Оброблено команду]: %s\n", line);
        }
    }

    free(line);
}

int main(void) {
    struct sigaction sa;
    struct pollfd pfd;
    time_t last_tick = time(NULL);

    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGWINCH, &sa, NULL);

    /* Реєструємо колбек-обробник і встановлюємо сирий режим термінала */
    rl_callback_handler_install("async-shell> ", line_handler);

    pfd.fd = STDIN_FILENO;
    pfd.events = POLLIN;

    while (g_running) {
        /* Обробка асинхронної зміни геометрії вікна термінала */
        if (g_resized) {
            g_resized = 0;
            rl_resize_terminal();
        }

        /* Очікуємо введення від користувача з таймаутом 500 мс */
        int ret = poll(&pfd, 1, 500);

        if (ret > 0 && (pfd.revents & POLLIN)) {
            /* Передаємо доступні байти Readline для обробки клавіш */
            rl_callback_read_char();
        }

        /* Фонова періодична робота: кожні 5 секунд показуємо повідомлення */
        time_t now = time(NULL);
        if (now - last_tick >= 5) {
            last_tick = now;

            /* Зберігаємо поточний стан вводу, друкуємо повідомлення й відновлюємо промпт */
            rl_save_prompt();
            write(1, "\n[Фонова подія]: сервер активний\n", 34);
            rl_restore_prompt();
            rl_forced_update_display();
        }
    }

    /* Обов'язкове відновлення початкового стану термінала перед виходом */
    rl_callback_handler_remove();
    printf("\nАсинхронний цикл завершено.\n");
    return 0;
}
```
```cpp
// repl_async.cpp — Неблокуючий цикл подій із Readline та poll() на C++20
#include <iostream>
#include <string_view>
#include <memory>
#include <chrono>
#include <csignal>
#include <cstring>
#include <unistd.h>
#include <poll.h>
#include <readline/readline.h>
#include <readline/history.h>

namespace async_repl {

inline volatile sig_atomic_t g_running{1};
inline volatile sig_atomic_t g_resized{0};

extern "C" void SignalHandler(int sig) {
    if (sig == SIGINT || sig == SIGTERM) {
        g_running = 0;
    } else if (sig == SIGWINCH) {
        g_resized = 1;
    }
}

// RAII обгортка для колбек-інтерфейсу Readline
class CallbackSession {
public:
    explicit CallbackSession(const char* prompt, rl_vcpfunc_t* handler) {
        rl_callback_handler_install(prompt, handler);
    }

    ~CallbackSession() {
        rl_callback_handler_remove();
    }

    CallbackSession(const CallbackSession&) = delete;
    CallbackSession& operator=(const CallbackSession&) = delete;

    void ReadChar() const noexcept {
        rl_callback_read_char();
    }

    void Resize() const noexcept {
        rl_resize_terminal();
    }
};

extern "C" void OnLineEntered(char* raw_line) {
    if (!raw_line) {
        g_running = 0;
        return;
    }

    std::unique_ptr<char, void(*)(void*)> line{raw_line, std::free};
    std::string_view text{line.get()};

    if (!text.empty()) {
        add_history(line.get());
        if (text == "quit" || text == "exit") {
            g_running = 0;
        } else {
            std::cout << "[Оброблено команду]: " << text << "\n";
        }
    }
}

} // namespace async_repl

int main() {
    struct sigaction sa{};
    sa.sa_handler = async_repl::SignalHandler;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGINT, &sa, nullptr);
    sigaction(SIGTERM, &sa, nullptr);
    sigaction(SIGWINCH, &sa, nullptr);

    async_repl::CallbackSession session{"async-shell> ", async_repl::OnLineEntered};

    pollfd pfd{};
    pfd.fd = STDIN_FILENO;
    pfd.events = POLLIN;

    auto last_tick = std::chrono::steady_clock::now();

    while (async_repl::g_running) {
        if (async_repl::g_resized) {
            async_repl::g_resized = 0;
            session.Resize();
        }

        int ret = poll(&pfd, 1, 500);

        if (ret > 0 && (pfd.revents & POLLIN)) {
            session.ReadChar();
        }

        auto now = std::chrono::steady_clock::now();
        if (std::chrono::duration_cast<std::chrono::seconds>(now - last_tick).count() >= 5) {
            last_tick = now;

            // Безпечне виведення фонового тексту без затирання введеного рядка
            rl_save_prompt();
            write(1, "\n[Фонова подія C++]: таймер спрацював\n", 40);
            rl_restore_prompt();
            rl_forced_update_display();
        }
    }

    std::cout << "\nАсинхронний цикл завершено.\n";
    return 0;
}
```
:::

## 3. Критичні підводні камені реалізації

Під час практичного використання GNU Readline у виробничих консольних системах необхідно враховувати кілька важливих архітектурних нюансів:

1. **Гарантія відновлення термінала при аварійному завершенні:** Якщо процес завершується через необроблений виняток, системний виклик `abort()` або сигнал `SIGSEGV` / `SIGTERM` під час активного сеансу Readline, дескриптор термінала залишається у сирому режимі (`ICANON=0, ECHO=0`). Користувач потрапляє в "зламаний термінал", де не відображаються натиснуті клавіші й не працює клавіша Enter. Застосування RAII-класів (`CallbackSession`, `HistoryManager`) та встановлення обробників `sigaction` є обов'язковою практикою для гарантованого виклику `rl_deprep_terminal()` або `rl_callback_handler_remove()`.
2. **Фоновий друк у колбек-режимі:** Якщо асинхронний мережевий потік викличе звичайний `printf()` під час того, як користувач редагує команду посередині рядка, новий текст змішається з промптом і зруйнує екранну позицію курсора. Щоб вивести текст чисто, обов'язково викликають послідовність `rl_save_prompt()`, прямий запис у дескриптор `write(1, ...)`, відновлення через `rl_restore_prompt()` та примусове оновлення екрана `rl_forced_update_display()`.
3. **Обробка `SIGWINCH` та помилки `EINTR` під час системного виклику `poll()`:** Сигнал зміни геометрії вікна перериває системний виклик `poll()` із кодом помилки `EINTR`. Програма не повинна сприймати це як критичний збій або виходити з циклу; слід перевірити прапорець розміру, викликати `rl_resize_terminal()` для оновлення точок перенесення рядків і безпечно продовжити виконання циклу.
4. **Управління життєвим циклом пам'яті в C++:** Функція `readline()` виділяє рядок через системний C-алокатор `malloc()`. У C++ неприпустимо передавати такий покажчик у звичайний `std::unique_ptr<char[]>` із видаленням через `delete[]` — це призводить до невизначеної поведінки (undefined behavior) через несумісність алокаторів. Використання спеціалізованого делетера `ReadlineDeleter` із викликом `std::free()` є єдиним коректним способом інтеграції.
5. **Компіляція та збірка:** Для компіляції наведених прикладів у терміналі Linux використовують прапорці `-lreadline` та стандарт C99 / C++20:
   ```sh
   gcc -std=c99 -Wall -Wextra repl_sync.c -lreadline -o repl_sync
   g++ -std=c++20 -Wall -Wextra repl_sync.cpp -lreadline -o repl_sync_cpp
   ```
