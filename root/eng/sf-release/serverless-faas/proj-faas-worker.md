# ⚙️ Практична реалізація FaaS-виконавця: керування пулом пісочниць, тайм-аути та обробка подій

Будь-яка платформа безсерверних обчислень опирається на внутрішній компонент хоста — **виконавець** (англ. *FaaS Worker Daemon*). Його завдання полягає у тому, щоб отримати запит на виклик функції, виділити ізольовану пісочницю (процес або мікровіртуальну машину), передати корисне навантаження події через канал введення-виведення, забезпечити суворе дотримання ліміту часу (тайм-ауту) і зібрати результати виконання разом із метриками спожитих ресурсів.

Нижче наведено повноцінний розбір системних механізмів ядра Linux та реалізацію легкозважного FaaS-виконавця, який демонструє ключові патерни: керування пулом теплих і холодних процесів, неблокуючий моніторинг дескрипторів через `poll()`, примусове завершення за тайм-аутом, контроль конкурентності та обмеження ресурсів.

## Системні механізми ізоляції пісочниці

У виробничих FaaS-платформах ізоляція коду спирається на три взаємодоповнюючі стовпи операційної системи Linux:

### 1. Простори назв ядра (Linux Namespaces)
Простори назв ізолюють системні ресурси так, що дочірній процес бачить власну віртуальну копію операційної системи:
- **PID Namespace (`CLONE_NEWPID`)**: процес функції стає `PID 1` у власному просторі. Він не бачить інших процесів хоста і не може надіслати їм системний сигнал `kill()`;
- **Mount Namespace (`CLONE_NEWNS`)**: функція отримує власне дерево монтування файлової системи (`pivot_root` або `chroot`). Доступ до кореневої системи хоста повністю блокується, а робочі каталоги монтуються в режимі `read-only`, за винятком тимчасового каталогу `/tmp`;
- **Network Namespace (`CLONE_NEWNET`)**: пісочниця отримує власний ізольований мережевий стек (інтерфейс `lo` та віртуальний міст `veth`), що дозволяє обмежувати або маршрутизувати мережевий трафік;
- **IPC Namespace (`CLONE_NEWIPC`)**: блокує спільну пам'ять (POSIX/SysV IPC) і черги повідомлень між пісочницями;
- **UTS Namespace (`CLONE_NEWUTS`)**: надає ізольоване ім'я хоста та домену.

### 2. Контрольні групи (cgroups v2)
Контрольні групи обмежують та відстежують використання фізичних ресурсів комп'ютера:
- **`memory.max`**: жорсткий ліміт оперативної пам'яті (наприклад, `536870912` байтів для 512 МБ). При спробі виділити більше ядро викликає OOM-killer і завершує процес;
- **`cpu.max`**: квота процесорного часу (CFS Bandwidth Control). Задається у вигляді пари `quota period` (наприклад, `50000 100000` виділяє рівно 50% одного процесорного ядра);
- **`io.max`**: обмеження швидкості дискових операцій (IOPS та байтів/с), що захищає SSD хоста від перевантаження шкідливими дисковими операціями;
- **`pids.max`**: ліміт максимальної кількості процесів і потоків (наприклад, 1024), що унеможливлює атаку типу «fork-бомба»;
- **`cgroup.freeze`**: запис значення `1` негайно зупиняє планування процесора для всіх процесів групи, переводячи пісочницю в заморожений стан без використання CPU.

### 3. Фільтрація системних викликів (Seccomp BPF) та привілеї
Механізм Secure Computing Mode завантажує в ядро програму BPF, яка перевіряє кожен системний виклик перед його виконанням. Усі виклики, пов'язані з адмініструванням ядра (`kexec_load`, `reboot`, `mount`, `ptrace`, `iopl`), негайно блокуються з кодом `EPERM` або сигналом `SIGSYS`. 

Крім того, виконавець скидає всі привілеї POSIX (Capabilities) та встановлює прапорець `prctl(PR_SET_NO_NEW_PRIVS, 1)`, що унеможливлює отримання підвищених прав через бінарні файли із прапорцем SUID.

---

## Захист хоста від OOM Killer та конфігурація пріоритетів ядра

Одне з найнебезпечніших явищ у FaaS-хостах — вичерпання загальної оперативної пам'яті вузла, коли сотні пісочниць одночасно виділяють великі масиви даних. Коли ядру Linux не вистачає вільної пам'яті для алокацій ядра, спрацьовує механізм вибору жертви OOM Killer.

Ядро обчислює показник «шкідливості» (англ. *badness score*) для кожного процесу в системі на основі відсотка спожитої пам'яті. Без належного налаштування існує ризик, що ядро вб'є сам демон-виконавець (FaaS Worker Daemon), оскільки він утримує у пам'яті великі буфери пулів пісочниць.

Щоб запобігти цьому, виконавець під час власної ініціалізації встановлює максимальний імунітет до OOM Killer, записуючи значення `-1000` у системний файл `/proc/self/oom_score_adj`:

```
echo -1000 > /proc/self/oom_score_adj
```

Значення `-1000` повністю виключає процес воркера з черги кандидатів на знищення. Натомість для кожної новоствореної пісочниці встановлюється контрольна група `memory.max`, яка ізолює надмірне споживання: ядро знищує лише процес усередині конкретної проблемної cgroup, не зачіпаючи сусідні функції та демон хоста.

---

## Архітектура та структура компонентів виконавця

Виконавець будується довкола п'яти фундаментальних обов'язків ядра:

1. **Менеджер пулу пісочниць (Sandbox Pool Manager)**: підтримує чергу вільних («теплих») процесів для кожної функції. Якщо вільний процес існує, час на ініціалізацію дорівнює нулю; якщо ні — створюється новий «холодний» процес;
2. **Контролер конкурентності та допуску (Admission Controller)**: контролює максимальну кількість одночасно працюючих пісочниць на хості. Якщо ліміт вичерпано, запити стають у чергу або відхиляються з кодом помилки `429 Too Many Requests`;
3. **Ізолятор середовища (Sandbox Runner)**: налаштовує закритий робочий каталог, очищає змінні оточення хоста, монтує анонімні канали IPC (англ. *Inter-Process Communication*) і запускає виконуваний файл функції;
4. **Сторожовий таймер (Execution Watchdog)**: відстежує дедлайн виконання за допомогою системного опитування `poll()` або `epoll()`, запобігаючи зависанню воркера при нескінченних циклах у користувацькому коді;
5. **Колектор телеметрії (Telemetry Collector)**: перехоплює потоки `stdout` та `stderr`, фіксує точний час роботи процесора (користувацький і системний час через `getrusage()`) та формує фінальний звіт про виклик.

```
       Вхідний запит: { function_id, payload, timeout_ms }
                              ↓
                  ┌───────────────────────┐
                  │ Admission Controller  │
                  └───────────────────────┘
                              ↓
                  ┌───────────────────────┐
                  │ Sandbox Pool Manager  │
                  └───────────────────────┘
                     /                 \
        (Теплий процес)               (Холодний старт)
              ↓                               ↓
      Взяти з черги пулу             Створити процес (fork/exec)
              \                               /
               →  ┌────────────────────────┐  ←
                  │   Sandbox Controller   │
                  │  • Запис payload (IPC) │
                  │  • poll() з таймаутом  │
                  │  • getrusage() метрики │
                  └────────────────────────┘
                              ↓
                 Звіт: { status, body, duration_ms, memory_kb }
```

---

## Реалізація FaaS-виконавця

Нижче наведено паралельні реалізації повноцінного FaaS-диспетчера: мовою **C++20** (системна реалізація на базі викликів POSIX, RAII та мультиплексування дескрипторів) та мовою **Python** (асинхронна реалізація на базі `asyncio.subprocess`).

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <chrono>
#include <optional>
#include <unordered_map>
#include <queue>
#include <cstring>
#include <cerrno>

#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <poll.h>
#include <signal.h>

// Результат виконання функції
struct ExecutionResult {
    bool success{false};
    bool timed_out{false};
    int exit_code{0};
    std::string response;
    std::string error_log;
    double duration_ms{0.0};
    long max_rss_kb{0};
    bool was_cold_start{false};
};

// RAII-обгортка для файлових дескрипторів
class PipeChannel {
public:
    PipeChannel() {
        int fds[2];
        if (pipe(fds) != 0) {
            throw std::runtime_error("Не вдалося створити pipe: " + std::string(strerror(errno)));
        }
        read_fd_ = fds[0];
        write_fd_ = fds[1];
    }

    ~PipeChannel() {
        close_read();
        close_write();
    }

    void close_read() noexcept {
        if (read_fd_ >= 0) { close(read_fd_); read_fd_ = -1; }
    }

    void close_write() noexcept {
        if (write_fd_ >= 0) { close(write_fd_); write_fd_ = -1; }
    }

    int read_fd() const noexcept { return read_fd_; }
    int write_fd() const noexcept { return write_fd_; }

    PipeChannel(const PipeChannel&) = delete;
    PipeChannel& operator=(const PipeChannel&) = delete;
    PipeChannel(PipeChannel&& o) noexcept : read_fd_(o.read_fd_), write_fd_(o.write_fd_) {
        o.read_fd_ = -1; o.write_fd_ = -1;
    }

private:
    int read_fd_{-1};
    int write_fd_{-1};
};

// Екземпляр ізольованої пісочниці
class SandboxInstance {
public:
    SandboxInstance(std::string binary_path, std::string function_id)
        : binary_path_(std::move(binary_path)), function_id_(std::move(function_id)) {}

    ~SandboxInstance() {
        terminate();
    }

    // Запуск ізольованого дочірнього процесу
    void spawn() {
        // Ігноруємо SIGPIPE у батьківському процесі для безпечного запису в канали
        signal(SIGPIPE, SIG_IGN);

        PipeChannel stdin_pipe;
        PipeChannel stdout_pipe;
        PipeChannel stderr_pipe;

        pid_t pid = fork();
        if (pid < 0) {
            throw std::runtime_error("Помилка fork(): " + std::string(strerror(errno)));
        }

        if (pid == 0) {
            // Дочірній процес (пісочниця)
            dup2(stdin_pipe.read_fd(), STDIN_FILENO);
            dup2(stdout_pipe.write_fd(), STDOUT_FILENO);
            dup2(stderr_pipe.write_fd(), STDERR_FILENO);

            // Закриття зайвих дескрипторів
            stdin_pipe.close_write();
            stdout_pipe.close_read();
            stderr_pipe.close_read();

            // Встановлення змінних оточення пісочниці
            setenv("AWS_LAMBDA_FUNCTION_NAME", function_id_.c_str(), 1);
            setenv("LAMBDA_TASK_ROOT", "/tmp", 1);

            char* const args[] = {const_cast<char*>(binary_path_.c_str()), nullptr};
            execv(binary_path_.c_str(), args);

            // Якщо execv зазнав невдачі
            std::cerr << "Помилка запуску бінарника: " << strerror(errno) << "\n";
            _exit(127);
        }

        // Батьківський процес (виконавець)
        pid_ = pid;
        is_alive_ = true;

        in_fd_ = stdin_pipe.write_fd();
        out_fd_ = stdout_pipe.read_fd();
        err_fd_ = stderr_pipe.read_fd();

        // Робимо дескриптори неблокуючими для безпечного читання через poll()
        fcntl(out_fd_, F_SETFL, fcntl(out_fd_, F_GETFL, 0) | O_NONBLOCK);
        fcntl(err_fd_, F_SETFL, fcntl(err_fd_, F_GETFL, 0) | O_NONBLOCK);

        // Передаємо володіння
        stdin_pipe.close_read();
        stdout_pipe.close_write();
        stderr_pipe.close_write();
    }

    // Виконання одного запиту з жорстким тайм-аутом
    ExecutionResult invoke(std::string_view payload, std::chrono::milliseconds timeout) {
        ExecutionResult res;
        auto start_time = std::chrono::steady_clock::now();

        if (!is_alive_) {
            res.success = false;
            res.error_log = "Пісочниця не активна";
            return res;
        }

        // 1. Відправка корисного навантаження у stdin функції
        std::string input = std::string(payload) + "\n";
        size_t written = 0;
        while (written < input.size()) {
            ssize_t bytes = write(in_fd_, input.data() + written, input.size() - written);
            if (bytes <= 0) {
                if (errno == EPIPE) {
                    res.success = false;
                    res.error_log = "Процес пісочниці аварійно закрив stdin (EPIPE)";
                    is_alive_ = false;
                    return res;
                }
                res.success = false;
                res.error_log = "Помилка запису у канал stdin пісочниці";
                return res;
            }
            written += static_cast<size_t>(bytes);
        }

        // 2. Очікування завершення або вичерпання тайм-ауту через poll()
        struct pollfd pfd[2];
        pfd[0].fd = out_fd_;
        pfd[0].events = POLLIN | POLLHUP;
        pfd[1].fd = err_fd_;
        pfd[1].events = POLLIN | POLLHUP;

        std::string stdout_buffer;
        std::string stderr_buffer;
        bool completed = false;

        while (!completed) {
            auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::steady_clock::now() - start_time);
            
            if (elapsed >= timeout) {
                // Перевищено ліміт часу — примусове знищення процесу
                res.timed_out = true;
                terminate();
                break;
            }

            int remaining_ms = static_cast<int>((timeout - elapsed).count());
            int ret = poll(pfd, 2, std::min(remaining_ms, 50));

            if (ret < 0) {
                if (errno == EINTR) continue;
                break;
            }

            if (ret > 0) {
                char buf[4096];
                if (pfd[0].revents & POLLIN) {
                    ssize_t n = read(out_fd_, buf, sizeof(buf));
                    if (n > 0) stdout_buffer.append(buf, n);
                }
                if (pfd[1].revents & POLLIN) {
                    ssize_t n = read(err_fd_, buf, sizeof(buf));
                    if (n > 0) stderr_buffer.append(buf, n);
                }

                // Перевірка завершення процесу
                int status;
                pid_t wp = waitpid(pid_, &status, WNOHANG);
                if (wp == pid_) {
                    is_alive_ = false;
                    completed = true;
                    if (WIFEXITED(status)) {
                        res.exit_code = WEXITSTATUS(status);
                        res.success = (res.exit_code == 0);
                    } else if (WIFSIGNALED(status)) {
                        res.exit_code = 128 + WTERMSIG(status);
                        res.success = false;
                    }
                }
            }
        }

        auto end_time = std::chrono::steady_clock::now();
        res.duration_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
        res.response = stdout_buffer;
        res.error_log = stderr_buffer;

        // Збір статистики споживання пам'яті через getrusage
        struct rusage usage{};
        getrusage(RUSAGE_CHILDREN, &usage);
        res.max_rss_kb = usage.ru_maxrss;

        return res;
    }

    void terminate() noexcept {
        if (is_alive_ && pid_ > 0) {
            // М'яка спроба зупинки
            kill(pid_, SIGTERM);
            
            // Очікування 100 мс
            usleep(100'000);
            
            int status;
            if (waitpid(pid_, &status, WNOHANG) == 0) {
                // Примусове знищення процесу
                kill(pid_, SIGKILL);
                waitpid(pid_, &status, 0);
            }
            is_alive_ = false;
        }

        if (in_fd_ >= 0) { close(in_fd_); in_fd_ = -1; }
        if (out_fd_ >= 0) { close(out_fd_); out_fd_ = -1; }
        if (err_fd_ >= 0) { close(err_fd_); err_fd_ = -1; }
    }

    bool is_alive() const noexcept { return is_alive_; }
    pid_t pid() const noexcept { return pid_; }

private:
    std::string binary_path_;
    std::string function_id_;
    pid_t pid_{-1};
    bool is_alive_{false};
    int in_fd_{-1};
    int out_fd_{-1};
    int err_fd_{-1};
};

// Менеджер пулу теплих пісочниць
class FaaSWorkerPool {
public:
    explicit FaaSWorkerPool(size_t max_warm_instances_per_function = 4)
        : max_warm_(max_warm_instances_per_function) {}

    ExecutionResult dispatch(const std::string& function_id, 
                             const std::string& binary_path,
                             std::string_view payload, 
                             std::chrono::milliseconds timeout) {
        std::unique_ptr<SandboxInstance> sandbox;
        bool cold_start = false;

        // 1. Пошук теплого екземпляра у черзі
        auto& queue = warm_pools_[function_id];
        while (!queue.empty()) {
            sandbox = std::move(queue.front());
            queue.pop();
            if (sandbox && sandbox->is_alive()) {
                break;
            }
            sandbox.reset();
        }

        // 2. Якщо теплий екземпляр відсутній — виконуємо холодний старт
        if (!sandbox) {
            cold_start = true;
            sandbox = std::make_unique<SandboxInstance>(binary_path, function_id);
            sandbox->spawn();
        }

        // 3. Виконання запиту
        ExecutionResult res = sandbox->invoke(payload, timeout);
        res.was_cold_start = cold_start;

        // 4. Повернення екземпляра в теплий пул, якщо він живий і не зазнав аварії
        if (sandbox->is_alive() && !res.timed_out && res.success) {
            if (queue.size() < max_warm_) {
                queue.push(std::move(sandbox));
            } else {
                sandbox->terminate();
            }
        }

        return res;
    }

private:
    size_t max_warm_;
    std::unordered_map<std::string, std::queue<std::unique_ptr<SandboxInstance>>> warm_pools_;
};

int main() {
    std::cout << "[FaaS Worker] Диспетчер готовий до обробки подій\n";
    FaaSWorkerPool pool(2);

    // Симуляція першого виклику (Холодний старт)
    std::cout << "\n--- Запит #1 (Холодний старт) ---\n";
    auto res1 = pool.dispatch("echo-service", "/bin/cat", "{\"event\": \"order_created\"}", std::chrono::milliseconds(2000));
    std::cout << "Успіх: " << std::boolalpha << res1.success << "\n"
              << "Холодний старт: " << res1.was_cold_start << "\n"
              << "Час виконання: " << res1.duration_ms << " мс\n"
              << "Відповідь: " << res1.response;

    // Симуляція повторного виклику (Теплий запуск)
    std::cout << "\n--- Запит #2 (Теплий запуск) ---\n";
    auto res2 = pool.dispatch("echo-service", "/bin/cat", "{\"event\": \"payment_received\"}", std::chrono::milliseconds(2000));
    std::cout << "Успіх: " << std::boolalpha << res2.success << "\n"
              << "Холодний старт: " << res2.was_cold_start << "\n"
              << "Час виконання: " << res2.duration_ms << " мс\n"
              << "Відповідь: " << res2.response;

    return 0;
}
```
```py
import asyncio
import time
import os
import json
from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class ExecutionResult:
    success: bool
    timed_out: bool
    exit_code: int
    response: str
    error_log: str
    duration_ms: float
    was_cold_start: bool

class AsyncSandbox:
    def __init__(self, binary_path: str, function_id: str):
        self.binary_path = binary_path
        self.function_id = function_id
        self.process: Optional[asyncio.subprocess.Process] = None
        self.is_alive = False

    async def spawn(self):
        env = os.environ.copy()
        env["AWS_LAMBDA_FUNCTION_NAME"] = self.function_id
        env["LAMBDA_TASK_ROOT"] = "/tmp"

        self.process = await asyncio.create_subprocess_exec(
            self.binary_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        self.is_alive = True

    async def invoke(self, payload: str, timeout_sec: float) -> ExecutionResult:
        if not self.is_alive or self.process is None:
            return ExecutionResult(False, False, -1, "", "Sandbox not active", 0.0, False)

        start_time = time.perf_counter()
        timed_out = False
        stdout_data, stderr_data = b"", b""
        exit_code = 0

        try:
            input_bytes = (payload + "\n").encode("utf-8")
            stdout_data, stderr_data = await asyncio.wait_for(
                self.process.communicate(input_bytes),
                timeout=timeout_sec
            )
            exit_code = self.process.returncode or 0
            self.is_alive = False  # Процес завершив роботу
        except asyncio.TimeoutError:
            timed_out = True
            await self.terminate()

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        success = (exit_code == 0) and not timed_out

        return ExecutionResult(
            success=success,
            timed_out=timed_out,
            exit_code=exit_code,
            response=stdout_data.decode("utf-8", errors="replace"),
            error_log=stderr_data.decode("utf-8", errors="replace"),
            duration_ms=duration_ms,
            was_cold_start=False
        )

    async def terminate(self):
        if self.process and self.is_alive:
            try:
                self.process.terminate()
                await asyncio.sleep(0.1)
                if self.process.returncode is None:
                    self.process.kill()
            except ProcessLookupError:
                pass
            self.is_alive = False

class AsyncFaaSPool:
    def __init__(self, max_warm: int = 4):
        self.max_warm = max_warm
        self.pools: Dict[str, List[AsyncSandbox]] = {}

    async def dispatch(self, function_id: str, binary_path: str, payload: str, timeout_sec: float) -> ExecutionResult:
        pool = self.pools.setdefault(function_id, [])
        sandbox = None
        was_cold = False

        while pool:
            candidate = pool.pop(0)
            if candidate.is_alive:
                sandbox = candidate
                break

        if sandbox is None:
            was_cold = True
            sandbox = AsyncSandbox(binary_path, function_id)
            await sandbox.spawn()

        res = await sandbox.invoke(payload, timeout_sec)
        res.was_cold_start = was_cold
        return res
```
:::

---

## Масштабування мультиплексування: epoll проти poll при тисячах пісочниць

У наведеному прикладі диспетчер використовує системний виклик `poll()` для спостереження за парою дескрипторів однієї активної пісочниці. Проте у промислових серверах, де один процес-виконавець одночасно керує сотнями паралельних потоків виконання, лінійне сканування масиву дескрипторів `poll()` зі складністю `O(N)` створює надмірне навантаження на процесор.

Для високопродуктивних серверів ядро Linux надає підсистему **`epoll`** зі складністю `O(1)`:
- Замість передачі масиву дескрипторів під час кожного виклику, дескриптори каналів реєструються в системному об'єкті ядра один раз через `epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev)`;
- Системний виклик `epoll_wait()` переходить у стан сну і прокидається лише тоді, коли ядро Linux безпосередньо фіксує надходження пакетів або заповнення буфера пайпа;
- Використання тригерів по зміні стану (Edge-Triggered Mode, `EPOLLET`) дозволяє мінімізувати системні перемикання контексту, що є критичним для утримання стабільної затримки викликів менше 5 мілісекунд.

---

## Розбір критичних системних пасток реалізації

Створення власного FaaS-виконавця пов'язане з кількома прихованими системними проблемами операційної системи Linux:

### 1. Переповнення буфера каналу IPC (Pipe Buffer Deadlock)
Стандартний розмір системного буфера анонімного каналу `pipe` в ядрі Linux становить 65 536 байтів (64 КБ). Якщо функція користувача генерує понад 64 КБ даних у `stdout` або `stderr` без зчитування з боку батьківського процесу, системний виклик `write()` у дочірньому процесі блокується назавжди. 

Якщо водночас батьківський процес блокується у виклику `waitpid()`, очікуючи повного завершення дочірнього процесу перед початком зчитування каналів, виникає нерозв'язний стан взаємного блокування (англ. *deadlock*):
- Дочірній процес чекає, поки батьківський звільнить буфер каналу;
- Батьківський процес чекає, поки дочірній завершить роботу.

Щоб уникнути цього, реалізація обов'язково переводить дескриптори у неблокуючий режим (`O_NONBLOCK`) та виконує мультиплексування введення-виведення через `poll()`, паралельно вичитуючи дані з буферів під час виконання коду.

### 2. Запобігання накопиченню процесів-зомбі (Zombie Process Reaping)
Коли дочірній процес завершує роботу, його пам'ять звільняється, але запис у системній таблиці процесів ядра Linux зберігається зі статусом `Z` (Zombie) доти, доки батьківський процес не викличе функцію сімейства `wait()` або `waitpid()`.

Якщо виконавець обслуговує тисячі короткоживучих викликів і не вичитує статуси завершення, таблиця дескрипторів ядра `/proc/sys/kernel/pid_max` швидко вичерпується (типове значення за замовчуванням — 32 768). У результаті хост перестає бути здатним створити будь-який новий процес, а виклики `fork()` повертають помилку `EAGAIN: Resource temporarily unavailable`.

### 3. Обробка сигналу SIGPIPE при аварії пісочниці
Якщо пісочниця раптово зазнає збою (наприклад, аварія через `Segmentation Fault` або завершення за OOM Killer) під час того, як батьківський виконавець записує вхідне корисне навантаження у канал `stdin_pipe`, операційна система Linux надсилає сигнал `SIGPIPE` процесу, що виконує `write()`. 

За замовчуванням дія сигналу `SIGPIPE` — негайне аварійне завершення процесу без виклику деструкторів! Це призводить до падіння всього FaaS-воркера та втрати всіх паралельних пісочниць на цьому вузлі. Щоб захистити систему, виконавець зобов'язаний явно ігнорувати цей сигнал через `signal(SIGPIPE, SIG_IGN)` та обробляти помилку `EPIPE`, яку повертає системний виклик `write()`.

### 4. Двоетапне гарантоване припинення за тайм-аутом (Two-phase Termination)
Коли спливає ліміт часу, надсилання одиночного сигналу `SIGTERM` є недостатнім: користувацький код може встановити власний обробник сигналу через `sigaction()` і проігнорувати його або заблокуватися у системному виклику, який не переривається. 

Виконавець реалізує надійну двоетапну схему:
1. Спочатку процесу надсилається м'який сигнал `SIGTERM`, надаючи короткий часовий інтервал (100 мс) для скидання буферів і закриття з'єднань;
2. Якщо після цього неблокуюча перевірка `waitpid(pid, &status, WNOHANG)` показує, що процес усе ще живий, надсилається безумовний сигнал `SIGKILL`, який обробляється безпосередньо планувальником ядра і не може бути перехоплений або заблокований програмою.

### 5. Витік стану та очищення файлової системи (Scratchpad Isolation)
Коли пісочниця використовується повторно для кількох викликів поспіль, файли, записані в тимчасовий каталог `/tmp` під час першого виклику, залишаються доступними для наступного виклику. 

Якщо запити надходять від різних користувачів або містять конфіденційні платіжні дані, це призводить до критичної вразливості витоку інформації (англ. *Cross-Invocation Data Leakage*). Виробничий виконавець після завершення виклику зобов'язаний очищати каталог `/tmp` або використовувати окремий тимчасовий простір монтування на базі `tmpfs` для кожного запиту.

### 6. Деградація пам'яті та ліміт кількості повторних викликів (Sandbox Recycling)
Навіть у коректно написаному коді тривале повторне використання пісочниці призводить до поступової фрагментації купи пам'яті (Heap fragmentation) та прихованих витоків пам'яті у сторонніх бібліотеках. 

Виробничий FaaS-виконавець впроваджує політику ротації екземплярів (англ. *Max Invocations Policy*):
- Кожна пісочниця веде лічильник виконаних викликів;
- Після досягнення встановленої межі (наприклад, 10 000 викликів) або якщо споживання пам'яті `ru_maxrss` перевищує 85% виділеного ліміту, пісочниця не повертається до пулу, а плавно знищується через `terminate()`, а замість неї створюється свіжий екземпляр.

### 7. Захист від вичерпання дескрипторів файлів (FD Leaks)
Кожен запуск пісочниці створює три файлові канали `pipe` (шість файлових дескрипторів). Якщо батьківський процес забуде закрити невикористовувані кінці каналів (наприклад, кінець для читання у батька після копіювання дескриптора), процес швидко досягне системного ліміту `ulimit -n` (типово 1024 дескриптори на процес). 

Застосування шаблону проектування RAII (клас `PipeChannel`) гарантує, що дескриптори закриваються автоматично при виході зі скоупу функцій навіть за наявності винятків C++.

---

## Заморожування через cgroups freezer проти зупинки через SIGSTOP

У періоди між викликами платформа повинна припиняти використання процесора пісочницею, зберігаючи її пам'ять прогрітою. Існує два механізми призупинення:

1. **Сигнал `SIGSTOP`**: призупиняє процес на рівні сигналів Unix. Проте дочірній процес може перехопити поведінку батька або інші процеси можуть дізнатися про статус через системні виклики `ptrace`. Крім того, багатопотокові застосунки можуть залишатися частково активними, якщо сигнал доставлено лише одному потоку;
2. **Контрольна група `cgroup.freeze`**: ядро атомарно заморожує всі потоки та дочірні процеси контрольної групи на рівні планувальника ядра. Процес не отримує квантів часу CPU, а його таймери й сокети переходять у стан очікування.

Важливо враховувати поведінку мережевих з'єднань: під час заморожування процес не відповідає на пакети TCP Keepalive віддалених серверів баз даних (PostgreSQL, Redis). Якщо час заморожування перевищує тайм-аут бездіяльності сервера бази даних, при розморожуванні перший же запит до сокета завершиться помилкою `Connection reset by peer (RST)`. Тому якісні драйвери баз даних для безсерверних середовищ завжди перевіряють валідність з'єднання перед відправкою запиту або використовують протоколи без встановлення постійного з'єднання (HTTP/REST).

---

## Адаптивне керування розміром пулу та закон Літтла

Визначення оптимальної кількості теплих пісочниць на воркері спирається на закон Літтла (англ. *Little's Law*):

```
L = λ · W
де:
L — середня кількість одночасно необхідних пісочниць;
λ — інтенсивність надходження вхідних подій (запитів/с);
W — середня тривалість виконання одного виклику (секунд).
```

Виконавець веде експоненційне ковзне середнє (EMA) інтенсивності трафіку `λ`:

```
λ_new = α · λ_current + (1 - α) · λ_old
```

Якщо інтенсивність трафіку спадає, воркер поступово знищує надлишкові теплі екземпляри за алгоритмом LRU (англ. *Least Recently Used*), звільняючи пам'ять хоста під інші функції. Якщо трафік зростає, воркер підтримує запас попередньо прогрітих пісочниць, усуваючи затримки холодного старту для майбутніх запитів.

---

## Мережева фільтрація та ізоляція через veth-інтерфейси

Для забезпечення повної мережевої ізоляції виконавець налаштовує пару віртуальних інтерфейсів `veth` (англ. *Virtual Ethernet*):
- Один кінець пари розміщується в мережевому просторі назв хоста і підключається до внутрішнього мережевого мосту (Linux Bridge `br0`);
- Другий кінець пари переноситься всередину Network Namespace пісочниці під іменем `eth0`.

За допомогою підсистеми `nftables` виконавець застосовує правила пакетної фільтрації:
1. Забороняється будь-який прямий трафік між різними пісочницями на одному хості (East-West Traffic Isolation);
2. Дозволяється доступ лише до локального сервера Runtime API (`127.0.0.1:9001`) та вихідний доступ у глобальну мережу через NAT (SNAT);
3. Блокуються спроби звернення до внутрішніх службових адрес хоста (наприклад, метаданих гіпервізора або локальних портів демона Docker).

---

## Штатна зупинка та осушення пулу воркера (Graceful Drain)

Коли хост отримує команду на планове перезавантаження або виведення з експлуатації (наприклад, при оновленні ядра операційної системи чи заміні заліза), демон-виконавець ініціює процедуру штатного осушення (англ. *graceful drain*):

1. Воркер негайно сповіщає планувальник площини керування про зміну власного статусу на `DRAINING`. Площина керування припиняє направляти нові виклики на цей вузол;
2. Диспетчер очікує завершення всіх активних викликів, які перебувають у фазі `Invoke`, у межах їхніх індивідуальних дедлайнів;
3. Для всіх вільних пісочниць у теплому пулі викликається метод `terminate()`, звільняючи дескриптори, файлові канали та віртуальну пам'ять;
4. Після завершення останнього активного запиту демон видаляє мережеві інтерфейси `veth`, очищає cgroups і повертає статус успішного завершення хосту.

---

## Простеження та розбивка затримки виклику (Tracing Breakdown)

Для точного моніторингу затримки виконавець вимірює тривалість кожної мікрофази обробки запиту:

```
Загальна затримка виклику (Total Latency):
├── t_acquire: Отримання пісочниці (0.01 мс тепла / 45.0 мс холодна)
├── t_write:   Запис корисного навантаження у канал stdin (0.1–0.5 мс)
├── t_exec:    Фактичний час виконання бізнес-логіки в пісочниці
├── t_read:    Зчитування відповіді зі stdout/stderr (0.1–0.8 мс)
└── t_recycle: Очищення / повернення в чергу пулу (0.05 мс)
```

Вимірювання цих інтервалів дозволяє інженерам платформи виявляти вузькі місця у системі введення-виведення та оптимізувати розміри пулу теплих пісочниць для мінімізації «хвоста» затримок (p99 latency).
