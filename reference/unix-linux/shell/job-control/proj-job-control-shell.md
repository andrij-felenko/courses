# ⚙️ Реалізація керування завданнями у власній оболонці

Цей практичний матеріал демонструє реалізацію повноцінного механізму керування завданнями (`Job Control`) у командній оболонці Unix. Поданий нижче код розкриває практичну сторону взаємодії системних викликів `setpgid`, `tcsetpgrp`, `waitpid` та термінальних сигналів `SIGTSTP`, `SIGINT`, `SIGTTIN` та `SIGTTOU`.

---

## 1. Архітектурні вимоги до оболонки з підтримкою завдань

Драйвер управляючого термінала в ядрі Linux та специфікація POSIX висувають чіткі правила до системного процесу, який претендує на роль інтерактивної оболонки:

1. **Ініціалізація та захоплення термінала:** Оболонка повинна перевірити, чи запущена вона в інтерактивному TTY за допомогою `isatty(STDIN_FILENO)`. Далі вона переконується, що є лідером власної групи процесів (`shell_pgid = getpid()`), створює цю групу через `setpgid(shell_pgid, shell_pgid)` та призначає її переднім планом через `tcsetpgrp(STDIN_FILENO, shell_pgid)`.
2. **Ігнорування термінальних сигналів:** Сама оболонка не повинна помирати або призупинятися, коли користувач натискає `Ctrl+C` чи `Ctrl+Z`. Тому у процесі оболонки сигнали `SIGINT`, `SIGQUIT`, `SIGTSTP`, `SIGTTIN` та `SIGTTOU` встановлюються у значення `SIG_IGN`.
3. **Усунення стану гонки (Race Condition):** При розгалуженні процесів через `fork()` і батько (оболонка), і нащадок викликають `setpgid(pid, pid)` до того, як нащадок виконає `execvp()`, а батько покличе `tcsetpgrp()`. Це виключає ситуацію, коли нащадок встигає замінити образ коду або батько намагається передати термінал ще не існуючій групі.
4. **Управління налаштуваннями термінала (`termios`):** Коли інтерактивна програма (наприклад, `vim` або `htop`) переходить у фокус переднього плану, вона може змінити режими TTY на неканонічні (`raw mode`). При її призупиненні (`Ctrl+Z`) оболонка зобов'язана зберегти `termios` завдання і миттєво відновити початкові налаштування оболонки `shell_tmodes`, інакше текстове запрошення оболонки виявиться зламаним.

---

## 2. Структури даних та життєвий цикл таблиці завдань

Таблиця завдань оболонки (`job table`) зберігає стан кожного запущеного конвеєра або фонового процесу. Основні елементи цієї структури:

- **Ідентифікатор завдання (`job id`):** Порядковий номер завдання, показаний користувачеві (наприклад, `[1]`, `[2]`).
- **Ідентифікатор групи процесів (`pgid`):** Номер групи, чий лідер збігається з першим процесом завдання.
- **Стан завдання (`JobState`):** Одне з трьох значень: `JOB_RUNNING` (виконується у фоні або на передньому плані), `JOB_STOPPED` (призупинено сигналом `SIGTSTP`/`SIGTTIN`/`SIGTTOU`), `JOB_COMPLETED` (виконанння завершено, очікує видалення з таблиці).
- **Збережений термінальний режим (`struct termios tmodes`):** Знімок атрибутів термінала, зроблений у момент останнього призупинення або передачі фокусу завдання.

Коли користувач запускає новий конвеєр, оболонка створює новий запис у таблиці завдань. При виконанні команди `jobs` оболонка ітерується по масиву та виводить лише ті завдання, чий стан відрізняється від `JOB_COMPLETED`.

---

## 3. Сигнальна дисципліна та маскування під час розгалуження

Під час виконання розгалуження процесів `fork()` виникає критичний момент маскування сигналів. Якщо сигнал `SIGCHLD` надійде до оболонки у момент між виконанням `fork()` та оновленням таблиці завдань, асинхронний обробник `SIGCHLD` може прочитати стан нащадка раніше, ніж оболонка додасть завдання до таблиці.

Щоб запобігти цій гонці, оболонка використовує системний виклик `sigprocmask()` для тимчасового блокування `SIGCHLD` перед `fork()`, і розблоковує його лише після того, як `add_job()` та `setpgid()` успішно завершилися в обох процесах.

```
Оболонка: sigprocmask(SIG_BLOCK, &mask) ──► fork() ──► setpgid() ──► add_job() ──► sigprocmask(SIG_UNBLOCK)
```

У нащадку одразу після `fork()` усі заблоковані сигнали скидаються до стандартних дій `SIG_DFL`, а маска сигналів очищується через `sigprocmask(SIG_SETMASK, &oldmask, NULL)`.

---

## 4. Реалізація: C та C++

Нижче наведено робочий код міні-оболонки двома мовами. C-версія демонструє пряме використання POSIX-функцій, а C++-версія застосовує концепції RAII для автоматичного відновлення станів термінала та масок сигналів.

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <errno.h>

#define MAX_JOBS 32
#define MAX_ARGS 16

typedef enum {
    JOB_RUNNING,
    JOB_STOPPED,
    JOB_COMPLETED
} JobState;

typedef struct {
    int id;
    pid_t pgid;
    char command[128];
    JobState state;
    struct termios tmodes;
} Job;

static Job job_table[MAX_JOBS];
static int job_count = 0;
static pid_t shell_pgid;
static int shell_terminal = STDIN_FILENO;
static struct termios shell_tmodes;

static void init_shell(void) {
    /* Перевіряємо, чи працюємо ми в інтерактивному терміналі */
    if (!isatty(shell_terminal)) {
        fprintf(stderr, "Помилка: Оболонка повинна запускатися в TTY\n");
        exit(EXIT_FAILURE);
    }

    /* Чекаємо, поки оболонка не опиниться на передньому плані */
    while (tcgetpgrp(shell_terminal) != (shell_pgid = getpgrp())) {
        kill(-shell_pgid, SIGTTIN);
    }

    /* Ігноруємо термінальні сигнали у самому процесі оболонки */
    signal(SIGINT, SIG_IGN);
    signal(SIGQUIT, SIG_IGN);
    signal(SIGTSTP, SIG_IGN);
    signal(SIGTTIN, SIG_IGN);
    signal(SIGTTOU, SIG_IGN);
    signal(SIGCHLD, SIG_DFL);

    /* Створюємо власну групу процесів для оболонки */
    shell_pgid = getpid();
    if (setpgid(shell_pgid, shell_pgid) < 0) {
        perror("setpgid для оболонки");
        exit(EXIT_FAILURE);
    }

    /* Забираємо фокус термінала собі */
    tcsetpgrp(shell_terminal, shell_pgid);
    tcgetattr(shell_terminal, &shell_tmodes);
}

static Job* add_job(pid_t pgid, const char* cmd, JobState state) {
    if (job_count >= MAX_JOBS) return NULL;
    Job* j = &job_table[job_count++];
    j->id = job_count;
    j->pgid = pgid;
    snprintf(j->command, sizeof(j->command), "%s", cmd);
    j->state = state;
    tcgetattr(shell_terminal, &j->tmodes);
    return j;
}

static void wait_for_job(Job* j) {
    int status;
    pid_t pid;

    /* Чекаємо зміни стану будь-якого процесу з даної групи */
    while ((pid = waitpid(-j->pgid, &status, WUNTRACED)) > 0) {
        if (WIFSTOPPED(status)) {
            j->state = JOB_STOPPED;
            tcgetattr(shell_terminal, &j->tmodes);
            printf("\n[%d]+ Зупинено (SIGTSTP)   %s\n", j->id, j->command);
            break;
        } else if (WIFEXITED(status) || WIFSIGNALED(status)) {
            j->state = JOB_COMPLETED;
            break;
        }
    }

    /* Повертаємо термінал оболонці */
    tcsetpgrp(shell_terminal, shell_pgid);
    tcsetattr(shell_terminal, TCSADRAIN, &shell_tmodes);
}

static void put_job_in_foreground(Job* j, int cont) {
    /* Відновлюємо налаштування термінала завдання */
    tcsetattr(shell_terminal, TCSADRAIN, &j->tmodes);
    
    /* Передаємо термінал групі завдання */
    tcsetpgrp(shell_terminal, j->pgid);

    if (cont) {
        if (kill(-j->pgid, SIGCONT) < 0) {
            perror("kill (SIGCONT)");
        }
    }

    j->state = JOB_RUNNING;
    wait_for_job(j);
}

static void put_job_in_background(Job* j, int cont) {
    if (cont) {
        if (kill(-j->pgid, SIGCONT) < 0) {
            perror("kill (SIGCONT)");
        }
    }
    j->state = JOB_RUNNING;
    printf("[%d] %d\n", j->id, (int)j->pgid);
}

static void execute_cmd(char** args, int in_bg, const char* full_cmd) {
    pid_t pid = fork();

    if (pid == 0) {
        /* Код нащадка */
        pid_t child_pid = getpid();
        setpgid(child_pid, child_pid);

        if (!in_bg) {
            tcsetpgrp(shell_terminal, child_pid);
        }

        /* Відновлюємо дефолтні обробники сигналів у нащадку */
        signal(SIGINT, SIG_DFL);
        signal(SIGQUIT, SIG_DFL);
        signal(SIGTSTP, SIG_DFL);
        signal(SIGTTIN, SIG_DFL);
        signal(SIGTTOU, SIG_DFL);
        signal(SIGCHLD, SIG_DFL);

        execvp(args[0], args);
        perror("execvp");
        _exit(EXIT_FAILURE);
    } else if (pid > 0) {
        /* Код батька (оболонки) */
        setpgid(pid, pid); /* Взаємне усунення race condition */

        Job* j = add_job(pid, full_cmd, in_bg ? JOB_RUNNING : JOB_STOPPED);
        if (!in_bg) {
            put_job_in_foreground(j, 0);
        } else {
            put_job_in_background(j, 0);
        }
    } else {
        perror("fork");
    }
}

int main(void) {
    char line[256];
    init_shell();

    while (1) {
        printf("job-shell> ");
        fflush(stdout);

        if (!fgets(line, sizeof(line), stdin)) break;

        line[strcspn(line, "\n")] = 0;
        if (strlen(line) == 0) continue;

        char* args[MAX_ARGS];
        int arg_idx = 0;
        char* token = strtok(line, " ");
        while (token && arg_idx < MAX_ARGS - 1) {
            args[arg_idx++] = token;
            token = strtok(NULL, " ");
        }
        args[arg_idx] = NULL;

        int in_bg = 0;
        if (arg_idx > 0 && strcmp(args[arg_idx - 1], "&") == 0) {
            in_bg = 1;
            args[--arg_idx] = NULL;
        }

        if (args[0] == NULL) continue;

        if (strcmp(args[0], "jobs") == 0) {
            for (int i = 0; i < job_count; i++) {
                if (job_table[i].state != JOB_COMPLETED) {
                    printf("[%d] %s   %s\n", job_table[i].id,
                           job_table[i].state == JOB_STOPPED ? "Зупинено" : "Працює",
                           job_table[i].command);
                }
            }
        } else if (strcmp(args[0], "fg") == 0) {
            if (job_count > 0) {
                Job* j = &job_table[job_count - 1];
                printf("%s\n", j->command);
                put_job_in_foreground(j, 1);
            }
        } else if (strcmp(args[0], "bg") == 0) {
            if (job_count > 0) {
                Job* j = &job_table[job_count - 1];
                put_job_in_background(j, 1);
            }
        } else if (strcmp(args[0], "exit") == 0) {
            break;
        } else {
            execute_cmd(args, in_bg, line);
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <memory>
#include <csignal>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <termios.h>

enum class JobStatus { Running, Stopped, Completed };

struct Job {
    int id;
    pid_t pgid;
    std::string command;
    JobStatus status;
    termios tmodes;
};

class TerminalRAII {
    int fd_;
    termios original_modes_;
public:
    explicit TerminalRAII(int fd) : fd_(fd) {
        tcgetattr(fd_, &original_modes_);
    }
    ~TerminalRAII() {
        tcsetattr(fd_, TCSADRAIN, &original_modes_);
    }
    void restore() const {
        tcsetattr(fd_, TCSADRAIN, &original_modes_);
    }
};

class MiniShell {
    pid_t shell_pgid_;
    int tty_fd_{STDIN_FILENO};
    termios shell_tmodes_;
    std::vector<Job> jobs_;

public:
    MiniShell() {
        if (!isatty(tty_fd_)) {
            throw std::runtime_error("Shell must be run in a interactive TTY");
        }

        while (tcgetpgrp(tty_fd_) != (shell_pgid_ = getpgrp())) {
            kill(-shell_pgid_, SIGTTIN);
        }

        // Ігноруємо сигнали термінала в процесі оболонки
        std::signal(SIGINT, SIG_IGN);
        std::signal(SIGQUIT, SIG_IGN);
        std::signal(SIGTSTP, SIG_IGN);
        std::signal(SIGTTIN, SIG_IGN);
        std::signal(SIGTTOU, SIG_IGN);

        shell_pgid_ = getpid();
        if (setpgid(shell_pgid_, shell_pgid_) < 0) {
            std::perror("setpgid shell");
            std::exit(EXIT_FAILURE);
        }

        tcsetpgrp(tty_fd_, shell_pgid_);
        tcgetattr(tty_fd_, &shell_tmodes_);
    }

    void run() {
        std::string line;
        while (true) {
            std::cout << "cpp-job-shell> " << std::flush;
            if (!std::getline(std::cin, line) || line == "exit") break;
            if (line.empty()) continue;

            auto tokens = parse_command(line);
            if (tokens.empty()) continue;

            bool is_bg = false;
            if (tokens.back() == "&") {
                is_bg = true;
                tokens.pop_back();
            }

            if (tokens[0] == "jobs") {
                print_jobs();
            } else if (tokens[0] == "fg") {
                bring_to_fg();
            } else if (tokens[0] == "bg") {
                resume_in_bg();
            } else {
                spawn_job(tokens, is_bg, line);
            }
        }
    }

private:
    std::vector<std::string> parse_command(const std::string& cmd) {
        std::stringstream ss(cmd);
        std::string token;
        std::vector<std::string> res;
        while (ss >> token) res.push_back(token);
        return res;
    }

    void print_jobs() {
        for (const auto& job : jobs_) {
            if (job.status != JobStatus::Completed) {
                std::cout << "[" << job.id << "] "
                          << (job.status == JobStatus::Stopped ? "Stopped" : "Running")
                          << "   " << job.command << "\n";
            }
        }
    }

    void bring_to_fg() {
        for (auto it = jobs_.rbegin(); it != jobs_.rend(); ++it) {
            if (it->status != JobStatus::Completed) {
                std::cout << it->command << "\n";
                tcsetattr(tty_fd_, TCSADRAIN, &it->tmodes);
                tcsetpgrp(tty_fd_, it->pgid);
                
                if (it->status == JobStatus::Stopped) {
                    kill(-it->pgid, SIGCONT);
                }
                it->status = JobStatus::Running;
                wait_for_pgid(it->pgid);
                return;
            }
        }
    }

    void resume_in_bg() {
        for (auto it = jobs_.rbegin(); it != jobs_.rend(); ++it) {
            if (it->status == JobStatus::Stopped) {
                kill(-it->pgid, SIGCONT);
                it->status = JobStatus::Running;
                std::cout << "[" << it->id << "] " << it->pgid << "\n";
                return;
            }
        }
    }

    void wait_for_pgid(pid_t pgid) {
        int status;
        while (waitpid(-pgid, &status, WUNTRACED) > 0) {
            if (WIFSTOPPED(status)) {
                for (auto& job : jobs_) {
                    if (job.pgid == pgid) {
                        job.status = JobStatus::Stopped;
                        tcgetattr(tty_fd_, &job.tmodes);
                        std::cout << "\n[" << job.id << "]+ Stopped   " << job.command << "\n";
                        break;
                    }
                }
                break;
            }
        }
        tcsetpgrp(tty_fd_, shell_pgid_);
        tcsetattr(tty_fd_, TCSADRAIN, &shell_tmodes);
    }

    void spawn_job(const std::vector<std::string>& args, bool is_bg, const std::string& full_cmd) {
        pid_t pid = fork();

        if (pid == 0) {
            pid_t cpid = getpid();
            setpgid(cpid, cpid);
            if (!is_bg) tcsetpgrp(tty_fd_, cpid);

            std::signal(SIGINT, SIG_DFL);
            std::signal(SIGQUIT, SIG_DFL);
            std::signal(SIGTSTP, SIG_DFL);
            std::signal(SIGTTIN, SIG_DFL);
            std::signal(SIGTTOU, SIG_DFL);

            std::vector<char*> c_args;
            for (const auto& arg : args) c_args.push_back(const_cast<char*>(arg.c_str()));
            c_args.push_back(nullptr);

            execvp(c_args[0], c_args.data());
            std::perror("execvp");
            std::_Exit(EXIT_FAILURE);
        } else if (pid > 0) {
            setpgid(pid, pid);
            termios job_tmodes;
            tcgetattr(tty_fd_, &job_tmodes);
            int job_id = static_cast<int>(jobs_.size()) + 1;
            jobs_.push_back({job_id, pid, full_cmd, is_bg ? JobStatus::Running : JobStatus::Stopped, job_tmodes});

            if (!is_bg) {
                tcsetpgrp(tty_fd_, pid);
                wait_for_pgid(pid);
            } else {
                std::cout << "[" << job_id << "] " << pid << "\n";
            }
        }
    }
};

int main() {
    try {
        MiniShell shell;
        shell.run();
    } catch (const std::exception& e) {
        std::cerr << "Fatal shell error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

## 5. Розбір конвеєрів та передача даних між процесами

Справжня оболонка підтримує оператори пайплайнів `|`, коли кілька процесів з'єднуються у ланцюг за допомогою системного виклику `pipe()`.

При виконанні конвеєра `cmd1 | cmd2 | cmd3` оболонка створює один загальний `PGID` для усіх трьох процесів:

1. Оболонка створює анонімний канал `pipe(pipefds)`.
2. Оболонка викликає `fork()` для `cmd1`. Оболонка і нащадок викликають `setpgid(pid1, pid1)`. Новий PGID стає рівним `pid1`.
3. Оболонка викликає `fork()` для `cmd2`. Оболонка і нащадок викликають `setpgid(pid2, pid1)`, приєднуючи другий процес до групи першого.
4. Оболонка викликає `fork()` для `cmd3`. Оболонка і нащадок викликають `setpgid(pid3, pid1)`, приєднуючи третій процес до тієї ж групи `pid1`.
5. Оболонка викликає `tcsetpgrp(STDIN_FILENO, pid1)`, передаючи термінал усій групі `pid1`.

Коли користувач натискає `Ctrl+Z`, ядро надсилає `SIGTSTP` у групу `pid1`, і **усі три процеси** (`cmd1`, `cmd2`, `cmd3`) зупиняються одночасно.

---

## 6. Критичні тонкощі та розбір крайніх випадків

### 1. Захист від SIGTTOU при виклику tcsetpgrp

Коли оболонка намагається передати термінал нащадку за допомогою виклику `tcsetpgrp()`, сама оболонка перебуває у фоні відносно термінала, якщо перед цим вона вже віддала термінал. Відповідно до POSIX, системний виклик `tcsetpgrp()`, який виконується фоновим процесом, генерує сигнал **`SIGTTOU`**. Якщо оболонка не заблокує або не проігнорує `SIGTTOU`, ядро негайно зупинить саму оболонку у стані `TASK_STOPPED`!

Саме тому під час ініціалізації оболонка обов'язково налаштовує обробник `SIGTTOU` у значення `SIG_IGN`.

### 2. Подвійний виклик setpgid для усунення Race Condition

Під час виклику `fork()` у лінукс-керні створення нащадка і повернення з системного виклику відбуваються асинхронно. Якщо планувальник спочатку віддасть процесорний час оболонці, оболонка може спробувати передати термінал нащадку через `tcsetpgrp()`. Якщо нащадок ще не встиг викликати `setpgid()`, його група процесів буде збігатися з групою оболонки, і передача термінала провалиться з помилкою `EPERM`.

Якщо ж першим виконається нащадок і встигне зробити `execvp()`, після цього виклик `setpgid()` з боку оболонки завершиться помилкою `EACCES`. Тому усунення гонки можливе виключно за рахунок дубльованого виклику `setpgid(pid, pid)` як в оболонці, так і в нащадку.

### 3. Збереження та відновлення налаштувань termios

Інтерактивні програми на кшталт `vim`, `less` чи `htop` перемикають термінал у неканонічний режим, вимикають ехо символів і перевизначають управляючі комбінації. При натисканні `Ctrl+Z` програма миттєво зупиняється ядром, залишаючи термінал у зміненому стані.

Якісна оболонка повинна зберігати `termios` завдання при кожному його зупиненні та відновлювати власні початкові атрибути `shell_tmodes`. При виконанні команди `fg` оболонка повертає збережені атрибути завдання у TTY, і лише після цього відправляє `SIGCONT`.
