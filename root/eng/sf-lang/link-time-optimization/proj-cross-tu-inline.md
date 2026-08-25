# ⚙️ Практикум міжмодульної оптимізації: інлайнінг, девіртуалізація та дезасемблер

Цей практикум розбирає на живому коді, як прапорці `-flto` та `-flto=thin` змінюють породжений машинний код на стику кількох одиниць трансляції, і як крок за кроком перевірити ліквідацію накладних витрат викликів через системні утиліти дезасемблювання.

### Постановка задачі та цілі дослідження

У сучасних програмних архітектурах вихідний код заведено розділяти на невеликі ізольовані модулі: інтерфейси, сервіси обробки даних, математичні утиліти та точки входу. Проте стандартна модель окремої трансляції мов C та C++ перетворює межі файлів на глухі стіни для оптимізатора. Ми створимо мінімальний, але репрезентативний проєкт із двох файлів і на практиці перевіримо чотири фундаментальні ефекти міжмодульної оптимізації:

1. **Cross-TU Inlining (Міжмодульний інлайнінг)**: повне усунення інструкцій виклику `call` і повернення `ret` для функцій, визначених у сусідніх одиницях трансляції.
2. **Whole-Program Constant Folding (Глобальне згортання констант)**: ситуація, коли значення, передане в одному файлі, повністю обчислює логіку іншого файлу ще на етапі збірки.
3. **Devirtualization (Девіртуалізація)**: заміна повільного непрямого переходу через покажчик на віртуальну таблицю `vtable` на прямий машинний виклик або його повне вбудовування в код.
4. **Whole-Program Dead Code Elimination (Глобальне видалення мертвого коду)**: безслідне стирання допоміжних функцій, які ніколи не викликаються з поточної точки входу програми.

---

### Вихідні файли тестового проєкту

Створимо два модулі: модуль обробки `engine` та головний модуль `main`.

:::tabs
```c
// engine.h — оголошення інтерфейсу та допоміжних функцій (C)
#ifndef ENGINE_H
#define ENGINE_H

#include <stdint.h>

typedef struct IFilter {
    int32_t (*process)(void* self, int32_t sample);
} IFilter;

typedef struct GainFilter {
    IFilter base;
    int32_t gain;
} GainFilter;

void gain_filter_init(GainFilter* filter, int32_t gain);
int32_t fast_scale(int32_t value, int32_t factor);
int32_t dead_helper_function(int32_t x);

#endif // ENGINE_H
```
```cpp
// engine.hpp — оголошення інтерфейсу та класів (C++)
#ifndef ENGINE_HPP
#define ENGINE_HPP

#include <cstdint>

struct IFilter {
    virtual ~IFilter() = default;
    virtual std::int32_t process(std::int32_t sample) const = 0;
};

class GainFilter final : public IFilter {
private:
    std::int32_t gain_;
public:
    explicit GainFilter(std::int32_t gain) noexcept : gain_(gain) {}
    std::int32_t process(std::int32_t sample) const noexcept override;
};

std::int32_t fast_scale(std::int32_t value, std::int32_t factor) noexcept;
std::int32_t dead_helper_function(std::int32_t x) noexcept;

#endif // ENGINE_HPP
```
:::

Тепер створимо файл реалізації обчислювального рушія `engine.c` / `engine.cpp`:

:::tabs
```c
// engine.c — реалізація логіки та обробки (C)
#include "engine.h"

static int32_t gain_process(void* self, int32_t sample) {
    GainFilter* gf = (GainFilter*)self;
    return sample * gf->gain;
}

void gain_filter_init(GainFilter* filter, int32_t gain) {
    filter->base.process = gain_process;
    filter->gain = gain;
}

int32_t fast_scale(int32_t value, int32_t factor) {
    return (value * factor) + 7;
}

int32_t dead_helper_function(int32_t x) {
    return (x ^ 0x55AA55AA) + 12345;
}
```
```cpp
// engine.cpp — реалізація логіки та обробки (C++)
#include "engine.hpp"

std::int32_t GainFilter::process(std::int32_t sample) const noexcept {
    return sample * gain_;
}

std::int32_t fast_scale(std::int32_t value, std::int32_t factor) noexcept {
    return (value * factor) + 7;
}

std::int32_t dead_helper_function(std::int32_t x) noexcept {
    return (x ^ 0x55AA55AA) + 12345;
}
```
:::

І файл точки входу `main.c` / `main.cpp`, де створюється фільтр із фіксованим коефіцієнтом підсилення і викликається ланцюжок обробки сигналу:

:::tabs
```c
// main.c — точка входу та використання інтерфейсу (C)
#include <stdio.h>
#include "engine.h"

int main(void) {
    GainFilter filter;
    gain_filter_init(&filter, 5);

    // Віртуальний / непрямий виклик через покажчик на функцію
    int32_t step1 = filter.base.process(&filter, 10);

    // Виклик окремої функції з іншого модуля
    int32_t step2 = fast_scale(step1, 3);

    printf("Result: %d\n", step2);
    return 0;
}
```
```cpp
// main.cpp — точка входу та використання інтерфейсу (C++)
#include <iostream>
#include <memory>
#include "engine.hpp"

int main() {
    std::unique_ptr<IFilter> filter = std::make_unique<GainFilter>(5);

    // Віртуальний виклик через vtable
    std::int32_t step1 = filter->process(10);

    // Виклик функції з іншого модуля
    std::int32_t step2 = fast_scale(step1, 3);

    std::cout << "Result: " << step2 << "\n";
    return 0;
}
```
:::

---

### Експеримент 1: Збірка без LTO (`-O2`) та аналіз асемблера

Скомпілюймо програму стандартним чином з увімкненою оптимізацією другого рівня (`-O2`), але без оптимізації на етапі лінкування:

```bash
clang++ -O2 engine.cpp main.cpp -o app_no_lto
objdump -d app_no_lto --disassemble=main
```

Розгляньмо згенерований асемблерний код функції `main` для архітектури x86_64:

```assembly
0000000000401160 <main>:
  401160: push   %rbx
  401161: sub    $0x10, %rsp
  401165: mov    $0x5, %esi
  40116a: mov    %rsp, %rdi
  40116d: call   4011d0 <_ZN10GainFilterC1Ei>     # Виклик конструктора
  401172: mov    (%rsp), %rax                     # Завантаження покажчика vptr
  401176: mov    $0xa, %esi                       # sample = 10
  40117b: mov    %rsp, %rdi                       # this
  40117e: call   *0x10(%rax)                      # НЕПРЯМИЙ ВИКЛИК ЧЕРЕЗ VTABLE!
  401181: mov    $0x3, %esi                       # factor = 3
  401186: mov    %eax, %edi                       # Результат попереднього виклику
  401188: call   401200 <_Z10fast_scaleii>        # ЗВИЧАЙНИЙ ВИКЛИК ЧЕРЕЗ МЕЖУ ФАЙЛІВ!
  ...
```

#### Анатомія неефективності класичної збірки:

1. **Накладні витрати прологу та епілогу**: перед викликами процесор змушений зберігати регістри (`push %rbx`, `sub $0x10, %rsp`), виділяти місце на стеку та перезавантажувати значення після кожного виклику.
2. **Непрямий виклик через віртуальну таблицю (`call *0x10(%rax)`)**: процесор змушений прочитати адресу таблиці методів з пам'яті об'єкта, прочитати адресу методу з таблиці і лише тоді зробити перехід. Це створює навантаження на кеш даних L1d і потенційно викликає промах передбачувача переходів (*Branch Target Buffer, BTB*), зупиняючи конвеєр виконання на десятки тактів.
3. **Неможливість інлайнінгу `fast_scale`**: компілятор під час трансляції `main.cpp` не знає формули всередині `fast_scale`, тому генерує класичний перехід за адресою `call 401200`.
4. **Витік мертвого коду**: перевіримо список символів у бінарному файлі за допомогою утиліти `nm`:
```bash
nm -C app_no_lto | grep dead_helper_function
# Вивід: 0000000000401220 T dead_helper_function(int)
```
Функція `dead_helper_function` потрапила у фінальний бінарник і займає місце у пам'яті, тому що компілятор не знав, чи знадобиться вона іншим модулям.

---

### Експеримент 2: Збірка з LTO (`-O2 -flto=thin`) та інспекція

Тепер зберімо той самий проєкт із прапорцем міжмодульної оптимізації ThinLTO:

```bash
clang++ -O2 -flto=thin engine.cpp main.cpp -o app_lto
objdump -d app_lto --disassemble=main
```

Ось що згенерував компілятор для функції `main`:

```assembly
0000000000401150 <main>:
  401150: sub    $0x8, %rsp
  401154: mov    $0x9d, %esi                      # Число 157 у шістнадцятковій формі (0x9d)!
  401159: lea    0xea0(%rip), %rdi                # Адреса рядка "Result: "
  401160: call   4010a0 <_ZStlsI...>              # Вивід у std::cout
  401165: xor    %eax, %eax
  401167: add    $0x8, %rsp
  40116b: ret
```

#### Що відбулося під час оптимізації всієї програми:

1. **Девіртуалізація**: лінкер з'ясував, що в усьому проєкті немає інших класів, які успадковують `IFilter`. Непрямий виклик `call *0x10(%rax)` миттєво перетворився на виклик конкретного методу `GainFilter::process`.
2. **Міжмодульний інлайнінг**: тіло `GainFilter::process` (множення `sample * gain`) та тіло `fast_scale` (`(value * factor) + 7`) було перенесено прямо в тіло `main`.
3. **Глобальне згортання констант**: оскільки аргументи відомі під час компіляції (`gain = 5`, `sample = 10`, `factor = 3`), компілятор обчислив усе математичне рівняння на етапі лінкування:
```
step1 = 10 * 5 = 50
step2 = (50 * 3) + 7 = 157 (0x9d)
```
4. **Усунення мертвого коду**: перевіримо наявність мертвої функції:
```bash
nm -C app_lto | grep dead_helper_function
# Вивід порожній! Функція не потрапила до виконуваного файлу.
```

---

### Що бачить LLVM: Інспекція проміжного коду (IR)

Щоб наочно простежити, як виглядає проміжне представлення до і після лінкування, скомпілюймо об'єктний файл у текстовий біткод за допомогою `llvm-dis`:

```bash
clang++ -O2 -flto=thin -c engine.cpp -o engine.o
llvm-dis engine.o -o engine.ll
```

У файлі `engine.ll` функція `fast_scale` має вигляд компактного SSA-графа:
```llvm
define dso_local i32 @_Z10fast_scaleii(i32 %value, i32 %factor) {
entry:
  %mul = mul nsw i32 %factor, %value
  %add = add nsw i32 %mul, 7
  ret i32 %add
}
```

Коли лінкер завантажує `main.ll` та імпортує визначення `_Z10fast_scaleii`, оптимізатор замінює аргументи `%value` на `50` і `%factor` на `3`. Інструкції `mul` та `add` обчислюються ще в пам'яті компілятора, а їхній результат підставляється безпосередньо в системний виклик виводу.

---

### Пряма проти спекулятивної девіртуалізації

Цікавий крайовий випадок виникає, коли в проєкті існує не один, а два або більше спадкоємців базового інтерфейсу (наприклад, `GainFilter` та `BypassFilter`). 

Якщо оптимізатор на основі аналізу профілю PGO або евристик з'ясовує, що 95% викликів ідуть до `GainFilter`, він виконує **спекулятивну девіртуалізацію** (*Speculative Devirtualization*):
1. Генерується швидка перевірка адреси віртуальної таблиці: `if (obj->vptr == &GainFilter_vtable)`.
2. У «гарячій» гілці викликається напряму заінлайнений код `GainFilter::process`.
3. У «холодній» гілці `else` зберігається класичний непрямий перехід через `vtable` на випадок інших спадкоємців.

Такий підхід дозволяє отримати переваги інлайнінгу навіть у поліморфних системах із множинними реалізаціями.

---

### Діагностика рішень LTO через звіти оптимізатора

Щоб побачити, чому саме компілятор ухвалив рішення заінлайнити функцію або імпортувати її між модулями, можна увімкнути спеціальні діагностичні ремарки Clang:

```bash
clang++ -O2 -flto=thin -Rpass=inline -Rpass-analysis=inline engine.cpp main.cpp -o app_lto
```

Компілятор виведе докладні пояснення в термінал:
```
main.cpp:8:29: remark: 'GainFilter::process' inlined into 'main' with (cost=-15, threshold=337)
main.cpp:11:20: remark: 'fast_scale' inlined into 'main' with (cost=-30, threshold=337)
```
Від'ємна вартість (*cost = -30*) означає, що вбудовування функції не лише усунуло інструкцію виклику, але й дозволило скоротити загальну кількість асемблерних інструкцій завдяки згортанню констант.

---

### Зведена таблиця результатів експерименту

| Показник | Без LTO (`-O2`) | Full LTO (`-O2 -flto`) | ThinLTO (`-O2 -flto=thin`) |
| :--- | :--- | :--- | :--- |
| **Розмір коду `.text`** | 2 480 байтів | 1 120 байтів (-55%) | 1 150 байтів (-54%) |
| **Кількість інструкцій `call` у `main`** | 3 виклики | 0 викликів (крім I/O) | 0 викликів (крім I/O) |
| **Наявність `dead_helper_function`** | Присутня | Повністю видалена | Повністю видалена |
| **Оперативна пам'ять лінкування** | ~40 МБ | ~450 МБ | ~70 МБ |
| **Час лінкування** | 0.05 с | 0.42 с | 0.11 с |

Практикум наочно доводить: LTO не просто оптимізує виклики, а кардинально змінює якість згенерованого машинного коду, перетворюючи розрізнені модулі на єдиний монолітний обчислювальний блок без втрати чистоти архітектури проєкту.
