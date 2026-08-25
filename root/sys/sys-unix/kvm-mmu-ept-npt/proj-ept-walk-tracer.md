# ⚙️ Дослідження поведінки KVM MMU: трасування EPT-подій і вимірювання затримок

Коли гостьова операційна система активно виділяє пам'ять, модифікує захист сторінок або бере участь у живій міграції (Live Migration), підсистема KVM MMU генерує сотні тисяч подій `EPT Violation` та змін записів таблиць тіньових сторінок (`SPTE`). Інструмент нижче демонструє, як безпосередньо з простору користувача зчитувати та аналізувати метрики KVM MMU через інтерфейс ядра `tracefs`.

## Задача та архітектура інструменту

Для діагностики продуктивності віртуалізації та локалізації вузьких місць у роботі з пам'яттю системному інженеру необхідно в реальному часі отримувати точну кількісну картину поведінки апаратного MMU. Необхідно відстежувати такі ключові метрики:
1. **Кількість виходів із віртуальної машини з причиною EPT Violation** (код виходу `0x30` / 48 на Intel VT-x або `VMEXIT_NPF` на процесорах AMD-V). Виникають при відкладеному виділенні сторінок (Demand Paging), перших доступах до пам'яті та спрацьовуванні механізму Dirty Logging.
2. **Частоту виникнення EPT Misconfiguration** (код виходу `0x31` / 49 на Intel). Виникають при зверненні до емульованих пристроїв MMIO (швидкий шлях Fast MMIO) або при некоректному форматі записів у таблицях EPT.
3. **Загальну кількість збоїв пам'яті (Page Faults)**, переданих у підсистему керування пам'яттю KVM.

Для низькорівневого зчитування подій інструмент взаємодіє з псевдофайловою системою `tracefs` (яка зазвичай монтується за шляхом `/sys/kernel/tracing/` або `/sys/kernel/debug/tracing/`). Робота з ядром будується за такою послідовністю:
- Перевірка наявності та монтування точки доступу до `tracefs`.
- Запис керуючого прапорця `1` у файл `enable` відповідних подій підсистеми KVM (`events/kvm/kvm_exit/enable` та `events/kvm/kvm_page_fault/enable`).
- Відкриття потокового файлу кільцевого буфера ядра `/sys/kernel/tracing/trace_pipe` для безперервного читання сформованих ядром текстових записів подій.
- Парсинг рядків у реальному часі, агрегація статистики в секундні інтервали та відображення частоти подій.
- Коректне перехоплення сигналів завершення (`SIGINT`, `SIGTERM`) із гарантованим вимкненням точок трасування, щоб уникнути деградації продуктивності хоста після зупинки утиліти.

## Механіка роботи кільцевого буфера trace_pipe

Ядро Linux виділяє для кожної підсистеми трасування ізольований кільцевий буфер (Ring Buffer) на кожне фізичне процесорне ядро хоста. Коли віртуальний процесор vCPU генерує подію `VM-exit`, обробник переривання в ядрі записує компактний бінарний дескриптор події в локальний буфер відповідного ядра.

Файл `trace_pipe` працює як потоковий інтерфейс над цими буферами:
- Читання є деструктивним: щойно рядок вичитано процесом користувача, ядро вивільняє відповідний слот пам'яті в кільцевому буфері.
- Якщо події надходять швидше, ніж застосунок встигає їх обробляти, ядро витісняє старі незчитані записи і генерує спеціальний маркер втрати подій `CPU X: [LOST N EVENTS]`.
- Читання є блокуючим: функція `read()` або `fgets()` блокує потік, поки хоча б одне ядро не згенерує нову подію.

## Реалізація утиліти на C та C++

Нижче наведено дві повноцінні, незалежні реалізації інструменту мовами C та сучасним C++20.

:::tabs
```c
/*
 * kvm_mmu_tracer.c — моніторинг подій KVM MMU та EPT через tracefs
 * Компіляція: gcc -O2 -Wall kvm_mmu_tracer.c -o kvm_mmu_tracer
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>
#include <time.h>

#define TRACE_BASE "/sys/kernel/tracing"
#define FALLBACK_TRACE_BASE "/sys/kernel/debug/tracing"

static volatile sig_atomic_t g_running = 1;

static void sig_handler(int sig) {
    (void)sig;
    g_running = 0;
}

static int write_file(const char *path, const char *val) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        return -1;
    }
    ssize_t len = strlen(val);
    if (write(fd, val, len) != len) {
        close(fd);
        return -1;
    }
    close(fd);
    return 0;
}

static const char *get_tracefs_root(void) {
    if (access(TRACE_BASE "/trace_pipe", R_OK) == 0) {
        return TRACE_BASE;
    }
    if (access(FALLBACK_TRACE_BASE "/trace_pipe", R_OK) == 0) {
        return FALLBACK_TRACE_BASE;
    }
    return NULL;
}

int main(void) {
    const char *root = get_tracefs_root();
    if (!root) {
        fprintf(stderr, "Помилка: tracefs не змонтовано або відсутні права root\n");
        return 1;
    }

    char path[256];
    snprintf(path, sizeof(path), "%s/events/kvm/kvm_exit/enable", root);
    if (write_file(path, "1") < 0) {
        perror("Не вдалося активувати kvm_exit");
        return 1;
    }

    snprintf(path, sizeof(path), "%s/events/kvm/kvm_page_fault/enable", root);
    write_file(path, "1");

    snprintf(path, sizeof(path), "%s/trace_pipe", root);
    FILE *pipe = fopen(path, "r");
    if (!pipe) {
        perror("Не вдалося відкрити trace_pipe");
        return 1;
    }

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    printf("Розпочато трасування KVM MMU подій (Ctrl+C для виходу)...\n");

    char line[1024];
    unsigned long long ept_violations = 0;
    unsigned long long ept_misconfigs = 0;
    unsigned long long page_faults = 0;
    unsigned long long other_exits = 0;

    time_t last_report = time(NULL);

    while (g_running && fgets(line, sizeof(line), pipe)) {
        if (strstr(line, "kvm_exit:")) {
            /* 0x30 = 48 (EPT Violation), 0x31 = 49 (EPT Misconfig) */
            if (strstr(line, "reason 0x30") || strstr(line, "reason EPT_VIOLATION")) {
                ept_violations++;
            } else if (strstr(line, "reason 0x31") || strstr(line, "reason EPT_MISCONFIG")) {
                ept_misconfigs++;
            } else {
                other_exits++;
            }
        } else if (strstr(line, "kvm_page_fault:")) {
            page_faults++;
        }

        time_t now = time(NULL);
        if (now - last_report >= 1) {
            printf("\r[KVM MMU] EPT Violations: %llu/s | Page Faults: %llu/s | Misconfigs: %llu/s | Інші виходи: %llu/s",
                   ept_violations, page_faults, ept_misconfigs, other_exits);
            fflush(stdout);
            ept_violations = 0;
            ept_misconfigs = 0;
            page_faults = 0;
            other_exits = 0;
            last_report = now;
        }
    }

    printf("\nЗавершення роботи. Вимикаємо точки трасування...\n");
    snprintf(path, sizeof(path), "%s/events/kvm/kvm_exit/enable", root);
    write_file(path, "0");
    snprintf(path, sizeof(path), "%s/events/kvm/kvm_page_fault/enable", root);
    write_file(path, "0");
    fclose(pipe);

    return 0;
}
```
```cpp
//
// kvm_mmu_tracer.cpp — сучасний ідіоматичний моніторинг KVM MMU на C++20
// Компіляція: g++ -std=c++20 -O2 -Wall kvm_mmu_tracer.cpp -o kvm_mmu_tracer_cpp
//
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <chrono>
#include <csignal>
#include <filesystem>
#include <memory>
#include <system_error>

namespace fs = std::filesystem;
using namespace std::chrono_literals;

namespace {
volatile std::sig_atomic_t g_running = 1;

void handle_signal(int) noexcept {
    g_running = 0;
}

class TracepointGuard {
public:
    explicit TracepointGuard(fs::path root_path)
        : root_(std::move(root_path)) {
        set_enabled("kvm/kvm_exit", true);
        set_enabled("kvm/kvm_page_fault", true);
    }

    ~TracepointGuard() {
        try {
            set_enabled("kvm/kvm_exit", false);
            set_enabled("kvm/kvm_page_fault", false);
        } catch (...) {
            // Деструктор не повинен викидати винятки
        }
    }

    TracepointGuard(const TracepointGuard&) = delete;
    TracepointGuard& operator=(const TracepointGuard&) = delete;

private:
    void set_enabled(std::string_view event, bool enable) {
        fs::path p = root_ / "events" / event / "enable";
        std::ofstream ofs(p);
        if (ofs.is_open()) {
            ofs << (enable ? "1\n" : "0\n");
        }
    }

    fs::path root_;
};

fs::path find_tracefs() {
    const fs::path primary = "/sys/kernel/tracing";
    const fs::path fallback = "/sys/kernel/debug/tracing";

    if (fs::exists(primary / "trace_pipe")) {
        return primary;
    }
    if (fs::exists(fallback / "trace_pipe")) {
        return fallback;
    }
    throw std::runtime_error("tracefs не знайдено (перевірте монтування та права sudo)");
}

struct MMUStats {
    uint64_t ept_violations = 0;
    uint64_t ept_misconfigs = 0;
    uint64_t page_faults = 0;
    uint64_t other_exits = 0;

    void reset() noexcept {
        ept_violations = 0;
        ept_misconfigs = 0;
        page_faults = 0;
        other_exits = 0;
    }
};
} // namespace

int main() {
    std::signal(SIGINT, handle_signal);
    std::signal(SIGTERM, handle_signal);

    try {
        const fs::path root = find_tracefs();
        TracepointGuard guard(root);

        std::ifstream pipe(root / "trace_pipe");
        if (!pipe.is_open()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити trace_pipe");
        }

        std::cout << "Трасування KVM MMU подій запущено. Очікування виходів...\n";

        MMUStats stats;
        std::string line;
        auto last_tick = std::chrono::steady_clock::now();

        while (g_running && std::getline(pipe, line)) {
            const std::string_view sv(line);

            if (sv.find("kvm_exit:") != std::string_view::npos) {
                if (sv.find("reason 0x30") != std::string_view::npos ||
                    sv.find("reason EPT_VIOLATION") != std::string_view::npos) {
                    stats.ept_violations++;
                } else if (sv.find("reason 0x31") != std::string_view::npos ||
                           sv.find("reason EPT_MISCONFIG") != std::string_view::npos) {
                    stats.ept_misconfigs++;
                } else {
                    stats.other_exits++;
                }
            } else if (sv.find("kvm_page_fault:") != std::string_view::npos) {
                stats.page_faults++;
            }

            const auto now = std::chrono::steady_clock::now();
            if (now - last_tick >= 1s) {
                std::cout << "\r[KVM MMU C++] EPT Violations: " << stats.ept_violations
                          << "/s | Page Faults: " << stats.page_faults
                          << "/s | Misconfigs: " << stats.ept_misconfigs
                          << "/s | Інші VM-exits: " << stats.other_exits << std::flush;
                stats.reset();
                last_tick = now;
            }
        }

        std::cout << "\nЗупинка трасування...\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

## Інтерпретація метрик та практичні висновки

1. **Стрибки EPT Violations**: Якщо під час старту застосунків або виділення пам'яті в гості частота EPT Violations сягає десятків тисяч на секунду, це свідчить про активну роботу Demand Paging (відкладеного виділення фреймів хостом). Якщо висока частота тримається стабільно протягом тривалого часу — можливо, увімкнено відстеження брудних сторінок (Dirty Logging під час міграції або створення бекапу наживо).
2. **Співвідношення з Huge Pages**: Перехід гостя на сторінки 2 МіБ зменшує кількість первинних EPT Violations у 512 разів, оскільки один збій виділяє одразу великий неперервний блок пам'яті замість 512 дрібних запитів.
3. **Наявність EPT Misconfigurations**: Поява Misconfigurations за відсутності високого навантаження на емульовані пристрої свідчить про наявність помилок у налаштуванні типів пам'яті MTRR/PAT або вичерпання підтримуваних залізом бітів адресації.

## Практичне тестування під навантаженням

Щоб перевірити коректність роботи інструменту, можна спровокувати спалах подій EPT Violation безпосередньо всередині віртуальної машини. Для цього достатньо запустити синтетичний генератор навантаження на пам'ять:

```bash
# Всередині гостьової віртуальної машини:
# Виділення та активний запис у 4 ГіБ пам'яті
stress-ng --vm 4 --vm-bytes 1G --vm-method all --timeout 30s
```

У цей момент на хості утиліта `kvm_mmu_tracer` покаже різкий стрибок метрики `EPT Violations` до 40 000–80 000 подій на секунду на етапі первинного заповнення сторінок, після чого частота знизиться до нуля, коли всі фізичні фрейми `HPA` будуть заповнені та прив'язані в EPT.

## Підводні камені та пастки трасування

- **Блокування читання з trace_pipe**: Потік `trace_pipe` працює як блокуючий канал (pipe). Якщо у віртуальній машині немає активності і процесори перебувають у стані сну `HLT`, нові події не надходитимуть, і лічильники оновляться лише після надходження наступного таймерного або зовнішнього переривання.
- **Оверхед глобального трасування**: Активація точки трасування `kvm_exit` без використання фільтра ядра поширюється на всі віртуальні машини та всі ядра vCPU хоста. На високонавантажених серверах із сотнями vCPU потік подій може перевантажити кільцевий буфер ядра (викликаючи втрату подій `[LOST EVENTS]`) та збільшити навантаження на процесори хоста на 5–15%. Для високопродуктивних середовищ рекомендується попередньо записувати вираз `exit_reason == 48` у файл `filter` події.
- **Привілеї доступу**: Будь-які операції запису у файли конфігурації `tracefs` вимагають прав суперкористувача `root` або наявності можливості `CAP_SYS_ADMIN`.
