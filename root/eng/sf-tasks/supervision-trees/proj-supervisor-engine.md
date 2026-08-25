# ⚙️ Проєктування ядра дерева нагляду на POSIX-процесах

У мовах без вбудованої віртуальної машини з легкодосяжними акторами (на зразок C або C++) найнадійнішим способом досягнення ізоляції пам'яті є рознесення завдань по окремих процесах операційної системи. Якщо робочий процес виконує розіменування некоректного покажчика, зазнає переповнення буфера або викликає `abort()`, апаратні механізми захисту пам'яті (MMU) та ядро операційної системи ізолюють збій, а батьківський процес отримує асинхронне сповіщення про завершення нащадка.

Наше інженерне завдання — спроєктувати автономне ядро наглядача (*supervisor engine*), яке керує групою дочірніх процесів, підтримує стратегії `ONE_FOR_ONE` та `REST_FOR_ONE`, веде строгий облік інтенсивності збоїв `(MaxR, MaxT)` для запобігання нескінченним циклам аварій і гарантує коректне двофазне завершення нащадків у строго зворотному порядку.

## Архітектурний задум та життєвий цикл

Наглядач функціонує як координатор подій життєвого циклу, робота якого розділена на п'ять чітких фаз:

1. **Фаза ініціалізації:** Наглядач послідовно породжує нащадків за допомогою системного виклику `fork()`. У дочірніх процесах скидаються успадковані маски сигналів, після чого викликається цільова робоча функція. Наглядач зберігає дескриптор `pid` та ініціалізує стан `is_alive = true`.
2. **Головний цикл очікування:** Батьківський процес викликає системний виклик `waitpid(-1, &status, 0)` (або вичитує події через дескриптор `signalfd`). Цей виклик блокує наглядача до моменту завершення будь-якого з підпорядкованих процесів.
3. **Аналіз причин завершення:** Отримавши сповіщення про смерть нащадка, наглядач за допомогою макросів `WIFEXITED`, `WEXITSTATUS`, `WIFSIGNALED` та `WTERMSIG` з'ясовує, чи був вихід штатним (код `0`), чи процес загинув від аварії або фатального сигналу.
4. **Перевірка політики відновлення та бюджету:** 
   - Якщо процес мав тип `TRANSIENT` і завершився успішно, наглядач лише оновлює свій реєстр і продовжує роботу.
   - Якщо процес вимагає перезапуску (`PERMANENT` або аварійний `TRANSIENT`), наглядач реєструє поточну часову позначку в ковзному буфері.
   - Якщо кількість аварій за останні `MaxT` секунд перевищує `MaxR`, наглядач фіксує системну відмову, примусово зупиняє всіх живих дітей через `SIGTERM`/`SIGKILL` і завершується з кодом помилки (ескалація).
5. **Застосування стратегії відновлення:**
   - `ONE_FOR_ONE`: перезапускається виключно загиблий процес.
   - `REST_FOR_ONE`: наглядач зупиняє всіх наступних нащадків у зворотному порядку, перезапускає винуватця аварії, а потім наново запускає наступних нащадків у прямому порядку.

## Реалізація двома мовами

Розглянемо повноцінну реалізацію ядра наглядача. У реалізації на C використовується класична структура з явним управлінням масивами та перевірками помилок системних викликів. У вкладці C++ застосовано ідіоматичний підхід: інкапсуляція в клас `Supervisor`, використання `std::vector`, таймерів `std::chrono::steady_clock` для захисту від стрибків системного часу NTP, безпечних лямбда-функцій та автоматичного очищення ресурсів у деструкторі за принципом RAII.

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>
#include <time.h>
#include <errno.h>

#define MAX_CHILDREN 8
#define MAX_RESTARTS_BUDGET 16

typedef enum {
    STRATEGY_ONE_FOR_ONE,
    STRATEGY_REST_FOR_ONE
} Strategy;

typedef enum {
    RESTART_PERMANENT,
    RESTART_TRANSIENT,
    RESTART_TEMPORARY
} RestartType;

typedef struct {
    const char *name;
    void (*worker_fn)(void *arg);
    void *arg;
    RestartType restart_type;
    pid_t pid;
    bool is_alive;
} ChildSpec;

typedef struct {
    Strategy strategy;
    int max_restarts;
    int max_seconds;
    time_t crash_timestamps[MAX_RESTARTS_BUDGET];
    int crash_count;
    ChildSpec children[MAX_CHILDREN];
    int child_count;
} Supervisor;

static void record_crash_and_check_budget(Supervisor *sup) {
    time_t now = time(NULL);
    
    // Очищаємо старі таймстеми поза вікном max_seconds
    int valid = 0;
    for (int i = 0; i < sup->crash_count; i++) {
        if (now - sup->crash_timestamps[i] <= sup->max_seconds) {
            sup->crash_timestamps[valid++] = sup->crash_timestamps[i];
        }
    }
    sup->crash_count = valid;

    if (sup->crash_count < MAX_RESTARTS_BUDGET) {
        sup->crash_timestamps[sup->crash_count++] = now;
    }

    if (sup->crash_count > sup->max_restarts) {
        fprintf(stderr, "[SUPERVISOR] Перевищено ліміт збоїв (%d за %d с). Ескалація!\n",
                sup->max_restarts, sup->max_seconds);
        // Зупиняємо всіх живих дітей
        for (int i = 0; i < sup->child_count; i++) {
            if (sup->children[i].is_alive) {
                kill(sup->children[i].pid, SIGTERM);
                waitpid(sup->children[i].pid, NULL, 0);
                sup->children[i].is_alive = false;
            }
        }
        exit(EXIT_FAILURE);
    }
}

static bool start_child(Supervisor *sup, int index) {
    ChildSpec *spec = &sup->children[index];
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return false;
    }
    if (pid == 0) {
        // Дочірній процес: скидаємо обробники сигналів і запускаємо роботу
        signal(SIGINT, SIG_DFL);
        signal(SIGTERM, SIG_DFL);
        spec->worker_fn(spec->arg);
        exit(EXIT_SUCCESS);
    }
    spec->pid = pid;
    spec->is_alive = true;
    printf("[SUPERVISOR] Запущено дочірній процес '%s' (PID=%d)\n", spec->name, pid);
    return true;
}

static void stop_child(ChildSpec *spec) {
    if (!spec->is_alive) return;
    printf("[SUPERVISOR] Зупинка процесу '%s' (PID=%d)\n", spec->name, spec->pid);
    kill(spec->pid, SIGTERM);
    
    // Очікуємо завершення до 2 секунд, потім примусовий kill
    for (int t = 0; t < 20; t++) {
        int status;
        pid_t res = waitpid(spec->pid, &status, WNOHANG);
        if (res == spec->pid) {
            spec->is_alive = false;
            return;
        }
        usleep(100000); // 100 мс
    }
    kill(spec->pid, SIGKILL);
    waitpid(spec->pid, NULL, 0);
    spec->is_alive = false;
}

void supervisor_run(Supervisor *sup) {
    // 1. Початковий запуск усіх нащадків у порядку оголошення
    for (int i = 0; i < sup->child_count; i++) {
        if (!start_child(sup, i)) {
            fprintf(stderr, "[SUPERVISOR] Не вдалося запустити '%s'\n", sup->children[i].name);
            return;
        }
    }

    // 2. Головний цикл спостереження
    while (true) {
        int status;
        pid_t died_pid = waitpid(-1, &status, 0);
        if (died_pid < 0) {
            if (errno == EINTR) continue;
            break; // Немає живих нащадків
        }

        int child_idx = -1;
        for (int i = 0; i < sup->child_count; i++) {
            if (sup->children[i].pid == died_pid) {
                child_idx = i;
                break;
            }
        }
        if (child_idx < 0) continue;

        ChildSpec *spec = &sup->children[child_idx];
        spec->is_alive = false;

        bool is_normal = WIFEXITED(status) && (WEXITSTATUS(status) == 0);
        printf("[SUPERVISOR] Процес '%s' (PID=%d) завершився. Код=%d, Нормально=%d\n",
               spec->name, died_pid, WEXITSTATUS(status), is_normal);

        bool need_restart = false;
        if (spec->restart_type == RESTART_PERMANENT) {
            need_restart = true;
        } else if (spec->restart_type == RESTART_TRANSIENT && !is_normal) {
            need_restart = true;
        }

        if (!need_restart) {
            printf("[SUPERVISOR] Процес '%s' не потребує перезапуску.\n", spec->name);
            continue;
        }

        record_crash_and_check_budget(sup);

        if (sup->strategy == STRATEGY_ONE_FOR_ONE) {
            start_child(sup, child_idx);
        } else if (sup->strategy == STRATEGY_REST_FOR_ONE) {
            // Зупиняємо всіх наступних дітей у зворотному порядку
            for (int i = sup->child_count - 1; i > child_idx; i--) {
                stop_child(&sup->children[i]);
            }
            // Перезапускаємо збійного нащадка
            start_child(sup, child_idx);
            // Запускаємо наступних нащадків наново
            for (int i = child_idx + 1; i < sup->child_count; i++) {
                start_child(sup, i);
            }
        }
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <memory>
#include <functional>
#include <system_error>
#include <thread>
#include <algorithm>
#include <unistd.h>
#include <sys/wait.h>
#include <signal.h>

enum class Strategy {
    OneForOne,
    RestForOne
};

enum class RestartType {
    Permanent,
    Transient,
    Temporary
};

struct ChildSpec {
    std::string name;
    std::function<void()> worker_fn;
    RestartType restart_type{RestartType::Permanent};
    pid_t pid{-1};
    bool is_alive{false};
};

class Supervisor {
public:
    Supervisor(Strategy strategy, int max_restarts, std::chrono::seconds max_time)
        : strategy_(strategy), max_restarts_(max_restarts), max_time_(max_time) {}

    ~Supervisor() {
        shutdown_all();
    }

    void add_child(std::string name, std::function<void()> fn, RestartType restart = RestartType::Permanent) {
        children_.push_back(ChildSpec{std::move(name), std::move(fn), restart, -1, false});
    }

    void run() {
        for (size_t i = 0; i < children_.size(); ++i) {
            if (!start_child(i)) {
                throw std::runtime_error("Не вдалося запустити нащадка: " + children_[i].name);
            }
        }

        while (has_living_children()) {
            int status = 0;
            pid_t died_pid = ::waitpid(-1, &status, 0);
            if (died_pid < 0) {
                if (errno == EINTR) continue;
                break;
            }

            auto it = std::find_if(children_.begin(), children_.end(),
                                   [died_pid](const ChildSpec& c) { return c.pid == died_pid; });
            if (it == children_.end()) continue;

            size_t child_idx = std::distance(children_.begin(), it);
            ChildSpec& spec = children_[child_idx];
            spec.is_alive = false;

            bool is_normal = WIFEXITED(status) && (WEXITSTATUS(status) == 0);
            std::cout << "[SUPERVISOR] Процес '" << spec.name << "' завершився. "
                      << "Нормально=" << std::boolalpha << is_normal << "\n";

            bool need_restart = (spec.restart_type == RestartType::Permanent) ||
                                (spec.restart_type == RestartType::Transient && !is_normal);

            if (!need_restart) {
                std::cout << "[SUPERVISOR] Процес '" << spec.name << "' не вимагає відновлення.\n";
                continue;
            }

            check_restart_budget();

            if (strategy_ == Strategy::OneForOne) {
                start_child(child_idx);
            } else if (strategy_ == Strategy::RestForOne) {
                for (size_t i = children_.size(); i-- > child_idx + 1; ) {
                    stop_child(i);
                }
                start_child(child_idx);
                for (size_t i = child_idx + 1; i < children_.size(); ++i) {
                    start_child(i);
                }
            }
        }
    }

private:
    bool start_child(size_t index) {
        ChildSpec& spec = children_[index];
        pid_t pid = ::fork();
        if (pid < 0) return false;
        if (pid == 0) {
            ::signal(SIGINT, SIG_DFL);
            ::signal(SIGTERM, SIG_DFL);
            spec.worker_fn();
            ::_exit(0);
        }
        spec.pid = pid;
        spec.is_alive = true;
        std::cout << "[SUPERVISOR] Запущено '" << spec.name << "' [PID " << pid << "]\n";
        return true;
    }

    void stop_child(size_t index) {
        ChildSpec& spec = children_[index];
        if (!spec.is_alive) return;

        std::cout << "[SUPERVISOR] Зупинка '" << spec.name << "' [PID " << spec.pid << "]\n";
        ::kill(spec.pid, SIGTERM);

        for (int i = 0; i < 20; ++i) {
            int status = 0;
            pid_t res = ::waitpid(spec.pid, &status, WNOHANG);
            if (res == spec.pid) {
                spec.is_alive = false;
                return;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }

        ::kill(spec.pid, SIGKILL);
        ::waitpid(spec.pid, nullptr, 0);
        spec.is_alive = false;
    }

    void check_restart_budget() {
        auto now = std::chrono::steady_clock::now();
        
        // Відкидаємо аварії, старіші за max_time_
        std::erase_if(crash_history_, [now, this](const auto& tp) {
            return now - tp > max_time_;
        });

        crash_history_.push_back(now);

        if (static_cast<int>(crash_history_.size()) > max_restarts_) {
            std::cerr << "[SUPERVISOR] Перевищено ліміт перезапусків! Ескалація аварії.\n";
            shutdown_all();
            throw std::runtime_error("Supervisor crash limit exceeded");
        }
    }

    void shutdown_all() {
        for (size_t i = children_.size(); i-- > 0; ) {
            stop_child(i);
        }
    }

    bool has_living_children() const {
        return std::any_of(children_.begin(), children_.end(),
                           [](const ChildSpec& c) { return c.is_alive; });
    }

    Strategy strategy_;
    int max_restarts_;
    std::chrono::seconds max_time_;
    std::vector<ChildSpec> children_;
    std::vector<std::chrono::steady_clock::time_point> crash_history_;
};
```
:::

## Покроковий розбір виконання стратегії REST_FOR_ONE

Розглянемо послідовність дій ядра при виникненні аварії в конвеєрі задач `[A, B, C]`:

1. Процеси `A` (PID 101), `B` (PID 102), `C` (PID 103) працюють у штатному режимі. Наглядач заблокований у системному виклику `waitpid()`.
2. У процесі `B` виникає збій пам'яті (`SIGSEGV`). Ядро операційної системи генерує сигнал `SIGCHLD`, розблоковуючи `waitpid()` у наглядачі.
3. Наглядач зіставляє повернутий PID 102 зі своїм реєстром і знаходить індекс `child_idx = 1`.
4. Оскільки стратегія визначена як `REST_FOR_ONE`, наглядач ітерується по масиву нащадків від кінця до `child_idx + 1` (тобто зупиняє процес `C` із PID 103).
5. Процесу `C` надсилається `SIGTERM`. Наглядач у неблокуючому циклі `waitpid(..., WNOHANG)` чекає до 2 секунд. Якщо процес `C` не встигає завершитися, надсилається жорсткий `SIGKILL`.
6. Наглядач породжує новий процес `B` через `fork()`, отримуючи новий PID 104, та ініціалізує його роботу.
7. Після успішного старту `B` наглядач запускає процес `C` (PID 105), повністю відновлюючи функціональний конвеєр. Процес `A` (PID 101) протягом усієї процедури працював без зупинки.

## Системні пастки та тонкощі реалізації

1. **Злиття сигналів (Signal Coalescing):** Стандарт POSIX не гарантує формування черги для стандартних сигналів. Якщо кілька дочірніх процесів падають практично одночасно, ядро ОС може об'єднати кілька сигналів `SIGCHLD` в один біт у бітовій масці очікування. Саме тому наглядач не повинен покладатися на підрахунок отриманих `SIGCHLD`: виклик `waitpid(-1, &status, WNOHANG)` має виконуватися в циклі доти, доки не поверне `0` або `-1` з `errno == ECHILD`.
2. **Перевикористання ідентифікаторів (PID Wrap-Around):** В операційних системах Linux простір `pid` є обмеженим (типово до 32768 або 4194304). Після завершення процесу його числовий `pid` може бути дуже швидко виділений ядром для зовсім іншої програми. Якщо наглядач надішле сигнал `kill(pid, SIGTERM)` із запізненням, не перевіривши, що процес усе ще належить до його групи, він може вбити сторонній системний процес.
3. **Успадкування дескрипторів файлів:** За замовчуванням виклик `fork()` копіює всю таблицю файлових дескрипторів батька у нащадка. Якщо наглядач тримає відкриті сокети або лог-файли, кожен дочірній процес отримає копію цих дескрипторів, що завадить їхньому закриттю при аварії. Усі відкриті дескриптори в наглядачі повинні обов'язково відкриватися з прапорцем `O_CLOEXEC` або закриватися безпосередньо після `fork()`.
4. **Стрибки системного часу:** Використання календарного часу `time(NULL)` або `std::chrono::system_clock` для розрахунку ковзного вікна `MaxT` є вразливим до коригувань годинника демоном NTP. Якщо системний час стрибне назад на 1 хвилину, старі аварії зависнуть у буфері, викликаючи хибну ескалацію. У продакшн-коді обов'язковим є використання монотонного таймера `CLOCK_MONOTONIC` або `std::chrono::steady_clock`.
