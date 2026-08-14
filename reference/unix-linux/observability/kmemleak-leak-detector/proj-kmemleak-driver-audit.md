# ⚙️ Практикум: Автоматизований аудит та локалізація витоків пам'яті у драйверах

<preknowlist>
- [Алокатори пам'яті ядра](book:unix-linux/kernel-memory-slab) — механізми kmalloc та free у ядрі Linux.
- [Псевдо-ФС: procfs, sysfs, debugfs](book:unix-linux/debugfs) — керування та читання даних з debugfs.
</preknowlist>

Практична локалізація витоків пам'яті в просторі ядра суттєво відрізняється від аналізу прикладних програм користувача. У прикладних додатках інструменти на кшталт Valgrind контролюють виконання коду через двійкову інструментацію, але у ядрі Linux такий підхід неможливий через високі накладні витрати та відсутність інтерпретатора. Інтеграція детектора Kmemleak у процес тестування вимагає чіткого розуміння життєвого циклу системного модуля, особливо у складних гілках обробки помилок (error recovery paths).

Більшість витоків пам'яті у реальних драйверах пристроїв виникають не у штатному потоці виконання, а під час обробки виняткових ситуацій: коли одна з п'яти алокацій у функції `probe()` зазнає збою, і код робить переходами `goto` некоректне вилучення раніше створених ресурсів. Оскільки мова C у ядрі не має вбудованої підтримки RAII (Resource Acquisition Is Initialization) або винятків (exceptions), відповідальність за послідовний розворот стеку виділених ресурсів у зворотному порядку повністю покладається на розробника.

Цей практикум демонструє повний цикл локалізації витоків пам'яті у системному драйвері: від створення модуля зі схованими помилками деалокації до побудови автоматизованого тестового стенду в просторі користувача та трансляції адрес ядра у конкретні рядки C-коду.

---

## 1. Сценарій: Драйвер із вкладеним витоком у гілці помилок

Розглянемо типову архітектуру драйвера пристрою. Драйвер виділяє головну структуру пристрою `struct dummy_dev`, яка містить вказівники на вкладені ресурси: кільцевий буфер обміну даними `struct dummy_ring` та безпосередній динамічний масив `data`.

У коді нижче реалізовано модуль ядра з прихованою помилкою. Під час вивантаження модуля розробник звільняє головну структуру та структуру кільцевого буфера, проте забуває деалокувати сам динамічний масив `ring->data`, на який посилався кільцевий буфер.

### Код проблемного модуля ядра (`dummy_leak_driver.c`):

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/slab.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Audit Test");
MODULE_DESCRIPTION("Buggy Driver for Kmemleak Audit");

struct dummy_ring {
    size_t capacity;
    u8 *data;
};

struct dummy_dev {
    int id;
    struct dummy_ring *ring;
};

static struct dummy_dev *g_device = NULL;

static int __init dummy_init(void)
{
    pr_info("dummy_leak_driver: Ініціалізація модуля...\n");

    /* 1. Виділяємо головну структуру пристрою */
    g_device = kmalloc(sizeof(struct dummy_dev), GFP_KERNEL);
    if (!g_device)
        return -ENOMEM;

    g_device->id = 42;

    /* 2. Виділяємо структуру кільцевого буфера */
    g_device->ring = kmalloc(sizeof(struct dummy_ring), GFP_KERNEL);
    if (!g_device->ring) {
        kfree(g_device);
        return -ENOMEM;
    }

    /* 3. Виділяємо буфер даних на 2048 байтів */
    g_device->ring->capacity = 2048;
    g_device->ring->data = kmalloc(g_device->ring->capacity, GFP_KERNEL);
    if (!g_device->ring->data) {
        kfree(g_device->ring);
        kfree(g_device);
        return -ENOMEM;
    }

    pr_info("dummy_leak_driver: Успішно завантажено, dev=%px, ring=%px, data=%px\n",
            g_device, g_device->ring, g_device->ring->data);
    return 0;
}

static void __exit dummy_exit(void)
{
    pr_info("dummy_leak_driver: Вивантаження модуля...\n");

    if (g_device) {
        if (g_device->ring) {
            /* ПОМИЛКА 1: Забули звільнити g_device->ring->data ! */
            kfree(g_device->ring);
        }
        /* ПОМИЛКА 2: Звільняємо g_device, втрачаючи посилання на data */
        kfree(g_device);
        g_device = NULL;
    }

    pr_info("dummy_leak_driver: Модуль вивантажено.\n");
}

module_init(dummy_init);
module_exit(dummy_exit);
```

### Механізм витоку у динамічній пам'яті ядра
Під час виконання функції `dummy_exit()` послідовно викликаються `kfree(g_device->ring)` та `kfree(g_device)`. Дерево слабів SLUB повертає ці два блоки у загальний пул вільної пам'яті. Однак динамічний масив `g_device->ring->data` розміром 2048 байтів залишається виділеним.

Оскільки єдиний вказівник на `data` містився у полі `g_device->ring->data`, після деалокації `ring` адреса буфера виявляється повністю втраченою. Глобальна змінна `g_device` скидається в `NULL`. При наступному проході Kmemleak сканер перевірить усі кореневі регіони ядра (`.data`, `.bss`, стеки) і підтвердить, що на блок `2048 байтів` не посилається жодна адреса у пам'яті.

Подібні помилки вкладеної деалокації часто виникають при передчасному поверненні з функцій через умовні оператори `return` або при неправильному порядковому зв'язуванні міток `goto out_err_free_ring:` у великих драйверах пристроїв.

---

## 2. Автоматизація тестування у просторі користувача

Для запобігання появі витоків у релізних версіях драйверів тестування необхідно автоматизувати у конвеєрі CI/CD (Continuous Integration). Програма тестування повинна виконати скидання попереднього стану Kmemleak, завантажити та вивантажити модуль, викликати синхронне сканування пам'яті через `debugfs` та проаналізувати вміст `/sys/kernel/debug/kmemleak`.

Записи у файл `/sys/kernel/debug/kmemleak` є блокуючими: коли процес користувача пише рядок `scan\n`, системний виклик `write()` не повертає керування доти, доки потік ядра не завершить повний обхід графу об'єктів.

Нижче наведено ідіоматичні реалізації інструменту тестування мовами C та C++.

:::tabs
```c
/* runner.c — C11 інструмент для автоматизації сканування Kmemleak */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdbool.h>

#define KMEMLEAK_PATH "/sys/kernel/debug/kmemleak"
#define BUF_SIZE 8192

static bool write_cmd(const char *cmd) {
    int fd = open(KMEMLEAK_PATH, O_WRONLY);
    if (fd < 0) {
        perror("Помилка відкриття " KMEMLEAK_PATH " для запису");
        return false;
    }
    ssize_t len = strlen(cmd);
    if (write(fd, cmd, len) != len) {
        perror("Помилка відправки команди у kmemleak");
        close(fd);
        return false;
    }
    close(fd);
    return true;
}

int main(void) {
    printf("[+] Очищення попередніх звітів kmemleak...\n");
    if (!write_cmd("clear\n")) return EXIT_FAILURE;

    printf("[+] Симуляція дій: завантаження та вивантаження модуля...\n");
    if (system("modprobe dummy_leak_driver 2>/dev/null || insmod ./dummy_leak_driver.ko") != 0) {
        fprintf(stderr, "[-] Не вдалося завантажити модуль\n");
        return EXIT_FAILURE;
    }
    sleep(1);
    system("rmmod dummy_leak_driver");

    printf("[+] Ініціація примусового сканування (scan)...\n");
    if (!write_cmd("scan\n")) return EXIT_FAILURE;

    printf("[+] Читання результатів аудіювання...\n");
    int fd = open(KMEMLEAK_PATH, O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття kmemleak для читання");
        return EXIT_FAILURE;
    }

    char buffer[BUF_SIZE];
    ssize_t bytes_read = read(fd, buffer, sizeof(buffer) - 1);
    close(fd);

    if (bytes_read <= 0) {
        printf("[SUCCESS] Витоків пам'яті не виявлено!\n");
        return EXIT_SUCCESS;
    }

    buffer[bytes_read] = '\0';
    printf("[WARNING] ЗНАЙДЕНО ВИ ТІК ПАМ'ЯТІ:\n%s\n", buffer);
    return EXIT_FAILURE;
}
```
```cpp
// runner.cpp — C++20 ідіоматичний інструмент аудіювання Kmemleak
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <thread>
#include <chrono>
#include <cstdlib>
#include <filesystem>

namespace fs = std::filesystem;
using namespace std::chrono_literals;

class KmemleakController {
    fs::path debugfs_path_;

public:
    explicit KmemleakController(fs::path path = "/sys/kernel/debug/kmemleak")
        : debugfs_path_(std::move(path)) {}

    bool send_command(std::string_view cmd) const {
        std::ofstream ofs(debugfs_path_);
        if (!ofs.is_open()) return false;
        ofs << cmd << std::endl;
        return ofs.good();
    }

    [[nodiscard]] std::string read_reports() const {
        std::ifstream ifs(debugfs_path_);
        if (!ifs.is_open()) return {};
        return std::string((std::istreambuf_iterator<char>(ifs)),
                            std::istreambuf_iterator<char>());
    }
};

int main() {
    KmemleakController controller;

    std::cout << "[+] Очищення стану Kmemleak...\n";
    if (!controller.send_command("clear")) {
        std::cerr << "[-] Помилка доступу до debugfs. Перевірте root-права.\n";
        return EXIT_FAILURE;
    }

    std::cout << "[+] Запуск циклу тестування драйвера...\n";
    std::system("insmod ./dummy_leak_driver.ko && rmmod dummy_leak_driver");

    std::this_thread::sleep_for(500ms);

    std::cout << "[+] Запуск сканування пам'яті ядра...\n";
    if (!controller.send_command("scan")) {
        std::cerr << "[-] Не вдалося відправити команду scan.\n";
        return EXIT_FAILURE;
    }

    const auto report = controller.read_reports();
    if (report.empty()) {
        std::cout << "[SUCCESS] Пам'ять ядра чиста. Витоків немає.\n";
        return EXIT_SUCCESS;
    }

    std::cout << "[DEFECT] Виявлено витік пам'яті у драйвері!\n";
    std::cout << report << std::endl;
    return EXIT_FAILURE;
}
```
:::

---

## 3. Аналіз звіту Kmemleak та декодування адрес

Після виконання тесту файл `/sys/kernel/debug/kmemleak` буде містити текстовий звіт про втрачений блок:

```text
unreferenced object 0xffff8881034c2000 (size 2048):
  comm "insmod", pid 2415, jiffies 4294951022 (age 5.240s)
  hex dump (first 32 bytes):
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace:
    [<00000000d1a2b3c4>] kmem_cache_alloc_trace+0x140/0x2c0
    [<00000000f4e3d2a1>] dummy_init+0x68/0xa0 [dummy_leak_driver]
    [<0000000081d2e5b6>] do_one_initcall+0x46/0x200
    [<0000000072a4c1f8>] do_init_module+0x5c/0x260
```

### Покроковий алгоритм розшифровки джерела витоку

1. **Аналіз зсуву у символьній таблиці ELF:** Звіт показує, що алокацію буфера виконано у функції `dummy_init` за відносним зсувом `+0x68` всередині модуля `dummy_leak_driver`.
2. **Декодування через `decode_stacktrace.sh`:**
   У вихідному коді ядра Linux є утиліта `scripts/decode_stacktrace.sh`, яка автоматично зіставляє віртуальні адреси з заголовками ELF та вихідними файлами C за наявності символів відлагодження (скомпільтовано з `CONFIG_DEBUG_INFO=y`):

   ```bash
   ./scripts/decode_stacktrace.sh ./vmlinux . < /sys/kernel/debug/kmemleak
   ```

   Результат виводу покаже точний номер рядка C-коду:

   ```text
   dummy_init (E:/develop/courses/dummy_leak_driver.c:42)
   ```

3. **Виправлення сирцевого коду:**
   У функції завершення роботи модуля `dummy_exit` додаємо звільнення вкладеного масиву `ring->data` перед деалокацією самої структури кільця:

   ```c
   static void __exit dummy_exit(void)
   {
       if (g_device) {
           if (g_device->ring) {
               /* ВИПРАВЛЕННЯ: Спочатку звільняємо динамічний масив даних */
               kfree(g_device->ring->data);
               kfree(g_device->ring);
           }
           kfree(g_device);
           g_device = NULL;
       }
   }
   ```

4. **Верифікація та чистий базлайн:**
   Після перекомпіляції модуля та повторного запуску інструменту `runner` (або `runner.cpp`) Kmemleak підтвердить відсутність втрачених об'єктів, а програма виведе підтвердження `[SUCCESS] Пам'ять ядра чиста`. 

---

## 4. Специфічні крайові випадки при аудиті реальних драйверів

Під час проведення практичного аудиту складних системних драйверів (наприклад, мережевих адаптерів Ethernet/Wi-Fi або контролерів накопичувачів NVMe) розробники часто зіштовхуються з нестандартними моделями управління пам'яттю, які вимагають додаткового анотування коду.

### 1. Драйвери DMA та апаратні кільцеві буфери
Драйвери пристроїв часто виділяють неперервні буфери для прямого доступу до пам'яті через виклики `dma_alloc_coherent()`. Функції DMA повертають фізичну адресу для контролера та віртуальну адресу для ядра. Якщо віртуальний вказівник зберігається у структурі, яка піддається маскуванню або зберігається в апаратному регістрі PCI, Kmemleak може видати False Positive. У таких випадках у функції ініціалізації буфера слід викликати `kmemleak_not_leak(virt_addr)` або `kmemleak_ignore(virt_addr)`.

### 2. Власні пули пам'яті (Memory Pools & Slab Caches)
Якщо драйвер створює власний приватний кеш через `kmem_cache_create()` або бере сторінки з `mempool_create()`, Kmemleak за замовчуванням відстежує лише самі блоки слабу. Якщо у цьому пулі реалізовано власну логіку повторного використання елементів без виклику `kfree()`, Kmemleak може вважати елементи витоками. Розробник повинен явно викликати `kmemleak_alloc()` при вилученні елемента з пулу та `kmemleak_free()` при поверненні в пул.

### 3. Асинхронні обробники та таймери ядра
Паралельні робочі черги (`workqueues`) та таймери ядра (`timer_list`) можуть виділяти пам'ять в асинхронному контексті. Під час виконання тестування важливо пересвідчитися, що всі скасовані робочі задачі (`cancel_work_sync()`) завершили своє виконання до момент початку сканування Kmemleak, інакше об'єкти тимчасового обробника будуть помилково класифіковані як недосяжні.
