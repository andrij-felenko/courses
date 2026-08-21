# 📋 Довідка команд install, export та CMakePackageConfigHelpers

У цьому довіднику зібрано повний синтаксис інструкцій інсталяції та експорту цілей CMake, опис стандартних змінних модуля `GNUInstallDirs`, параметри функцій генерації файлів конфігурації `CMakePackageConfigHelpers` та макрос виявлення транзитивних залежностей `CMakeFindDependencyMacro`.

## Команда install(TARGETS)

Команда `install(TARGETS)` реєструє правила копіювання двійкових артефактів цілей у дерево інсталяції та прив'язує їх до іменованих наборів експорту.

```cmake
install(TARGETS <target>... [EXPORT <export-name>]
        [RUNTIME_DEPENDENCIES <args>...]
        [<artifact-type>
         [DESTINATION <dir>]
         [PERMISSIONS <permissions>...]
         [CONFIGURATIONS [Debug|Release|...]]
         [COMPONENT <component>]
         [NAMELINK_COMPONENT <component>]
         [OPTIONAL] [EXCLUDE_FROM_ALL]
         [NAMELINK_ONLY|NAMELINK_SKIP]
        ]...
        [INCLUDES DESTINATION [<dir> ...]]
        [FILE_SET <set-name> [DESTINATION <dir>] ...]
)
```

### Типи двійкових артефактів

Поведінка цілі залежить від типу артефакту, що створюється компілятором і лінкером на конкретній платформі:

| Ключове слово | Призначення та поведінка на операційних системах |
| :--- | :--- |
| `ARCHIVE` | Статичні бібліотеки (`.a` на Linux/macOS, `.lib` на Windows), а також файли таблиць імпорту динамічних бібліотек (`.lib`) на платформі Windows під час складання компілятором MSVC або Clang-cl. |
| `LIBRARY` | Динамічні бібліотеки (`.so` на Linux, `.dylib` на macOS), крім файлів DLL у Windows, а також завантажувані модульні плагіни (`MODULE`-бібліотеки). |
| `RUNTIME` | Виконувані двійкові файли (`ELF`-бінарники на Linux, `Mach-O` на macOS, `.exe` на Windows), а також безпосередньо файли динамічних бібліотек (`.dll`) на операційній системі Windows. |
| `OBJECTS` | Об'єктні файли цілей, створених через команду `add_library(... OBJECT)`. |
| `PUBLIC_HEADER` | Заголовкові файли, перелічені у властивості цілі `PUBLIC_HEADER` (застарілий механізм CMake 2.x/3.x, замінений на `FILE_SET`). |
| `PRIVATE_HEADER`| Заголовкові файли, перелічені у внутрішній властивості цілі `PRIVATE_HEADER`. |
| `INCLUDES DESTINATION` | Додає зазначений шлях до властивості `INTERFACE_INCLUDE_DIRECTORIES` імпортованої цілі під час експорту (діє аналогічно генераторному виразу `$<INSTALL_INTERFACE:...>`). |
| `FILE_SET` | Іменований набір файлів заголовків (CMake 3.23+), створений через команду `target_sources(... FILE_SET ...)`. |

### Ключові параметри та прапорці команди

- `EXPORT <export-name>` — зв'язує перелічені цілі з логічним набором експорту. Дозволяє згодом зберегти метадані цих цілей у файл за допомогою виклику `install(EXPORT)`. Цей ключ не виконує фізичного експорту самостійно, він лише реєструє зв'язок у пам'яті генератора.
- `DESTINATION <dir>` — шлях до каталогу встановлення артефакту. Якщо передано відносний шлях, він автоматично відраховується від кореня `CMAKE_INSTALL_PREFIX`. Якщо передано абсолютний системний шлях, артефакт записується за вказаною точною адресою (що порушує переміщуваність пакета).
- `PERMISSIONS <permissions>...` — явне задання прав доступу до встановлених файлів у файловій системі POSIX. Допустимі значення: `OWNER_READ`, `OWNER_WRITE`, `OWNER_EXECUTE`, `GROUP_READ`, `GROUP_WRITE`, `GROUP_EXECUTE`, `WORLD_READ`, `WORLD_WRITE`, `WORLD_EXECUTE`, `SETUID`, `SETGID`. За замовчуванням виконувані файли отримують права `0755`, а статичні та заголовкові файли — `0644`.
- `CONFIGURATIONS <config>...` — обмежує дію правила інсталяції лише вказаними типами збірки (наприклад `Release`, `Debug`, `RelWithDebInfo`, `MinSizeRel`). Правило ігнорується, якщо поточна конфігурація не збігається з переліченими.
- `COMPONENT <component>` — ім'я компонента встановлення (наприклад `runtime`, `development`, `headers`, `documentation`). Дозволяє вибірково встановлювати окремі частини пакета через виклик `cmake --install build --component <component>`.
- `NAMELINK_ONLY` — встановлює виключно символічне посилання без версії (наприклад `libfoo.so` -> `libfoo.so.1.2.0`). Застосовується авторами дистрибутивів Linux для відокремлення файлів розробки (`-dev` пакети) від файлів виконання.
- `NAMELINK_SKIP` — встановлює бібліотеку з сонеймом та версією (`libfoo.so.1.2.0`, `libfoo.so.1`), але пропускає символічне посилання без версії `libfoo.so`. Використовується для формування базових рантайм-пакетів.
- `RUNTIME_DEPENDENCIES` — аналізує динамічні бінарники цілі та копіює всі сторонні спільні бібліотеки, від яких вони залежать (доступно з CMake 3.21, корисно для створення автономних бандлів під Windows та macOS).

---

## Команда install(EXPORT)

Команда `install(EXPORT)` генерує і встановлює файл сценарію CMake, який відновлює структуру імпортованих цілей (Imported Targets) для зареєстрованого набору експорту.

```cmake
install(EXPORT <export-name>
        [DESTINATION <dir>]
        [NAMESPACE <namespace::>]
        [FILE <filename.cmake>]
        [PERMISSIONS <permissions>...]
        [CONFIGURATIONS <config>...]
        [COMPONENT <component>]
        [EXPORT_LINK_INTERFACE_LIBRARIES]
        [CXX_MODULES_DIRECTORY <directory>]
)
```

### Параметри команди

| Параметр | Опис та семантика |
| :--- | :--- |
| `EXPORT <export-name>` | Ім'я набору експорту, збігається зі значенням аргументу `EXPORT` у попередніх викликах `install(TARGETS)`. |
| `DESTINATION <dir>` | Каталог встановлення згенерованого `.cmake`-файла (за стандартом `${CMAKE_INSTALL_LIBDIR}/cmake/<PackageName>`). |
| `NAMESPACE <namespace::>` | Префікс простору імен, який додається до імен імпортованих цілей (наприклад `MyLib::` перетворить ціль `core` на `MyLib::core`). Захищає від колізій імен у споживача. |
| `FILE <filename.cmake>` | Ім'я створюваного файла експорту (за замовчуванням `<export-name>.cmake`, наприклад `MyLibTargets.cmake`). |
| `COMPONENT <component>` | Компонент інсталяції (зазвичай `development` або `Devel`). |
| `EXPORT_LINK_INTERFACE_LIBRARIES` | Примусово експортує повні інтерфейси лінкування цілей (CMake 3.30+). |
| `CXX_MODULES_DIRECTORY <directory>` | Каталог для експорту метаданих C++20 модулів (CMake 3.28+). |

---

## Інсталяція файлів та каталогів: install(FILES) та install(DIRECTORY)

Для копіювання документації, ліцензійних угод та каталогів заголовків використовуються команди `install(FILES)` та `install(DIRECTORY)`:

```cmake
# Встановлення окремих файлів
install(FILES <file>...
        DESTINATION <dir>
        [PERMISSIONS <permissions>...]
        [CONFIGURATIONS <config>...]
        [COMPONENT <component>]
        [RENAME <new-name>]
        [OPTIONAL]
)

# Встановлення структури каталогів
install(DIRECTORY <dir>...
        DESTINATION <dir>
        [FILE_PERMISSIONS <permissions>...]
        [DIRECTORY_PERMISSIONS <permissions>...]
        [USE_SOURCE_PERMISSIONS]
        [CONFIGURATIONS <config>...]
        [COMPONENT <component>]
        [FILES_MATCHING]
        [PATTERN <pattern> | REGEX <regex>]
        [EXCLUDE] [PERMISSIONS <permissions>...]
)
```

### Нюанс завершального слеша в install(DIRECTORY)

Поведінка команди `install(DIRECTORY)` залежить від наявності завершального слеша `/` у шляху вихідного каталогу:
- `install(DIRECTORY include/ DESTINATION include)` — завершальний слеш копіює **лише вміст** каталогу `include/` усередину `${CMAKE_INSTALL_INCLUDEDIR}` (файли `include/foo.h` потраплять у `${CMAKE_INSTALL_PREFIX}/include/foo.h`).
- `install(DIRECTORY include DESTINATION include)` — відсутність слеша копіює **сам каталог разом з іменем**, утворюючи вкладену структуру `${CMAKE_INSTALL_PREFIX}/include/include/foo.h`.

---

## Команди export(TARGETS) та export(EXPORT)

Команди сімейства `export()` генерують файл імпортованих цілей безпосередньо для дерева збірки (Build Tree), без потреби виконувати команду інсталяції.

```cmake
# Експорт списку конкретних цілей
export(TARGETS <target>...
       [NAMESPACE <namespace::>]
       [APPEND]
       FILE <filename.cmake>
       [EXPORT_LINK_INTERFACE_LIBRARIES]
       [CXX_MODULES_DIRECTORY <directory>]
)

# Експорт за назвою експортного набору
export(EXPORT <export-name>
       [NAMESPACE <namespace::>]
       [FILE <filename.cmake>]
       [CXX_MODULES_DIRECTORY <directory>]
)
```

- `FILE <filename.cmake>` — обов'язковий шлях до вихідного файла (зазвичай у каталозі збірки `${CMAKE_CURRENT_BINARY_DIR}/MyLibTargets.cmake`).
- `APPEND` — дописує нові цілі в кінець наявного файла експорту замість його перезапису.
- Цільове призначення: модульне тестування залежних проєктів у CI без проміжної інсталяції або зв'язування компонентів у монорепозиторіях.

---

## Модуль GNUInstallDirs

Модуль надає стандартні змінні шляхів інсталяції, що відповідають угодам GNU Coding Standards та конвенціям дистрибутивів Linux, macOS і Windows.

Підключення:
```cmake
include(GNUInstallDirs)
```

### Таблиця стандартних змінних

| Змінна відносного шляху | Змінна абсолютного шляху | Типове значення на Linux / POSIX | Призначення |
| :--- | :--- | :--- | :--- |
| `CMAKE_INSTALL_BINDIR` | `CMAKE_INSTALL_FULL_BINDIR` | `bin` | Виконувані файли програм для користувача |
| `CMAKE_INSTALL_SBINDIR` | `CMAKE_INSTALL_FULL_SBINDIR` | `sbin` | Системні виконувані файли системного адміністратора |
| `CMAKE_INSTALL_LIBEXECDIR` | `CMAKE_INSTALL_FULL_LIBEXECDIR` | `libexec` (або `lib`) | Допоміжні виконувані файли для внутрішнього виклику |
| `CMAKE_INSTALL_LIBDIR` | `CMAKE_INSTALL_FULL_LIBDIR` | `lib`, `lib64` або `lib/<arch-triple>` | Скомпільовані об'єктні та динамічні бібліотеки |
| `CMAKE_INSTALL_INCLUDEDIR` | `CMAKE_INSTALL_FULL_INCLUDEDIR` | `include` | Файли заголовків C та C++ (`.h`, `.hpp`) |
| `CMAKE_INSTALL_DATAROOTDIR`| `CMAKE_INSTALL_FULL_DATAROOTDIR`| `share` | Корінь архітектурно-незалежних даних |
| `CMAKE_INSTALL_DATADIR` | `CMAKE_INSTALL_FULL_DATADIR` | `${CMAKE_INSTALL_DATAROOTDIR}` (`share`) | Текстові дані, схеми, ресурси |
| `CMAKE_INSTALL_MANDIR` | `CMAKE_INSTALL_FULL_MANDIR` | `${CMAKE_INSTALL_DATAROOTDIR}/man` | Сторінки документації man pages |
| `CMAKE_INSTALL_DOCDIR` | `CMAKE_INSTALL_FULL_DOCDIR` | `${CMAKE_INSTALL_DATAROOTDIR}/doc/<pkg>`| Документація користувача |
| `CMAKE_INSTALL_SYSCONFDIR` | `CMAKE_INSTALL_FULL_SYSCONFDIR` | `etc` | Конфігураційні файли системи хоста |

> **Важливо для переміщуваності:** у командах `install(TARGETS ... DESTINATION ...)` та `install(EXPORT ... DESTINATION ...)` завжди слід використовувати **відносні змінні** (`CMAKE_INSTALL_LIBDIR`, `CMAKE_INSTALL_INCLUDEDIR`), а не абсолютні (`CMAKE_INSTALL_FULL_*`), інакше пакет втрачає переміщуваність.

---

## Модуль CMakePackageConfigHelpers

Модуль автоматизує створення двох критичних файлів пакета: `<PackageName>Config.cmake` (із релокованими шляхами) та `<PackageName>ConfigVersion.cmake` (з логікою перевірки версій).

Підключення:
```cmake
include(CMakePackageConfigHelpers)
```

### Функція configure_package_config_file()

Генерує файл конфігурації із вхідного шаблону `.cmake.in`, замінюючи спеціальні макроси на безпечні відносні шляхи.

```cmake
configure_package_config_file(
    <input-file>
    <output-file>
    INSTALL_DESTINATION <dir>
    [PATH_VARS <var1> <var2>...]
    [NO_SET_AND_CHECK_MACRO]
    [NO_CHECK_REQUIRED_COMPONENTS_MACRO]
    [INSTALL_PREFIX <prefix>]
)
```

#### Параметри:
- `<input-file>` — шлях до шаблону (наприклад `cmake/MyLibConfig.cmake.in`).
- `<output-file>` — шлях до згенерованого файла (наприклад `${CMAKE_CURRENT_BINARY_DIR}/MyLibConfig.cmake`).
- `INSTALL_DESTINATION <dir>` — каталог, куди згодом буде встановлено цей файл конфігурації (наприклад `${CMAKE_INSTALL_LIBDIR}/cmake/MyLib`). На основі цієї глибини макрос `@PACKAGE_INIT@` вираховує відносне зміщення до префікса.
- `PATH_VARS <var>...` — перелік змінних шляхів (наприклад `CMAKE_INSTALL_INCLUDEDIR`, `CMAKE_INSTALL_LIBDIR`, `MYLIB_DATA_DIR`). Для кожної зазначеної змінної `VAR` у згенерованому коді створюється безпечний макрос `@PACKAGE_VAR@`.
- `NO_SET_AND_CHECK_MACRO` — вимикає генерацію допоміжного макроса `set_and_check()`.
- `NO_CHECK_REQUIRED_COMPONENTS_MACRO` — вимикає генерацію макроса `check_required_components()`.

#### Макроси шаблону Config.cmake.in:

1. `@PACKAGE_INIT@` — обов'язковий макрос на початку шаблону. Розгортається у код, який визначає змінну `PACKAGE_PREFIX_DIR` відносно положення встановленого конфігураційного файла.
2. `set_and_check(<var> "@PACKAGE_<path_var>@")` — створює змінну шляху та генерує фатальну помилку конфігурації, якщо зазначений каталог відсутній на диску.
3. `check_required_components(<PackageName>)` — макрос наприкінці шаблону. Перевіряє, чи всі компоненти, передані споживачем у виклику `find_package(MyLib COMPONENTS foo bar REQUIRED)`, були успішно знайдені й позначені як `MyLib_foo_FOUND = TRUE`.

---

### Функція write_basic_package_version_file()

Генерує файл перевірки сумісності версій `<PackageName>ConfigVersion.cmake`.

```cmake
write_basic_package_version_file(
    <output-file>
    [VERSION <major.minor.patch>]
    COMPATIBILITY <mode>
    [ARCH_INDEPENDENT]
)
```

#### Параметри:
- `<output-file>` — шлях до створюваного файла версії (наприклад `${CMAKE_CURRENT_BINARY_DIR}/MyLibConfigVersion.cmake`).
- `VERSION <version>` — версія пакета (якщо опущено, використовується значення `${PROJECT_VERSION}`).
- `COMPATIBILITY <mode>` — алгоритм порівняння запитаної споживачем версії та встановленої версії пакета:

| Режим COMPATIBILITY | Правило сумісності версій |
| :--- | :--- |
| `SameMajorVersion` | Стандартне семантичне версіонування (SemVer): версії з однаковим Major є сумісними, якщо встановлена версія ≥ запитаної (наприклад встановлена `2.4` підходить під запит `2.1`, але `3.0` відхиляється; для `0.x` версій вимагається точний збіг `0.x`). |
| `SameMinorVersion` | Суворіша сумісність: зміна Minor вважається несумісною (наприклад встановлена `1.2.4` підходить під запит `1.2.1`, але запит `1.3.0` відхиляється). |
| `AnyNewerVersion` | Пакет вважається сумісним із будь-якою запитаною версією, якщо встановлена версія ≥ запитаної (підходить для повністю зворотно сумісних C-бібліотек). |
| `ExactVersion` | Вимагає абсолютно точного збігу номерів версій аж до Patch/Tweak (корисно для тісно пов'язаних плагінів). |

- `ARCH_INDEPENDENT` — вимикає генерацію перевірки 32/64-бітної розрядності процесора хоста (`CMAKE_SIZEOF_VOID_P`). Прапорець є обов'язковим для заголовочних бібліотек (header-only), щоб 64-бітний генератор міг безперешкодно знаходити пакет, встановлений у системі з будь-якою архітектурою.

---

## Модуль CMakeFindDependencyMacro

Модуль надає функцію `find_dependency()`, призначену для безпечного пошуку транзитивних залежностей усередині файлів `<PackageName>Config.cmake`.

Підключення (всередині `Config.cmake.in`):
```cmake
include(CMakeFindDependencyMacro)
```

### Виклик функції

```cmake
find_dependency(<dep-name> [<version>] [EXACT] [QUIET] [CONFIG|NO_MODULE] [COMPONENTS <components>...])
```

### Відмінності від звичайного find_package()

| Критерій | `find_package(...)` | `find_dependency(...)` |
| :--- | :--- | :--- |
| **Трансляція помилки** | У разі збою без `REQUIRED` мовчки продовжує роботу або створює локальні змінні помилки. | Якщо залежність не знайдено, негайно перериває обробку `Config.cmake`, встановлює `<PackageName>_FOUND = FALSE` і формує зрозуміле діагностичне повідомлення для споживача. |
| **Прапорець QUIET** | Не наслідує автоматично режим тиші від зовнішнього виклику батьківського пакета. | Автоматично переймає стан `QUIET` із батьківського виклику `find_package(MyLib QUIET)`. |
| **Прапорець REQUIRED**| Якщо викликано з `REQUIRED`, може викинути фатальну помилку в несподіваному місці замість акуратної відмови пакета. | Якщо батьківський виклик був обов'язковим, транслює статус помилки наверх із повним збереженням контексту. |

---

## Діагностика та налагодження пошуку пакетів

Під час зневадження роботи експортованих пакетів у CMake передбачено діагностичні змінні:

1. `CMAKE_FIND_DEBUG_MODE=ON` — вмикає детальний журнал усіх шляхів файлової системи, які CMake сканує під час виконання `find_package()` (доступно з версії 3.17):
   ```cmake
   set(CMAKE_FIND_DEBUG_MODE ON)
   find_package(MyLib CONFIG REQUIRED)
   set(CMAKE_FIND_DEBUG_MODE OFF)
   ```
2. Командний рядок CLI:
   ```bash
   cmake -B build -S . --debug-find-pkg=MyLib
   ```
   Цей прапорець виводить повне дерево пошуку для конкретного пакета `MyLib`, показуючи кожен перевірений файл `<PackageName>Config.cmake` та причину його прийняття або відхилення.
