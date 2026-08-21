# 📋 Довідник методів, атрибутів та команд Conan 2.x

У розробці пакетів для екосистеми Conan 2.x рецепт `conanfile.py` є самостійною програмою мовою Python, що визначає клас, успадкований від `conan.ConanFile`. Рушій пакетного менеджера викликає методи цього класу у строго визначені моменти життєвого циклу обчислення графа залежностей.

На відміну від статичних файлів конфігурації у форматі JSON чи YAML, об'єктна модель Python надає розробнику можливість динамічно адаптувати структуру збірки до операційної системи, архітектури процесора, версії компілятора та нестандартних опцій цільової платформи.

Нижче наведено вичерпний технічний опис декларативних полів, методів життєвого циклу, структури контракту `cpp_info`, архітектури компонентів та інтерфейсу командного рядка утиліти `conan`.

## Декларативні атрибути класу ConanFile

Атрибути верхнього рівня класу `ConanFile` визначають статичні метадані пакета, доступну комбінаторну матрицю платформних налаштувань, опції користувача та правила експорту файлів.

| Атрибут | Тип | Обов'язковий | Призначення |
| :--- | :--- | :--- | :--- |
| `name` | `str` | Так (для бібліотек) | Унікальне ім'я пакета у нижньому регістрі. Дозволено символи ASCII, цифри, дефіси, крапки та підкреслення. |
| `version` | `str` | Так (або `set_version()`) | Версія пакета за правилами семантичного версіонування SemVer (наприклад, `"1.4.2"` або `"2.0.0-rc1"`). |
| `license` | `str` | Ні | Стандартизований ідентифікатор ліцензії SPDX або назва ліцензійної угоди (наприклад, `"MIT"`, `"Apache-2.0"`). |
| `author` | `str` | Ні | Контактні дані розробника або відповідальної інженерної команди (`"Ім'я <email@company.internal>"`). |
| `url` | `str` | Ні | Посилання на репозиторій версій самого рецепта Conan. |
| `homepage` | `str` | Ні | Офіційний вебсайт або репозиторій вихідного коду оригінальної бібліотеки чи утиліти. |
| `description` | `str` | Ні | Короткий опис функціонального призначення та можливостей бібліотеки. |
| `topics` | `tuple[str]` | Ні | Список тегів для індексації, класифікації та швидкого пошуку пакета в реєстрах. |
| `package_type` | `str` | Так (у Conan 2.x) | Тип створюваного артефакту: `"library"`, `"static-library"`, `"shared-library"`, `"header-library"`, `"application"`, `"build-scripts"`, `"python-require"`. |
| `settings` | `tuple[str]` | Ні | Кортеж вхідних параметрів платформи: `("os", "arch", "compiler", "build_type")`. Безпосередньо впливають на обчислення `package_id`. |
| `options` | `dict[str, list]` | Ні | Словник доступних опцій збірки та списку їхніх допустимих значень: `{"shared": [True, False], "fPIC": [True, False]}`. |
| `default_options` | `dict[str, Any]` | Ні | Словник значень опцій за замовчуванням: `{"shared": False, "fPIC": True}`. |
| `generators` | `tuple[str]` | Ні | Список генераторів файлів конфігурації за замовчуванням: `("CMakeToolchain", "CMakeDeps")`. |
| `exports_sources`| `str` / `tuple` | Ні | Шаблони імен файлів джерел, що експортуються разом із рецептом: `("CMakeLists.txt", "src/*", "include/*")`. |
| `no_copy_source` | `bool` | Ні | Оптимізація: забороняє копіювання вихідного коду в проміжну папку збірки, якщо система збірки підтримує out-of-source компіляцію. |

### Семантика поля package_type

Поле `package_type` у версії Conan 2.x грає критичну роль у розрахунку графа: воно повідомляє генераторам `CMakeDeps`, `PkgConfigDeps` та `VirtualBuildEnv`, як саме слід підключати артефакт.

- `"application"`: створює виконуваний двійковий файл. Conan автоматично експортує каталог `bin/` у системну змінну `PATH` середовища виконання, але забороняє підключення цього пакета як бібліотеки через `target_link_libraries`.
- `"static-library"` та `"shared-library"`: явно визначають тип бінарного зв'язування, керуючи необхідністю прапорця `-fPIC` та правилами транзитивного поширення прапорців лінкера.
- `"header-library"`: позначає бібліотеку без скомпільованих двійкових об'єктів. Автоматично очищує налаштування компілятора під час обчислення `package_id`.
- `"build-scripts"` / `"python-require"`: спеціалізовані пакети для повторного використання спільних допоміжних скриптів або базових класів рецептів Python.

## Методи життєвого циклу рецепта

Життєвий цикл рецепта розбитий на ізольовані кроки. Кожен метод має суворо окреслену зону відповідальності і виконується рушієм лише тоді, коли граф залежностей переходить у відповідну фазу.

### 1. Методи динамічної ідентифікації

Ці методи викликаються найпершими, ще до того, як Conan почне аналізувати налаштування платформи та розраховувати залежності. Вони дозволяють динамічно зчитувати номер версії з тегів системи контролю версій Git або службових файлів репозиторію.

```python
def set_name(self):
    """Динамічне визначення імені пакета перед побудовою графа."""
    self.name = "distributed_telemetry"

def set_version(self):
    """Динамічне зчитування версії з файлу версії або системних змінних."""
    from conan.tools.files import load
    import os
    version_file = os.path.join(self.recipe_folder, "version.txt")
    if os.path.exists(version_file):
        self.version = load(self, version_file).strip()
    else:
        self.version = "0.1.0-dev"
```

### 2. Методи конфігурації, опцій та валідації

Методи цієї групи відповідають за узгодження комбінаторної матриці параметрів. Вони видаляють непідтримувані опції, налаштовують значення за замовчуванням залежно від платформи та перевіряють мінімальні вимоги до компілятора.

```python
def config_options(self):
    """Коригування доступності опцій до побудови графа."""
    # На операційній системі Windows код завжди позиційно-незалежний, прапорець fPIC не має сенсу
    if self.settings.os == "Windows":
        self.options.rm_safe("fPIC")

def configure(self):
    """Встановлення взаємозв'язків між опціями та видалення зайвих налаштувань."""
    if self.options.get_safe("shared"):
        # Для динамічних бібліотек на Linux прапорець fPIC є обов'язковим
        self.options.rm_safe("fPIC")
    
    # Якщо бібліотека є чистою реалізацією на мові C, налаштування стандартної бібліотеки C++ не потрібне
    if self.package_type == "shared-library":
        self.settings.rm_safe("compiler.libcxx")

def validate(self):
    """Перевірка сумісності конфігурації. Викликається для кожного вузла графа."""
    from conan.errors import ConanInvalidConfiguration
    from conan.tools.scm import Version

    # Заборона збірки застарілими компіляторами
    if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "11":
        raise ConanInvalidConfiguration("Цей пакет вимагає компілятор GCC 11 або новіший для підтримки концептів C++20")
    
    # Перевірка конфліктних комбінацій опцій
    if self.settings.os == "Windows" and self.options.get_safe("shared") and self.settings.compiler.get_safe("runtime") == "MT":
        raise ConanInvalidConfiguration("Динамічна бібліотека на Windows не може використовувати статичний рантайм /MT")
```

### 3. Метод структурування каталогів (layout)

Метод `layout()` є фундаментальним нововведенням Conan 2.x. Він декларує фізичне розташування каталогів вихідного коду, тимчасових об'єктних файлів збірки, згенерованих файлів конфігурацій та кінцевого пакета.

```python
def layout(self):
    """Стандартизація просторової структури файлів."""
    from conan.tools.cmake import cmake_layout
    # cmake_layout автоматично налаштовує підкаталоги з урахуванням багатоконфігураційних генераторів (Visual Studio, Xcode)
    cmake_layout(self, src_folder=".", build_folder="build")
```

Після виконання методу `layout()` стають доступними такі простори імен шляхів:
- `self.folders.source` — абсолютний або відносний шлях до каталогу з вихідним кодом проєкту;
- `self.folders.build` — каталог, де система збірки розміщує скомпільовані об'єктні файли `.o`/`.obj`;
- `self.folders.generators` — каталог, куди записуються файли `*Config.cmake` та `conan_toolchain.cmake`;
- `self.folders.package` — каталог фінальних встановлених файлів бібліотеки;
- `self.cpp.source.includedirs` — шляхи до заголовків у джерельному дереві для режиму прямого редагування (editable packages);
- `self.cpp.build.libdirs` — шляхи до скомпільованих бібліотек до виконання фази пакування.

### 4. Оголошення залежностей (requirements та build_requirements)

У Conan 2.x усі залежності суворо розділені за контекстами виконання: цільові бібліотеки (Host Context) та інструменти середовища компіляції (Build Context).

```python
def requirements(self):
    """Оголошення бібліотек, які лінкуються у фінальний продукт (Host Context)."""
    # transitive_headers=True означає, що публічні заголовки цього пакета містять #include <fmt/core.h>
    self.requires("fmt/10.2.1", transitive_headers=True)
    
    # transitive_libs=True передає лінкеру вимогу лінкувати openssl усім кінцевим споживачам
    self.requires("openssl/3.2.0", transitive_headers=True, transitive_libs=True)

    if self.options.get_safe("with_compression", True):
        self.requires("zlib/1.3.1")

def build_requirements(self):
    """Оголошення інструментів, що мають виконуватися на хост-машині збірки (Build Context)."""
    # Системи збірки та компілятори
    self.tool_requires("cmake/[>=3.25]")
    self.tool_requires("ninja/1.11.1")
    
    # Генератори коду (виконуються на хості збірки)
    self.tool_requires("protobuf/3.21.12")
    
    # Фреймворки модульного тестування (не потрапляють у граф кінцевих користувачів)
    self.test_requires("gtest/1.14.0")
```

### 5. Завантаження вихідного коду (source)

Метод `source()` завантажує вихідний код із зовнішніх джерел. Він викликається рівно один раз для кожної нової ревізії рецепта, а завантажені файли зберігаються в каталозі джерел локального кешу і залишаються доступними для всіх наступних бінарних збірок під різні платформи.

```python
def source(self):
    """Отримання офіційного архіву вихідних текстів або клонування репозиторію."""
    from conan.tools.files import get, patch
    
    get(self,
        url=f"https://github.com/example/libnetwork/archive/v{self.version}.tar.gz",
        sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        strip_root=True)
    
    # Застосування виправлень за потреби
    if os.path.exists("patches/fix-arm-build.patch"):
        patch(self, patch_file="patches/fix-arm-build.patch")
```

### 6. Генерація інтеграційних конфігурацій (generate)

Метод `generate()` запускається безпосередньо перед початком компіляції. Його завдання — створити файли опису оточення для конкретної системи збірки споживача або бібліотеки.

```python
def generate(self):
    """Створення файлів CMakeToolchain, CMakeDeps та змінних середовища."""
    from conan.tools.cmake import CMakeToolchain, CMakeDeps
    from conan.tools.env import VirtualBuildEnv, VirtualRunEnv

    # Створення conan_toolchain.cmake із точними прапорцями компілятора
    tc = CMakeToolchain(self)
    tc.variables["BUILD_TESTS"] = False
    tc.variables["ENABLE_CUSTOM_ALLOCATOR"] = True
    tc.generate()

    # Створення <Pkg>Config.cmake файлів для всіх знайдених requirements
    deps = CMakeDeps(self)
    deps.generate()

    # Експорт змінних середовища для запуску інструментів з tool_requires (наприклад, protoc)
    build_env = VirtualBuildEnv(self)
    build_env.generate()
```

### 7. Компіляція та пакування артефактів (build та package)

```python
def build(self):
    """Конфігурація та компіляція бібліотеки через виклики системи збірки."""
    from conan.tools.cmake import CMake
    cmake = CMake(self)
    cmake.configure()
    cmake.build()

def package(self):
    """Копіювання зібраних заголовків, бібліотек та ліцензій у package_folder."""
    from conan.tools.cmake import CMake
    from conan.tools.files import copy
    import os

    cmake = CMake(self)
    cmake.install()
    
    # Обов'язкове ліцензійне очищення: збереження юридичних умов ліцензії в пакеті
    copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
```

### 8. Опис контракту для споживачів (package_info)

Метод `package_info()` є єдиним джерелом правди про те, як зовнішні споживачі мають компонувати скомпільовану бібліотеку. Інформація, записана в об'єкт `self.cpp_info`, транслюється генераторами `CMakeDeps` або `PkgConfigDeps` у цілі CMake (`target_link_libraries`) чи файли `.pc`.

```python
def package_info(self):
    """Оголошення експортованих бібліотек, прапорців та CMake-цілей."""
    self.cpp_info.libs = ["network_core", "network_crypto"]
    self.cpp_info.includedirs = ["include"]
    self.cpp_info.libdirs = ["lib"]
    self.cpp_info.defines = ["NETWORK_ENGINE_STATIC=1"]
    
    # Канонічне ім'я файлу конфігурації: find_package(NetworkEngine CONFIG REQUIRED)
    self.cpp_info.set_property("cmake_file_name", "NetworkEngine")
    
    # Канонічне ім'я імпортованої цілі: NetworkEngine::NetworkEngine
    self.cpp_info.set_property("cmake_target_name", "NetworkEngine::NetworkEngine")

    # Системні бібліотеки цільової операційної системи
    if self.settings.os in ["Linux", "FreeBSD"]:
        self.cpp_info.system_libs = ["pthread", "dl", "rt", "m"]
    elif self.settings.os == "Windows":
        self.cpp_info.system_libs = ["ws2_32", "crypt32", "secur32"]
    elif self.settings.os == "Macos":
        self.cpp_info.frameworks = ["CoreFoundation", "Security"]
```

## Архітектура компонентів у self.cpp_info

Якщо бібліотека складається з декількох модулів, які можуть використовуватися окремо (наприклад, як бібліотека OpenSSL надає `OpenSSL::Crypto` та `OpenSSL::SSL`, або як Boost розбитий на десятки підбібліотек), Conan 2.x надає механізм компонентів:

```python
def package_info(self):
    self.cpp_info.set_property("cmake_file_name", "OpenSSL")

    # Компонент криптографії
    self.cpp_info.components["crypto"].libs = ["crypto"]
    self.cpp_info.components["crypto"].set_property("cmake_target_name", "OpenSSL::Crypto")
    if self.settings.os in ["Linux", "FreeBSD"]:
        self.cpp_info.components["crypto"].system_libs = ["dl", "pthread"]

    # Компонент SSL, що залежить від внутрішнього компонента crypto
    self.cpp_info.components["ssl"].libs = ["ssl"]
    self.cpp_info.components["ssl"].requires = ["crypto"]
    self.cpp_info.components["ssl"].set_property("cmake_target_name", "OpenSSL::SSL")
```

Генератор `CMakeDeps` автоматично транслює компоненти в окремі імпортовані цілі CMake із правильними зв'язками між ними, дозволяючи споживачу лінкувати тільки необхідну частину бібліотеки без затягування зайвих залежностей.

## Керування системним оточенням (VirtualBuildEnv та VirtualRunEnv)

Conan 2.x автоматично ізолює змінні оточення процесів збірки. Коли пакет оголошує `tool_requires` (наприклад, інструмент генерації коду або нову версію CMake), генератор `VirtualBuildEnv` створює набір командних сценаріїв:
- `conanbuild.sh` / `conanbuild.bat`: додає каталоги `bin/` інструментів збірки у початок системної змінної `PATH`.
- `deactivate_conanbuild.sh` / `deactivate_conanbuild.bat`: відновлює вихідний стан змінних оточення після завершення компіляції.

Для запуску тестів або локальних виконуваних файлів генератор `VirtualRunEnv` створює файли `conanrun.sh` / `conanrun.bat`, які коректно налаштовують змінні динамічного завантажувача бібліотек: `LD_LIBRARY_PATH` у Linux, `DYLD_LIBRARY_PATH` у macOS та `PATH` у Windows, запобігаючи помилкам відсутності динамічних бібліотек `.so`/`.dll` під час виконання.

Також доступний механізм взаємодії з системними пакетними менеджерами операційної системи через клас `SystemPackageTool`. Якщо бібліотека потребує низькорівневих системних заголовків ядра (наприклад, `libudev-dev` чи `libasound2-dev` у дистрибутивах Debian/Ubuntu), метод `system_requirements()` може автоматично викликати системний пакувальник перед початком збірки.

## Довідник атрибутів об'єкта cpp_info

Об'єкт `self.cpp_info` надає деталізоване керування всіма аспектами лінкування та компіляції споживачів.

| Поле `cpp_info` | Тип | Значення за замовчуванням | Опис |
| :--- | :--- | :--- | :--- |
| `libs` | `list[str]` | `[]` | Список імен бібліотечних файлів без префікса `lib` та розширення (наприклад, `["ssl", "crypto"]`). |
| `includedirs` | `list[str]` | `["include"]` | Шляхи до каталогів заголовкових файлів відносно `package_folder`. |
| `libdirs` | `list[str]` | `["lib"]` | Каталоги розташування статичних або імпортних бібліотек. |
| `bindirs` | `list[str]` | `["bin"]` | Каталоги виконуваних файлів та динамічних бібліотек на Windows (`.dll`). |
| `defines` | `list[str]` | `[]` | Препроцесорні макроозначення, які споживач отримує автоматично. |
| `cflags` | `list[str]` | `[]` | Додаткові прапорці компілятора мови C. |
| `cxxflags` | `list[str]` | `[]` | Додаткові прапорці компілятора мови C++. |
| `sharedlinkflags`| `list[str]` | `[]` | Прапорці лінкування динамічних бібліотек. |
| `exelinkflags` | `list[str]` | `[]` | Прапорці лінкування виконуваних файлів. |
| `system_libs` | `list[str]` | `[]` | Системні бібліотеки ОС, які лінкер має додати автоматично (`pthread`, `ws2_32`). |
| `frameworks` | `list[str]` | `[]` | Системні фреймворки macOS/iOS (`CoreFoundation`, `Security`). |
| `components` | `dict` | `{}` | Словник ізольованих компонентів пакета (наприклад, `OpenSSL::Crypto` та `OpenSSL::SSL`). |

## Інтерфейс командного рядка Conan 2.x

Утиліта `conan` надає розгалужений CLI для повного керування графом, кешем, профілями та віддаленими репозиторіями.

| Команда | Основні прапорці | Призначення |
| :--- | :--- | :--- |
| `conan install <path>` | `--profile:host=<p>`, `--profile:build=<p>`, `--build=missing`, `--lockfile=<file>`, `-o <pkg:opt=val>` | Обчислення графа, завантаження бінарників та запуск генераторів (`CMakeDeps`, `CMakeToolchain`). |
| `conan create <path>` | `--profile:host=<p>`, `--profile:build=<p>`, `--build=missing`, `--test-folder=<dir>` | Повний цикл: завантаження джерел, збірка, пакування у локальний кеш та запуск валідаційного пакета `test_package`. |
| `conan build <path>` | `--profile:host=<p>`, `--profile:build=<p>`, `--source-folder=<dir>`, `--build-folder=<dir>` | Локальна збірка коду пакета в поточному робочому каталозі розробника без експорту в кеш. |
| `conan graph info <path>` | `--profile:host=<p>`, `--profile:build=<p>`, `--format=html/json` | Діагностика графа: візуалізація дерева залежностей, обчислених `package_id` та конфліктів версій. |
| `conan profile detect` | `--force` | Автоматичне виявлення встановленого компілятора та створення базового профілю `default`. |
| `conan profile show` | `--profile=<p>` | Відображення налаштувань, опцій та змінних конфігурації зазначеного файлу профілю. |
| `conan remote add <name> <url>` | `--index=<n>`, `--force` | Додавання нового віддаленого сервера пакетів (ConanCenter, корпоративний JFrog Artifactory). |
| `conan remote list` | — | Список усіх підключених віддалених репозиторіїв та їхнього пріоритету опитування. |
| `conan remote login <name> <user>` | `-p <password>` | Аутентифікація в захищеному корпоративному сховищі пакетів. |
| `conan upload <pkg/ver>` | `-r <remote>`, `--all`, `--confirm`, `--check` | Завантаження рецептів та зібраних бінарних пакетів із локального кешу на віддалений сервер. |
| `conan lock create <path>` | `--profile:host=<p>`, `--profile:build=<p>`, `--lockfile-out=<file>` | Генерація файлу фіксації графа `conan.lock` із точними версіями, RREV та PREV. |
| `conan editable add <path> <pkg/ver>` | — | Реєстрація пакета в режимі редагування: залежні проєкти беруть джерела та бінарники напряму з робочої папки. |
| `conan editable remove <pkg/ver>` | — | Вимкнення режиму редагування для зазначеного пакета. |
| `conan cache clean` | `*` | Очищення тимчасових папок збірок та невикористовуваних завантажень у кеші `~/.conan2/p/`. |
