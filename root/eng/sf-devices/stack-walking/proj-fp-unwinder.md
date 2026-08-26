# ⚙️ Реалізація швидкого стек-трейсера за покажчиком кадру

Коли процес отримує критичний сигнал аварійного завершення (`SIGSEGV`, `SIGFPE`, `SIGILL`, `SIGABRT`), стан середовища виконання стає повністю непередбачуваним. Стандартні засоби діагностики, такі як `printf`, `std::cout`, виділення динамічної пам'яті (`malloc`, `operator new`) або системні функції захоплення м'ютексів (`pthread_mutex_lock`), стають смертельно небезпечними. Якщо сигнал падіння прийшов у момент, коли інший потік (або той самий потік) утримував внутрішній замок аллокатора кучі, повторна спроба виділити пам'ять усередині обробника сигналу призведе до вічного взаємного блокування (англ. *deadlock*), і процес зависне, так і не сформувавши звіт про помилку.

Стандарт POSIX суворо вимагає, щоб усередині обробників асинхронних сигналів використовувалися виключно **асинхронно-сигнально-безпечні** (англ. *async-signal-safe*) функції. Щоб гарантовано зафіксувати точний ланцюг викликів у мить катастрофи, розробникові потрібен автономний розмотувач стека, який працює без звернення до кучі, не використовує бібліотечні блокування та спирається виключно на апаратний ланцюг покажчиків кадру.

### Архітектура та інваріанти розмотувача

При компіляції програми з прапором `-fno-omit-frame-pointer` компілятор зв'язує кожен стековий кадр в односпрямований список. Для 64-бітної архітектури x86-64 поточне значення фізичного регістра `RBP` вказує на комірку пам'яті на стеку, куди пролог функції зберіг значення покажчика кадру викликаючої функції. Одразу за цим покажчиком — за адресою `RBP + 8` (або `x29 + 8` для регістра зв'язку `x30` на архітектурі AArch64) — розташована збережена адреса повернення `RIP`, яка вказує на наступну інструкцію після виклику.

Надійний алгоритм розмотування стека зобов'язаний реалізувати п'ять обов'язкових інженерних перевірок безпеки пам'яті:

1. **Вирівнювання покажчика кадру**: адреса кожного кадру мусить бути строго вирівняна на межу машинного слова (`fp % sizeof(void*) == 0`). Невирівняний покажчик однозначно свідчить про спотворення стека, пошкодження пам'яті або виконання коду з випадкової адреси.
2. **Перевірка меж діапазону стека**: адреса кадру мусить знаходитися в межах адресного простору стека поточного потоку (`stack_bottom <= fp < stack_top`). Для основного потоку програми стек зазвичай обмежений розміром 8 МБ, а для створених потоків його межі можна визначити через `pthread_attr_getstack`.
3. **Монотонне зростання адрес**: оскільки стек архітектур x86-64 та ARM зростає в бік менших адрес пам'яті, кожен наступний кадр батьківської функції зобов'язаний знаходитися за строго більшою адресою (`next_fp > current_fp`). Порушення цієї умови виявляє циклічні зациклення або підробку кадру при переповненні локального масиву.
4. **Захист від нескінченної глибини**: жорстке обмеження максимальної кількості ітерацій (наприклад, 64 кадри) захищає діагностичний обробник від зависання у випадку безкінечної рекурсії або вичерпання пам'яті стека.
5. **Прямий вивід без використання буферизованого вводу/виводу**: форматування числових шістнадцяткових адрес здійснюється у виділеному статичному буфері на стеку за допомогою бітових зсувів, а виведення тексту в консоль виконується виключно через прямий системний виклик `write(STDERR_FILENO, ...)` (або `syscall(SYS_write, ...)`).

### Реалізація розмотувача

:::tabs
```c
#define _GNU_SOURCE
#include <unistd.h>
#include <stdint.h>
#include <stddef.h>
#include <signal.h>
#include <sys/syscall.h>

#define MAX_FRAMES 64

// Структура класичного стекового кадру x86-64
struct stack_frame {
    struct stack_frame* saved_fp;
    void* return_address;
};

// Сигнально-безпечне перетворення 64-бітної адреси у шістнадцятковий рядок
static void print_hex(uintptr_t val, char* out_buf, size_t* out_len) {
    static const char hex_digits[] = "0123456789abcdef";
    out_buf[0] = '0';
    out_buf[1] = 'x';
    for (int i = 15; i >= 0; --i) {
        out_buf[2 + (15 - i)] = hex_digits[(val >> (i * 4)) & 0x0f];
    }
    out_buf[18] = '\n';
    *out_len = 19;
}

// Функція розмотування стека за ланцюгом Frame Pointer
int unwind_frame_pointer(void** buffer, int max_depth) {
    if (!buffer || max_depth <= 0) {
        return 0;
    }

    // Зчитуємо початкове значення базового покажчика кадру
    uintptr_t current_fp = (uintptr_t)__builtin_frame_address(0);
    int count = 0;

    // Орієнтовна верхня межа стека для перевірки діапазону адрес
    uintptr_t stack_limit = current_fp + (8 * 1024 * 1024); // 8 МБ ліміту

    while (current_fp != 0 && count < max_depth) {
        // Перевірка 1: перевірка кратності 8 байтам
        if (current_fp & (sizeof(void*) - 1)) {
            break;
        }

        struct stack_frame* frame = (struct stack_frame*)current_fp;
        
        // Зберігаємо адресу повернення для подальшого декодування
        buffer[count++] = frame->return_address;

        uintptr_t next_fp = (uintptr_t)frame->saved_fp;

        // Перевірка 2: монотонність зростання адрес і межі стека
        if (next_fp <= current_fp || next_fp >= stack_limit) {
            break;
        }

        current_fp = next_fp;
    }

    return count;
}

// Асинхронно-сигнально-безпечний друк зібраного стека у STDERR
void safe_print_stacktrace(void* const* buffer, int depth) {
    static const char header[] = "=== Stack Backtrace ===\n";
    (void)syscall(SYS_write, STDERR_FILENO, header, sizeof(header) - 1);

    char num_buf[32];
    for (int i = 0; i < depth; ++i) {
        size_t len = 0;
        print_hex((uintptr_t)buffer[i], num_buf, &len);
        (void)syscall(SYS_write, STDERR_FILENO, "  #", 3);
        (void)syscall(SYS_write, STDERR_FILENO, num_buf, len);
    }
}
```
```cpp
#include <array>
#include <span>
#include <string_view>
#include <cstdint>
#include <cstddef>
#include <unistd.h>
#include <sys/syscall.h>

namespace diagnostic {

struct alignas(sizeof(void*)) StackFrame {
    const StackFrame* saved_fp{nullptr};
    const void* return_address{nullptr};
};

class AsyncSignalSafePrinter {
public:
    static void write_literal(std::string_view msg) noexcept {
        (void)::syscall(SYS_write, STDERR_FILENO, msg.data(), msg.size());
    }

    static void write_address(std::uintptr_t addr) noexcept {
        constexpr std::string_view hex_chars = "0123456789abcdef";
        std::array<char, 20> buf{"0x0000000000000000\n"};

        for (int i = 15; i >= 0; --i) {
            buf[2 + (15 - i)] = hex_chars[(addr >> (i * 4)) & 0x0f];
        }
        (void)::syscall(SYS_write, STDERR_FILENO, buf.data(), buf.size());
    }
};

class StackWalker {
public:
    static constexpr std::size_t DefaultMaxDepth = 64;

    template <std::size_t Capacity>
    static std::size_t walk(std::span<const void*, Capacity> destination) noexcept {
        auto current_fp = reinterpret_cast<std::uintptr_t>(__builtin_frame_address(0));
        std::size_t collected = 0;
        const auto stack_limit = current_fp + (8 * 1024 * 1024);

        while (current_fp != 0 && collected < destination.size()) {
            if ((current_fp & (sizeof(void*) - 1)) != 0) {
                break;
            }

            const auto* frame = reinterpret_cast<const StackFrame*>(current_fp);
            destination[collected++] = frame->return_address;

            const auto next_fp = reinterpret_cast<std::uintptr_t>(frame->saved_fp);
            if (next_fp <= current_fp || next_fp >= stack_limit) {
                break;
            }

            current_fp = next_fp;
        }

        return collected;
    }

    static void dump_to_stderr(std::span<const void*> trace) noexcept {
        AsyncSignalSafePrinter::write_literal("=== C++ Stack Backtrace ===\n");
        for (const auto* addr : trace) {
            AsyncSignalSafePrinter::write_literal("  [frame] ");
            AsyncSignalSafePrinter::write_address(reinterpret_cast<std::uintptr_t>(addr));
        }
    }
};

} // namespace diagnostic
```
:::

### Специфіка архітектури AArch64 та регістр x30

На 64-бітній архітектурі ARM (AArch64) угода про виклики AAPCS64 використовує фіксовану пару регістрів `x29` (Frame Pointer) та `x30` (Link Register). При кожному виклику інструкція `bl target_func` автоматично записує адресу повернення в регістр `x30`.

Стандартний пролог AArch64 записує обидва регістри однією паровою інструкцією:

```asm
stp x29, x30, [sp, #-16]!   // 1. Зберегти FP та LR на стек і зсунути SP на 16 байтів
mov x29, sp                 // 2. Встановити x29 на нову верхівку стека
```

Відповідно, у пам'яті кадру AArch64 за адресою `[x29 + 0]` розташовано збережений покажчик кадру `saved_fp`, а за адресою `[x29 + 8]` — збережений регістр зв'язку `x30` (адреса повернення). Це робить структуру кадру AArch64 двійково ідентичною x86-64, дозволяючи використовувати той самий алгоритм обходу ланцюга.

### Обробка сигнальних трамплінів (Signal Trampolines)

Коли ядро операційної системи передає керування в зареєстрований обробник сигналу (`sigaction`), воно формує на стеку спеціальний **сигнальний кадр** (англ. *signal frame* або *ucontext frame*), що містить копію всіх збережених регістрів процесора на момент переривання.

Після завершення обробника керування повертається в ядро через системний виклик `sigreturn` (так званий трамплін сигналу). Простий розмотувач за покажчиком кадру натрапить на сигнальний кадр як на розрив ланцюга, оскільки ядро не створює класичного прологу функції для точки переривання.

Щоб подолати сигнальний трамплін, системні розмотувачі вичитують структуру `ucontext_t` із третього аргументу розширеного обробника `sa_sigaction(int sig, siginfo_t* info, void* ucontext)` і безпосередньо витягують знімок регістрів `uc_mcontext.gregs[REG_RIP]` та `uc_mcontext.gregs[REG_RBP]`, продовжуючи розмотування від точки виникнення апаратного збою.

### Типові пастки компілятора та крайові випадки

1. **Функції-листки (Leaf Functions)**: функції, які не здійснюють вкладених викликів інших підпрограм і не використовують значного обсягу локальної пам'яті, компілятор оптимізує за замовчуванням, опускаючи генерацію прологу збереження `RBP`. У момент аварії всередині такої функції регістр `RBP` все ще вказує на кадр її викликаючої функції, тому перша зібрана адреса повернення перестрибне один рівень виклику вгору.
2. **Пошкодження пам'яті через переповнення буфера (Stack Smashing)**: якщо помилка в програмі призвела до запису за межі локального масиву, комірка збереженого покажчика `saved_fp` на стеку буде перезаписана сторонніми даними. Спроба безперевірочного розіменування покажчика `frame->saved_fp` викличе вторинний апаратний збій (англ. *double fault*) і аварійну загибель процесу. Захисні перевірки вирівнювання та монотонності адрес гарантують безпечну зупинку розмотувача в такій точці.
3. **Оптимізація хвостових викликів (Tail Call Elimination)**: якщо останнім виразом функції є прямий виклик іншої підпрограми (`return execute_subtask();`), компілятор перетворює інструкцію `call` на звичайний безумовний стрибок `jmp`. При цьому стековий кадр поточної функції перетирається кадром нової функції, і проміжна підпрограма повністю зникає з ланцюга викликів. Це є абсолютно легітимною оптимізацією, але розробник повинен пам'ятати про неї при читанні звітів розмотувача.
4. **Нестандартні кадри середовищ виконання JIT**: віртуальні машини мов Java (JVM), JavaScript (V8) або WebAssembly часто використовують оптимізовані власні угоди про виклики, де покажчик кадру може зберігатися в інших регістрах або не підтримувати стандартного вирівнювання x86-64 ABI. У таких змішаних стеках стандартний Frame Pointer unwinder зупиняється на межі нативного коду C++ та JIT-фрейму, вимагаючи спеціалізованих плагінів профайлера для перетину межі середовищ.
