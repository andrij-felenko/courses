# ⚙️ Створення надійного пошукового модуля FindMyLib.cmake

Цей практичний посібник розбирає покроковий процес створення надійного, переміщуваного та сумісного зі стандартами Modern CMake модуля пошуку `Find<PackageName>.cmake` для сторонньої бібліотеки, яка не надає власних конфігураційних файлів CMake. Його відкривають, коли потрібно інтегрувати в проєкт зовнішню C або C++ бібліотеку (зібрану через Make, Autotools чи встановлену вручну в систему), забезпечити виявлення її заголовків, бібліотечних файлів різної конфігурації, розбір версії, роботу з компонентами, використання підказок `pkg-config`, вибір статичного чи динамічного лінкування, підтримку мультиархітектурних платформ, роботу з фреймворками macOS, налаштування інтерфейсних властивостей стандарту мови, інтеграцію з менеджерами пакетів, тестування та автоматичне створення графа імпортованих цілей у просторі імен `MyLib::MyLib`.

---

## 1. Постановка задачі та анатомія сторонньої бібліотеки

Уявімо типову інженерну ситуацію: у проєкті використовується високопродуктивна бібліотека стиснення `FastCodec`, написана на чистому C. Бібліотека поширюється у вигляді вихідних кодів із власним низькорівневим `Makefile` або встановлюється в систему адміністратором із tar-архіву чи нестандартного пакета. Вона не має ані `FastCodecConfig.cmake`, ані готових імпортованих цілей для CMake.

Після типового встановлення бібліотека розкладається по каталогах файлової системи за класичною Unix-схемою:
- Заголовкові файли інтерфейсу: `<prefix>/include/fastcodec/fastcodec.h` та `<prefix>/include/fastcodec/fastcodec_features.h`.
- Файли компільованої бібліотеки на платформах Linux/Unix: статичний архів `<prefix>/lib/libfastcodec.a` або динамічний спільний об'єкт `<prefix>/lib/libfastcodec.so`.
- Файли компільованої бібліотеки на платформі macOS: або динамічні файли `libfastcodec.dylib`, або запакований системний фреймворк `FastCodec.framework`.
- Файли компільованої бібліотеки на платформі Windows: бібліотека імпорту `<prefix>/lib/fastcodec.lib` та відповідна динамічна бібліотека `<prefix>/bin/fastcodec.dll`.
- Версія бібліотеки жорстко зафіксована препроцесорними макросами безпосередньо у файлі `fastcodec.h`.
- Бібліотека має додатковий модульний компонент паралельної обробки даних `PARALLEL`, активація якого вимагає наявності системної бібліотеки потоків виконання `pthread`.

Наша інженерна мета — створити переміщуваний сценарій `cmake/FindFastCodec.cmake`, який дозволить будь-якому споживачу підключити залежність одним декларативним рядком:

```cmake
find_package(FastCodec 2.0 REQUIRED COMPONENTS PARALLEL)
```

і зв'язати її з власною ціллю через стандартний виклик `target_link_libraries(my_app PRIVATE FastCodec::FastCodec)`. При цьому споживач не повинен вручну перевіряти шляхи до заголовків, писати директиви `include_directories()` чи турбуватися про те, чи зібрано проєкт у режимі `Debug`, чи в `Release`.

---

## 2. Крок 1: Використання pkg-config як постачальника підказок

Багато традиційних бібліотек C на Unix-подібних системах під час інсталяції генерують файл опису `fastcodec.pc` для утиліти `pkg-config`. Сам по собі `pkg-config` не вміє створювати повноцінні цілі CMake з урахуванням конфігурацій MSVC чи крос-компіляції, проте він є чудовим джерелом точних підказок про шляхи встановлення.

Модуль пошуку починається зі спроби тихо опитати `pkg-config` за допомогою вбудованого модуля `FindPkgConfig`:

```cmake
# cmake/FindFastCodec.cmake

# 0. Отримуємо підказки від pkg-config, якщо утиліта доступна в системі
find_package(PkgConfig QUIET)
if(PKG_CONFIG_FOUND)
    pkg_check_modules(PC_FastCodec QUIET fastcodec)
endif()
```

Макрос `pkg_check_modules` створює набір префіксних змінних, зокрема `PC_FastCodec_INCLUDE_DIRS` та `PC_FastCodec_LIBRARY_DIRS`. Ми не використовуємо ці змінні напряму для лінкування, але передаємо їх як підказки `HINTS` у наступні команди пошуку. Це дає змогу автоматично знаходити бібліотеки, встановлені в нестандартні префікси на зразок Homebrew на macOS (`/opt/homebrew`) або дистрибутивні каталоги `/usr/lib64`.

---

## 3. Крок 2: Пошук каталогів заголовкових файлів

Наступним кроком модуль пошуку повинен визначити, де саме в операційній системі розташовані заголовкові файли. Для цього використовується команда `find_path()`.

Головне правило безпечного пошуку: ніколи не шукати загальний каталог `include` чи абстрактний файл із поширеним ім'ям на зразок `codec.h` або `types.h`. Якщо в системі встановлено кілька різних мультимедійних бібліотек, CMake може випадково знайти чужий файл із таким самим іменем і підставити хибний каталог. Тому ми шукаємо відносний шлях із префіксом підкаталогу: `fastcodec/fastcodec.h`.

```cmake
# 1. Пошук кореневого каталогу включення заголовків
find_path(FastCodec_INCLUDE_DIR
    NAMES
        fastcodec/fastcodec.h
    HINTS
        ${PC_FastCodec_INCLUDE_DIRS}
        ${FastCodec_ROOT}
        ENV FastCodec_ROOT
        ${FASTCODEC_ROOT}
        ENV FASTCODEC_ROOT
    PATH_SUFFIXES
        include
        include/fastcodec
    DOC "Каталог із заголовковими файлами бібліотеки FastCodec"
)
```

Розберемо деталі роботи цієї команди:
- Результат записується в кеш-змінну `FastCodec_INCLUDE_DIR`. Якщо файл фізично розташований за шляхом `/opt/custom/include/fastcodec/fastcodec.h`, а пошук здійснювався за `NAMES fastcodec/fastcodec.h`, значенням змінної стане базовий каталог `/opt/custom/include`. Завдяки цьому директива `#include <fastcodec/fastcodec.h>` у коді користувача знайде файл без додаткових модифікацій.
- Секція `HINTS` явно перевіряє шляхи від `pkg-config` та змінні префікса пакета, передані розробником через аргументи командного рядка (`-DFastCodec_ROOT=/opt/custom`) або через змінні оточення. Префікси з `HINTS` перевіряються раніше за стандартні системні каталоги `/usr/include` та `/usr/local/include`, що дозволяє розробнику перевизначити системну версію бібліотеки власною збіркою.

---

## 4. Крок 3: Видобування та розбір версії із заголовка

Коли файл заголовка виявлено на диску, модуль повинен визначити точний номер версії встановленої бібліотеки. Спроба з'ясувати версію шляхом компіляції та запуску тестового виконуваного файла через `try_run()` є грубою помилкою: вона повністю ламає процес крос-компіляції, коли зібраний бінарний файл не може бути запущений на хост-машині.

Найбільш надійний та швидкий спосіб — пряме зчитування тексту заголовка засобами CMake за допомогою команди `file(STRINGS ... REGEX ...)`:

:::tabs
```c
/* fastcodec/fastcodec.h */
#define FASTCODEC_VERSION_MAJOR 2
#define FASTCODEC_VERSION_MINOR 4
#define FASTCODEC_VERSION_PATCH 1
#define FASTCODEC_VERSION_STRING "2.4.1"
```
```cpp
// fastcodec/fastcodec.h
#define FASTCODEC_VERSION_MAJOR 2
#define FASTCODEC_VERSION_MINOR 4
#define FASTCODEC_VERSION_PATCH 1
#define FASTCODEC_VERSION_STRING "2.4.1"
```
:::

Для вилучення значень із цих макроозначень використовуємо регулярні вирази:

```cmake
if(FastCodec_INCLUDE_DIR AND EXISTS "${FastCodec_INCLUDE_DIR}/fastcodec/fastcodec.h")
    # Зчитуємо лише рядки, що містять макроси версії, не завантажуючи весь файл
    file(STRINGS "${FastCodec_INCLUDE_DIR}/fastcodec/fastcodec.h" _fastcodec_version_lines
         REGEX "^#define[ \t]+FASTCODEC_VERSION_(MAJOR|MINOR|PATCH)[ \t]+[0-9]+")

    # Витягуємо окремі компоненти версії
    string(REGEX MATCH "FASTCODEC_VERSION_MAJOR[ \t]+([0-9]+)" _ "${_fastcodec_version_lines}")
    set(FastCodec_VERSION_MAJOR "${CMAKE_MATCH_1}")

    string(REGEX MATCH "FASTCODEC_VERSION_MINOR[ \t]+([0-9]+)" _ "${_fastcodec_version_lines}")
    set(FastCodec_VERSION_MINOR "${CMAKE_MATCH_1}")

    string(REGEX MATCH "FASTCODEC_VERSION_PATCH[ \t]+([0-9]+)" _ "${_fastcodec_version_lines}")
    set(FastCodec_VERSION_PATCH "${CMAKE_MATCH_1}")

    if(FastCodec_VERSION_MAJOR AND FastCodec_VERSION_MINOR AND FastCodec_VERSION_PATCH)
        set(FastCodec_VERSION "${FastCodec_VERSION_MAJOR}.${FastCodec_VERSION_MINOR}.${FastCodec_VERSION_PATCH}")
    endif()

    unset(_fastcodec_version_lines)
endif()
```

Цей алгоритм працює миттєво під час стадії конфігурації, не створює тимчасових файлів на диску та підтримує будь-які цільові архітектури (включно з ARM, RISC-V та мікроконтролерами).

---

## 5. Крок 4: Пошук компільованих бібліотек і керування статичним лінкуванням

Наступний крок — знайти скомпільовані бінарні файли бібліотеки. Тут виникає кілька важливих практичних задач: підтримка конфігурацій `Release`/`Debug`, розпізнавання розрядності архітектури, підтримка фреймворків macOS та можливість для користувача явно обрати статичну чи динамічну версію бібліотеки.

### 5.1. Керування суфіксами бібліотек (статичне проти динамічного)

Якщо користувач встановив опцію `FastCodec_USE_STATIC_LIBS = ON`, модуль повинен тимчасово обмежити пошук розширеннями статичних архівів (`.a` на Unix, `.lib` на Windows):

```cmake
# Зберігаємо поточний стан суфіксів пошуку бібліотек
set(_fastcodec_orig_suffixes ${CMAKE_FIND_LIBRARY_SUFFIXES})

if(FastCodec_USE_STATIC_LIBS)
    if(WIN32)
        set(CMAKE_FIND_LIBRARY_SUFFIXES .lib .a)
    else()
        set(CMAKE_FIND_LIBRARY_SUFFIXES .a)
    endif()
endif()
```

### 5.2. Врахування мультиархітектурних каталогів

На 64-розрядних дистрибутивах Linux (RHEL, Fedora, Debian multiarch) бібліотеки можуть знаходитися у підкаталогах `lib64` або `lib/x86_64-linux-gnu` / `lib/aarch64-linux-gnu`. Ми формуємо список `PATH_SUFFIXES` із врахуванням змінної `CMAKE_SIZEOF_VOID_P`:

```cmake
set(_fastcodec_path_suffixes lib)
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    list(APPEND _fastcodec_path_suffixes lib64 "lib/${CMAKE_LIBRARY_ARCHITECTURE}")
endif()
```

### 5.3. Пошук фреймворків на платформі macOS

На платформі Apple macOS бібліотека може поширюватися як традиційний динамічний файл `.dylib`, так і у вигляді запакованого фреймворку `FastCodec.framework`. Змінна `CMAKE_FIND_FRAMEWORK` визначає пріоритет:
- Якщо встановлено `FIRST` (типово на macOS), `find_library()` спочатку шукатиме фреймворк у `/Library/Frameworks` та `~/Library/Frameworks`.
- Якщо встановлено `LAST`, перевага надаватиметься файлам `.dylib` у префіксах UNIX (`/usr/local/lib`, `/opt/homebrew/lib`).
- Якщо встановлено `NEVER`, пошук фреймворків повністю вимикається.

Модуль `FindFastCodec.cmake` не вимагає спеціальних перевірок для фреймворків: стандартна команда `find_library()` автоматично розпізнає структуру `.framework` і повертає коректний шлях до каталогу фреймворка.

### 5.4. Пошук конфігурацій Release та Debug

На компіляторах сімейства MSVC (Windows) та в багатоконфігураційних генераторах Visual Studio і Xcode бібліотеки для налагодження (`Debug`) та фінальної збірки (`Release`) скомпільовані з різними прапорцями рантайму C/C++ (`/MDd` проти `/MD`). Змішування таких об'єктних файлів в одному процесі гарантовано призводить до пошкодження пам'яті (падіння при звільненні пам'яті через несумісні алокатори).

Тому модуль пошуку повинен окремо шукати оптимізовану та налагоджувальну версії:

```cmake
# Пошук оптимізованої (Release) версії бібліотеки
find_library(FastCodec_LIBRARY_RELEASE
    NAMES
        fastcodec
        libfastcodec
    HINTS
        ${PC_FastCodec_LIBRARY_DIRS}
        ${FastCodec_ROOT}
        ENV FastCodec_ROOT
    PATH_SUFFIXES
        ${_fastcodec_path_suffixes}
        bin
    DOC "Шлях до Release бібліотеки FastCodec"
)

# Пошук налагоджувальної (Debug) версії (зазвичай має суфікс d або _d)
find_library(FastCodec_LIBRARY_DEBUG
    NAMES
        fastcodecd
        fastcodec_d
        libfastcodecd
        libfastcodec_d
    HINTS
        ${PC_FastCodec_LIBRARY_DIRS}
        ${FastCodec_ROOT}
        ENV FastCodec_ROOT
    PATH_SUFFIXES
        ${_fastcodec_path_suffixes}
        bin
    DOC "Шлях до Debug бібліотеки FastCodec"
)

# Відновлюємо оригінальні суфікси після пошуку
set(CMAKE_FIND_LIBRARY_SUFFIXES ${_fastcodec_orig_suffixes})
unset(_fastcodec_orig_suffixes)
unset(_fastcodec_path_suffixes)

# Допоміжний макрос для об'єднання конфігурацій
include(SelectLibraryConfigurations)
select_library_configurations(FastCodec)
```

Макрос `select_library_configurations(FastCodec)` працює наступним чином:
- Якщо знайдено обидва файли (`FastCodec_LIBRARY_RELEASE` і `FastCodec_LIBRARY_DEBUG`), він створює список `FastCodec_LIBRARIES` спеціального формату: `optimized;<шлях_до_release>;debug;<шлях_до_debug>`.
- Якщо виявлено лише один із файлів, він присвоює змінній `FastCodec_LIBRARY` шлях до наявного файла, а `FastCodec_LIBRARIES` вказує на нього ж.
- Це гарантує повну сумісність як із сучасними імпортованими цілями, так і зі старими сценаріями `target_link_libraries(app PRIVATE ${FastCodec_LIBRARIES})`.

---

## 6. Крок 5: Обробка компонентів та додаткових залежностей

Багато великих бібліотек постачаються частинами. Наприклад, базовий функціонал `FastCodec` містить лише послідовне стиснення даних, а модуль `PARALLEL` додає багатопотокове стиснення за допомогою пулу потоків.

Коли споживач викликає `find_package(FastCodec COMPONENTS PARALLEL)`, CMake передає список запитаних модулів у змінну `FastCodec_FIND_COMPONENTS`. Модуль пошуку повинен перевірити кожен компонент окремо та зафіксувати його статус у змінній `FastCodec_<Component>_FOUND`:

```cmake
set(FastCodec_PARALLEL_FOUND FALSE)

if("PARALLEL" IN_LIST FastCodec_FIND_COMPONENTS)
    # Перевіряємо заголовок на наявність прапорця активації багатопотоковості
    if(FastCodec_INCLUDE_DIR AND EXISTS "${FastCodec_INCLUDE_DIR}/fastcodec/fastcodec_features.h")
        file(STRINGS "${FastCodec_INCLUDE_DIR}/fastcodec/fastcodec_features.h" _has_parallel
             REGEX "^#define[ \t]+FASTCODEC_HAS_PARALLEL[ \t]+1")
        if(_has_parallel)
            # Компонент вимагає системної бібліотеки потоків
            find_package(Threads QUIET)
            if(Threads_FOUND)
                set(FastCodec_PARALLEL_FOUND TRUE)
            endif()
        endif()
        unset(_has_parallel)
    endif()
endif()
```

Якщо компонент виявився відсутнім, а користувач вказав його в секції `COMPONENTS` (як обов'язковий), макрос стандартизованої валідації автоматично визнає весь пакет не знайденим.

---

## 7. Крок 6: Стандартизована валідація результатів

Після збору всіх шляхів, номерів версій та стану компонентів ми передаємо керування стандартному макросу `FindPackageHandleStandardArgs`:

```cmake
include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(FastCodec
    REQUIRED_VARS
        FastCodec_LIBRARY
        FastCodec_INCLUDE_DIR
    VERSION_VAR
        FastCodec_VERSION
    HANDLE_COMPONENTS
)
```

Цей макрос позбавляє автора сценарію від необхідності вручну писати громіздкі перевірки умов `if(FastCodec_INCLUDE_DIR AND FastCodec_LIBRARY)` та формувати діагностичні повідомлення. Він автоматично виконує такі задачі:
1. Перевіряє, що всі змінні зі списку `REQUIRED_VARS` містять коректні шляхи (не є порожніми і не містять маркер `-NOTFOUND`).
2. Порівнює знайдений рядок `FastCodec_VERSION` із вимогами користувача (враховуючи діапазони версій та прапорець `EXACT`).
3. Перевіряє змінні `FastCodec_<Comp>_FOUND` для всіх обов'язкових компонентів.
4. Якщо перевірка успішна, встановлює змінну `FastCodec_FOUND = TRUE` і друкує інформаційне повідомлення:
   `-- Found FastCodec: /usr/local/lib/libfastcodec.so (found suitable version "2.4.1", minimum required is "2.0")`
5. Якщо будь-яка з перевірок зазнає невдачі, макрос встановлює `FastCodec_FOUND = FALSE`, друкує вичерпне повідомлення з переліком відсутніх артефактів і (якщо у виклику передано `REQUIRED`) негайно зупиняє генерацію фатальною помилкою.

---

## 8. Крок 7: Створення імпортованої цілі (IMPORTED Target)

Кульмінація написання модуля — створення цілі `FastCodec::FastCodec`. Саме вона перетворює сторонню бібліотеку на повноцінний об'єкт Modern CMake, який інкапсулює шляхи заголовків, бінарні файли для кожної конфігурації, вимоги стандарту мови та транзитивні прапорці:

```cmake
if(FastCodec_FOUND AND NOT TARGET FastCodec::FastCodec)
    # Створюємо імпортовану ціль із типом UNKNOWN
    add_library(FastCodec::FastCodec UNKNOWN IMPORTED)

    # Прив'язуємо каталог заголовків як інтерфейсну вимогу
    set_target_properties(FastCodec::FastCodec PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${FastCodec_INCLUDE_DIR}"
    )

    # Прив'язуємо Release бінарний файл, якщо він є
    if(FastCodec_LIBRARY_RELEASE)
        set_property(TARGET FastCodec::FastCodec APPEND PROPERTY
            IMPORTED_CONFIGURATIONS RELEASE)
        set_target_properties(FastCodec::FastCodec PROPERTIES
            IMPORTED_LOCATION_RELEASE "${FastCodec_LIBRARY_RELEASE}"
        )
    endif()

    # Прив'язуємо Debug бінарний файл, якщо він є
    if(FastCodec_LIBRARY_DEBUG)
        set_property(TARGET FastCodec::FastCodec APPEND PROPERTY
            IMPORTED_CONFIGURATIONS DEBUG)
        set_target_properties(FastCodec::FastCodec PROPERTIES
            IMPORTED_LOCATION_DEBUG "${FastCodec_LIBRARY_DEBUG}"
        )
    endif()

    # Якщо немає явного поділу на конфігурації, використовуємо загальну локацію
    if(NOT FastCodec_LIBRARY_RELEASE AND NOT FastCodec_LIBRARY_DEBUG)
        set_target_properties(FastCodec::FastCodec PROPERTIES
            IMPORTED_LOCATION "${FastCodec_LIBRARY}"
        )
    endif()

    # Якщо знайдено динамічну бібліотеку на Windows, задаємо імпортну бібліотеку
    if(WIN32 AND FastCodec_LIBRARY MATCHES "\\.lib$")
        # Шукаємо відповідний DLL файл поруч або у bin
        get_filename_component(_lib_dir "${FastCodec_LIBRARY}" DIRECTORY)
        find_file(FastCodec_DLL
            NAMES fastcodec.dll
            HINTS "${_lib_dir}/../bin" "${_lib_dir}"
        )
        if(FastCodec_DLL)
            set_target_properties(FastCodec::FastCodec PROPERTIES
                IMPORTED_IMPLIB "${FastCodec_LIBRARY}"
                IMPORTED_LOCATION "${FastCodec_DLL}"
            )
        endif()
    endif()

    # Якщо активовано компонент багатопотоковості, додаємо транзитивну залежність
    if(FastCodec_PARALLEL_FOUND)
        set_property(TARGET FastCodec::FastCodec APPEND PROPERTY
            INTERFACE_LINK_LIBRARIES Threads::Threads
        )
        set_property(TARGET FastCodec::FastCodec APPEND PROPERTY
            INTERFACE_COMPILE_DEFINITIONS FASTCODEC_PARALLEL_ENABLED=1
        )
    endif()
endif()
```

Чому ми обираємо тип `UNKNOWN IMPORTED`? Тому що на етапі конфігурації ми не знаємо напевне, чи є знайдений файл `.a` статичною бібліотекою, чи імпортним описом спільного об'єкта. Тип `UNKNOWN` дозволяє CMake відкласти точне визначення формату до моменту лінкування конкретної цільової платформи.

---

## 9. Крок 8: Модульний поділ на окремі цілі компонентів та псевдоніми

Якщо бібліотека має кілька незалежних модулів (наприклад, окрему утиліту командного рядка чи криптографічний модуль `FastCodec::Crypto`), найкращою практикою є створення окремих імпортованих цілей для кожного компонента з точними зв'язками між ними:

```cmake
# Створення цілі окремого компонента FastCodec::Parallel
if(FastCodec_PARALLEL_FOUND AND NOT TARGET FastCodec::Parallel)
    add_library(FastCodec::Parallel INTERFACE IMPORTED)
    target_link_libraries(FastCodec::Parallel INTERFACE 
        FastCodec::FastCodec 
        Threads::Threads
    )
    target_compile_definitions(FastCodec::Parallel INTERFACE 
        FASTCODEC_PARALLEL_ENABLED=1
    )
endif()
```

Такий підхід дає змогу споживачу обирати мінімальний набір залежностей: лінкування з `FastCodec::FastCodec` дає лише базове ядро без залежності від потоків, тоді як лінкування з `FastCodec::Parallel` автоматично підтягує і ядро, і системні потоки.

---

## 10. Крок 9: Забезпечення зворотної сумісності та маскування змінних

Для підтримки старих підпроєктів, які ще не перейшли на роботу з цілями, ми дублюємо шляхи в традиційні змінні та приховуємо технічні змінні кешу:

```cmake
if(FastCodec_FOUND)
    set(FastCodec_INCLUDE_DIRS "${FastCodec_INCLUDE_DIR}")
    set(FastCodec_LIBRARIES "${FastCodec_LIBRARY}")
endif()

# Приховуємо внутрішні змінні в графічних інтерфейсах ccmake / cmake-gui
mark_as_advanced(
    FastCodec_INCLUDE_DIR
    FastCodec_LIBRARY
    FastCodec_LIBRARY_RELEASE
    FastCodec_LIBRARY_DEBUG
    FastCodec_DLL
)
```

Команда `mark_as_advanced()` переводить змінні в категорію розширених налаштувань, запобігаючи візуальному захаращенню списку опцій проєкту.

---

## 11. Перевірка роботи модуля в споживчому проєкті

Щоб підключити створений модуль до збірки, ми розміщуємо його в каталозі `cmake/` нашого проєкту та додаємо цей каталог до списку `CMAKE_MODULE_PATH` у головному файлі `CMakeLists.txt`:

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(ImageCompressor LANGUAGES C CXX)

# Додаємо локальний каталог модулів до пошуку
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

# Знаходимо нашу бібліотеку
find_package(FastCodec 2.0 REQUIRED COMPONENTS PARALLEL)

# Створюємо ціль програми
add_executable(compress_tool src/main.cpp)

# Лінкуємо імпортовану ціль — заголовки, бібліотеки та макроси приходять автоматично
target_link_libraries(compress_tool PRIVATE FastCodec::FastCodec)
```

Споживчий код може використовувати як мову C, так і ідіоматичний C++ з автоматичним керуванням ресурсами (RAII):

:::tabs
```c
/* src/main.c */
#include <fastcodec/fastcodec.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    printf("FastCodec C client, version %s\n", FASTCODEC_VERSION_STRING);
    
    fastcodec_config_t config;
    fastcodec_get_default_config(&config);
    
    fastcodec_ctx_t* ctx = fastcodec_create_context(&config);
    if (!ctx) {
        fprintf(stderr, "Помилка ініціалізації контексту стиснення\n");
        return EXIT_FAILURE;
    }
    
    printf("Контекст стиснення успішно створено.\n");
    fastcodec_free_context(ctx);
    return EXIT_SUCCESS;
}
```
```cpp
// src/main.cpp
#include <fastcodec/fastcodec.h>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string_view>

struct FastCodecDeleter {
    void operator()(fastcodec_ctx_t* ctx) const noexcept {
        if (ctx) {
            fastcodec_free_context(ctx);
        }
    }
};

using SafeContext = std::unique_ptr<fastcodec_ctx_t, FastCodecDeleter>;

SafeContext make_codec_context() {
    fastcodec_config_t config;
    fastcodec_get_default_config(&config);
    
    fastcodec_ctx_t* raw = fastcodec_create_context(&config);
    if (!raw) {
        throw std::runtime_error("Не вдалося виділити ресурси для FastCodec");
    }
    return SafeContext(raw);
}

int main() {
    std::cout << "FastCodec C++ client, version " 
              << std::string_view(FASTCODEC_VERSION_STRING) << "\n";
    try {
        auto ctx = make_codec_context();
        std::cout << "Контекст стиснення успішно ініціалізовано через RAII.\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

## 12. Інтеграція з пакетними менеджерами та заміна на Config Mode

Сучасні пакетні менеджери (vcpkg або Conan) можуть збирати `FastCodec` із вихідних кодів і генерувати для нього власний конфігураційний файл `FastCodecConfig.cmake`. Щоб наш модуль пошуку не конфліктував із менеджером пакетів, рекомендується надати пріоритет режиму конфігурації за допомогою змінної `CMAKE_FIND_PACKAGE_PREFER_CONFIG`:

```cmake
# Якщо бібліотеку встановлено через vcpkg, шукати спершу FastCodecConfig.cmake
set(CMAKE_FIND_PACKAGE_PREFER_CONFIG TRUE)
find_package(FastCodec 2.0 REQUIRED)
```

Коли встановлено `CMAKE_FIND_PACKAGE_PREFER_CONFIG = TRUE`, CMake спочатку намагається знайти файл виробника `FastCodecConfig.cmake` за шляхами `CMAKE_PREFIX_PATH` менеджера пакетів, і лише якщо його немає, звертається до нашого сценарію `FindFastCodec.cmake` у `CMAKE_MODULE_PATH`. Це створює плавний місток між застарілими системами та сучасною екосистемою C++, запобігаючи використанню евристичного модуля там, де вже існує точний конфігураційний опис від пакувальника.

---

## 13. Автоматизоване тестування модуля пошуку через CTest

Щоб переконатися, що створений модуль `FindFastCodec.cmake` не зламається при зміні версій CMake чи на нових операційних системах, рекомендується додати автоматичний тест конфігурації у тестовий набір проєкту:

```cmake
# tests/CMakeLists.txt
enable_testing()

# Тест перевіряє, що виклик find_package успішно проходить у чистому середовищі
add_test(
    NAME test_find_fastcodec
    COMMAND ${CMAKE_COMMAND}
        -D CMAKE_MODULE_PATH=${CMAKE_CURRENT_SOURCE_DIR}/../cmake
        -D FastCodec_ROOT=${TEST_FASTCODEC_PREFIX}
        -P ${CMAKE_CURRENT_SOURCE_DIR}/test_find_fastcodec_script.cmake
)
```

Сценарій `test_find_fastcodec_script.cmake` містить лише виклик `find_package(FastCodec 2.0 REQUIRED)` та перевірку `if(NOT TARGET FastCodec::FastCodec) message(FATAL_ERROR ...)`. Запуск `ctest --output-on-failure` підтверджує працездатність модуля на етапі безперервної інтеграції (CI).

---

## 14. Діагностика та налагодження пошуку через CLI

Коли під час складної крос-компіляції або в оточенні з багатьма встановленими версіями бібліотеки CMake вибирає неправильний файл, розробник може увімкнути режим детального трасування:

```bash
cmake -B build -S . --debug-find-pkg=FastCodec
```

Цей прапорець виводить у термінал повний список усіх шляхів, які перевіряв CMake, причини відхилення невідповідних версій та точні змінні, отримані від операційної системи. Якщо потрібно побачити повне розкриття кожного рядка сценарію `FindFastCodec.cmake`, використовують режим трасування `--trace-expand`.

---

## 15. Розподіл та перевикористання модулів пошуку між проєктами

Якщо компанія чи команда розробників використовує кілька внутрішніх C/C++ бібліотек без підтримки CMake, найкращою практикою є створення окремого спільного Git-репозиторію `cmake-modules`. Цей репозиторій підключається як Git-сабмодуль або завантажується на етапі конфігурації через модуль `FetchContent`:

```cmake
include(FetchContent)
FetchContent_Declare(
    company_cmake_modules
    GIT_REPOSITORY https://git.company.internal/tools/cmake-modules.git
    GIT_TAG        v1.4.0
)
FetchContent_MakeAvailable(company_cmake_modules)
list(APPEND CMAKE_MODULE_PATH "${company_cmake_modules_SOURCE_DIR}/modules")
```

Така організація гарантує, що покращення модулів пошуку, виправлення помилок виявлення нових версій бібліотек чи оптимізації під нові компілятори стають доступними всім підпроєктам організації без дублювання коду.

---

## 16. Типові інженерні пастки та способи їх усунення

1. **Конфлікт однакових імен заголовків:** якщо шукати файл за загальним іменем `fastcodec.h` без вказання батьківського каталогу, CMake може виявити іншу бібліотеку в системі, яка має такий самий файл. Завжди передавайте у `find_path()` префіксний шлях `fastcodec/fastcodec.h`.
2. **Проблема відносних шляхів у multi-config генераторах:** на платформах із підтримкою Debug та Release ніколи не записуйте в `IMPORTED_LOCATION` значення `FastCodec_LIBRARIES`, якщо воно містить ключові слова `optimized` та `debug`. Ці слова призначені лише для команди `target_link_libraries()`, а у властивостях цілей вони викликають помилку генерації. Завжди налаштовуйте властивості `IMPORTED_LOCATION_RELEASE` та `IMPORTED_LOCATION_DEBUG` окремо.
3. **Забутий пошук DLL на Windows:** якщо для динамічної бібліотеки на Windows вказати лише `fastcodec.lib` у властивості `IMPORTED_LOCATION`, виконуваний файл скомпілюється й злінкується без помилок, але під час запуску впаде з системним вікном про відсутність `fastcodec.dll`. Для спільних бібліотек під Windows файл `.lib` записують у властивість `IMPORTED_IMPLIB`, а шлях до `.dll` — в `IMPORTED_LOCATION`.
4. **Некоректна поведінка при перевизначенні префікса:** якщо розробник викликає CMake із параметром `-DFastCodec_ROOT=/custom/path`, а модуль пошуку не містить перевірки цієї змінної в секції `HINTS`, CMake знайде застарілу системну бібліотеку в `/usr/lib`, проігнорувавши явне бажання користувача. Завжди додавайте змінні `${FastCodec_ROOT}` та `ENV{FastCodec_ROOT}` до списку підказок `HINTS`.
5. **Ігнорування крос-компіляційного sysroot:** під час крос-компіляції системні бібліотеки хоста не повинні потрапляти у збірку. Використання `HINTS` та змінних `CMAKE_PREFIX_PATH` гарантує, що за наявності `CMAKE_FIND_ROOT_PATH` CMake автоматично перенаправить пошук усередину цільового sysroot і не допустить змішування двійкових файлів архітектури хоста з цільовими.
