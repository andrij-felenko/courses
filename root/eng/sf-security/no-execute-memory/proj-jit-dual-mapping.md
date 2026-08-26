# ⚙️ Безпечна динамічна кодогенерація: реалізація подвійного мапінгу JIT-пам'яті

Динамічна компіляція «на льоту» (Just-In-Time / JIT), що лежить в основі рушіїв V8 (Node.js, Chromium), JVM HotSpot, WebKit JavaScriptCore та .NET CLR, вимагає одночасного вирішення двох взаємовиключних завдань: компілятор повинен формувати й записувати нові машинні інструкції в оперативну пам'ять, а процесор — безперешкодно виконувати ці інструкції без порушення апаратного правила `W^X`.

---

## 1. Архітектурна проблема: наївний mprotect() проти безпеки

Традиційний наївний підхід до організації JIT-буфера полягає в постійному динамічному перемиканні прав доступу до однієї й тієї самої області пам'яті через системний виклик `mprotect()`:

```
[Виділення пам'яті: PROT_READ | PROT_WRITE]
                 │
                 ▼
[Компілятор генерує машинний код у буфер]
                 │
                 ▼
[mprotect(ptr, size, PROT_READ | PROT_EXEC)]  <── Накладні витрати ядра + скидання TLB
                 │
                 ▼
[Виклик згенерованої функції]
                 │
                 ▼
[mprotect(ptr, size, PROT_READ | PROT_WRITE)]  <── Вікно гонитви (Race Condition)
```

Цей підхід має дві критичні вади, які роблять його непридатним для сучасних промислових рушіїв:

1. **Високі накладні витрати ядра та скидання TLB:** Кожен виклик `mprotect()` вимагає повноцінного системного переходу в простір ядра (Ring 3 -> Ring 0), взяття блокувань структур віртуальної пам'яті процесу (`mmap_lock` у ядрі Linux), модифікації бітів у дереві таблиць сторінок та розсилання міжпроцесорних переривань (Inter-Processor Interrupts, IPI) на всі активні процесорні ядра для інвалідації записів у буферах асоціативної трансляції (TLB Shootdown). У високонавантажених веб-рушіях, де компіляція функцій відбувається тисячі разів на секунду, постійні скидання TLB деградують продуктивність усієї системи.
2. **Вікно вразливості та стан гонитви (TOCTOU / Thread Race):** У багатопотокових середовищах права на сторінки пам'яті є загальними для всього процесу. Коли один фоновий потік компілятора викликає `mprotect(PROT_READ | PROT_WRITE)` для оновлення скомпільованого методу, сторінка стає доступною на запис для **всіх** інших потоків застосунку. Якщо в цей час інший потік виконує ненадійний код або зазнає атаки через вразливість псування пам'яті (Heap Overflow, Use-After-Free), зловмисник отримує вікно часу, протягом якого може підмінити машинний код у JIT-буфері на власний шелкод.

---

## 2. Механізм подвійного відображення (Dual Mapping) на рівні ядра та MMU

Техніка **подвійного відображення** (англ. *Dual Mapping*) розв'язує цю дилему за допомогою фундаментальної властивості підсистеми віртуальної пам'яті: одна фізична сторінка оперативної пам'яті (Page Frame) може одночасно мати довільну кількість різних віртуальних адрес із незалежними наборами прав доступу.

В ядрі Linux це реалізується через взаємодію підсистеми віртуальної файлової системи (VFS) та блоку керування пам'яттю (MMU):

1. **Створення анонімного файлового об'єкта:** Системний виклик `memfd_create()` створює в оперативній пам'яті анонімний інод у спеціальній підсистемі `tmpfs`/`shmem`. Цей об'єкт не має прив'язки до диска чи файлової системи, а виділені для нього сторінки живуть виключно в сторінковому кеші (Page Cache) ядра.
2. **Перше відображення (відображення запису `V_write`):** Виклик `mmap()` створює структуру `vm_area_struct` у просторі користувача з правами `PROT_READ | PROT_WRITE` та прапорцем `MAP_SHARED`. Таблиці сторінок процесу налаштовуються так, що віртуальні адреси діапазону `V_write` транслюються у відповідні фізичні кадри з бітом запису (`R/W = 1`) та встановленим бітом заборони виконання (`NX = 1`).
3. **Друге відображення (відображення виконання `V_exec`):** Другий виклик `mmap()` для того самого дескриптора створює іншу структуру `vm_area_struct` за абсолютно іншою віртуальною адресою `V_exec` із правами `PROT_READ | PROT_EXEC` та прапорцем `MAP_SHARED`. Таблиці сторінок для цього діапазону транслюють адреси на **ті самі фізичні кадри**, але з правами тільки для читання (`R/W = 0`) і дозволеним виконанням (`NX = 0`).

```
+──────────────────────────────────────────────────────────────────────────+
|                     Віртуальний адресний простір                         |
|                                                                          |
|  [ V_write: 0x7f1000 ] (Права: RW, NX=1)   [ V_exec: 0x7f8000 ] (RX, NX=0) |
|           │                                         │                    |
|           │        Таблиці сторінок (PTE)           │                    |
|           └───────────────────┬─────────────────────┘                    |
|                               ▼                                          |
|                [ Фізичний кадр DRAM (PFN 4128) ]                         |
|                (Спільний машинний код у пам'яті)                         |
+──────────────────────────────────────────────────────────────────────────+
```

Коли потік компілятора записує нові інструкції за адресою `V_write`, дані фізично потрапляють у кадр пам'яті. Оскільки адреса `V_exec` посилається на той самий фізичний кадр, процесор може негайно виконати ці інструкції за адресою `V_exec`, не змінюючи прапорці в таблицях сторінок і не здійснюючи жодного системного виклику.

---

## 3. Практична реалізація подвійного JIT-рушія

Нижче наведено робочу реалізацію подвійного буфера мовами C та C++. Рушій виділяє анонімний дескриптор, конфігурує два незалежні мапінги, генерує машинний код для обчислення лінійної математичної функції `calculate(a, b) = a * 3 + b + 7`, скидає кеш інструкцій та безпечно виконує функцію за адресою виконання.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/syscall.h>

/* Сигнатура динамічно скомпільованої функції: int64_t func(int64_t a, int64_t b) */
typedef int64_t (*jit_func_t)(int64_t, int64_t);

/* Структура подвійного JIT-буфера */
typedef struct {
    int fd;
    size_t size;
    uint8_t *write_view;   /* Відображення для запису (PROT_READ | PROT_WRITE) */
    const void *exec_view; /* Відображення для виконання (PROT_READ | PROT_EXEC) */
} jit_buffer_t;

/* Ініціалізація та налаштування подвійного відображення */
int jit_buffer_init(jit_buffer_t *buf, size_t requested_size) {
    if (!buf || requested_size == 0) return -1;

    /* Вирівнювання розміру за межею сторінки апаратного MMU (4096 байтів) */
    long page_size = sysconf(_SC_PAGESIZE);
    buf->size = (requested_size + page_size - 1) & ~(page_size - 1);

    /* 1. Створення анонімного файлового дескриптора в пам'яті */
    buf->fd = memfd_create("jit_dual_mapped", MFD_CLOEXEC);
    if (buf->fd < 0) {
        perror("memfd_create failed");
        return -1;
    }

    /* 2. Фіксація розміру спільного сегмента пам'яті */
    if (ftruncate(buf->fd, (off_t)buf->size) < 0) {
        perror("ftruncate failed");
        close(buf->fd);
        return -1;
    }

    /* 3. Перший мапінг: доступ лише для запису та читання (RW) */
    buf->write_view = (uint8_t *)mmap(NULL, buf->size,
                                       PROT_READ | PROT_WRITE,
                                       MAP_SHARED, buf->fd, 0);
    if (buf->write_view == MAP_FAILED) {
        perror("mmap RW failed");
        close(buf->fd);
        return -1;
    }

    /* 4. Другий мапінг: доступ лише для виконання та читання (RX) */
    buf->exec_view = mmap(NULL, buf->size,
                          PROT_READ | PROT_EXEC,
                          MAP_SHARED, buf->fd, 0);
    if (buf->exec_view == MAP_FAILED) {
        perror("mmap RX failed");
        munmap(buf->write_view, buf->size);
        close(buf->fd);
        return -1;
    }

    return 0;
}

/* Коректне звільнення ресурсів */
void jit_buffer_free(jit_buffer_t *buf) {
    if (!buf) return;
    if (buf->exec_view && buf->exec_view != MAP_FAILED) {
        munmap((void *)buf->exec_view, buf->size);
    }
    if (buf->write_view && buf->write_view != MAP_FAILED) {
        munmap(buf->write_view, buf->size);
    }
    if (buf->fd >= 0) {
        close(buf->fd);
    }
    buf->write_view = NULL;
    buf->exec_view = NULL;
    buf->fd = -1;
}

int main(void) {
    jit_buffer_t jit;
    if (jit_buffer_init(&jit, 4096) != 0) {
        fprintf(stderr, "[-] Помилка створення JIT-буфера\n");
        return EXIT_FAILURE;
    }

    printf("[+] JIT Dual Buffer створено:\n");
    printf("    Write view (RW): %p\n", (void *)jit.write_view);
    printf("    Exec view  (RX): %p\n", jit.exec_view);

    /* Машинні інструкції x86-64 для функції f(a, b) = a * 3 + b + 7
     * System V AMD64 ABI:
     *   a знаходиться в RDI, b знаходиться в RSI, результат у RAX
     */
    const uint8_t code[] = {
        0x48, 0x8d, 0x04, 0x7f, /* lea rax, [rdi + rdi*2] ; RAX = a * 3        */
        0x48, 0x01, 0xf0,       /* add rax, rsi           ; RAX = (a * 3) + b  */
        0x48, 0x83, 0xc0, 0x07, /* add rax, 7             ; RAX += 7           */
        0xc3                    /* ret                    ; повернення         */
    };

    /* 1. Запис машинного коду через RW-покажчик */
    memcpy(jit.write_view, code, sizeof(code));

    /* 2. Інвалідація кешу інструкцій (Instruction Cache Flushing) */
    __builtin___clear_cache((char *)jit.write_view, (char *)jit.write_view + sizeof(code));

    /* 3. Виклик функції через RX-покажчик */
    jit_func_t fn = (jit_func_t)jit.exec_view;
    int64_t arg1 = 10;
    int64_t arg2 = 5;
    int64_t result = fn(arg1, arg2);

    /* Очікувано: 10 * 3 + 5 + 7 = 42 */
    printf("[+] Результат виклику JIT-коду: calculate(%ld, %ld) = %ld\n", arg1, arg2, result);

    if (result == 42) {
        printf("[✓] Інваріант W^X збережено, код виконано успішно.\n");
    }

    jit_buffer_free(&jit);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <vector>
#include <span>
#include <system_error>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <fcntl.h>

namespace jit {

/**
 * @brief Безпечний клас подвійного JIT-буфера з автоматичним керуванням життєвим циклом (RAII).
 */
class DualMappedBuffer {
public:
    explicit DualMappedBuffer(size_t requested_size) {
        long page_size = ::sysconf(_SC_PAGESIZE);
        size_ = (requested_size + page_size - 1) & ~(page_size - 1);

        /* 1. Створення анонімного файлового об'єкта */
        fd_ = ::memfd_create("jit_cpp_dual_mapped", MFD_CLOEXEC);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "memfd_create failed");
        }

        /* 2. Встановлення ємності буфера */
        if (::ftruncate(fd_, static_cast<off_t>(size_)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "ftruncate failed");
        }

        /* 3. Створення відображення запису (RW) */
        void *w_ptr = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE, MAP_SHARED, fd_, 0);
        if (w_ptr == MAP_FAILED) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "mmap RW failed");
        }
        write_view_ = static_cast<uint8_t *>(w_ptr);

        /* 4. Створення відображення виконання (RX) */
        void *x_ptr = ::mmap(nullptr, size_, PROT_READ | PROT_EXEC, MAP_SHARED, fd_, 0);
        if (x_ptr == MAP_FAILED) {
            ::munmap(write_view_, size_);
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "mmap RX failed");
        }
        exec_view_ = x_ptr;
    }

    ~DualMappedBuffer() noexcept {
        if (exec_view_ && exec_view_ != MAP_FAILED) {
            ::munmap(exec_view_, size_);
        }
        if (write_view_ && write_view_ != MAP_FAILED) {
            ::munmap(write_view_, size_);
        }
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    /* Семантика переміщення з передачею володіння дескрипторами */
    DualMappedBuffer(const DualMappedBuffer &) = delete;
    DualMappedBuffer &operator=(const DualMappedBuffer &) = delete;

    DualMappedBuffer(DualMappedBuffer &&other) noexcept
        : fd_(other.fd_), size_(other.size_),
          write_view_(other.write_view_), exec_view_(other.exec_view_) {
        other.fd_ = -1;
        other.size_ = 0;
        other.write_view_ = nullptr;
        other.exec_view_ = nullptr;
    }

    DualMappedBuffer &operator=(DualMappedBuffer &&other) noexcept {
        if (this != &other) {
            this->~DualMappedBuffer();
            fd_ = other.fd_;
            size_ = other.size_;
            write_view_ = other.write_view_;
            exec_view_ = other.exec_view_;
            other.fd_ = -1;
            other.size_ = 0;
            other.write_view_ = nullptr;
            other.exec_view_ = nullptr;
        }
        return *this;
    }

    /**
     * @brief Запис скомпільованого машинного коду через безпечний span.
     */
    void emit_code(std::span<const uint8_t> code, size_t offset = 0) {
        if (offset + code.size() > size_) {
            throw std::out_of_range("JIT buffer capacity exceeded");
        }
        std::memcpy(write_view_ + offset, code.data(), code.size());
        __builtin___clear_cache(reinterpret_cast<char *>(write_view_ + offset),
                                reinterpret_cast<char *>(write_view_ + offset + code.size()));
    }

    /**
     * @brief Отримання типізованого покажчика на скомпільовану функцію.
     */
    template <typename FuncSig>
    [[nodiscard]] FuncSig get_function(size_t offset = 0) const noexcept {
        const uint8_t *entry = static_cast<const uint8_t *>(exec_view_) + offset;
        return reinterpret_cast<FuncSig>(const_cast<uint8_t *>(entry));
    }

    [[nodiscard]] const void *exec_address() const noexcept { return exec_view_; }
    [[nodiscard]] const void *write_address() const noexcept { return write_view_; }

private:
    int fd_{-1};
    size_t size_{0};
    uint8_t *write_view_{nullptr};
    void *exec_view_{nullptr};
};

} // namespace jit

int main() {
    try {
        jit::DualMappedBuffer jit_buf(4096);

        std::cout << "[+] JIT RAII Buffer створено:\n"
                  << "    Write view (RW): " << jit_buf.write_address() << "\n"
                  << "    Exec view  (RX): " << jit_buf.exec_address() << "\n";

        /* Машинні інструкції x86-64 для f(a, b) = a * 3 + b + 7 */
        const std::vector<uint8_t> code = {
            0x48, 0x8d, 0x04, 0x7f, /* lea rax, [rdi + rdi*2] */
            0x48, 0x01, 0xf0,       /* add rax, rsi           */
            0x48, 0x83, 0xc0, 0x07, /* add rax, 0x07          */
            0xc3                    /* ret                    */
        };

        jit_buf.emit_code(code);

        using JITSignature = int64_t (*)(int64_t, int64_t);
        auto calculate = jit_buf.get_function<JITSignature>();

        int64_t a = 10;
        int64_t b = 5;
        int64_t res = calculate(a, b);

        std::cout << "[+] Результат виконання: calculate(" << a << ", " << b << ") = " << res << "\n";
        if (res == 42) {
            std::cout << "[✓] C++ JIT-тест пройдено успішно!\n";
        }
    } catch (const std::exception &ex) {
        std::cerr << "[-] Помилка JIT: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 4. Критичні підводні камені та захист від експлуатації

При практичній експлуатації архітектури Dual Mapping у сучасних середовищах розробки виникають три специфічні виклики:

### 1. Неузгодженість кешу інструкцій (Instruction Cache Coherency)

Процесорні ядра мають фізично розділені кеші першого рівня: кеш даних (L1d) та кеш інструкцій (L1i). Запис коду через покажчик `write_view` оновлює виключно L1d або системну DRAM.

На процесорах архітектури x86/x86-64 апаратна логіка забезпечує автоматичну синхронізацію («snooping») конвеєра інструкцій при зміні пам'яті. Однак на архітектурах ARM (AArch64) та RISC-V кеш інструкцій не є апаратно когерентним із кешем даних. Якщо потік записує інструкції в пам'ять і негайно передає керування на `exec_view`, конвеєр процесора виконає застарілі байти, що залишилися в L1i від попередніх операцій.

Для забезпечення переносимості коду компілятор зобов'язаний явно викликати інструкції очищення кешу інструкцій (`ISB` / `DC CVAU` на ARM, або кросплатформенну вбудовану функцію компилятора `__builtin___clear_cache(start, end)`).

### 2. Розрахунок відносних адрес переходів (RIP-relative Addressing)

Більшість інструкцій умовних та безумовних переходів, викликів функцій (`call offset32`) та завантаження даних (`mov rax, [rip + offset32]`) кодують зміщення відносно лічильника команд `RIP`.

Оскільки потік компілятора генерує код у буфері `write_view`, а виконання відбуватиметься за адресою `exec_view`, розрахунок усіх відносних зміщень повинен здійснюватися **виключно відносно адреси `exec_view`**. Помилка у визначенні бази зміщення призведе до непередбачуваного стрибка у довільну область пам'яті та аварійного падіння процесу.

### 3. Приховування адреси `write_view` від зловмисників

Адреса `write_view` є найбільш привабливою ціллю для атакувальника. Якщо в програмі існує вразливість витоку адрес (Address Leak), нападник може дізнатися розташування `write_view` у пам'яті й за допомогою примітиву довільного запису (Arbitrary Write) записати туди шкідливий шелкод.

Сучасні рушії впроваджують додаткові бар'єри захисту:
- **Apple APRR (Fast Permission Switching):** На чипах Apple Silicon перемикання прав виконання/запису реалізовано через спеціальні апаратні регістри `SPRR`/`APRR` та функцію `pthread_jit_write_protect_np()`, що змінює права на рівні окремого потоку за лічені такти процесора без системних викликів.
- **Intel MPK (Memory Protection Keys):** Дозволяє призначити сторінкам `write_view` спеціальний ключ захисту, який за замовчуванням блокує доступ на запис на рівні регістрів процесора (`PKRU`), відкриваючи його лише на короткий інтервал часу безпосередньої роботи компілятора.
