# ⚙️ Практична реалізація резолвера символів kallsyms

Парсинг `/proc/kallsyms` у просторі користувача та динамічний пошук адрес усередині ядра вимагає урахування обмежень безпеки `kptr_restrict` та видалення експорту `kallsyms_lookup_name()` у ядрі 5.7+. Нижче наведено завершений проєкт користувацької утиліти та модуля ядра.

---

## 1. Концепція та архітектура проєкту

При розробці системних утиліт відлагодження інженерам часто необхідно перетворювати довільні адреси пам'яті (наприклад, з дампу `dmesg`, профілювальника `perf` або стеку eBPF) у людсько-читабельні назви функцій без підключення громіздких відлагоджувачів на кшталт `gdb`.

Проєкт розв'язує цю задачу на двох рівнях:

1. **Простір користувача (User-Space Resolver):** Утиліта відкриває псевдофайл `/proc/kallsyms`, динамічно зчитує всі записи символів, відфільтровує масковані нульові адреси (наслідки дії `kptr_restrict`), завантажує дані у динамічний масив у пам'яті RAM, сортує їх за зростанням адрес та надає бінарний пошук `O(log N)` для миттєвого знаходження функції та розрахунку зміщення у байтах.
2. **Простір ядра (Kernel-Space Probe Module):** Завантажуваний модуль ядра демонструє, як у сучасних ядрах Linux (версії 5.7+), де прямий експорт `kallsyms_lookup_name` видалено, безпечно отримати адресу будь-якого неекспортованого символу (наприклад, `sys_call_table`) за допомогою інструменту `kprobes` та вивести адреси у журнал через специфікатори `%pS`, `%ps` та `%pB`.

---

## 2. Реалізація у просторі користувача (User-Space)

Нижче наведено дві ідіоматичні реалізації утиліти користувацького простору: класичну версію мовою C (стандарт POSIX C99) та сучасну об'єктно-орієнтовану версію мовою C++20.

### Детальний аналіз алгоритму, вирівнювання пам'яті та обробки крайових випадків

Парсинг та аналіз віртуальної файлової системи `/proc/kallsyms` у користувацькому просторі вимагає ретельної обробки специфічних крайових випадків, пов'язаних із безпекою, продуктивністю кеш-пам'яті та форматом даних операційної системи Linux.

#### 1. Обробка параметра безпеки kptr_restrict
Якщо параметр sysctl `kernel.kptr_restrict` встановлено у значення `1`, а програма запускається від імені звичайного користувача без права `CAP_SYSLOG`, ядро повертає рядки, де замість дійсних 64-бітних віртуальних адрес виводиться нульовий заповнювач:

```
0000000000000000 T vfs_read
0000000000000000 T sys_open
```

Програма виявляє такі нульові записи `entry->address == 0` під час розбору кожного рядка за допомогою `sscanf` або `std::istringstream`. Такі записи ігноруються і не додаються до таблиці, оскільки виконувати бінарний пошук по масиву нулів неможливо. Якщо після завершення читання файлу лічильник дійсних адрес дорівнює нулю, утиліта повідомляє користувача про необхідність виклику програми через `sudo` або підвищення привілеїв.

#### 2. Динамічне виділення, вирівнювання структур та масштабування пам'яті
Кількість символів у сучасному ядрі Linux коливається від 50 000 до 250 000 залежно від включення `CONFIG_KALLSYMS_ALL` та кількості завантажених модулів. 

Структура `symbol_entry_t` розроблена з урахуванням вирівнювання пам'яті (англ. *memory alignment*): 64-бітне поле `address` розміщено першим, що гарантує відсутність додаткових невидимих байтів заповнення (padding) на 64-бітних архітектурах.
- У версії мовою **C** виділення пам'яті починається з базового буфера на 8192 елементи. При досягненні ліміту ємність подвоюється через `realloc()`. Це гарантує амортизовану складність додавання `O(1)`.
- У версії мовою **C++20** використовується клас `std::vector<SymbolEntry>`. Перед початком парсингу викликається `symbols_.reserve(65536)`, що запобігає зайвій фрагментації оперативної пам'яті та зменшує кількість системних викликів `brk`/`mmap`.

#### 3. Алгоритм бінарного пошуку та обчислення зміщення
Записи у `/proc/kallsyms` є переважно впорядкованими за базовим адресом ядра `vmlinux`, проте при завантаженні динамічних модулів ядра (`.ko`) нові символи виділяються у спеціальному діапазоні пам'яті модулів `0xffffffffc0000000+`. Це може порушувати загальну монотонність масиву.

Тому утиліта примусово виконує сортування масиву за допомогою швидкого сортування `qsort()` (у C) або оптимізованого алгоритму `std::ranges::sort()` (у C++) за ключем `address`. Складність сортування становить `O(N log N)`.

Після сортування для довільної шуканої адреси `target_addr` виконується бінарний пошук `upper_bound` зі складністю `O(log N)`:
- Пошук знаходить перший символ, адреса якого **суворо більша** за `target_addr`.
- Елемент, що передує йому (зменшення ітератора на 1), є функцією або змінною, всередині якої лежить шукана адреса.
- Байтове зміщення обчислюється за формулою: `offset = target_addr - symbol.address`.

:::tabs
```c
/* kallsyms_resolver.c — Ідіоматична реалізація мовою C (POSIX C99) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>

#define MAX_LINE_LEN 256
#define MAX_SYM_NAME 128

typedef struct {
    uint64_t address;
    char type;
    char name[MAX_SYM_NAME];
    char module[64];
} symbol_entry_t;

typedef struct {
    symbol_entry_t *entries;
    size_t count;
    size_t capacity;
} symbol_table_t;

static int compare_by_address(const void *a, const void *b) {
    const symbol_entry_t *sa = (const symbol_entry_t *)a;
    const symbol_entry_t *sb = (const symbol_entry_t *)b;
    if (sa->address < sb->address) return -1;
    if (sa->address > sb->address) return 1;
    return 0;
}

symbol_table_t *symbol_table_load(const char *filepath) {
    FILE *fp = fopen(filepath, "r");
    if (!fp) {
        perror("Помилка відкриття /proc/kallsyms");
        return NULL;
    }

    symbol_table_t *table = malloc(sizeof(symbol_table_t));
    if (!table) {
        fclose(fp);
        return NULL;
    }

    table->capacity = 8192;
    table->count = 0;
    table->entries = malloc(table->capacity * sizeof(symbol_entry_t));
    if (!table->entries) {
        free(table);
        fclose(fp);
        return NULL;
    }

    char line[MAX_LINE_LEN];
    while (fgets(line, sizeof(line), fp)) {
        if (table->count >= table->capacity) {
            size_t new_cap = table->capacity * 2;
            symbol_entry_t *new_entries = realloc(table->entries, new_cap * sizeof(symbol_entry_t));
            if (!new_entries) break;
            table->entries = new_entries;
            table->capacity = new_cap;
        }

        symbol_entry_t *entry = &table->entries[table->count];
        entry->module[0] = '\0';

        int parsed = sscanf(line, "%lx %c %127s [%63[^]]]",
                            &entry->address, &entry->type,
                            entry->name, entry->module);

        if (parsed >= 3) {
            /* Перевірка маскування kptr_restrict */
            if (entry->address != 0) {
                table->count++;
            }
        }
    }

    fclose(fp);
    qsort(table->entries, table->count, sizeof(symbol_entry_t), compare_by_address);
    return table;
}

const symbol_entry_t *symbol_table_lookup(const symbol_table_t *table, uint64_t addr, uint64_t *out_offset) {
    if (!table || table->count == 0) return NULL;

    size_t low = 0;
    size_t high = table->count - 1;
    size_t best_idx = table->count;

    while (low <= high) {
        size_t mid = low + (high - low) / 2;
        if (table->entries[mid].address <= addr) {
            best_idx = mid;
            low = mid + 1;
        } else {
            if (mid == 0) break;
            high = mid - 1;
        }
    }

    if (best_idx < table->count) {
        if (out_offset) {
            *out_offset = addr - table->entries[best_idx].address;
        }
        return &table->entries[best_idx];
    }
    return NULL;
}

void symbol_table_free(symbol_table_t *table) {
    if (table) {
        free(table->entries);
        free(table);
    }
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <hex_address>\n", argv[0]);
        return 1;
    }

    uint64_t target_addr = strtoull(argv[1], NULL, 16);
    symbol_table_t *table = symbol_table_load("/proc/kallsyms");
    if (!table) {
        fprintf(stderr, "Не вдалося завантажити таблицю символів. Перевірте kptr_restrict або права root.\n");
        return 1;
    }

    printf("Успішно завантажено %zu дійсних символів з /proc/kallsyms\n", table->count);

    uint64_t offset = 0;
    const symbol_entry_t *sym = symbol_table_lookup(table, target_addr, &offset);
    if (sym) {
        if (sym->module[0] != '\0') {
            printf("Адреса 0x%lx -> %s+0x%lx/??? [%s] (Тип: %c)\n",
                   target_addr, sym->name, offset, sym->module, sym->type);
        } else {
            printf("Адреса 0x%lx -> %s+0x%lx (Тип: %c)\n",
                   target_addr, sym->name, offset, sym->type);
        }
    } else {
        printf("Символ для адреси 0x%lx не знайдено.\n", target_addr);
    }

    symbol_table_free(table);
    return 0;
}
```
```cpp
// kallsyms_resolver.cpp — Ідіоматична реалізація мовою C++20 (RAII, STL, std::ranges)
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <algorithm>
#include <optional>
#include <cstdint>
#include <iomanip>
#include <stdexcept>

struct SymbolEntry {
    std::uint64_t address{0};
    char type{'?'};
    std::string name;
    std::string module;
};

class KernelSymbolResolver {
public:
    explicit KernelSymbolResolver(const std::string& kallsyms_path = "/proc/kallsyms") {
        load_from_file(kallsyms_path);
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return symbols_.size();
    }

    struct LookupResult {
        const SymbolEntry& symbol;
        std::uint64_t offset;
    };

    [[nodiscard]] std::optional<LookupResult> lookup(std::uint64_t address) const {
        if (symbols_.empty()) return std::nullopt;

        auto it = std::upper_bound(
            symbols_.begin(), symbols_.end(), address,
            [](std::uint64_t val, const SymbolEntry& entry) {
                return val < entry.address;
            }
        );

        if (it != symbols_.begin()) {
            --it;
            std::uint64_t offset = address - it->address;
            return LookupResult{*it, offset};
        }
        return std::nullopt;
    }

private:
    std::vector<SymbolEntry> symbols_;

    void load_from_file(const std::string& path) {
        std::ifstream file(path);
        if (!file.is_open()) {
            throw std::runtime_error("Не вдалося відкрити файл: " + path);
        }

        std::string line;
        symbols_.reserve(65536);

        while (std::getline(file, line)) {
            if (line.empty()) continue;

            std::istringstream iss(line);
            std::string addr_str;
            char type;
            std::string name;

            if (!(iss >> addr_str >> type >> name)) continue;

            std::uint64_t addr = std::stoull(addr_str, nullptr, 16);
            if (addr == 0) continue; // Фільтрація маскування kptr_restrict

            std::string module;
            std::string extra;
            if (iss >> extra && extra.front() == '[') {
                module = extra.substr(1, extra.find(']') - 1);
            }

            symbols_.push_back(SymbolEntry{addr, type, std::move(name), std::move(module)});
        }

        std::ranges::sort(symbols_, [](const SymbolEntry& a, const SymbolEntry& b) {
            return a.address < b.address;
        });
    }
};

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <hex_address>\n";
        return 1;
    }

    std::uint64_t target_addr = std::stoull(argv[1], nullptr, 16);

    try {
        KernelSymbolResolver resolver("/proc/kallsyms");
        std::cout << "Успішно завантажено " << resolver.size() << " дійсних символів.\n";

        if (auto result = resolver.lookup(target_addr)) {
            const auto& [sym, offset] = *result;
            std::cout << "Адреса 0x" << std::hex << target_addr
                      << " -> " << sym.name << "+0x" << offset;
            if (!sym.module.empty()) {
                std::cout << " [" << sym.module << "]";
            }
            std::cout << " (Тип: " << sym.type << ")\n";
        } else {
            std::cout << "Символ для адреси не знайдено.\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

---

## 3. Реалізація у просторі ядра (Kernel-Space Module)

Наведений нижче завантажуваний модуль ядра ілюструє роботу з `kallsyms` усередині ядра Linux. Оскільки у сучасних ядрах (5.7+) функцію `kallsyms_lookup_name` видалено з макросу експорту `EXPORT_SYMBOL`, модуль застосовує елегантний і безпечний спосіб її динамічного пошуку через підсистему `kprobes`.

### Принцип роботи, обробка помилок та внутрішньоядерна механіка kprobes:

1. **Реєстрація тимчасового зонда:** Модуль ініціалізує структуру `struct kprobe`, вказуючи рядкове ім'я символу `.symbol_name = "kallsyms_lookup_name"`.
2. **Внутрішній пошук kprobes:** Під час виклику `register_kprobe(&kp)` ядро Linux використовує власний внутрішній незахищений механізм пошуку точок трасування, знаходить віртуальну адресу цієї функції у `vmlinux` і заповнює поле `kp.addr`.
3. **Обробка можливих помилок:** Якщо функція `register_kprobe()` повертає від'ємне значення (наприклад, `-ENOENT`, якщо символ з якоїсь причини відсутній у підсистемі kprobes), модуль перериває завантаження і повертає помилку через `pr_err()`.
4. **Скасування зонда:** При успішній реєстрації модуль копіює адресу з `kp.addr` у локальний вказівник на функцію `my_kallsyms_lookup_name` і негайно скасовує зонд через `unregister_kprobe(&kp)`. Це мінімізує оверхед і не залишає впроваджених breakpoint-інструкцій у коді ядра.
5. **Виклики неекспортованих символів:** Зберігаючи знайдений вказівник, модуль викликає його для розшуку неекспортованої таблиці системних викликів `sys_call_table`.
6. **Друк логів у dmesg:** Демонструється автоматичне форматування адрес у лог ядра за допомогою модифікаторів `%pS`, `%ps` та `%pB`.

```c
/* kallsyms_probe_module.c — Завантажуваний модуль ядра Linux (C Kernel-Space) */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/kprobes.h>
#include <linux/kallsyms.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Unix Observability Course");
MODULE_DESCRIPTION("Демонстраційний модуль kallsyms та розв'язання неекспортованих символів у ядрі 5.7+");

typedef unsigned long (*kallsyms_lookup_name_t)(const char *name);
static kallsyms_lookup_name_t my_kallsyms_lookup_name = NULL;

static struct kprobe kp = {
    .symbol_name = "kallsyms_lookup_name",
};

static int __init kallsyms_demo_init(void)
{
    int ret;
    pr_info("=== [kallsyms_demo] Завантаження модуля ===\n");

    /* Крок 1: Реєстрація kprobe для отримання адреси kallsyms_lookup_name у ядрах 5.7+ */
    ret = register_kprobe(&kp);
    if (ret < 0) {
        pr_err("[kallsyms_demo] Не вдалося зареєструвати kprobe, помилка: %d\n", ret);
        return ret;
    }

    my_kallsyms_lookup_name = (kallsyms_lookup_name_t)kp.addr;
    unregister_kprobe(&kp);

    if (!my_kallsyms_lookup_name) {
        pr_err("[kallsyms_demo] Вказівник на kallsyms_lookup_name дорівнює NULL!\n");
        return -EINVAL;
    }

    pr_info("[kallsyms_demo] kallsyms_lookup_name знайдено за адресою: %ps (0x%px)\n",
            my_kallsyms_lookup_name, my_kallsyms_lookup_name);

    /* Крок 2: Динамічний пошук неекспортованого символу sys_call_table */
    unsigned long sys_call_table_addr = my_kallsyms_lookup_name("sys_call_table");
    if (sys_call_table_addr) {
        pr_info("[kallsyms_demo] sys_call_table знайдено за адресою: %pS\n",
                (void *)sys_call_table_addr);
    } else {
        pr_warn("[kallsyms_demo] Символ sys_call_table не знайдено.\n");
    }

    /* Крок 3: Демонстрація різних специфікаторів форматування %pS у printk */
    void *current_func_addr = (void *)kallsyms_demo_init;
    pr_info("[kallsyms_demo] %pS  : %pS\n", current_func_addr, current_func_addr);
    pr_info("[kallsyms_demo] %ps  : %ps\n", current_func_addr, current_func_addr);
    pr_info("[kallsyms_demo] %pB  : %pB\n", current_func_addr, current_func_addr);

    return 0;
}

static void __exit kallsyms_demo_exit(void)
{
    pr_info("=== [kallsyms_demo] Вивантаження модуля ===\n");
}

module_init(kallsyms_demo_init);
module_exit(kallsyms_demo_exit);
```

### Інструкція зі збірки та тестування

Для побудови модуля використовується стандартний Makefile ядра:

```makefile
obj-m += kallsyms_probe_module.o
KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	make -C $(KDIR) M=$(PWD) modules

clean:
	make -C $(KDIR) M=$(PWD) clean
```

Компіляція та запуск у системі:

```bash
# Збірка модуля
make

# Завантаження модуля у ядро
sudo insmod kallsyms_probe_module.ko

# Перегляд результатів виводу у системному журналі
sudo dmesg | tail -n 10

# Вивантаження модуля
sudo rmmod kallsyms_probe_module
```
