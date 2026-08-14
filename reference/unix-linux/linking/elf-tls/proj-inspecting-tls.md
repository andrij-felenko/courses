# ⚙️ Практичне дослідження та аналіз TLS у коді

Цей практичний посібник містить повні, готові до компіляції приклади вихідного коду мовами C та C++ для аналізу моделей доступу до Thread-Local Storage, прямої маніпуляції та зчитання регістра `FS` на архітектурі x86_64, а також покрокові інструкції з дослідження готових бінарних файлів інструментами `readelf`, `objdump` та системним налагоджувачем `gdb`.

## 1. Дослідження адрес пам'яті та регістра FS у багатопотоковому середовищі

Під час аналізу роботи TLS принципово важливо побачити, як змінюються адреси потоко-локальних змінних у фізично різних потоках виконання та яке відношення вони мають до базової адреси регістра `FS`.

У наведених нижче прикладах створюється декілька паралельних потоків. Кожен потік визначає власну базову адресу TCB (читаючи self-pointer за зміщенням `FS:0`) і розраховує байтові різниці між адресами `thread_local` змінних та базою `FS`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <asm/prctl.h>
#include <sys/prctl.h>
#include <unistd.h>

int arch_prctl(int code, unsigned long *addr);

/* Оголошення TLS-змінних з різними специфікованими моделями доступу */
__thread int global_tls_var = 100;
__attribute__((tls_model("local-exec"))) __thread int le_tls_var = 200;
__attribute__((tls_model("initial-exec"))) __thread int ie_tls_var = 300;

void print_tls_info(const char *thread_name) {
    uintptr_t fs_base = 0;
    uintptr_t fs_syscall = 0;
    
    /* Зчитування значення self-pointer з FS:0 за допомогою асемблерної вставки */
#if defined(__x86_64__)
    __asm__ __volatile__("mov %%fs:0, %0" : "=r"(fs_base));
#endif

    /* Альтернативне зчитування через системний виклик arch_prctl */
    arch_prctl(ARCH_GET_FS, &fs_syscall);

    printf("=== [%s] (ID потоку: %lu) ===\n", thread_name, (unsigned long)pthread_self());
    printf("  Базова адреса FS (з FS:0): 0x%lx\n", (unsigned long)fs_base);
    printf("  Базова адреса FS (з syscall): 0x%lx\n", (unsigned long)fs_syscall);
    
    /* Обчислення від'ємних або позитивних зміщень у байтах */
    intptr_t off_global = (char*)&global_tls_var - (char*)fs_base;
    intptr_t off_le     = (char*)&le_tls_var - (char*)fs_base;
    intptr_t off_ie     = (char*)&ie_tls_var - (char*)fs_base;

    printf("  &global_tls_var: 0x%p | зміщення від FS: %ld байтів\n", (void*)&global_tls_var, (long)off_global);
    printf("  &le_tls_var:     0x%p | зміщення від FS: %ld байтів\n", (void*)&le_tls_var, (long)off_le);
    printf("  &ie_tls_var:     0x%p | зміщення від FS: %ld байтів\n", (void*)&ie_tls_var, (long)off_ie);
    printf("\n");
}

void* worker_thread(void* arg) {
    print_tls_info((const char*)arg);
    return NULL;
}

int main(void) {
    pthread_t thread1, thread2;

    print_tls_info("Головний потік (Main)");

    pthread_create(&thread1, NULL, worker_thread, "Робочий потік 1");
    pthread_create(&thread2, NULL, worker_thread, "Робочий потік 2");

    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    return 0;
}
```
```cpp
#include <iostream>
#include <thread>
#include <vector>
#include <string_view>
#include <format>
#include <cstdint>
#include <asm/prctl.h>
#include <sys/prctl.h>

extern "C" int arch_prctl(int code, unsigned long *addr);

// Оголошення потоко-локальних змінних у C++11 із вибором моделей доступу
thread_local int global_tls_var = 100;
[[gnu::tls_model("local-exec")]] thread_local int le_tls_var = 200;
[[gnu::tls_model("initial-exec")]] thread_local int ie_tls_var = 300;

class TLSInspector {
public:
    static std::uintptr_t get_fs_base() noexcept {
        std::uintptr_t fs_base = 0;
#if defined(__x86_64__)
        __asm__ __volatile__("mov %%fs:0, %0" : "=r"(fs_base));
#endif
        return fs_base;
    }

    static std::uintptr_t get_fs_via_syscall() noexcept {
        unsigned long fs_syscall = 0;
        ::arch_prctl(ARCH_GET_FS, &fs_syscall);
        return fs_syscall;
    }

    static void print_info(std::string_view thread_name) {
        const auto fs_base = get_fs_base();
        const auto fs_syscall = get_fs_via_syscall();
        const auto* fs_ptr = reinterpret_cast<const char*>(fs_base);

        std::cout << std::format("=== [{}] (ID: {}) ===\n", thread_name, std::this_thread::get_id());
        std::cout << std::format("  Базова адреса FS (з FS:0): 0x{:x}\n", fs_base);
        std::cout << std::format("  Базова адреса FS (з syscall): 0x{:x}\n", fs_syscall);

        const auto off_global = reinterpret_cast<const char*>(&global_tls_var) - fs_ptr;
        const auto off_le     = reinterpret_cast<const char*>(&le_tls_var) - fs_ptr;
        const auto off_ie     = reinterpret_cast<const char*>(&ie_tls_var) - fs_ptr;

        std::cout << std::format("  &global_tls_var: 0x{:p} | зміщення від FS: {} байтів\n",
                                 static_cast<const void*>(&global_tls_var), off_global);
        std::cout << std::format("  &le_tls_var:     0x{:p} | зміщення від FS: {} байтів\n",
                                 static_cast<const void*>(&le_tls_var), off_le);
        std::cout << std::format("  &ie_tls_var:     0x{:p} | зміщення від FS: {} байтів\n\n",
                                 static_cast<const void*>(&ie_tls_var), off_ie);
    }
};

int main() {
    TLSInspector::print_info("Головний потік (Main)");

    std::vector<std::jthread> threads;
    threads.emplace_back([] { TLSInspector::print_info("Робочий потік 1"); });
    threads.emplace_back([] { TLSInspector::print_info("Робочий потік 2"); });

    return 0;
}
```
:::

### Покроковий аналіз результатів виконання:

При запуску скомпільованої програми ви побачите консольний вивід подібного вигляду:

```text
=== [Головний потік (Main)] (ID потоку: 140737353889536) ===
  Базова адреса FS (з FS:0): 0x7ffff7da2740
  Базова адреса FS (з syscall): 0x7ffff7da2740
  &global_tls_var: 0x7ffff7da273c | зміщення від FS: -4 байтів
  &le_tls_var:     0x7ffff7da2738 | зміщення від FS: -8 байтів
  &ie_tls_var:     0x7ffff7da2734 | зміщення від FS: -12 байтів

=== [Робочий потік 1] (ID потоку: 140737286788608) ===
  Базова адреса FS (з FS:0): 0x7ffff759f640
  Базова адреса FS (з syscall): 0x7ffff759f640
  &global_tls_var: 0x7ffff759f63c | зміщення від FS: -4 байтів
  &le_tls_var:     0x7ffff759f638 | зміщення від FS: -8 байтів
  &ie_tls_var:     0x7ffff759f634 | зміщення від FS: -12 байтів
```

#### Ключові висновки з експерименту:
1. **Збіг адрес отримання регістра**: адреса `FS`, зчитана з self-pointer за зміщенням `FS:0`, до останнього біта збігається зі значенням `ARCH_GET_FS`, повернутим системним викликом `arch_prctl`. Зчитування через `FS:0` виконується за 1 інструкцію `mov`, тоді як системний виклик `arch_prctl` вимагає перемикання контексту в режим ядра.
2. **Різні базові адреси `FS` для різних потоків**: кожен потік має власну унікальну адресу TCB (`0x7ffff7da2740` для головного потоку проти `0x7ffff759f640` для робочого потоку).
3. **Ідентичність від'ємних зміщень**: незважаючи на те, що абсолютні віртуальні адреси змінних у двох потоках абсолютно різні, їхні зміщення відносно регістра `FS` є **абсолютно однаковими** (`-4`, `-8`, `-12` байтів).
4. **Підтвердження топології Variant II**: усі зміщення відносно `FS` мають від'ємне значення, що точно відповідає архітектурній специфікації ELF TLS для x86_64, де дані TLS розміщуються безпосередньо перед управляючою структурою TCB.

## 2. Аналіз динамічного завантаження плагінів через dlopen

Для дослідження лінивої алокації TLS (Lazy TLS Allocation) та роботи вектора DTV створимо динамічну бібліотеку-плагін `libplugin.so`, яка завантажується за допомогою `dlopen()`.

### Крок 2.1. Вихідний код плагіна (plugin.c / plugin.cpp)

Скомпілюємо наступний код у динамічну бібліотеку:

:::tabs
```c
#include <stdio.h>

/* Змінна у динамічному плагіні за замовчуванням дістає модель General Dynamic */
__thread int plugin_counter = 42;

void plugin_print_tls(void) {
    unsigned long fs_base = 0;
#if defined(__x86_64__)
    __asm__ __volatile__("mov %%fs:0, %0" : "=r"(fs_base));
#endif

    plugin_counter += 10;
    printf("[libplugin.so] &plugin_counter: 0x%p (значення: %d)\n", 
           (void*)&plugin_counter, plugin_counter);
    printf("[libplugin.so] Базова адреса FS: 0x%lx\n", fs_base);
    printf("[libplugin.so] Зверніть увагу: адреса не є статичним від'ємним зміщенням від FS!\n");
}
```
```cpp
#include <iostream>
#include <format>
#include <cstdint>

extern "C" {

thread_local int plugin_counter = 42;

void plugin_print_tls() {
    std::uintptr_t fs_base = 0;
#if defined(__x86_64__)
    __asm__ __volatile__("mov %%fs:0, %0" : "=r"(fs_base));
#endif

    plugin_counter += 10;
    std::cout << std::format("[libplugin.so] &plugin_counter: 0x{:p} (значення: {})\n",
                             static_cast<void*>(&plugin_counter), plugin_counter);
    std::cout << std::format("[libplugin.so] Базова адреса FS: 0x{:x}\n", fs_base);
    std::cout << "[libplugin.so] Адреса алокована динамічно через DTV та __tls_get_addr\n";
}

}
```
:::

Команда для збирання динамічної бібліотеки:
```bash
gcc -shared -fPIC plugin.c -o libplugin.so
```

### Крок 2.2. Код головного хоста завантаження (host.c / host.cpp)

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <pthread.h>

typedef void (*plugin_func_t)(void);

void* thread_routine(void* arg) {
    const char* lib_path = (const char*)arg;
    
    printf("--> [Worker Thread] Завантаження %s через dlopen()...\n", lib_path);
    void* handle = dlopen(lib_path, RTLD_NOW);
    if (!handle) {
        fprintf(stderr, "dlopen error: %s\n", dlerror());
        return NULL;
    }

    plugin_func_t func = (plugin_func_t)dlsym(handle, "plugin_print_tls");
    if (func) {
        /* Перший виклик розвертає ліниву алокацію в DTV через __tls_get_addr */
        func();
    }

    dlclose(handle);
    return NULL;
}

int main(int argc, char** argv) {
    const char* plugin_path = (argc > 1) ? argv[1] : "./libplugin.so";

    pthread_t thread;
    pthread_create(&thread, NULL, thread_routine, (void*)plugin_path);
    pthread_join(thread, NULL);

    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <thread>
#include <dlfcn.h>
#include <stdexcept>

class DynamicPlugin {
    void* handle_{nullptr};

public:
    explicit DynamicPlugin(std::string_view path) {
        handle_ = ::dlopen(path.data(), RTLD_NOW);
        if (!handle_) {
            throw std::runtime_error(::dlerror());
        }
    }

    ~DynamicPlugin() {
        if (handle_) {
            ::dlclose(handle_);
        }
    }

    void execute(std::string_view symbol_name) {
        using func_t = void (*)();
        auto func = reinterpret_cast<func_t>(::dlsym(handle_, symbol_name.data()));
        if (!func) {
            throw std::runtime_error(::dlerror());
        }
        func();
    }
};

int main(int argc, char** argv) {
    const std::string_view plugin_path = (argc > 1) ? argv[1] : "./libplugin.so";

    std::jthread worker([plugin_path] {
        try {
            std::cout << "--> [Worker Thread] Динамічне завантаження плагіна...\n";
            DynamicPlugin plugin(plugin_path);
            plugin.execute("plugin_print_tls");
        } catch (const std::exception& ex) {
            std::cerr << "Помилка плагіна: " << ex.what() << '\n';
        }
    });

    return 0;
}
```
:::

Збирання та запуск:
```bash
gcc host.c -o host -ldl -lpthread
./host ./libplugin.so
```

## 3. Комплексний аналіз ELF-бінарників інструментами CLI

У системному програмуванні для аналізу компонування пам'яті та релокацій у виконуваних файлах використовується серія утиліт GNU Binary Utilities (binutils).

### 3.1. Інспектування заголовків PT_TLS через readelf

Для аналізу характеристик шаблону TLS виконуємо утиліту `readelf` з прапорцем `-l` (Program Headers):

```bash
readelf -l ./host | grep -A 2 TLS
```

Консольний результат:
```text
  TLS            0x0000000000002e10 0x0000000000403e10 0x0000000000403e10
                 0x0000000000000020 0x0000000000000060  R      0x10
```

#### Детальний розбір параметрів виводу:
- **`Offset = 0x2e10`**: фізичне зміщення секції `.tdata` всередині ELF-файла на диску.
- **`VirtAddr = 0x403e10`**: віртуальна адреса шаблону при статичному відображенні у віртуальну пам'ять.
- **`FileSiz = 0x20` (32 байти)**: сумарний розмір ініціалізованих змінних секції `.tdata`. Динамічний завантажувач скопіює саме 32 байти під час створення нового потоку.
- **`MemSiz = 0x60` (96 байтів)**: повний обсяг пам'яті TLS-блоку. Алгебраїчна різниця `0x60 - 0x20 = 0x40` (64 байти) визначає обсяг неініціалізованої секції `.tbss`, яку завантажувач занулить у пам'яті.
- **`Align = 0x10` (16 байтів)**: максимальне вирівнювання базової адреси TLS-блоку у пам'яті.

### 3.2. Перевірка релокаційних записів TLS

Щоб з'ясувати, які саме типи релокацій згенеровано компілятором для TLS-змінних у динамічній бібліотеці або виконуваному файлі, застосовується прапор `-r` (Relocations):

```bash
readelf -r ./libplugin.so | grep TLS
```

Приклад виводу для бібліотеки з моделью General Dynamic:
```text
000000003fd8  000200000013 R_X86_64_TLSGD      0000000000000000 plugin_counter + 0
```
Тип релокації `R_X86_64_TLSGD` свідчить про те, що динамічний завантажувач створить пару записів у таблиці GOT для розрахунку параметрів `tls_index` під час виклику runtime-функції `__tls_get_addr`.

### 3.3. Дизасемблювання та аналіз релаксацій через objdump

Для інспектування згенерованих інструкцій та виявлення дій релаксацій компонувальника застосовується дизасемблер `objdump`:

```bash
objdump -d -M intel ./host | grep -A 12 "<print_tls_info>:"
```

Якщо компонувальник застосував релаксацію **Local Exec (LE)**, ви побачите спрощену інструкцію замість виклику функції:

```assembly
  40114a:   mov    rax, QWORD PTR fs:0
  401153:   sub    rax, 0x4
  401157:   mov    eax, DWORD PTR [rax]
```

#### Аналіз транзиції GD → LE у виводі objdump:
Якщо об'єктний файл згенеровано для General Dynamic, але зкомпоновано статично у підсумковий бінарник, `objdump` покаже, як компонувальник заповнив місце виклику `call __tls_get_addr` NOP-падингом (`0x66 0x66 0x90`), перетворивши виклик функції на прямий доступ до пам'яті через регістр `FS`.

### 3.4. Перевірка символьних відлагоджувальних записів DWARF через readelf

Для аналізу того, як відлагоджувач дізнається про розміщення потоко-локальних змінних, можна проінспектувати секції DWARF:

```bash
readelf -Wi ./host | grep -A 5 "DW_AT_location"
```

У виводі ви побачите спеціальні байти операцій DWARF: `DW_OP_consts` та `DW_OP_form_tls_address`. Ця послідовність інструкцій підказує налагоджувачу `gdb`, що для отримання адреси змінної потрібно прочитати базову адресу TCB з регістра `FS` та додати до неї декодоване зміщення.

## 4. Глибоке налагодження TLS у системному налагоджувачі GDB

Утиліта GDB надає прямий доступ до регістра `FS` та дозволяє покроково відстежувати стан TCB та вектора DTV під час виконання програми.

### Покрокова сесія налагодження:

1. **Запуск GDB та встановлення точок зупинки**:
```text
gdb ./host
(gdb) break main
(gdb) break worker_thread
(gdb) run
```

2. **Перегляд регістра FS та структури TCB**:
```text
(gdb) # Зчитування 64-бітної базової адреси FS
(gdb) p/x $fs_base
$1 = 0x7ffff7da2740

(gdb) # Перевірка self-pointer (значення за адресою FS:0 має збігатися з $fs_base)
(gdb) x/gx $fs_base
0x7ffff7da2740: 0x07ffff7da2740

(gdb) # Перегляд вказівника на DTV (за адресою FS:0x08)
(gdb) x/gx $fs_base + 0x8
0x7ffff7da2748: 0x07ffff7da2b70
```

3. **Аналіз елементів вектора DTV**:
```text
(gdb) # Зчитування нульового елемента DTV (лічильник генерації модулів)
(gdb) set $dtv = *(void**)($fs_base + 8)
(gdb) x/gx $dtv
0x7ffff7da2b70: 0x0000000000000001

(gdb) # Зчитування першого елемента DTV (вказівник на TLS первинного модуля)
(gdb) x/gx $dtv + 8
0x7ffff7da2b78: 0x07ffff7da2000
```

4. **Відстеження викликів __tls_get_addr та перевірка адреси плагіна**:
```text
(gdb) continue
(gdb) # Перехід у робочий потік
(gdb) disassemble __tls_get_addr
(gdb) print &plugin_counter
$2 = (int *) 0x7ffff759e910
```

5. **Перевірка реєстрації деструкторів C++ thread_local об'єктів**:
```text
(gdb) # Встановлення breakpoint на функцію реєстрації деструкторів
(gdb) break __cxa_thread_atexit_impl
(gdb) continue
(gdb) # Дослідження аргументів реєстрації: rdi = dtor, rsi = obj, rdx = dso_handle
(gdb) info registers rdi rsi rdx
```

### 5. Практичний підсумковий порівняльний чек-лист інструментів CLI

Для зручності проведення аналізу TLS при роботі з довільними бінарними файлами підсумуємо основні команди інспектування в єдину таблицю:

| Прапор / Команда | Інструмент | Ціль аналізу та очікуваний результат |
| :--- | :--- | :--- |
| `readelf -l <file> \| grep TLS` | `readelf` | Поразити наявність заголовка `PT_TLS`, дізнатися розміри `.tdata` (`FileSiz`) та `.tbss` (`MemSiz - FileSiz`). |
| `readelf -r <file> \| grep TLS` | `readelf` | Виявити типи релокацій TLS (`R_X86_64_TLSGD`, `R_X86_64_TLSLD`, `R_X86_64_GOTTPOFF`, `R_X86_64_TPOFF32`). |
| `objdump -d -M intel <file>` | `objdump` | Проаналізувати асемблерні інструкції адресації (`mov fs:...`, `call __tls_get_addr`) та перевірити релаксації. |
| `readelf -Wi <file>` | `readelf` | Інспектувати записи DWARF (`DW_OP_form_tls_address`) для перевірки відлагоджувальної інформації. |
| `p/x $fs_base` | `gdb` | Зчитати поточне 64-бітне значення базової адреси `FS` у внутрішній сесії налагоджувача GDB. |
| `x/gx $fs_base + 0x8` | `gdb` | Зчитати вказівник на масив DTV (Dynamic Thread Vector) з заголовка TCB. |

Завдяки цьому комплексу інструментів розробник може повністю простежити весь шлях TLS-змінної — від оголошення у вихідному коді C/C++ до низькорівневої адресації на рівні регістрів процесора.
