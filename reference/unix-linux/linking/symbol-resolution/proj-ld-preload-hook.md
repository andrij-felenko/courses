# ⚙️ Практикум: перехоплення malloc/free та захист від рекурсії

Цей практичний матеріал демонструє створення надійної shared-бібліотеки перехоплення пам'яті за допомогою `LD_PRELOAD` та `dlsym(RTLD_NEXT)`, аналізує пастку рекурсивної ініціалізації в glibc та висвітлює безпечну роботу в багатопотоковому середовищі.

Перехоплення системних функцій пам'яті вимагає особливої обережності. Оскільки динамічний розподільник пам'яті бере участь у кожній операції створення об'єктів у просторі користувача, будь-яка помилка або непередбачений виклик усередині вашого перехоплювача може призвести до аварійного завершення всієї операційної системи або окремих процесів.

## 1. Проблема bootstrap-ініціалізації в glibc

Наївна спроба написати перехоплювач пам'яті через `dlsym(RTLD_NEXT, "malloc")` стикається із прихованою пасткою в GNU C Library: функція `dlsym` для власних внутрішніх потреб (зокрема для виділення таблиць локального простору імен або формування текстових повідомлень про помилки) усередині викликає `calloc` або `malloc`.

Якщо ваша функція-перехоплювач `malloc` викликає `dlsym`, а `dlsym` під час першого звернення знову викликає `malloc`, виникає взаємне зациклення (bootstrap recursion), яке закінчується аварійним завершенням програми через переповнення стека (Stack Overflow). Цю ситуацію важко відлагодити звичайним відлагоджувальником, оскільки стек викликів містить тисячі однакових фреймів `dlsym` -> `malloc` -> `dlsym`.

Для вирішення цієї проблеми застосовують метод **статичного аварійного буфера (bootstrap buffer)**. Основні кроки алгоритму захисту:
1. Визначають глобальний атомарний або статичний прапорець ініціалізації, який сигналізує про те, що процес розв'язання символів уже триває у даному потоці.
2. Якщо виклик `malloc` або `calloc` надійшов під час виконання `dlsym`, пам'ять виділяється з наперед визначеного стабільного масиву у секції `.bss`, який не потребує виклику системного розподільника.
3. Після успішного розв'язання `dlsym(RTLD_NEXT)` прапорець скидається, а подальші виклики перенаправляються до справжнього `malloc` з `libc.so`.
4. Під час виклику `free` перехоплювач перевіряє, чи належить вказівник адресу стаціонарного bootstrap-буфера. Якщо так, звільнення ігнорується, бо стаціонарний буфер не потребує повернення системі.

Ця техніка є стандартом для створення санітайзерів пам'яті (AddressSanitizer, LeakSanitizer) та комерційних профілювальників продуктивності у Linux.

## 2. Безпечне логування без виклику динамічної пам'яті

Друга поширена пастка — використання високорівневих функцій форматованого виводу `printf()`, `fprintf()` або `std::cout` всередині перехоплювача `malloc`. Форматований вивід у C/C++ стандартом виділяє внутрішні буфери потоків ввода-виводу за допомогою того самого `malloc`.

Спроба викликати `printf` усередині `malloc` призведе до повторного входу у ваш хук та безкінечної рекурсії. Крім того, потоки I/O використовують внутрішні locks (м'ютекси), що може викликати взаємне блокування (deadlock) у багатопотокових програмах.

Тому логування інформації про адреси та розміри виділених блоків слід виконувати виключно через низькорівневий системний виклик `write(2)` з використанням безалокаційного перетворення чисел у рядок. Системний виклик `write(2)` звертається безпосередньо до ядра Linux через таблицю викликів, оминаючи всі C-буфери простору користувача.

Для підготовки рядків виводу використовують локальні масиви фіксованого розміру на стеку функції та пряме перетворення початкових бітів у шістнадцятковий формат, що повністю гарантує відсутність прихованих викликів системного розподільника пам'яті.

## 3. Реалізація C та C++ бібліотеки-перехоплювача

Нижче наведено повні ідіоматичні реалізації перехоплювача пам'яті для мов C та C++.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <unistd.h>
#include <string.h>

/* Вказівники на оригінальні функції libc */
static void *(*real_malloc)(size_t size) = NULL;
static void (*real_free)(void *ptr) = NULL;

/* Статичний буфер для фази ініціалізації (bootstrap) */
#define BOOTSTRAP_CAPACITY (64 * 1024)
static char bootstrap_buffer[BOOTSTRAP_CAPACITY];
static size_t bootstrap_used = 0;
static int inside_init = 0;

/* Низькорівневий вивід числа у STDERR_FILENO без виділення пам'яті */
static void write_hex(size_t val) {
    char buf[20];
    char hex[] = "0123456789abcdef";
    int idx = 18;
    buf[19] = '\n';
    if (val == 0) {
        buf[idx--] = '0';
    } else {
        while (val > 0 && idx >= 2) {
            buf[idx--] = hex[val % 16];
            val /= 16;
        }
    }
    buf[idx--] = 'x';
    buf[idx] = '0';
    write(STDERR_FILENO, &buf[idx], 20 - idx);
}

static void write_msg(const char *msg) {
    write(STDERR_FILENO, msg, strlen(msg));
}

static void init_hooks(void) {
    inside_init = 1;
    real_malloc = (void *(*)(size_t))dlsym(RTLD_NEXT, "malloc");
    real_free = (void (*)(void *))dlsym(RTLD_NEXT, "free");
    inside_init = 0;

    if (!real_malloc || !real_free) {
        write_msg("myhook: FATAL - failed to resolve libc symbols\n");
        _exit(1);
    }
}

void *malloc(size_t size) {
    /* Якщо dlsym викликає malloc під час ініціалізації */
    if (inside_init) {
        if (bootstrap_used + size > BOOTSTRAP_CAPACITY) {
            write_msg("myhook: bootstrap buffer exhausted\n");
            return NULL;
        }
        void *ptr = &bootstrap_buffer[bootstrap_used];
        bootstrap_used += (size + 7) & ~7; /* вирівнювання на 8 байтів */
        return ptr;
    }

    if (!real_malloc) {
        init_hooks();
    }

    void *ptr = real_malloc(size);

    write_msg("myhook: malloc(");
    write_hex(size);
    write_msg(") = ");
    write_hex((size_t)ptr);

    return ptr;
}

void free(void *ptr) {
    if (!ptr) return;

    /* Ігноруємо звільнення з статичного bootstrap-буфера */
    if (ptr >= (void *)bootstrap_buffer && ptr < (void *)(bootstrap_buffer + BOOTSTRAP_CAPACITY)) {
        return;
    }

    if (!real_free) {
        init_hooks();
    }

    write_msg("myhook: free(");
    write_hex((size_t)ptr);

    real_free(ptr);
}
```
```cpp
#define _GNU_SOURCE
#include <iostream>
#include <array>
#include <atomic>
#include <string_view>
#include <dlfcn.h>
#include <unistd.h>
#include <cstdint>

namespace memory_hook {

class MemoryTracker {
public:
    using MallocFn = void* (*)(size_t);
    using FreeFn = void (*)(void*);

    static MemoryTracker& instance() noexcept {
        static MemoryTracker tracker;
        return tracker;
    }

    void* allocate(size_t size) noexcept {
        if (initializing_.load(std::memory_order_relaxed)) {
            return allocate_bootstrap(size);
        }

        if (!real_malloc_) {
            init();
        }

        void* ptr = real_malloc_(size);
        log_operation("malloc", size, ptr);
        return ptr;
    }

    void deallocate(void* ptr) noexcept {
        if (!ptr) return;

        if (is_bootstrap_ptr(ptr)) {
            return;
        }

        if (!real_free_) {
            init();
        }

        log_operation("free", 0, ptr);
        real_free_(ptr);
    }

private:
    MemoryTracker() = default;

    static constexpr size_t kBootstrapSize = 64 * 1024;
    alignas(16) std::array<char, kBootstrapSize> bootstrap_buf_{};
    size_t bootstrap_used_{0};

    std::atomic<bool> initializing_{false};
    MallocFn real_malloc_{nullptr};
    FreeFn real_free_{nullptr};

    bool is_bootstrap_ptr(const void* ptr) const noexcept {
        const auto* byte_ptr = reinterpret_cast<const char*>(ptr);
        return byte_ptr >= bootstrap_buf_.data() &&
               byte_ptr < (bootstrap_buf_.data() + bootstrap_buf_.size());
    }

    void* allocate_bootstrap(size_t size) noexcept {
        const size_t aligned_size = (size + 15) & ~size_t(15);
        if (bootstrap_used_ + aligned_size > kBootstrapSize) {
            safe_write("myhook: bootstrap buffer overflow\n");
            return nullptr;
        }
        void* ptr = &bootstrap_buf_[bootstrap_used_];
        bootstrap_used_ += aligned_size;
        return ptr;
    }

    void init() noexcept {
        initializing_.store(true, std::memory_order_relaxed);
        real_malloc_ = reinterpret_cast<MallocFn>(dlsym(RTLD_NEXT, "malloc"));
        real_free_ = reinterpret_cast<FreeFn>(dlsym(RTLD_NEXT, "free"));
        initializing_.store(false, std::memory_order_relaxed);

        if (!real_malloc_ || !real_free_) {
            safe_write("myhook: FATAL failed dlsym\n");
            _exit(1);
        }
    }

    static void safe_write(std::string_view sv) noexcept {
        ::write(STDERR_FILENO, sv.data(), sv.size());
    }

    void log_operation(std::string_view op, size_t size, void* ptr) noexcept {
        char buf[128];
        int len = 0;
        if (op == "malloc") {
            len = ::snprintf(buf, sizeof(buf), "[hook] malloc(%zu) = %p\n", size, ptr);
        } else {
            len = ::snprintf(buf, sizeof(buf), "[hook] free(%p)\n", ptr);
        }
        if (len > 0) {
            ::write(STDERR_FILENO, buf, static_cast<size_t>(len));
        }
    }
};

} // namespace memory_hook

extern "C" {

void* malloc(size_t size) {
    return memory_hook::MemoryTracker::instance().allocate(size);
}

void free(void* ptr) {
    memory_hook::MemoryTracker::instance().deallocate(ptr);
}

}
```
:::

## 4. Збірка та інспектування роботи перехоплювача

Для випробування перехоплювача необхідно зібрати вихідний код у позиційно-незалежну спільну бібліотеку (DSO) за допомогою прапорців `-shared` та `-fPIC`:

```bash
# Збірка C-версії перехоплювача
gcc -shared -fPIC -O2 -o libmyhook.so hook.c -ldl

# Збірка C++ версії перехоплювача з підтримкою C++20
g++ -shared -fPIC -O2 -std=c++20 -o libmyhook.so hook.cpp -ldl
```

Тестування на будь-якій системній утиліті виконується шляхом експорту `LD_PRELOAD`:

```bash
LD_PRELOAD=./libmyhook.so ls -l /tmp
```

У результаті у потік помилок `stderr` буде виведено повний журнал виділень та звільнень динамічної пам'яті, які здійснює утиліта `ls` під час виконання.

Якщо необхідно впевнитися, що перехоплювач правильно зчитується динамічним лінкером, можна скористатися прапорцем налагодження `LD_DEBUG`:

```bash
LD_DEBUG=bindings LD_PRELOAD=./libmyhook.so ls 2>&1 | grep malloc
```

Вивід покаже, як динамічний лінкер `ld.so` пов'язує символ `malloc` з вашою бібліотекою `libmyhook.so`, підтверджуючи успішне розв'язання та перекриття символів.

## 5. Обробка крайових випадків у багатопотоковому середовищі

При розгортанні перехоплювачів у високонавантажених багатопотокових застосунках виникають додаткові вимоги до синхронізації. У разі одночасного старту кількох потоків виклики `malloc` можуть надійти паралельно ще до того, як перший потік завершить ініціалізацію вказівника `real_malloc`.

Для вирішення цієї проблеми у версії C++ використано атомарний прапорець `std::atomic<bool>` із розслабленим порядком пам'яті (`std::memory_order_relaxed`), що виключає стан гонки (data race). У C-версії можна застосувати примітив `pthread_once` або безалокаційні атомарні операції C11 `stdatomic.h`.

Крім того, необхідно враховувати функцію `fork(2)`. Якщо процес створює дочірній процес за допомогою `fork`, стан локальних буферів та прапорців ініціалізації успадковується. Для обробки викликів `fork` у перехоплювачах реєструють обробники `pthread_atfork`, які скидають внутрішній стан або оновлюють дескриптори логування.

## 6. Тестування на пропрієтарних бінарних файлах та аналіз за допомогою GDB

При практичному розгортанні `LD_PRELOAD` перехоплювачів на комерційних бінарниках без вихідного коду часто виникають ситуації, коли програма містить власні реалізації розподільника пам'яті (наприклад, tcmalloc або jemalloc), вбудовані статично.

У такому разі зовнішній виклик `malloc` з `libc.so` може взагалі не здійснюватися, бо внутрішні модулі звертаються безпосередньо до вбудованого розподільника. Для перевірки того, чи використовує бінарний файл динамічний `malloc` з `libc`, слід перевірити секцію `.dynsym` за допомогою утиліти `nm -D` або запустити програму під керуванням `gdb`:

```bash
gdb ./target_app
(gdb) set environment LD_PRELOAD ./libmyhook.so
(gdb) catch load
(gdb) run
```

Команди `gdb` дозволяють перевірити порядок завантаження бібліотек у таблиці пошуку `ld.so` та переконатися, що ваша перехоплювальна бібліотека зайняла першу позицію в простірі імен символів.
