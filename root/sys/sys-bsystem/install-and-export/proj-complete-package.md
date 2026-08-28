# ⚙️ Повний виробничий проєкт створення та споживання пакета CMake

У цьому практичному проєкті розібрано повний виробничий цикл створення сучасної модульної бібліотеки на C++, підготовки її до експорту, генерації релокованого пакета для `find_package()` та підключення у зовнішній клієнтській програмі.

## Постановка задачі

Ми розробляємо модульну бібліотеку `Hyperion`, призначену для високопродуктивних обчислень та телеметрії. Проєкт складається з двох взаємопов'язаних компонентів із різними вимогами до збірки:

1. **`Hyperion::core`** — скомпільована бібліотека, яка містить стан рушія обчислень та алгоритм підрахунку контрольних сум FNV-1a. Вона повинна підтримувати складання як у статичному (`STATIC`), так і в динамічному (`SHARED`) варіантах із коректним експортом двійкових символів на всіх платформах.
2. **`Hyperion::math`** — заголовочна бібліотека (header-only / `INTERFACE`), яка надає набір шаблонів швидкої векторної арифметики на базі C++20 концептів (`std::floating_point`, `std::integral`) та представлень `std::span`.

До системи збірки та пакування висуваються такі жорсткі вимоги:
- **Двоїстість використання:** бібліотека має бездоганно компілюватися та проходити тести всередині власного репозиторію (Build Tree), а після інсталяції в системний каталог чи префікс менеджера пакетів (Install Tree) — надавати однаковий інтерфейс імпортованих цілей.
- **Повна переміщуваність (relocatability):** каталог інсталяції не повинен містити жодного жорстко закодованого абсолютного шляху хост-машини. Встановлений пакет має безперешкодно працювати після перейменування каталогу чи перенесення на інший комп'ютер.
- **Автоматизація конфігурації:** створення файлів `HyperionConfig.cmake`, `HyperionConfigVersion.cmake` та `HyperionTargets.cmake` має виконуватися за допомогою стандартних модулів `GNUInstallDirs` та `CMakePackageConfigHelpers`.
- **Семантичне версіонування:** підтримка автоматичної перевірки сумісності версій клієнтських запитів за правилом `SameMajorVersion`.

---

## Структура репозиторію

Організуємо файлову структуру проєкту з чітким розділенням публічних інтерфейсів, вихідного коду реалізації, шаблонів конфігурації та прикладів використання:

```text
hyperion-project/
├── CMakeLists.txt
├── cmake/
│   └── HyperionConfig.cmake.in
├── include/
│   └── hyperion/
│       ├── export.hpp
│       ├── core.hpp
│       └── math.hpp
├── src/
│   └── core.cpp
├── tests/
│   └── test_core.cpp
└── examples/
    └── consumer_app/
        ├── CMakeLists.txt
        └── main.cpp
```

Каталог `include/hyperion/` містить публічні заголовки, доступні зовнішнім споживачам. Каталог `src/` ізолює приватну реалізацію, а `cmake/` містить шаблон конфігураційного файла для `find_package()`.

---

## Вихідний код компонентів бібліотеки

### 1. Заголовковий файл макросів експорту `include/hyperion/export.hpp`

Для коректного складання динамічної бібліотеки (`SHARED`) у Windows компілятор MSVC вимагає явного позначення символів ключовим словом `__declspec(dllexport)` під час компіляції самої бібліотеки та `__declspec(dllimport)` під час її підключення у клієнтському коді. Натомість у Linux (GCC/Clang) використовується атрибут видимості `__attribute__((visibility("default")))`.

:::code proj-complete-package/cpp/1-zaholovkovyi-fail.hpp

Зверніть увагу на макрос `hyperion_core_EXPORTS`: CMake автоматично визначає цей макрос під час збірки цілі `hyperion_core` як спільної бібліотеки (`SHARED`). Коли цей самий заголовок включається споживачем, макрос відсутній, і `HYPERION_API` автоматично перемикається на `__declspec(dllimport)`.

### 2. Публічний заголовок скомпільованого ядра `include/hyperion/core.hpp`

Клас `Engine` інкапсулює внутрішній стан та надає метод для обчислення некриптографічного хешу FNV-1a над довільним рядковим буфером:

:::code proj-complete-package/cpp/2-publichnyi-zaholovok.hpp

### 3. Реалізація ядра `src/core.cpp`

:::code proj-complete-package/cpp/3-realizatsiia-iadra-src.cpp

### 4. Заголовочний модуль `include/hyperion/math.hpp`

Модуль реалізує шаблон підсумовування елементів вектора, обмежуючи типи даних за допомогою концептів мови C++20:

:::code proj-complete-package/cpp/4-zaholovochnyi-modul.hpp

---

## Шаблон конфігурації `cmake/HyperionConfig.cmake.in`

Файл конфігурації виконується під час виклику `find_package(Hyperion CONFIG)` у клієнтському проєкті. Шаблон містить мінімальний захисний код:

:::code proj-complete-package/cmake/shablon-konfihuratsii.cmake

Макрос `@PACKAGE_INIT@` генерує код для визначення відносного кореня інсталяції `PACKAGE_PREFIX_DIR`. Макрос `check_required_components(Hyperion)` гарантує, що якщо споживач передав список компонентів `COMPONENTS core math`, конфігурація перевірить їхню доступність.

---

## Головний сценарій збірки `CMakeLists.txt`

Сценарій `CMakeLists.txt` реалізує повний життєвий цикл збірки, тестування, експорту цілей та генерації пакетних метаданих:

:::code proj-complete-package/cmake/holovnyi-stsenarii-zbirky.cmake

Зверніть увагу на реєстрацію псевдонімів `add_library(Hyperion::core ALIAS hyperion_core)`. Це дозволяє писати модульні тести та приклади всередині самого репозиторію точно так само, як це робитиме зовнішній споживач: лінкуючись із `Hyperion::core`, а не з внутрішнім іменем `hyperion_core`. Блок `if(NOT BUILD_SHARED_LIBS)` гарантує, що у статичному режимі макрос `HYPERION_STATIC_DEFINE` транзитивно передається через властивість `INTERFACE_COMPILE_DEFINITIONS` усім споживачам.

---

## Збірка та інсталяція в ізольований каталог

Виконаємо конфігурацію, компіляцію та інсталяцію бібліотеки у тимчасовий каталог `/tmp/hyperion-dist`:

:::code proj-complete-package/sh/zbirka-ta-instaliatsiia-v.sh

### Анатомія створеного каталогу інсталяції

Після виконання команди `cmake --install` каталог `/tmp/hyperion-dist` містить повністю автономну структуру файлів:

```text
/tmp/hyperion-dist/
├── include/
│   └── hyperion/
│       ├── core.hpp
│       ├── export.hpp
│       └── math.hpp
├── lib/
│   ├── libhyperion_core.so (або .dylib на macOS чи .lib на Windows)
│   └── cmake/
│       └── Hyperion/
│           ├── HyperionConfig.cmake
│           ├── HyperionConfigVersion.cmake
│           ├── HyperionTargets.cmake
│           └── HyperionTargets-release.cmake
```

Розберемо вміст згенерованих файлів:
- **`HyperionTargets.cmake`** — містить визначення імпортованих цілей `add_library(Hyperion::core SHARED IMPORTED)` та `add_library(Hyperion::math INTERFACE IMPORTED)`. Він обчислює змінну `_IMPORT_PREFIX` підняттям на 3 рівні вгору від `lib/cmake/Hyperion/` до кореня `/tmp/hyperion-dist`.
- **`HyperionTargets-release.cmake`** — прив'язує властивість `IMPORTED_LOCATION_RELEASE` цілі `Hyperion::core` до відносного файлу `${_IMPORT_PREFIX}/lib/libhyperion_core.so`.
- **`HyperionConfigVersion.cmake`** — містить алгоритм перевірки SemVer. Якщо споживач запитає версію `1.0.0` або `1.2.0`, файл встановить `PACKAGE_VERSION_COMPATIBLE = TRUE`. Якщо споживач запитає `2.0.0`, файл встановить `PACKAGE_VERSION_COMPATIBLE = FALSE`.
- **`HyperionConfig.cmake`** — містить розгорнутий макрос `@PACKAGE_INIT@` та директиву `include` для підключення `HyperionTargets.cmake`.

---

## Клієнтський проєкт-споживач

Створимо ізольований клієнтський проєкт `consumer_app`, який використовує нашу бібліотеку виключно через механізм `find_package()`.

### Файл опису збірки `examples/consumer_app/CMakeLists.txt`

:::code proj-complete-package/cmake/fail-opysu-zbirky-examples.cmake

### Вихідний код клієнта `examples/consumer_app/main.cpp`

Клієнтський код використовує обидва компоненти: скомпільований клас `Engine` та шаблонну заголовочну функцію `accumulate_span`:

:::code proj-complete-package/cpp/vykhidnyi-kod-kliienta.cpp

---

## Компіляція споживача та перевірка переміщуваності

Сконфігуруємо та запустимо програму споживача, передавши шлях до префікса інсталяції через змінну `CMAKE_PREFIX_PATH`:

:::code proj-complete-package/sh/kompiliatsiia-spozhyvacha.sh

Результат виконання програми:
```text
Engine: TelemetryAlpha
Metrics sum: 40
Payload hash: 0x6e7b1a2f
```

### Демонстрація переміщуваності (Relocation Test)

Найсуворішою перевіркою коректності генерації пакета є тест фізичного переміщення каталогу інсталяції в нове місце у файловій системі. Якщо в конфігураційних файлах залишився хоча б один жорсткий абсолютний шлях, повторна збірка споживача завершиться помилкою.

Виконаємо переміщення:

:::code proj-complete-package/sh/demonstratsiia.sh

Збірка та запуск виконуються бездоганно. Це на практиці доводить, що система динамічного обчислення `_IMPORT_PREFIX` у згенерованому `HyperionTargets.cmake` та макрос `@PACKAGE_INIT@` у `HyperionConfig.cmake` повністю ізолюють пакет від структури файлової системи машини збірки.

---

## Аналіз діагностики та крайових випадків

Розглянемо типові поведінкові сценарії системи збірки під час зміни конфігурації клієнта:

1. **Запит несумісної версії:**
   Якщо споживач змінить виклик на `find_package(Hyperion 2.0.0 REQUIRED CONFIG)`, генератор звернеться до `HyperionConfigVersion.cmake`, порівняє мажорну версію `2` з поточною `1.2.0` і зупинить конфігурацію з чітким діагностичним повідомленням:
   ```text
   Could not find a configuration file for package "Hyperion" that is compatible with requested version "2.0.0".
   The following configuration files were considered but not accepted:
     /tmp/hyperion-relocated/lib/cmake/Hyperion/HyperionConfig.cmake, version: 1.2.0
   ```
2. **Зневадження пошуку через CMAKE_FIND_DEBUG_MODE:**
   Якщо клієнтський проєкт не знаходить пакет, запуск із діагностикою показує повний перелік перевірених шляхів:
   ```bash
   cmake -B build-debug -S examples/consumer_app --debug-find-pkg=Hyperion
   ```
   Це дозволяє миттєво побачити, чи враховано змінну `CMAKE_PREFIX_PATH` і за якими саме префіксами шукався файл `HyperionConfig.cmake`.
