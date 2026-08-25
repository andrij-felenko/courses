# Нюанси Android: NDK, ABI, рівень API

<preknowlist>
- [Крос-компіляція: хост, ціль і що між ними](root:sys-bsystem/cross-compilation)
- [Цільовий тріплет і sysroot](root:sys-bsystem/target-triple-sysroot)
- [Файл тулчейна: як CMake дізнається про чужу платформу](root:sys-bsystem/cmake-toolchain-file)
- [Статичне та динамічне компонування в Linux](root:sys-unix/static-and-dynamic-linking)
- [Порушення правила єдиного визначення (ODR)](root:sys-plang-cpp/odr-and-linkage)
</preknowlist>

Спроба скомпілювати готову C чи C++ бібліотеку звичайним компілятором для Linux (наприклад, під цільову архітектуру `aarch64-unknown-linux-gnu`) і завантажити отриманий файл `.so` в Android-застосунок через виклик `System.loadLibrary()` або нативний `dlopen()` завершується аварійною зупинкою в перші ж мілісекундах роботи. Системний динамічний лінкер `/system/bin/linker64` миттєво повертає помилку `dlopen failed: cannot locate symbol ...` або виявляє невідповідність заголовків ELF. Хоча Android побудований на базі ядра Linux, його користувацький простір (userspace) не має нічого спільного зі стандартним дистрибутивом GNU/Linux. Тут відсутня бібліотека GNU C (glibc), немає стандартного завантажувача `ld.so`, динамічне компонування жорстко обмежене просторами імен лінкера (Linker Namespaces), а кожен системний виклик фільтрується політиками Seccomp і SELinux під наглядом середовища виконання Android Runtime (ART).

Для створення нативного коду під цю специфічну платформу компанія Google постачає Android Native Development Kit (NDK). Це не просто набір крос-компіляторів, а складна інженерна екосистема, що поєднує інструменти LLVM Clang, системні заголовки та заглушки бібліотеки Bionic libc, файл тулчейна для систем збірки CMake та середовище пакування у двійкові пакети APK і AAB. Успішна збірка нативних модулів вимагає глибокого розуміння чотирьох фундаментальних вимірів: архітектури NDK toolchain, цільових ABI процесора, рівнів API платформи (`minSdkVersion`) та моделі компонування рантайму C++.

---

## 1. Архітектура Android NDK та бібліотека Bionic libc

Кожен випуск Android NDK містить повноцінний самодостатній набір інструментів (toolchain), побудований на базі компілятора Clang та компонувальника LLD з проєкту LLVM. У сучасних версіях NDK розробникам більше не потрібно вручну генерувати окремі автономні ланцюжки інструментів (Standalone Toolchains): єдиний каталог `toolchains/llvm/prebuilt/<host-tag>/` містить один екземпляр бінарників `clang` та `clang++`, які здатні генерувати машинний код для будь-якої підтримуваної цільової архітектури шляхом передачі спеціалізованого цільового тріплету.

![Архітектура NDK Toolchain, Sysroot та Bionic](/root/sys/sys-bsystem/android-ndk-nuances/img/ndk-toolchain-sysroot.svg)
*Взаємодія хостового тулчейна Clang, заглушок NDK sysroot та середовища Bionic на цільовому пристрої.*

### Анатомія цільового тріплету
Коли система збірки звертається до компілятора, вона передає прапорець цілі у форматі:
```text
<arch>-linux-android<API>-clang
```
Наприклад, виклик `aarch64-linux-android29-clang` повідомляє компілятору Clang одразу три ключові параметри:
1. `aarch64`: цільова 64-бітна архітектура процесора ARMv8-A.
2. `linux-android`: операційна система Android на базі ядра Linux, що вмикає специфічні правила генерації коду, вирівнювання та формат таблиць розгортання стека (unwind tables).
3. `29`: мінімальний рівень API Android (Android 10), під який компілюється код. Цей номер автоматично визначає значення препроцесорного макроса `__ANDROID_API__=29` і задає версіонування символів Bionic.

### Bionic libc: системна бібліотека мобільного світу
Ключова відмінність Android від класичних операційних систем сімейства Unix полягає у використанні Bionic libc замість GNU C Library (glibc) або musl. Bionic було створено з нуля під жорсткі вимоги мобільних пристроїв: мінімальне споживання оперативної пам'яті, надшвидкий запуск процесів (через форк від шаблону Zygote), низькі накладні витрати на системні виклики та ліцензія BSD, що не накладає вірусних вимог GPL на пропрієтарні драйвери виробників обладнання.

Однак оптимізація Bionic супроводжується значними функціональними обмеженнями, про які зобов'язаний знати кожен системний інженер:
* **Відсутність повноцінної підтримки локалей (`locale`):** Bionic не підтримує зміну локалі через виклик `setlocale()` на щось інше, крім стандартних режимів `"C"` або `"POSIX"` (з неявним припущенням кодування UTF-8). Спроба підключити важкі бібліотеки парсингу тексту, що спираються на POSIX-функції локалізації або інтерфейси `iconv.h`, призводить до помилок компонування або некоректної обробки символів, оскільки `iconv` не є частиною Bionic.
* **Специфіка реалізації потоків POSIX (`pthreads`):** у Bionic відсутня підтримка функції `pthread_cancel()`. Причина цього архітектурного рішення фундаментальна: в середовищі Android нативні потоки тісно інтегровані з віртуальною машиною ART/Dalvik. Асинхронне переривання потоку без гарантованого виконання блоків очищення може призвести до блокування внутрішніх м'ютексів збирача сміття (Garbage Collector) або пошкодження стану пам'яті Java-об'єктів. Замість цього розробники змушені використовувати кооперативні механізми переривання через атомарні прапорці чи канали сповіщень.
* **Вбудовані алокатори пам'яті з апаратним захистом:** на відміну від glibc, де використовується алокатор ptmalloc, у Bionic історично застосовувався jemalloc, а в сучасних версіях Android (починаючи з Android 11) стандартом став алокатор Scudo. Він оптимізований для виявлення вразливостей пошкодження пам'яті (double-free, heap buffer overflow, use-after-free) і підтримує технологію апаратного тегування пам'яті ARM Memory Tagging Extension (MTE) на архітектурах ARMv8.5-A+.
* **Динамічний лінкер із просторами імен (Linker Namespaces):** починаючи з Android 7.0 (API 24), динамічний лінкер `/system/bin/linker` (для 32-бітних систем) та `/system/bin/linker64` (для 64-бітних) реалізує сувору ізоляцію бібліотек. Застосунок має право динамічно підвантажувати через `dlopen()` виключно офіційні NDK-бібліотеки зі списку NDK Public Libraries (такі як `libc.so`, `libm.so`, `libz.so`, `liblog.so`, `libEGL.so`, `libvulkan.so`) та власні `.so` файли, запаковані всередину APK. Будь-яка спроба викликати `dlopen("libart.so")` чи підключити приватну системну бібліотеку з каталогу `/system/lib64/` завершиться фатальною помилкою доступу.

---

## 2. Цільові двійкові інтерфейси (ABI)

Двійковий інтерфейс застосунку (Application Binary Interface, ABI) визначає точний контракт взаємодії машинного коду з процесором та операційною системою: набір інструкцій, розмір і порядок байтів (endianness), регістровий розподіл параметрів під час виклику функцій (calling convention), розкладку типів даних у пам'яті та правила вирівнювання стека.

Сучасний Android NDK підтримує чотири офіційні ABI:

| ABI | Архітектура процесора | Розрядність | Набір інструкцій та розширення | Основне призначення |
|---|---|---|---|---|
| `arm64-v8a` | ARMv8-A (AArch64) | 64 біти | NEON, FP, 64-бітні регістри, AAPCS64 | Усі сучасні смартфони, планшети, телевізори |
| `armeabi-v7a` | ARMv7-A (32-bit ARM) | 32 біти | Thumb-2, VFPv3-D16 (NEON за замовчуванням з r21) | Бюджетні пристрої, застарілі телефони, носимі ґаджети |
| `x86_64` | x86-64 (AMD64) | 64 біти | MMX, SSE4.2, POPCNT, 64-бітний режим | Емулятори Android Studio, пристрої ChromeOS |
| `x86` | IA-32 (x86) | 32 біти | MMX, SSE3, SSSE3 | Застарілі 32-бітні емулятори |

Застарілі архітектури `armeabi` (ARMv5 без апаратної плаваючої коми), `mips` та `mips64` було безповоротно видалено в NDK r17 через відсутність реальних комерційних пристроїв на ринку.

### Нюанси архітектури `armeabi-v7a`
Для 32-бітного ARM-коду NDK за замовчуванням генерує інструкції Thumb-2 (`-mthumb`), що являють собою суміш 16-бітних та 32-бітних команд. Це зменшує розмір бінарного файлу на 25–35% порівняно зі стандартним 32-бітним режимом ARM (`-marm`) при практично ідентичній швидкодії. Крім того, починаючи з версії NDK r21, для `armeabi-v7a` векторний рушій ARM NEON (`-mfpu=neon`) увімкнено за замовчуванням, тоді як у старіших версіях вимагався ручний прапорець або підтримка лише базового блоку VFPv3-D16 (всього 16 регістрів FPU проти 32 у повноцінному NEON).

Головне системне обмеження `armeabi-v7a` — 32-бітний адресний простір, де одному процесу доступно щонайбільше 3–4 ГБ віртуальної пам'яті (з яких значну частину займає адресний простір ядра та ART heap).

### Нюанси архітектури `arm64-v8a`
64-бітна архітектура AArch64 повністю відмовилася від компромісів: вона не має режиму Thumb, використовує фіксовані 32-бітні коди інструкцій, надає 31 універсальний 64-бітний регістр (`x0`–`x30`), 32 регістри для векторів NEON/плаваючої коми довжиною 128 бітів кожен (`v0`–`v31`) та обов'язкову підтримку апаратних операцій з плаваючою комою подвійної точності за стандартом IEEE 754.

### Вирівнювання сторінок 16 КБ (16 KB Page Size у Android 15+)
Протягом понад десятиліття всі пристрої Android використовували ядро Linux зі стандартним розміром сторінки віртуальної пам'яті 4 КБ (4096 байтів). Однак зі збільшенням обсягів оперативної пам'яті та ускладненням графічних навантажень розмір сторінки 4 КБ став вузьким місцем трансляції адрес через часті промахи буфера TLB (Translation Lookaside Buffer).

Починаючи з Android 15 (та в емуляторах з відповідною конфігурацією), Google запровадив підтримку ядер з розміром сторінки 16 КБ (16384 байти). Це підвищує загальну швидкодію системи на 5–10%, але створює серйозну загрозу для нативного коду.

![Вимога вирівнювання сегментів ELF під розмір сторінки 16 KB](/root/sys/sys-bsystem/android-ndk-nuances/img/elf-page-alignment-16k.svg)
*Конфлікт сторінкового відображення mmap при вирівнюванні 4 KB на ядрі з 16 KB сторінками та його вирішення.*

Механізм завантаження спільної бібліотеки `.so` в пам'ять спирається на системний виклик ядра `mmap()`, який відображає сегменти `PT_LOAD` з ELF-файлу безпосередньо у віртуальний адресний простір процесу. Для успішного відображення без копіювання ядро вимагає дотримання інваріанта рівності залишків ділення:
```text
p_vaddr % PageSize == p_offset % PageSize
```
де `p_vaddr` — віртуальна адреса завантаження сегмента, а `p_offset` — зміщення цього сегмента від початку ELF-файлу на диску.

Якщо бібліотеку було скомпільовано зі старим вирівнюванням `max-page-size=4096`, зміщення другого сегмента (наприклад, сегмента даних `RW`) у файлі може бути вирівняно лише на `0x1000` (4 КБ). При спробі виконати `dlopen()` на ядрі з 16 КБ сторінками умова `0x6000 % 16384 == 0x1000 % 16384` порушується, ядро не здатне відобразити файл сторінками по 16 КБ, і лінкер повертає критичну помилку:
```text
dlopen failed: "libapp.so" has text relocations / LOAD segment not page-aligned
```

Для забезпечення сумісності всі сучасні проєкти мають компонуватися з обов'язковим прапорцем компонувальника LLD:
```text
-Wl,-z,max-page-size=16384
```
Бібліотека, вирівняна на 16 КБ, залишається на 100% сумісною і зі старими ядрами 4 КБ, оскільки число 16384 ділиться на 4096 без залишку.

Перевірити коректність вирівнювання зібраного бінарника можна за допомогою утиліти `llvm-readelf`:
```bash
llvm-readelf -l libapp.so | grep -A 2 LOAD
```
У виводі стовпець `Align` для кожного сегмента `LOAD` повинен містити значення `0x4000` (16 КБ) або більше.

---

## 3. Рівні API (API Levels), `minSdkVersion` та заглушки sysroot

У конфігурації Android-проєкту ключову роль відіграє параметр `minSdkVersion`. Для розробника на Java або Kotlin він означає мінімальну версію системи, на якій дозволено встановити застосунок. Проте для компілятора C/C++ цей параметр є жорсткою межею доступності системних викликів ядра та функцій Bionic libc.

### Макрос `__ANDROID_API__` та атрибути заголовків
Під час конфігурації CMake або прямого виклику Clang параметр `minSdkVersion` передається через макрос `-D__ANDROID_API__=<N>`. Усі заголовки NDK sysroot (Unified Headers) використовують атрибути компілятора виду `__INTRODUCED_IN(api_level)`.

Розглянемо оголошення та використання функцій у клієнтському коді:

:::tabs
@tab C
```c
#include <sys/epoll.h>
#include <sys/random.h>
#include <unistd.h>
#include <errno.h>

/* Системні оголошення Bionic libc у заголовках NDK */
int epoll_create(int size);
int epoll_create1(int flags) __INTRODUCED_IN(21);
ssize_t getrandom(void *buf, size_t buflen, unsigned int flags) __INTRODUCED_IN(28);

/* Безпечний виклик системного API */
int initialize_event_loop(void) {
    /* Якщо __ANDROID_API__ < 21, epoll_create1 буде заблоковано на етапі збірки */
    int fd = epoll_create1(EPOLL_CLOEXEC);
    if (fd < 0) {
        return -errno;
    }
    return fd;
}
```
@tab C++
```cpp
#include <sys/epoll.h>
#include <sys/random.h>
#include <unistd.h>
#include <span>
#include <system_error>

namespace sys {
[[nodiscard]] inline int initialize_event_loop() {
    int fd = ::epoll_create1(EPOLL_CLOEXEC);
    if (fd < 0) {
        throw std::system_error(errno, std::generic_category(), "epoll_create1 failed");
    }
    return fd;
}

inline void fill_secure_random(std::span<std::byte> buffer) {
    ssize_t res = ::getrandom(buffer.data(), buffer.size_bytes(), 0);
    if (res < 0) {
        throw std::system_error(errno, std::generic_category(), "getrandom failed");
    }
}
} // namespace sys
```
:::

Якщо проект налаштовано на `minSdkVersion = 19`, компілятор зустрічає виклик `getrandom()` і перевіряє умову: оскільки поточний рівень `__ANDROID_API__ (19) < 28`, символ оголошується недоступним. Якщо розробник спробує обійти компілятор через власне попереднє оголошення сигнатури, збій станеться на етапі лінкування.

### Заглушки sysroot (Stub Libraries)
NDK не містить повноцінних бінарників `libc.so` чи `libm.so` з кодом реалізації — адже справжні системні бібліотеки вже встановлено в образ кожного фізичного пристрою Android. Натомість NDK містить спеціальні файли-заглушки (stubs) у каталогах:
```text
$NDK/toolchains/llvm/prebuilt/<host>/sysroot/usr/lib/<triple>/<API>/libc.so
```
Ці файли мають мізерний розмір (декілька кілобайтів) і містять виключно таблицю експортованих символів (ELF Dynamic Symbol Table). Для `API = 19` у таблиці символів заглушки `libc.so` фізично немає запису `getrandom` або `epoll_create1`. Тому компонувальник `lld` негайно видає помилку `undefined reference to 'getrandom'`.

### Хронологія появи ключових системних викликів Bionic

* **Android 5.0 (API 21):** переломний реліз в історії NDK. Запроваджено підтримку 64-бітних архітектур (`arm64-v8a`, `x86_64`), додано виклики `epoll_create1()`, `accept4()`, `dup3()`, `pipe2()`, `eventfd()`, а також запроваджено вимогу обов'язкової підтримки PIE (Position Independent Executables).
* **Android 6.0 (API 23):** додано системні виклики роботи з каталогами `seekdir()`, `telldir()`, покращено підтримку багатопотокових атоміків C11.
* **Android 8.0 (API 26):** додано підтримку розширеного контексту роботи з файлами `futimens()`, розширено POSIX-таймери.
* **Android 9.0 (API 28):** додано офіційну обгортку Bionic для системного виклику `getrandom()` (до цього розробники мусили зчитувати байти безпосередньо з псевдопристрою `/dev/urandom` або викликати ядро через сирий `syscall(__NR_getrandom, ...)`).
* **Android 10 (API 29):** запроваджено APEX-модулі для системного рантайму, бібліотека `libc.so` перемістилася в каталог `/apex/com.android.runtime/lib64/bionic/libc.so`.

### Проблема 32-бітного часу (Year 2038 Problem на 32-бітних ABI)
Критичним крайовим випадком сумісності Bionic є розмір типу даних `time_t` на 32-бітних архітектурах (`armeabi-v7a` та `x86`). У класичному glibc перехід на 64-бітний `time_t` реалізується через макрос `_TIME_BITS=64`. Проте в Bionic на 32-бітних ABI тип `time_t` жорстко зафіксований як 32-бітне значуще ціле число (`int32_t`).

Зміна розміру `time_t` у структурах Bionic (наприклад, у `struct stat` або `struct timeval`) зруйнувала б двійкову сумісність (ABI breakage) з усіма скомпільованими бібліотеками за всю історію Android. Тому 32-бітні програми для Android гарантовано зіткнуться з переповненням часу в січні 2038 року. На 64-бітних архітектурах (`arm64-v8a`, `x86_64`) тип `time_t` був спочатку визначений як 64-бітний (`int64_t`), тому 64-бітний нативний код позбавлений цієї проблеми.

---

## 4. Рантайм C++: руйнування ODR та вибір між `libc++_static` і `libc++_shared`

У сучасному NDK єдиною підтримуваною реалізацією стандартної бібліотеки C++ є LLVM libc++. Розробник має обрати один із двох режимів компонування рантайму через параметр `ANDROID_STL`:
1. `c++_static`: статичне зв'язування з бібліотекою `libc++_static.a`.
2. `c++_shared`: динамічне зв'язування зі спільною бібліотекою `libc++_shared.so`.

![Конфлікт ODR та стану RTTI при використанні libc++_static](/root/sys/sys-bsystem/android-ndk-nuances/img/libcxx-odr-collision.svg)
*Конфлікт ODR та стану RTTI при використанні libc++_static у кількох .so проти єдиного libc++_shared.so.*

### Механізм катастрофи з `libc++_static`
Статичний рантайм виглядає привабливим для простих проєктів: модуль `.so` стає повністю автономним і не вимагає завантаження додаткових файлів бібліотек. Однак використання `c++_static` є безпечним **виключно у випадку, коли весь Android-застосунок містить рівно один спільний модуль `.so`**.

Щойно у проєкті з'являється дві або більше C++ бібліотек (наприклад, `libengine.so` та `libnetwork.so`, або якщо ви підключаєте сторонню прекомпільовану бібліотеку на кшталт OpenCV чи PyTorch), використання `libc++_static` призводить до фатальних наслідків:

1. **Руйнування системи обробки винятків та RTTI:**
   У C++ ідентифікація типів під час виконання (Run-Time Type Information) та зіставлення блоків `catch` спираються на унікальність об'єктів `std::type_info` та інформацію про розгортання стека. Якщо `libengine.so` і `libnetwork.so` вшивають кожна власну статичну копію `libc++`, у пам'яті процесу виникають два дублікати внутрішніх структур STL.
   Коли функція в `libnetwork.so` генерує виняток:
   ```cpp
   throw std::runtime_error("Мережевий таймаут");
   ```
   а зовнішній код у `libengine.so` намагається його перехопити:
   ```cpp
   try {
       network->fetch();
   } catch (const std::exception& e) {
       // Цей блок НЕ виконається!
   }
   ```
   обробник винятків не розпізнає тип, оскільки адреса таблиці віртуальних методів (`vtable`) або дескриптора `typeinfo` з `libnetwork.so` не збігається з локальним екземпляром у `libengine.so`. В результаті програма викликає `std::terminate()` і процес застосунку падає.

2. **Порушення правила єдиного визначення (ODR) для глобального стану:**
   Стандартна бібліотека C++ містить глобальні змінні стану: потоки введення/виведення (`std::cin`, `std::cout`), структури локалей `std::locale`, пули виділення пам'яті за замовчуванням у поліморфних алокаторах (`std::pmr`) та глобальні м'ютекси синхронізації. При статичному лінкуванні кожен модуль оперує власним незалежним екземпляром цих змінних, що призводить до витоків пам'яті, блокувань або пошкодження буферів.

3. **Роздування розміру APK:**
   Кожна бібліотека збільшується на сотні кілобайт через дублювання однакового коду функцій STL.

### Правило вибору: `c++_shared`
Для будь-якого промислового застосунку, що складається з кількох модулів, слід використовувати виключно `ANDROID_STL := c++_shared`. У цьому випадку система збірки додає спільну бібліотеку `libc++_shared.so` у фінальний APK-пакет.

Всі модулі проєкту містять запис `DT_NEEDED: libc++_shared.so` у своїх заголовках ELF. Динамічний лінкер завантажує єдиний екземпляр рантайму в адресний простір процесу, гарантуючи коректну роботу RTTI, надійне перехоплення винятків між межами `.so` файлів та єдиний глобальний стан.

---

## 5. Інтеграція з CMake та Gradle

Сучасні проєкти для Android використовують систему збірки Gradle із плагіном Android Gradle Plugin (AGP), який делегує компіляцію C/C++ коду зовнішньому генератору CMake через блок `externalNativeBuild`.

Взаємодія здійснюється через офіційний файл тулчейна NDK:
```text
$ANDROID_NDK_HOME/build/cmake/android.toolchain.cmake
```

Докладний опис усіх підтримуваних параметрів файлу тулчейна, їхніх типів даних та значень за замовчуванням винесено в окрему довідку [Змінні CMake тулчейну Android NDK](root:sys-bsystem/android-ndk-nuances/api-ndk-cmake-variables.md).

### Як AGP налаштовує збірку під капотом
Коли Gradle виконує таску збірки нативного коду (наприклад, `:app:configureCMakeDebug[arm64-v8a]`), він запускає CMake із чітко сформованим набором аргументів:
```bash
cmake \
  -H/workspace/app/src/main/cpp \
  -DCMAKE_SYSTEM_NAME=Android \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DCMAKE_SYSTEM_VERSION=29 \
  -DANDROID_PLATFORM=android-29 \
  -DANDROID_ABI=arm64-v8a \
  -DCMAKE_ANDROID_ARCH_ABI=arm64-v8a \
  -DANDROID_NDK=/opt/android-sdk/ndk/27.0.12077973 \
  -DCMAKE_ANDROID_NDK=/opt/android-sdk/ndk/27.0.12077973 \
  -DCMAKE_TOOLCHAIN_FILE=/opt/android-sdk/ndk/27.0.12077973/build/cmake/android.toolchain.cmake \
  -DCMAKE_MAKE_PROGRAM=/opt/android-sdk/cmake/3.22.1/bin/ninja \
  -DCMAKE_LIBRARY_OUTPUT_DIRECTORY=/workspace/app/build/intermediates/cxx/Debug/obj/arm64-v8a \
  -DCMAKE_BUILD_TYPE=Debug \
  -DANDROID_STL=c++_shared \
  -B/workspace/app/.cxx/Debug/arm64-v8a \
  -GNinja
```

### Пакування у APK/AAB та атрибут `extractNativeLibs`
Після компіляції генератор Ninja розміщує скомпільовані файли `lib*.so` у вихідному каталозі, звідки AGP копіює їх у структуру каталогу пакування:
```text
app.apk/
└── lib/
    ├── arm64-v8a/
    │   ├── libc++_shared.so
    │   └── libnative-lib.so
    └── armeabi-v7a/
        ├── libc++_shared.so
        └── libnative-lib.so
```

Історично Android під час встановлення APK копіював усі `.so` файли з zip-архіву у внутрішнє сховище застосунку `/data/app/<package>/lib/<arch>/`. Це призводило до подвійного використання дискової пам'яті (бібліотека зберігалася і в APK, і окремим файлом на диску).

Починаючи з Android 6.0 (API 23), операційна система підтримує пряме виконання коду з архіву APK без його розпакування на диск завдяки системному прапорцю в `AndroidManifest.xml`:
```xml
<application
    android:extractNativeLibs="false"
    ... >
```
У сучасних версіях AGP значення `android:extractNativeLibs="false"` є стандартом за замовчуванням. Для того щоб це працювало, система збірки виконує дві критичні вимоги:
1. Бібліотеки `.so` зберігаються всередині APK-архіву **без стиснення** (Stored / Compression Method 0).
2. Утиліта `zipalign` вирівнює початок кожного `.so` файлу всередині zip-контейнера на межу 4 КБ або 16 КБ (`zipalign -p 16384`).

Завдяки цьому динамічний лінкер системи виконує прямий виклик `mmap()` на зміщення всередині закритого файлу `.apk`, заощаджуючи сотні мегабайтів простору флеш-пам'яті та прискорюючи запуск програми.

---

## 6. Приклад організації JNI-модуля та діагностика бінарників

Розглянемо практичний приклад реалізації нативної бібліотеки, яка виконує логування через системний сервіс Android Logcat, коректно обробляє помилки та взаємодіє з JNI.

:::tabs
@tab C
```c
#include <jni.h>
#include <android/log.h>
#include <string.h>
#include <stdlib.h>

#define LOG_TAG "NativeEngine"
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)

JNIEXPORT jstring JNICALL
Java_com_example_app_NativeBridge_processPayload(
    JNIEnv *env,
    jobject thiz,
    jstring input_str)
{
    if (input_str == NULL) {
        LOGE("Отримано нульовий покажчик на рядок з Java");
        return NULL;
    }

    const char *native_chars = (*env)->GetStringUTFChars(env, input_str, NULL);
    if (native_chars == NULL) {
        LOGE("Помилка виділення пам'яті під UTF-8 рядок");
        return NULL;
    }

    size_t len = strlen(native_chars);
    LOGI("Обробка корисного навантаження довжиною %zu байтів", len);

    char *buffer = (char *)malloc(len + 32);
    if (buffer == NULL) {
        (*env)->ReleaseStringUTFChars(env, input_str, native_chars);
        LOGE("Не вдалося виділити буфер обробки");
        return NULL;
    }

    strcpy(buffer, "Android NDK Output: ");
    strcat(buffer, native_chars);

    jstring result = (*env)->NewStringUTF(env, buffer);

    free(buffer);
    (*env)->ReleaseStringUTFChars(env, input_str, native_chars);

    return result;
}
```
@tab C++
```cpp
#include <jni.h>
#include <android/log.h>
#include <string>
#include <string_view>
#include <memory>
#include <stdexcept>

namespace {
constexpr std::string_view kLogTag = "NativeEngine";

template <typename... Args>
void log_info(std::string_view fmt_str, Args&&... args) {
    std::string msg = (sizeof...(args) == 0) 
        ? std::string(fmt_str) 
        : std::string(fmt_str);
    __android_log_print(ANDROID_LOG_INFO, kLogTag.data(), "%s", msg.c_str());
}

template <typename... Args>
void log_error(std::string_view fmt_str, Args&&... args) {
    __android_log_print(ANDROID_LOG_ERROR, kLogTag.data(), "%s", fmt_str.data());
}

// RAII-обгортка для гарантованого звільнення JNI UTF рядків
class ScopedUtfChars {
public:
    ScopedUtfChars(JNIEnv* env, jstring jstr)
        : env_(env), jstr_(jstr), chars_(env->GetStringUTFChars(jstr, nullptr)) {}

    ~ScopedUtfChars() {
        if (chars_ != nullptr) {
            env_->ReleaseStringUTFChars(jstr_, chars_);
        }
    }

    ScopedUtfChars(const ScopedUtfChars&) = delete;
    ScopedUtfChars& operator=(const ScopedUtfChars&) = delete;

    [[nodiscard]] const char* get() const noexcept { return chars_; }
    [[nodiscard]] std::string_view view() const noexcept {
        return chars_ ? std::string_view(chars_) : std::string_view{};
    }

private:
    JNIEnv* env_;
    jstring jstr_;
    const char* chars_;
};
} // namespace

extern "C" JNIEXPORT jstring JNICALL
Java_com_example_app_NativeBridge_processPayload(
    JNIEnv* env,
    jobject /* thiz */,
    jstring input_str) noexcept
{
    if (input_str == nullptr) {
        log_error("Отримано нульовий покажчик на рядок з Java");
        return nullptr;
    }

    ScopedUtfChars utf_input(env, input_str);
    if (utf_input.get() == nullptr) {
        log_error("Помилка отримання символів UTF-8");
        return nullptr;
    }

    try {
        std::string_view payload = utf_input.view();
        log_info("Обробка корисного навантаження у безпечному контексті C++");

        std::string processed = "Android NDK Output: ";
        processed.append(payload);

        return env->NewStringUTF(processed.c_str());
    } catch (const std::exception& ex) {
        log_error(ex.what());
        return nullptr;
    }
}
```
:::

### Інспекція та діагностика зібраних `.so` бібліотек
Під час розробки нативних модулів розробник регулярно стикається з помилками лінкування або збоями під час завантаження через `dlopen()`. Для інспекції артефактів NDK надає потужний набір утиліт LLVM у каталозі `$NDK/toolchains/llvm/prebuilt/<host>/bin/`:

1. **Перевірка залежностей завантаження (`DT_NEEDED`):**
   ```bash
   llvm-readelf -d app/build/intermediates/cxx/Release/obj/arm64-v8a/libnative-lib.so
   ```
   У секції `Dynamic section` слід звернути увагу на рядки `(NEEDED)`:
   ```text
   0x0000000000000001 (NEEDED)             Shared library: [liblog.so]
   0x0000000000000001 (NEEDED)             Shared library: [libc++_shared.so]
   0x0000000000000001 (NEEDED)             Shared library: [libc.so]
   0x0000000000000001 (NEEDED)             Shared library: [libm.so]
   ```
   Якщо замість `libc++_shared.so` залежність відсутня, але використовується C++, модуль було помилково зібрано зі статичним STL (`c++_static`).

2. **Діагностика нерозв'язаних символів через Logcat:**
   Коли динамічний лінкер Android не може завантажити бібліотеку, детальний опис помилки записується в системний журнал:
   ```bash
   adb logcat -s linker,DEBUG,AndroidRuntime
   ```
   Типове повідомлення:
   ```text
   CANNOT LINK EXECUTABLE "libnative-lib.so": cannot locate symbol "getrandom" referenced by "libnative-lib.so"...
   ```
   свідчить про те, що модуль було скомпільовано з високим значенням `__ANDROID_API__` (наприклад, 28), а спроба запуску виконується на старішому пристрої з Android 8.0 (API 26), де у системному `libc.so` цей символ ще не існував.
