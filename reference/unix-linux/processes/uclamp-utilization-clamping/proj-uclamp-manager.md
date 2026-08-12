# ⚙️ Реалізація менеджера утилізації uclamp для потоків та Cgroups

Цей проєкт показує розробку виробничого менеджера профілів продуктивності для Linux-систем із суворими вимогами до низької затримки (low latency) та енергозбереження. Менеджер динамічно змінює параметри утилізації `uclamp_min` та `uclamp_max` для потоків додатка залежно від поточного стану виконання та ролі конкретного потоку.

## Концепція та архітектура профілів

Під час розробки високозавантажених застосунків (наприклад, графічних рушіїв, аудіоплеєрів реального часу або мережевих серверів) виникає потреба розділити потоки на декілька категорій за їхнім впливом на сприйняття користувача та енергоспоживання:

1. **Профіль Latency-Critical (Інтерактивний потік):**
   Використовується під час відтворення UI-анімацій, обробки аудіосигналів або обробки мережевих пакетів. Встановлює `uclamp_min = 600` (~58% від максимальної ємності CPU), що гарантує негайне розганяння тактової частоти регулятором `schedutil` і вибір продуктивного ядра (MID/BIG у системі ARM DynamIQ) без затримки розігріву PELT.
2. **Профіль Background-Saver (Фоновий потік):**
   Використовується під час виконання періодичного збереження даних, індексації або логування. Встановлює `uclamp_max = 250` (~24% від максимальної ємності CPU), що забороняє регулятору частоти піднімати тактову частоту ядра вище енергоефективного рівня і утримує потік на LITTLE-ядрах.
3. **Профіль Default (Стандартне планування):**
   Скидає обмеження до початкового стану системи (`uclamp_min = 0`, `uclamp_max = 1024`), повертаючи потік до стандартного режиму планування CFS без додаткових фільтрів.

## Детальний розбір реалізації мовами C та C++

У реалізаціях мовами C та C++ нижче демонструється виклик системного виклику `sched_setattr(2)` з налаштуванням прапорів `SCHED_FLAG_UTIL_CLAMP_MIN` та `SCHED_FLAG_UTIL_CLAMP_MAX`. 

У коді на мові C ми самостійно оголошуємо заголовок структури `sched_attr` та обгортку над системним викликом `syscall(SYS_sched_setattr, ...)`, оскільки системна бібліотека glibc може не надавати прямої обгортки у старих версіях системних заголовочних файлів.

Приклад на мові C++ реалізований у сучасному ідіоматичному стилі C++23 із застосуванням типу `std::expected` для безпечної повернення помилок без використання класичних винятків або сирих вказівників, із чітким розділенням профілів через перелічуваний тип `enum class Profile`. Обгортка дозволяє динамічно перемикати режими роботи потоку під час зміни інтерфейсних станів.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/syscall.h>
#include <linux/sched/types.h>

#ifndef SYS_sched_setattr
#define SYS_sched_setattr 314
#endif

#ifndef SCHED_FLAG_UTIL_CLAMP_MIN
#define SCHED_FLAG_UTIL_CLAMP_MIN 0x20
#endif

#ifndef SCHED_FLAG_UTIL_CLAMP_MAX
#define SCHED_FLAG_UTIL_CLAMP_MAX 0x40
#endif

static int sys_sched_setattr(pid_t pid, const struct sched_attr *attr, unsigned int flags) {
    return syscall(SYS_sched_setattr, pid, attr, flags);
}

int set_thread_uclamp(pid_t tid, unsigned int min_util, unsigned int max_util) {
    struct sched_attr attr;
    memset(&attr, 0, sizeof(attr));
    attr.size = sizeof(attr);
    attr.sched_policy = SCHED_OTHER;

    attr.sched_flags = 0;
    if (min_util <= 1024) {
        attr.sched_flags |= SCHED_FLAG_UTIL_CLAMP_MIN;
        attr.sched_util_min = min_util;
    }
    if (max_util <= 1024) {
        attr.sched_flags |= SCHED_FLAG_UTIL_CLAMP_MAX;
        attr.sched_util_max = max_util;
    }

    if (sys_sched_setattr(tid, &attr, 0) < 0) {
        perror("sys_sched_setattr failed");
        return -1;
    }

    return 0;
}

int main(void) {
    pid_t tid = gettid();
    printf("[C] Налаштування uclamp для потоку TID=%d...\n", tid);

    if (set_thread_uclamp(tid, 600, 1024) == 0) {
        printf("[C] Успішно застосовано профіль Latency-Critical (uclamp_min=600)\n");
    }

    usleep(100000);

    if (set_thread_uclamp(tid, 0, 250) == 0) {
        printf("[C] Успішно застосовано профіль Background Saver (uclamp_max=250)\n");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <system_error>
#include <expected>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/sched/types.h>

namespace sys {
    #ifndef SYS_sched_setattr
    #define SYS_sched_setattr 314
    #endif

    #ifndef SCHED_FLAG_UTIL_CLAMP_MIN
    #define SCHED_FLAG_UTIL_CLAMP_MIN 0x20
    #endif

    #ifndef SCHED_FLAG_UTIL_CLAMP_MAX
    #define SCHED_FLAG_UTIL_CLAMP_MAX 0x40
    #endif
}

class UtilizationClamp {
public:
    enum class Profile {
        LatencyCritical,
        BackgroundEnergySaver,
        Default
    };

    static std::expected<void, std::error_code> apply(pid_t tid, Profile profile) noexcept {
        struct sched_attr attr{};
        attr.size = sizeof(attr);
        attr.sched_policy = SCHED_OTHER;

        switch (profile) {
            case Profile::LatencyCritical:
                attr.sched_flags = SCHED_FLAG_UTIL_CLAMP_MIN | SCHED_FLAG_UTIL_CLAMP_MAX;
                attr.sched_util_min = 600;  // Підтягуємо мінімум до ~58%
                attr.sched_util_max = 1024; // Не обмежуємо максимум
                break;
            case Profile::BackgroundEnergySaver:
                attr.sched_flags = SCHED_FLAG_UTIL_CLAMP_MIN | SCHED_FLAG_UTIL_CLAMP_MAX;
                attr.sched_util_min = 0;
                attr.sched_util_max = 256;  // Затискаємо максимум до ~25%
                break;
            case Profile::Default:
                attr.sched_flags = SCHED_FLAG_UTIL_CLAMP_MIN | SCHED_FLAG_UTIL_CLAMP_MAX;
                attr.sched_util_min = 0;
                attr.sched_util_max = 1024;
                break;
        }

        long res = ::syscall(SYS_sched_setattr, tid, &attr, 0);
        if (res < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }
};

int main() {
    pid_t tid = ::gettid();
    std::cout << "[C++] Налаштування uclamp для потоку TID=" << tid << "...\n";

    auto res = UtilizationClamp::apply(tid, UtilizationClamp::Profile::LatencyCritical);
    if (!res) {
        std::cerr << "Помилка застосування профілю: " << res.error().message() << '\n';
        return 1;
    }
    std::cout << "[C++] Успішно встановлено профіль LatencyCritical (uclamp_min=600)\n";

    ::usleep(100000);

    res = UtilizationClamp::apply(tid, UtilizationClamp::Profile::BackgroundEnergySaver);
    if (!res) {
        std::cerr << "Помилка застосування профілю: " << res.error().message() << '\n';
        return 1;
    }
    std::cout << "[C++] Успішно встановлено профіль BackgroundEnergySaver (uclamp_max=256)\n";

    return 0;
}
```
:::

## Перевірка та верифікація роботи у системі Linux

Після виклику системного виклику `sched_setattr(2)` розробник може підтвердити застосування параметрів у ядрі декількома незалежними шляхами:

1. **Інспекція через procfs:**
   Кожен потік у Linux має текстовий інтерфейс статусу планувальника `/proc/<PID>/task/<TID>/sched`. Прочитавши його, можна переконатися у підтвердженні значений полів `uclamp.min` та `uclamp.max`:
   ```bash
   cat /proc/self/task/$(gettid)/sched | grep uclamp
   ```
   У відповідь ядро повертає дійсні нормалізовані значення 0–1024 та стан прапора `uclamp.user_defined`.

2. **Трейсинг подій регулятора частоти:**
   Підсистема трейсингу ядра `ftrace` дозволяє відслідковувати реальні запити регулятора `schedutil` до драйвера CPUFreq під час виконання програми:
   ```bash
   echo 1 > /sys/kernel/tracing/events/sched/sched_util_clamp/enable
   cat /sys/kernel/tracing/trace_pipe
   ```
   У логування потрапляють миттєві значення `util_cfs` (фізичний PELT) та `util_clamp` (підсумкове значення після фільтрації), що підтверджує ефективний вплив коду на тактову частоту CPU.

3. **Перевірка Cgroups v2 ефективних значень:**
   Якщо процес виконується всередині cgroup з обмеженими значеннями, підсумкове значення утилізації завжди вибирається як найбільш строге обмеження між налаштуваннями потоку та налаштуваннями cgroup. Перевірити ефективний стан можна у файлі `cpu.stat` відповідної cgroup. Це дозволяє гарантувати, що локальні налаштування потоку не перевищують лімітів всієї групи.

## Оптимізація та аналіз продуктивності

Під час інтеграції uclamp у реальні виробничі сервіси слід враховувати кілька важливих факторів продуктивності:

- **Витрати системних викликів:** Не слід викликати `sched_setattr(2)` на кожному такті обчислювального циклу (наприклад, усередині гарячого циклу обробки кадрів). Виклик системного виклику має контекстний перехід `user->kernel`, який займає від 100 до 300 наносекунд. Перемикати профілі слід лише під час зміни стану потоку (наприклад, при переході додатку у фоновий режим або отриманні нового фокусу введення).
- **Взаємодія з CPUAffinity:** uclamp доповнює, але не замінює прив'язку потоків до ядер (CPU affinity). Якщо потік примусово прив'язаний лише до LITTLE-ядра за допомогою `sched_setaffinity(2)`, навіть високий `uclamp_min` не зможе перемістити його на BIG-ядро. Тому для гнучкого планування рекомендується залишати потоку доступ до всіх ядер системи, дозволяючи планувальнику EAS приймати рішення на основі утилізації.
- **Обробка привілеїв `CAP_SYS_NICE`:** Під час розробки контейнеризованих додатків або сервісів під управлінням `systemd` переконайтеся, що процес має потрібні мандати безпеки для підвищення `uclamp_min`. У юнітах `systemd` це налаштовується опцією `CapabilityBoundingSet=CAP_SYS_NICE`.

## Практичний сценарій застосування у високонавантажених серверах

У високонавантажених веб-серверах (наприклад, NGINX або Node.js) uclamp дозволяє розділити головний потік прийому з'єднань (event loop thread) та воркер-потоки стиснення даних. Прив'язка `uclamp_min = 500` для event loop запобігає затримкам обробки нових TCP-з'єднань при періодичному простої, гарантуючи миттєвий відгук мережевого стеків ядра.

## Захист від starvation та виснаження ресурсів

Застосування `uclamp_max` для фонових задач гарантує захист інтерактивних процесів від голодування (starvation). Оскільки фоновий потік обмежений у частоті та ємності ядра, планивальник зберігає вільні обчислювальні ресурси для швидкого виконання коротких сплесків обчислень додатків користувача.

## Тестування під навантаженням через rt-app

Для автоматизованого тестування ефективності uclamp у лабораторіях розробники ядра використовують утиліту `rt-app`. Створення тестового сценарію з циклічною зміною фаз активності дозволяє точно виміряти затримку відгуку регулятора `schedutil` на різних апаратних платформах, гарантуючи відповідність SLA системи.

## Рекомендації для контейнеризованих середовищ (Kubernetes/Docker)

У контейнерних середовищах на базі Kubernetes рекомендується поєднувати `cpu.weight` з налаштуваннями `cpu.uclamp.min` для Pods класу Guaranteed або Burstable. Це дозволяє запобігти падінню тактової частоти вузла під час міжпакетних пауз у роботі критичних сервісів.
