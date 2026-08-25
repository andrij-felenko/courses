# 📋 Повний довідник команди find_package та допоміжних модулів

Цей довідник містить вичерпний опис сигнатур команди `find_package()`, усіх її аргументів, режимів виконання, алгоритмів обходу файлової системи, створюваних змінних, взаємодії з постачальниками залежностей, реєстром пакетів, узгодження багатоконфігураційних генераторів, політик сумісності, а також повний інтерфейс допоміжних макросів `FindPackageHandleStandardArgs`, `CMakePackageConfigHelpers`, `SelectLibraryConfigurations`, `FindPackageMessage` та `CMakeFindDependencyMacro`. Його відкривають, коли потрібно точно налаштувати пошук зовнішнього пакета, написати власний конфігураційний файл чи модуль пошуку або з'ясувати точний порядок обробки каталогів, властивостей імпортованих цілей і діагностики помилок.

---

## 1. Сигнатури команди find_package

Команда `find_package()` має три форми виклику: базову скорочену, розширену сигнатуру режиму модуля (Module Mode) та повну сигнатуру режиму конфігурації (Config Mode).

### 1.1. Базова (універсальна) сигнатура

У базовій формі CMake спочатку намагається знайти модуль `Find<PackageName>.cmake` (якщо не передано заборону `CONFIG` чи `NO_MODULE`), а в разі його відсутності автоматично перемикається в режим пошуку конфігураційного файла `<PackageName>Config.cmake` або `<package-name>-config.cmake`:

```cmake
find_package(<PackageName> [<version>] [EXACT] [QUIET] [REQUIRED]
             [[COMPONENTS] <components>...]
             [OPTIONAL_COMPONENTS <components>...]
             [REGISTRY_VIEW (64|32|64_32|32_64|HOST|TARGET|BOTH)]
             [GLOBAL]
             [NO_POLICY_SCOPE]
             [BYPASS_PROVIDER])
```

### 1.2. Явний виклик режиму модуля (Module Mode)

Коли вказано ключове слово `MODULE`, CMake виконує виключно пошук сценарію `Find<PackageName>.cmake`. Якщо файл не знайдено, перехід до пошуку конфігураційних файлів виробника не відбувається:

```cmake
find_package(<PackageName> [MODULE] [<version>] [EXACT] [QUIET] [REQUIRED]
             [[COMPONENTS] <components>...]
             [OPTIONAL_COMPONENTS <components>...]
             [REGISTRY_VIEW (64|32|64_32|32_64|HOST|TARGET|BOTH)]
             [GLOBAL]
             [NO_POLICY_SCOPE]
             [BYPASS_PROVIDER])
```

### 1.3. Повна сигнатура режиму конфігурації (Config Mode)

Повна форма вимикає пошук файлів `Find<PackageName>.cmake` і дозволяє детально керувати списком назв конфігураційних файлів, префіксами, суфіксами та вибірково вимикати окремі групи системних шляхів:

```cmake
find_package(<PackageName> [version] [EXACT] [QUIET]
             [REQUIRED] [[COMPONENTS] components...]
             [OPTIONAL_COMPONENTS components...]
             [CONFIG|NO_MODULE]
             [GLOBAL]
             [NO_POLICY_SCOPE]
             [BYPASS_PROVIDER]
             [NAMES name1 [name2 ...]]
             [CONFIGS config1 [config2 ...]]
             [HINTS path1 [path2 ...]]
             [PATHS path1 [path2 ...]]
             [REGISTRY_VIEW (64|32|64_32|32_64|HOST|TARGET|BOTH)]
             [PATH_SUFFIXES suffix1 [suffix2 ...]]
             [NO_DEFAULT_PATH]
             [NO_PACKAGE_ROOT_PATH]
             [NO_CMAKE_PATH]
             [NO_CMAKE_ENVIRONMENT_PATH]
             [NO_SYSTEM_ENVIRONMENT_PATH]
             [NO_CMAKE_PACKAGE_REGISTRY]
             [NO_CMAKE_SYSTEM_PATH]
             [NO_CMAKE_SYSTEM_PACKAGE_REGISTRY]
             [CMAKE_FIND_ROOT_PATH_BOTH |
              ONLY_CMAKE_FIND_ROOT_PATH |
              NO_CMAKE_FIND_ROOT_PATH])
```

---

## 2. Опис параметрів команди find_package

Кожен аргумент команди керує або суворістю перевірки, або набором шуканих складових, або алгоритмом обходу файлової системи.

### 2.1. Керування версією та суворістю

- `<version>`: запит мінімальної або точної версії у форматі `major[.minor[.patch[.tweak]]]`. Також підтримується запит діапазону версій (з CMake 3.19), наприклад `1.2...1.8` або `1.2...<2.0`.
- `EXACT`: вимагає точного збігу версії. У Config Mode сумісність перевіряє `<PackageName>ConfigVersion.cmake`. Без цього прапорця версія `2.4` вважається прийнятною, якщо запитано `2.1` (за умови відповідності правилам сумісності).
- `QUIET`: вимикає інформаційні повідомлення та попередження, якщо пакет або його необов'язкові компоненти не знайдено. Якщо вказано водночас із `REQUIRED`, фатальне повідомлення про помилку все одно друкується в разі невдачі.
- `REQUIRED`: зупиняє процес конфігурації з фатальною помилкою (`FATAL_ERROR`), якщо шуканий пакет (або хоча б один обов'язковий компонент) не знайдено.

### 2.2. Компоненти

- `COMPONENTS <components>...`: список обов'язкових компонентів (модулів, плагінів, підбібліотек). Якщо хоча б один із них відсутній, пакет вважається не знайденим.
- `OPTIONAL_COMPONENTS <components>...`: список додаткових компонентів, відсутність яких не призводить до збою пошуку. Статус кожного компонента фіксується у змінній `<PackageName>_<Component>_FOUND`.

### 2.3. Керування областю цілей і політиками

- `GLOBAL`: автоматично підвищує видимість усіх створених імпортованих цілей до глобального рівня (`GLOBAL`), роблячи їх доступними в батьківських каталогах і паралельних підпроєктах дерева збірки (з CMake 3.24).
- `NO_POLICY_SCOPE`: вимикає створення нової області політик CMake під час виконання знайденого модуля чи конфігураційного файла. За замовчуванням зміни політик усередині знайденого пакета не витікають назовні.
- `BYPASS_PROVIDER`: ігнорує зареєстрований постачальник залежностей (`dependency provider`, зареєстрований через `cmake_language(SET_DEPENDENCY_PROVIDER)`), примушуючи виконати стандартний внутрішній пошук CMake.

### 2.4. Специфікація імен та шляхів (Config Mode)

- `NAMES name1 [name2 ...]`: альтернативні імена пакета. За замовчуванням шукається `<PackageName>Config.cmake` або `<package-name>-config.cmake`. Якщо вказано `NAMES foo bar`, шукатимуться також `fooConfig.cmake`, `barConfig.cmake` тощо.
- `CONFIGS config1 [config2 ...]`: точні імена конфігураційних файлів для пошуку замість стандартних шаблонів.
- `HINTS path1 [path2 ...]`: каталоги, які перевіряються з високим пріоритетом (до стандартних системних шляхів). Зазвичай сюди передають шляхи, обчислені за іншими знайденими артефактами.
- `PATHS path1 [path2 ...]`: додаткові жорсткі каталоги для пошуку, які перевіряються з низьким пріоритетом (після системних шляхів).
- `PATH_SUFFIXES suffix1 [suffix2 ...]`: підкаталоги, які автоматично дописуються до кожного шуканого префікса (наприклад `cmake`, `lib/cmake/<name>`, `share/<name>/cmake`).
- `REGISTRY_VIEW`: керує переглядом реєстру Windows на 64-розрядних системах. Дозволяє явно обрати 32-розрядний (`32`), 64-розрядний (`64`) або комбінований вигляд.

### 2.5. Фільтрація та вимикання груп шляхів

Прапорці з префіксом `NO_` дозволяють звузити пошук і уникнути підхоплення випадкових системних бібліотек:

- `NO_DEFAULT_PATH`: скорочення, яке вимикає всі стандартні системні шляхи, змінні оточення та реєстри, обмежуючи пошук виключно переданими `HINTS` та `PATHS`.
- `NO_PACKAGE_ROOT_PATH`: не перевіряти префікси зі змінних `<PackageName>_ROOT` та `ENV{<PackageName>_ROOT}`.
- `NO_CMAKE_PATH`: не перевіряти каталоги зі змінних `CMAKE_PREFIX_PATH`, `CMAKE_FRAMEWORK_PATH`, `CMAKE_APPBUNDLE_PATH`.
- `NO_CMAKE_ENVIRONMENT_PATH`: не перевіряти шляхи зі змінних оточення `CMAKE_PREFIX_PATH` тощо.
- `NO_SYSTEM_ENVIRONMENT_PATH`: не шукати у змінній оточення `PATH`.
- `NO_CMAKE_PACKAGE_REGISTRY`: ігнорувати записи в користувацькому реєстрі пакетів CMake (`~/.cmake/packages` або HKCU).
- `NO_CMAKE_SYSTEM_PATH`: не перевіряти системні платформні шляхи (`CMAKE_SYSTEM_PREFIX_PATH`: `/usr`, `/usr/local` тощо).
- `NO_CMAKE_SYSTEM_PACKAGE_REGISTRY`: ігнорувати системний реєстр пакетів CMake (`/var/lib/cmake/packages` або HKLM).

---

## 3. Алгоритм та макети пошуку конфігураційних файлів

У режимі Config Mode CMake будує повні шляхи для пошуку файла конфігурації, перебираючи кожен базовий префікс `<prefix>` зі списку шляхів разом із набором стандартних підкаталогів.

### 3.1. Стандартні підкаталоги пошуку у префіксі

Для кожного базового каталогу `<prefix>` (де ім'я пакета позначається як `<name>`, а версія як `<version>`) перевіряються такі макети розміщення:

```text
<prefix>/
<prefix>/(cmake|CMake)/
<prefix>/<name>*/
<prefix>/<name>*/(cmake|CMake)/
<prefix>/(lib/<arch>|lib*|share)/cmake/<name>*/
<prefix>/(lib/<arch>|lib*|share)/<name>*/
<prefix>/(lib/<arch>|lib*|share)/<name>*/(cmake|CMake)/
<prefix>/<name>*/(lib/<arch>|lib*|share)/cmake/<name>*/
<prefix>/<name>*/(lib/<arch>|lib*|share)/<name>*/
<prefix>/<name>*/(lib/<arch>|lib*|share)/<name>*/(cmake|CMake)/
```

Усередині кожного з цих каталогів CMake перевіряє наявність файлів із такими шаблонами імен (з урахуванням або без урахування регістру літер):

```text
<PackageName>Config.cmake
<PackageName>-config.cmake
<lowercase_packagename>-config.cmake
```

### 3.2. Макети для Apple Frameworks та Application Bundles

На платформі macOS за наявності `CMAKE_FRAMEWORK_PATH` або стандартних системних шляхів до фреймворків додатково перевіряються спеціальні макети:

```text
<prefix>/<name>.framework/Resources/
<prefix>/<name>.framework/Resources/CMake/
<prefix>/<name>.framework/Versions/*/Resources/
<prefix>/<name>.framework/Versions/*/Resources/CMake/
<prefix>/<name>.app/Contents/Resources/
<prefix>/<name>.app/Contents/Resources/CMake/
```

---

## 4. Змінні оточення та змінні конфігурації пошуку

CMake надає набір глобальних змінних, які визначають, де саме шукатимуться файли під час виконання `find_package()`.

### 4.1. Керування шляхами пошуку (вхідні змінні)

| Змінна CMake / Оточення | Призначення та поведінка |
| :--- | :--- |
| `CMAKE_MODULE_PATH` | Список каталогів, де CMake шукає файли `Find<PackageName>.cmake` у Module Mode перед зверненням до власних вбудованих модулів. |
| `CMAKE_PREFIX_PATH` | Список кореневих префіксів встановлення (наприклад `/opt/custom;/usr/local`). У кожному префіксі CMake шукає конфігураційні файли у підкаталогах `lib/cmake/`, `share/`, `include/` тощо. |
| `<PackageName>_ROOT` | Префікс конкретного пакета (змінна CMake або оточення). Має найвищий пріоритет у пошуку (політика `CMP0074`). |
| `<PackageName>_DIR` | Прямий шлях до каталогу, що містить `<PackageName>Config.cmake`. Якщо задано, CMake завантажує файл одразу без сканування інших шляхів. |
| `CMAKE_DISABLE_FIND_PACKAGE_<PackageName>` | Якщо встановлено в `TRUE`, виклик `find_package(<PackageName>)` негайно повертає статус невдачі, ніби пакет не встановлено. |
| `CMAKE_FIND_DEBUG_MODE` | Якщо встановлено в `TRUE` (або передано `--debug-find` у CLI), виводить у консоль детальний журнал кожного перевіреного шляху та причини відхилення файлів. |
| `CMAKE_FIND_ROOT_PATH` | Корінь цільової системи під час крос-компіляції (sysroot). Усі шляхи пошуку перенаправляються всередину цього каталогу. |
| `CMAKE_FIND_ROOT_PATH_MODE_PACKAGE` | Режим фільтрації префіксів під час крос-компіляції: `ONLY` (лише всередині sysroot), `NEVER` (ігнорувати sysroot), `BOTH` (шукати в обох місцях). |

### 4.2. Службові змінні запиту (передаються у сценарій пошуку)

Коли CMake викликає `Find<PackageName>.cmake` або `<PackageName>Config.cmake`, він автоматично встановлює такі змінні для інформування сценарію про умови виклику:

| Змінна | Опис |
| :--- | :--- |
| `CMAKE_FIND_PACKAGE_NAME` | Ім'я пакета, яке зараз обробляється. |
| `<PackageName>_FIND_VERSION` | Повний запитаний рядок версії. |
| `<PackageName>_FIND_VERSION_EXACT` | `TRUE`, якщо користувач передав прапорець `EXACT`. |
| `<PackageName>_FIND_QUIETLY` | `TRUE`, якщо користувач передав прапорець `QUIET`. |
| `<PackageName>_FIND_REQUIRED` | `TRUE`, якщо користувач передав прапорець `REQUIRED`. |
| `<PackageName>_FIND_COMPONENTS` | Список усіх запитаних компонентів (і обов'язкових, і необов'язкових). |
| `<PackageName>_FIND_REQUIRED_<comp>` | `TRUE`, якщо компонент `<comp>` був переданий як обов'язковий. |

### 4.3. Результуючі змінні (вихідні змінні)

Після завершення виклику `find_package(<PackageName>)` встановлюються такі змінні в поточній області видимості:

| Змінна | Тип | Опис значення |
| :--- | :--- | :--- |
| `<PackageName>_FOUND` | `BOOLEAN` | `TRUE`, якщо пакет знайдено та всі обов'язкові компоненти й версія задовольняють вимогам; інакше `FALSE`. |
| `<PackageName>_VERSION` | `STRING` | Повний знайдений рядок версії (наприклад `1.2.4.10`). |
| `<PackageName>_VERSION_MAJOR` | `STRING` | Мажорний номер версії (`1`). |
| `<PackageName>_VERSION_MINOR` | `STRING` | Мінорний номер версії (`2`). |
| `<PackageName>_VERSION_PATCH` | `STRING` | Номер патчу (`4`). |
| `<PackageName>_VERSION_TWEAK` | `STRING` | Додатковий номер виправлення (`10`). |
| `<PackageName>_VERSION_COUNT` | `INTEGER` | Кількість компонентів у номері знайденої версії (від 1 до 4). |
| `<PackageName>_<Component>_FOUND` | `BOOLEAN` | Встановлюється для кожного компонента, переданого в `COMPONENTS` чи `OPTIONAL_COMPONENTS`. |
| `<PackageName>_CONFIG` | `FILEPATH` | Повний шлях до знайденого конфігураційного файла (тільки в Config Mode). |

---

## 5. Допоміжні команди пошуку артефактів (find_path, find_library, find_file)

Модулі пошуку `Find<PackageName>.cmake` будуються на базі низькорівневих команд виявлення файлів заголовків та бібліотечних файлів.

### 5.1. Сигнатура find_path

Шукає каталог, що містить вказаний заголовковий файл:

```cmake
find_path(<VAR>
          name | NAMES name1 [name2 ...]
          [HINTS path1 [path2 ...]]
          [PATHS path1 [path2 ...]]
          [PATH_SUFFIXES suffix1 [suffix2 ...]]
          [DOC "Короткий опис для кешу"]
          [NO_DEFAULT_PATH]
          [REQUIRED])
```

- Результат записується в кеш-змінну `<VAR>` типу `PATH`. Якщо файл знайдено за шляхом `/usr/include/foo/foo.h`, а шукалося `foo/foo.h`, змінна набуде значення `/usr/include`.
- Якщо файл не знайдено, змінна встановлюється у `<VAR>-NOTFOUND`.

### 5.2. Сигнатура find_library

Шукає файл компільованої статичної або динамічної бібліотеки:

```cmake
find_library(<VAR>
             name | NAMES name1 [name2 ...]
             [NAMES_PER_DIR]
             [HINTS path1 [path2 ...]]
             [PATHS path1 [path2 ...]]
             [PATH_SUFFIXES suffix1 [suffix2 ...]]
             [DOC "Опис для кешу"]
             [NO_DEFAULT_PATH]
             [REQUIRED])
```

- CMake автоматично додає до імені системні префікси (`lib`) та розширення (`.so`, `.a`, `.dylib`, `.lib`), виходячи з поточної цільової платформи.
- `NAMES_PER_DIR`: змінює черговість обходу: замість перевірки першого імені за всіма каталогами, CMake перевіряє всі альтернативні імена в межах одного каталогу перед переходом до наступного.

---

## 6. Інтерфейс макросу FindPackageHandleStandardArgs

Модуль `FindPackageHandleStandardArgs` забезпечує стандартизовану обробку результатів пошуку в сценаріях `Find<PackageName>.cmake`, формує інформаційні повідомлення про статус та автоматично перевіряє наявність усіх необхідних складових.

### 6.1. Сигнатура find_package_handle_standard_args

```cmake
include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(<PackageName>
    (DEFAULT_MSG | "Користувацьке повідомлення про помилку")
    REQUIRED_VARS <var1> [<var2>...]
    [VERSION_VAR <version_var>]
    [HANDLE_VERSION_RANGE]
    [HANDLE_COMPONENTS]
    [CONFIG_MODE]
    [NAME_MISMATCHED]
    [REASON_FAILURE_MESSAGE <reason_var>])
```

### 6.2. Параметри макросу

- `<PackageName>`: ім'я пакета. Має збігатися з іменем у виклику `find_package()`. Якщо назва не збігається, прапорець `NAME_MISMATCHED` дозволяє придушити попередження.
- `DEFAULT_MSG`: стандартний шаблон повідомлення: `Found <PackageName>: <var1> (found version "<version>")` або повідомлення про помилку з переліком відсутніх змінних.
- `REQUIRED_VARS <var1> [<var2>...]`: перелік обов'язкових змінних, які мають бути істинними (не порожніми і не `-NOTFOUND`), щоб пакет вважався знайденим. Зазвичай це `<PackageName>_LIBRARY` та `<PackageName>_INCLUDE_DIR`.
- `VERSION_VAR <version_var>`: ім'я змінної, що містить розібраний рядок версії. Макрос автоматично перевіряє її на сумісність із версією, запитаною користувачем у `find_package()`.
- `HANDLE_VERSION_RANGE`: вмикає підтримку діапазонів версій (CMake 3.19+).
- `HANDLE_COMPONENTS`: автоматично перевіряє змінні `<PackageName>_<Comp>_FOUND` для всіх компонентів, переданих у виклику `find_package()`, і генерує звіт про відсутні обов'язкові модулі.
- `CONFIG_MODE`: призначено для конфігураційних файлів виробника; перевіряє сумісність так само, як у Config Mode.
- `REASON_FAILURE_MESSAGE <reason_var>`: додатковий детальний опис причини відмови, якщо перевірка не пройшла.

---

## 7. Допоміжні модулі: SelectLibraryConfigurations та FindPackageMessage

### 7.1. Модуль SelectLibraryConfigurations

Під час написання `Find<PackageName>.cmake` на платформах із підтримкою окремих конфігурацій збірки (Windows / MSVC) часто знаходять окремо версію бібліотеки для Release і для Debug. Модуль `SelectLibraryConfigurations` об'єднує їх у єдину структуру генераторних виразів:

```cmake
include(SelectLibraryConfigurations)

# Очікує заповнені Foo_LIBRARY_RELEASE та Foo_LIBRARY_DEBUG
select_library_configurations(Foo)

# В результаті створює змінну Foo_LIBRARIES:
# optimized;<path_release>;debug;<path_debug>
# а також Foo_LIBRARY, що вказує на одну з них.
```

### 7.2. Модуль FindPackageMessage

Дозволяє друкувати повідомлення про знайдений пакет лише один раз за сесію конфігурації, запобігаючи спаму в консолі під час повторних запусків:

```cmake
include(FindPackageMessage)

find_package_message(Foo
    "Знайдено Foo: ${Foo_LIBRARIES} (версія ${Foo_VERSION})"
    "[${Foo_LIBRARIES}][${Foo_INCLUDE_DIRS}][${Foo_VERSION}]")
```

Рядок у квадратних дужках слугує кешованим відбитком стану: повідомлення друкується лише тоді, коли відбиток змінюється.

---

## 8. Допоміжні засоби створення конфігурацій (CMakePackageConfigHelpers)

Модуль `CMakePackageConfigHelpers` автоматизує генерацію двох критично важливих файлів: файла перевірки версії та головного переміщуваного конфігураційного файла.

### 8.1. Генерація файла версії: write_basic_package_version_file

```cmake
include(CMakePackageConfigHelpers)

write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/FooConfigVersion.cmake"
    VERSION "${PROJECT_VERSION}"
    COMPATIBILITY (AnyNewerVersion | SameMajorVersion | SameMinorVersion | ExactVersion)
    [ARCH_INDEPENDENT])
```

#### Режими сумісності (COMPATIBILITY)

- `AnyNewerVersion`: будь-яка версія, новіша або рівна за запитану, вважається сумісною. Підходить для повністю зворотно сумісних бібліотек або утиліт без суворого ABI.
- `SameMajorVersion`: семантичне версіонування (SemVer). Сумісною є будь-яка версія з тим самим мажорним номером `Major` і мінорним номером `Minor >= requested_minor`. Для версії `0.X.Y` вимагається точний збіг `Minor`.
- `SameMinorVersion`: сумісною є лише версія з тим самим мажорним і мінорним номером `Major.Minor` (наприклад `1.2.5` сумісна з `1.2.0`, але несумісна з `1.3.0`).
- `ExactVersion`: вимагається абсолютний збіг версії (до рівня `patch` або `tweak`).

#### Прапорець ARCH_INDEPENDENT

Якщо вказано `ARCH_INDEPENDENT`, згенерований файл версії не перевіряє розрядність архітектури (`CMAKE_SIZEOF_VOID_P`, 32 чи 64 біти). Це обов'язково для бібліотек із самих заголовків (header-only) або скриптових пакетів, які встановлюються у спільний каталог `share/cmake/`.

### 8.2. Генерація переміщуваного конфіга: configure_package_config_file

```cmake
configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/FooConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/FooConfig.cmake"
    INSTALL_DESTINATION "lib/cmake/Foo"
    [PATH_VARS var1 [var2...]]
    [NO_SET_AND_CHECK_MACRO]
    [NO_CHECK_REQUIRED_COMPONENTS_MACRO]
    [INSTALL_PREFIX <prefix>])
```

#### Макроси шаблону .cmake.in

У вхідному файлі шаблону обов'язково розміщують рядок `@PACKAGE_INIT@`. Під час конфігурації CMake замінює його на службовий код визначення відносного шляху встановлення та надає допоміжні макроси:

- `set_and_check(<var> <relative_path>)`: встановлює змінну шляху відносно поточного розташування конфігураційного файла та перевіряє, що вказаний каталог фізично існує на диску.
- `check_required_components(<PackageName>)`: перевіряє, чи всі обов'язкові компоненти, які замовив користувач, були успішно знайдені та завантажені, і встановлює `<PackageName>_FOUND` у `FALSE` у разі нестачі.

---

## 9. Транзитивні залежності у конфігураціях: CMakeFindDependencyMacro

Конфігураційний файл пакета не повинен викликати сирий `find_package()` для пошуку своїх залежностей, оскільки це призводить до втрати контексту (`QUIET`, `REQUIRED`) та засмічення області видимості. Замість цього використовується макрос `find_dependency()`.

### 9.1. Використання find_dependency

```cmake
include(CMakeFindDependencyMacro)

# Передаються ті самі аргументи, що й у find_package, крім QUIET та REQUIRED
find_dependency(OpenSSL 1.1.1)
find_dependency(ZLIB REQUIRED)
find_dependency(Threads)
```

### 9.2. Властивості макросу find_dependency

1. **Прокидання прапорців:** якщо вихідний виклик `find_package(Foo QUIET)` містив `QUIET`, усі виклики `find_dependency()` всередині `FooConfig.cmake` автоматично виконуються в режимі `QUIET`.
2. **Обробка помилок:** якщо залежність не знайдено, макрос негайно встановлює `<PackageName>_FOUND` у `FALSE`, записує зрозуміле діагностичне повідомлення у `<PackageName>_NOT_FOUND_MESSAGE` і виконує команду `return()`, припиняючи виконання поточного конфігураційного файла.

---

## 10. Властивості імпортованих цілей (IMPORTED Target Properties)

Імпортовані цілі (`add_library(<name> UNKNOWN IMPORTED)`), що створюються конфігураційними файлами або модулями пошуку, несуть набір властивостей, які передаються залежним цілям під час лінкування:

| Властивість цілі | Опис та призначення |
| :--- | :--- |
| `IMPORTED_LOCATION` | Повний шлях до скомпільованого бінарного файла бібліотеки (`.so`, `.dylib`, `.a`). |
| `IMPORTED_LOCATION_<CONFIG>` | Шлях до бінарного файла для конкретної конфігурації (наприклад `IMPORTED_LOCATION_RELEASE` або `IMPORTED_LOCATION_DEBUG`). |
| `IMPORTED_IMPLIB` | На платформі Windows: шлях до бібліотеки імпорту (`.lib`) для динамічної бібліотеки (`.dll`). |
| `IMPORTED_CONFIGURATIONS` | Список доступних конфігурацій збірки для цієї цілі (наприклад `RELEASE;DEBUG`). |
| `INTERFACE_INCLUDE_DIRECTORIES` | Шляхи до заголовкових файлів, які автоматично додаються до компілятора споживача через `-I` або `/I`. |
| `INTERFACE_COMPILE_DEFINITIONS` | Макроозначення препроцесора (`-DFOO_ENABLE_FEATURE`), що автоматично прокидаються споживачам. |
| `INTERFACE_COMPILE_OPTIONS` | Прапорці компілятора, необхідні для коректного вжитку заголовків бібліотеки. |
| `INTERFACE_LINK_LIBRARIES` | Транзитивні залежності: інші імпортовані цілі або прапорці лінкера (`-lpthread`, `-latomic`), які споживач має підтягнути автоматично. |
| `IMPORTED_NO_SONAME` | Вимикає перевірку внутрішнього поля `SONAME` для спільних бібліотек на Unix-подібних платформах. |

---

## 11. Узгодження конфігурацій збірки (Configuration Mapping)

Коли споживач збирає свій проєкт у конфігурації, відмінній від конфігурацій зібраного імпортованого пакета (наприклад, споживач збирає `RelWithDebInfo` або `MinSizeRel`, тоді як встановлений сторонній пакет має лише бінарні файли `Release`), CMake застосовує механізм зіставлення конфігурацій:

```cmake
# Глобальне зіставлення для всіх цілей проєкту:
# Якщо ціль не має конфігурації RelWithDebInfo, брати Release
set(CMAKE_MAP_IMPORTED_CONFIG_RELWITHDEBINFO Release "")

# Або налаштування на рівні конкретної імпортованої цілі:
set_target_properties(Foo::Core PROPERTIES
    MAP_IMPORTED_CONFIG_RELWITHDEBINFO "Release;Debug;"
    MAP_IMPORTED_CONFIG_MINSIZEREL "Release;"
)
```

Список конфігурацій у значенні властивості визначає пріоритет спадання: якщо першу вказану конфігурацію не знайдено, CMake перевіряє наступну. Порожній елемент у кінці списку дозволяє обрати будь-яку наявну конфігурацію як запасний варіант.

---

## 12. Реєстр пакетів CMake (Package Registry)

CMake підтримує механізм автоматичного виявлення пакетів, зібраних локально в дереві збірки без їх попереднього встановлення в системні каталоги (`make install`).

### 12.1. Користувацький реєстр пакетів (User Package Registry)

Команда `export(PACKAGE <PackageName>)` створює запис у домашньому каталозі користувача, який вказує безпосередньо на каталог збірки проєкту:

- **Linux / macOS:** файл `~/.cmake/packages/<PackageName>/<hash>`, де файл містить рядок із абсолютним шляхом до каталогу збірки.
- **Windows:** розділ системного реєстру `HKEY_CURRENT_USER\Software\Kitware\CMake\Packages\<PackageName>` із ключем, значенням якого є шлях до каталогу збірки.

Під час виклику `find_package(<PackageName>)` CMake перевіряє цей реєстр і може підтягнути конфігураційний файл безпосередньо з каталогу іншого проєкту. Якщо таку поведінку потрібно вимкнути, використовують прапорець `NO_CMAKE_PACKAGE_REGISTRY` або встановлюють змінну `CMAKE_FIND_USE_PACKAGE_REGISTRY` у `FALSE`.

### 12.2. Системний реєстр пакетів (System Package Registry)

Призначений для загальносистемних інсталяторів стороннього програмного забезпечення:

- **Linux / macOS:** каталог `/var/lib/cmake/packages/<PackageName>`.
- **Windows:** розділ `HKEY_LOCAL_MACHINE\Software\Kitware\CMake\Packages\<PackageName>`.

Вимикається прапорцем `NO_CMAKE_SYSTEM_PACKAGE_REGISTRY` або змінною `CMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY = FALSE`.

---

## 13. Перехоплення пошуку через Dependency Providers та FetchContent

Починаючи з версії CMake 3.24, у мові з'явився механізм перехоплення викликів `find_package()` за допомогою постачальників залежностей:

```cmake
# Реєстрація постачальника залежностей (викликається у файлі тулчейна)
cmake_language(SET_DEPENDENCY_PROVIDER my_custom_provider
               SUPPORTED_METHODS FIND_PACKAGE)

function(my_custom_provider method package_name)
    if(method STREQUAL "FIND_PACKAGE")
        message(STATUS "Перехоплено пошук пакета: ${package_name}")
        # Тут можна автоматично завантажити джерела через FetchContent
        # або підтягнути бінарні пакети через зовнішній менеджер
    endif()
endfunction()
```

Якщо під час виклику `find_package()` передано прапорець `BYPASS_PROVIDER`, зареєстрований постачальник ігнорується, і CMake виконує стандартний алгоритм пошуку у файловій системі.

Також модуль `FetchContent` надає інтеграцію з `find_package()` через механізм перенаправлення `CMAKE_FIND_PACKAGE_REDIRECTS_DIR`: якщо залежність завантажена й зібрана як підпроєкт через `FetchContent_MakeAvailable(foo)`, наступні виклики `find_package(foo)` у сторонніх підкаталогах автоматично задовольняються згенерованим псевдоконфігом, не звертаючись до системи.

---

## 14. Ключові політики CMake, пов'язані з пошуком пакетів

Поведінка `find_package` еволюціонувала в різних версіях CMake і контролюється спеціальними політиками (Policies):

| Політика | Версія | Суть та призначення |
| :--- | :--- | :--- |
| `CMP0074` | 3.12 | Використання змінних `<PackageName>_ROOT` та `ENV{<PackageName>_ROOT}` як префіксів найвищого пріоритету. У старій поведінці `OLD` ці змінні ігнорувалися. |
| `CMP0144` | 3.27 | Використання верхнього регістру `<PACKAGENAME>_ROOT` у пошуку префіксів. |
| `CMP0017` | 2.8.4 | Надає пріоритет файлам із `CMAKE_ROOT/Modules` над файлами в проєкті для внутрішніх модулів CMake, запобігаючи випадковому перехопленню базових сценаріїв. |
| `CMP0057` | 3.3 | Підтримка оператора `IN_LIST` у командах `if()`, що спрощує перевірку переданих компонентів усередині сценаріїв пошуку. |
| `CMP0148` | 3.27 | Вилучення застарілих модулів `FindPythonInterp` та `FindPythonLibs` на користь єдиного сучасного модуля `FindPython3`. |
