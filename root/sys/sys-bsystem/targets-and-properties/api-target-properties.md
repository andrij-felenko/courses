# 📋 Довідка властивостей цілі CMake

Це перелік властивостей, які справді доводиться ставити руками, з відповіддю на три питання про кожну: **звідки в неї береться усталене значення**, **якою командою її пишуть** і **чи їде вона до того, хто з ціллю злінкується**. Далі — сигнатури всіх п'яти команд читання й запису та поведінка читання в крайніх випадках.

Перелік потрібен через те, що набір властивостей у CMake відкритий. У цілі не структура з полями, а словник «ім'я → рядок», і запис під невідомим іменем проходить мовчки: `CXX_STANARD` запишеться так само успішно, як `CXX_STANDARD`, просто ніхто його не прочитає. Ім'я властивості ніде не перевіряється — отже, єдина перевірка, яка існує, це перелік.

> Усе звірено з документацією **CMake 4.4.2**. Прочерк у колонці «з версії» означає, що можливість давніша за 3.0, з якої Kitware такі позначки веде.

## Що означають колонки

**Започатковує.** У момент **створення** цілі CMake читає щось зовнішнє — змінну `CMAKE_<ВЛАСТИВІСТЬ>` або однойменну властивість каталогу — і кладе прочитане у властивість новоствореної цілі. Це знімок, зроблений один раз; далі ціль живе своїм значенням. Звідси практичний наслідок: змінна, задана нижче за `add_library`, на цю ціль не подіє взагалі.

**Ставлять.** Команда, якою значення пишуть на саму ціль. Де є `target_*`-команда, беруть її: лише вона вміє розкласти запис на дві половини ключовими словами `PRIVATE`/`PUBLIC`/`INTERFACE` ([вимоги вжитку](topic:sys-bsystem/usage-requirements)). Решту ставлять через `set_target_properties`.

**Дзеркало `INTERFACE_`.** Друга властивість із тим самим іменем під префіксом. На саму ціль вона не впливає зовсім — її вміст додається тому, хто з ціллю злінкується. Прочерк означає, що дзеркала немає: значення нікуди не передається, і кожна ціль мусить задати його собі сама.

## Опис компіляції й лінкування

| Властивість | Започатковує | Ставлять | Дзеркало | З версії |
| --- | --- | --- | --- | --- |
| `SOURCES` | — | `add_library()`, `add_executable()`, `target_sources()` | `INTERFACE_SOURCES` | — |
| `INCLUDE_DIRECTORIES` | властивість каталогу `INCLUDE_DIRECTORIES` | `target_include_directories()` | `INTERFACE_INCLUDE_DIRECTORIES` | — |
| `COMPILE_DEFINITIONS` | властивість каталогу `COMPILE_DEFINITIONS` | `target_compile_definitions()` | `INTERFACE_COMPILE_DEFINITIONS` | — |
| `COMPILE_OPTIONS` | властивість каталогу `COMPILE_OPTIONS` | `target_compile_options()` | `INTERFACE_COMPILE_OPTIONS` | — |
| `COMPILE_FEATURES` | — | `target_compile_features()` | `INTERFACE_COMPILE_FEATURES` | — |
| `LINK_LIBRARIES` | — | `target_link_libraries()` | `INTERFACE_LINK_LIBRARIES` | — |
| `LINK_OPTIONS` | властивість каталогу `LINK_OPTIONS` | `target_link_options()` | `INTERFACE_LINK_OPTIONS` | 3.13 |
| `LINK_DIRECTORIES` | властивість каталогу `LINK_DIRECTORIES` | `target_link_directories()` | `INTERFACE_LINK_DIRECTORIES` | 3.13 |
| `PRECOMPILE_HEADERS` | — | `target_precompile_headers()` | `INTERFACE_PRECOMPILE_HEADERS` | 3.16 |

Усі дев'ять приймають [генераторні вирази](topic:sys-bsystem/generator-expressions). Каталожні властивості, з яких вони починаються, наповнюють старі команди без імені цілі — `include_directories()`, `add_compile_definitions()` (або ще давніша `add_definitions()`), `add_compile_options()`, `add_link_options()`, `link_directories()`; каталог, своєю чергою, дістає початкове значення від батьківського, тому такий запис протікає вниз по дереву сам собою.

Три уточнення, які легко проґавити:

- **`include_directories()` — не чистий знімок.** Вона править не лише властивість каталогу, а й `INCLUDE_DIRECTORIES` **уже створених** цілей поточного файлу. Решта каталожних команд так не роблять, тож поведінка тут не однакова, як здається.
- **`-D` у визначеннях зайве.** З CMake 3.26 провідне `-D` в елементі `COMPILE_DEFINITIONS` знімається. Пишуть `IMG_SIMD` або `IMG_LEVEL=3`, не `-DIMG_SIMD`.
- **Системні заголовки — окреме дзеркало.** Ключове слово `SYSTEM` у `target_include_directories()` кладе шлях у `INTERFACE_SYSTEM_INCLUDE_DIRECTORIES`, і компілятор мовчить про попередження з тих заголовків.

## Мова, вигляд результату, місце в проєкті

Тут `target_*`-команд немає: усе ставлять `set_target_properties`, і майже нічого не передається далі по графу.

| Властивість | Започатковує | Дзеркало | З версії |
| --- | --- | --- | --- |
| `CXX_STANDARD` | `CMAKE_CXX_STANDARD` | — | — |
| `CXX_STANDARD_REQUIRED` | `CMAKE_CXX_STANDARD_REQUIRED` | — | — |
| `CXX_EXTENSIONS` | `CMAKE_CXX_EXTENSIONS` | — | — |
| `POSITION_INDEPENDENT_CODE` | `CMAKE_POSITION_INDEPENDENT_CODE` | `INTERFACE_POSITION_INDEPENDENT_CODE` | — |
| `OUTPUT_NAME` | — | — | — |
| `RUNTIME_OUTPUT_DIRECTORY` | `CMAKE_RUNTIME_OUTPUT_DIRECTORY` | — | — |
| `LIBRARY_OUTPUT_DIRECTORY` | `CMAKE_LIBRARY_OUTPUT_DIRECTORY` | — | — |
| `ARCHIVE_OUTPUT_DIRECTORY` | `CMAKE_ARCHIVE_OUTPUT_DIRECTORY` | — | — |
| `VERSION`, `SOVERSION` | — | — | — |
| `EXPORT_NAME` | — | — | — |
| `FOLDER` | `CMAKE_FOLDER` | — | 3.12 |
| `IMPORTED_LOCATION` | — | — | — |
| `TYPE` | — (лише читання) | — | — |

- **`CXX_STANDARD`** приймає `98`, `11`, `14`, `17` (з 3.8), `20` (з 3.12), `23` (з 3.20), `26` (з 3.25). Коли компілятор потрібного стандарту не має, CMake **тихо підставляє попередній** — саме це й вимикає `CXX_STANDARD_REQUIRED`. Дзеркала в усієї трійці немає навмисно: бібліотека не може вимагати стандарт від того, хто нею користується, через ці властивості. Для вимоги є `target_compile_features(img PUBLIC cxx_std_17)` — її `INTERFACE_COMPILE_FEATURES` передається як слід.
- **`POSITION_INDEPENDENT_CODE`** усталено `True` для `SHARED` і `MODULE`. Її дзеркало — виняток серед усіх `INTERFACE_`: воно нічого не додає, а **вимагає**, щоб той, хто лінкується, мав таке саме значення. Узгодженість CMake перевіряє механізмом `COMPATIBLE_INTERFACE_BOOL` і на розбіжність зупиняється.
- **Каталоги виходу.** Багатоконфігураційні генератори (Visual Studio, Xcode, Ninja Multi-Config) дописують до вказаного шляху ще й підтеку конфігурації — якщо це заважає, шлях задають генераторним виразом.
- **`VERSION` і `SOVERSION`** для спільної бібліотеки означають різне: перша — версія збірки, друга — версія ABI, і саме з них будуються символьні посилання й `soname` ([динамічне лінкування](topic:sf-lang/dynamic-linking)). На macOS вони лягають у *current* і *compatibility version*, на Windows із `VERSION` беруть `major.minor` для версії образу.
- **`FOLDER`** розкладає цілі по теках у дереві IDE; шанують її лише генератори Visual Studio та Xcode. З CMake 3.26 глобальна `USE_FOLDERS`, без якої вона раніше не діяла, усталено ввімкнена (політика `CMP0143`).
- **`IMPORTED_LOCATION`** — шлях до готового файлу [імпортованої цілі](topic:sys-bsystem/find-package); для конкретної конфігурації його перебиває `IMPORTED_LOCATION_<CONFIG>`.
- **`EXPORT_NAME`** — ім'я, під яким ціль потрапить у набір експорту; усталено береться власне ім'я цілі ([install і export](topic:sys-bsystem/install-and-export)).
- **`TYPE`** віддає `STATIC_LIBRARY`, `MODULE_LIBRARY`, `SHARED_LIBRARY`, `OBJECT_LIBRARY`, `INTERFACE_LIBRARY`, `EXECUTABLE` або одне з внутрішніх імен (цілі-дії — `UTILITY`). Записати її не можна.

## Команди читання й запису

```cmake
set_target_properties(<ціль>... PROPERTIES <влас1> <знач1> [<влас2> <знач2>]...)

set_property(TARGET <ціль>...
             [APPEND] [APPEND_STRING]
             PROPERTY <влас> [<знач>...])

get_target_property(<змінна> <ціль> <влас>)

get_property(<змінна> TARGET <ціль>
             PROPERTY <влас>
             [SET | DEFINED | BRIEF_DOCS | FULL_DOCS])

define_property(TARGET PROPERTY <влас> [INHERITED]
                [BRIEF_DOCS <текст>...] [FULL_DOCS <текст>...]
                [INITIALIZE_FROM_VARIABLE <змінна>])
```

`set_target_properties` бере кілька цілей і кілька пар «властивість — значення» одразу, але завжди **замінює** попереднє значення. `set_property` бере одну властивість, зате вміє дописувати: `APPEND` додає елемент до списку (порожні значення пропускає), `APPEND_STRING` доклеює текст до наявного рядка, не перетворюючи його на список. Псевдонім (`ALIAS`) не приймає жодна з двох — на псевдоніми властивості лише читають.

## Що повертає читання

| Випадок | `get_target_property` | `get_property … PROPERTY` |
| --- | --- | --- |
| властивість задано | значення | значення |
| властивість не задано | `<змінна>-NOTFOUND` | змінну **не визначено** взагалі |
| цілі не існує | помилка конфігурації | помилка конфігурації |

`-NOTFOUND` дописується до **імені змінної**, а не властивості: після `get_target_property(std img CXX_STANDARD)` з незаданим стандартом у `std` буде рядок `std-NOTFOUND`. Це не примха — `if()` вважає хибою будь-який рядок, що закінчується на `-NOTFOUND`, тож `if(std)` спрацює правильно без окремої перевірки. Різниця з `get_property` має свій наслідок: він змінної не чіпає, тому там може лишитися значення від попереднього читання, і її розважливо чистити перед викликом.

Помилка на неіснуючій цілі — теж рішення, а не збіг: до CMake 3.0 такий виклик мовчки віддавав `-NOTFOUND`, і одруківка в імені цілі маскувалася під «властивості немає». Поведінку змінила політика `CMP0045` ([політики CMake](topic:sys-bsystem/cmake-policies)).

Два ключові слова, які плутають між собою:

- `SET` — чи **записано** значення на цій цілі. Єдиний спосіб відрізнити «не задано» від «задано порожнім рядком»: обидва випадки в звичайному читанні виглядають однаково хибними.
- `DEFINED` — чи властивість **оголошено** командою `define_property`. Про те, чи є в цілі значення, не каже нічого.

І головне обмеження, спільне для обох команд: читання віддає рядок **такий, як його записано**. Якщо у значенні є генераторний вираз — `$<CONFIG:Debug>`, `$<TARGET_PROPERTY:…>` — назад прийде сам текст виразу, необчислений. CMake розкриє його аж на генерації, коли ваш код давно відпрацював.

> 🔧 **Навіщо це.** Через мовчазний запис перевірка «що насправді лежить на цілі» — не педантизм, а щоденний інструмент. Пара `get_target_property` плюс `get_property(… SET)` за один прогін конфігурації показує і значення, і те, чи воно взагалі ваше, а не з `CMAKE_`-змінної. Що з цього дістане компілятор — питання іншого етапу, і відповідь на нього шукають у `cmake --build … --verbose`.

## Оголошення власної властивості

`define_property` не створює значення. Воно заявляє, що властивість із таким іменем існує, і дає їй два вміння, яких у звичайного запису немає.

`INHERITED` вмикає підняття на рівень вище під час читання через `get_property`: немає на цілі — дивимося в каталог, немає там — у глобальні. Пастка: `APPEND` до успадкованої властивості до батьківського значення **не** дописує — якщо на самій цілі нічого не задано, дописування поводиться як звичайний запис.

`INITIALIZE_FROM_VARIABLE` (з 3.23) дає вашій властивості той самий механізм, яким `CMAKE_CXX_STANDARD` започатковує `CXX_STANDARD`. Обмеження суворі: працює лише для властивостей цілі, ім'я змінної мусить **закінчуватися** іменем властивості й не починатися на `CMAKE_` чи `_CMAKE_`, а в імені властивості має бути щонайменше одне підкреслення. Здвоєний префікс в іменах — плата за це правило, зате чужу змінну сюди не підставиш випадково.

```cmake
define_property(TARGET PROPERTY MYAPP_LAYER
                INITIALIZE_FROM_VARIABLE MYAPP_DEFAULT_MYAPP_LAYER)

set(MYAPP_DEFAULT_MYAPP_LAYER "core")
add_library(img img.cpp)              # MYAPP_LAYER цілі img = core
```

Що `define_property` **не** робить: воно не змушує CMake відкидати незнайомі імена. Одруківка в `set_target_properties` пройде так само мовчки, як і до оголошення.

## Мінімальний повний опис цілі

```cmake
add_library(img img.cpp resize.cpp)
add_library(img::img ALIAS img)

target_include_directories(img PUBLIC include PRIVATE src)
target_compile_definitions(img PUBLIC IMG_SIMD)
target_compile_features(img PUBLIC cxx_std_17)
target_link_libraries(img PRIVATE Threads::Threads)
set_property(TARGET img APPEND PROPERTY COMPILE_OPTIONS -Wall -Wextra)

set_target_properties(img PROPERTIES
    OUTPUT_NAME imgcore
    VERSION 1.4.2
    SOVERSION 1
    POSITION_INDEPENDENT_CODE ON
    EXPORT_NAME img
    FOLDER "libs")

get_target_property(kind img TYPE)
get_property(pic_set TARGET img PROPERTY POSITION_INDEPENDENT_CODE SET)
message(STATUS "${kind}, PIC задано явно: ${pic_set}")
# -- STATIC_LIBRARY, PIC задано явно: 1
```
