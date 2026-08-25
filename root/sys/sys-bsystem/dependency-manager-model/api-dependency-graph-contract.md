# 📋 Специфікація контрактів маніфестів, профілів та генераторів

Цей документ визначає формальні структури даних, правила синтаксичного розбору та семантичні контракти, за якими менеджери пакетів C++ (Conan, vcpkg) описують вимоги до залежностей, конфігурують тулчейни компіляції та транслюють розв'язані графи у властивості імпортованих цілей CMake й дескриптори `pkg-config`.

Будь-яка система керування залежностями в C++ функціонує як транслятор між трьома шарами абстракції:
1. **Шар декларації проєкту (Маніфест):** фіксує імена бібліотек, допустимі версійні обмеження та опціональні прапорці можливостей.
2. **Шар контексту компіляції (Профіль та триплет):** задає точні параметри цільової платформи, тип стандартної бібліотеки, режим рантайму та інструменти збірки.
3. **Шар споживання у системі збірки (Контракт генератора):** перетворює фізичні шляхи на диску у стандартизовані імпортовані цілі системи збірки з точним розмежуванням публічних та приватних вимог використання.

---

## 1. Специфікація маніфестів: vcpkg.json та conanfile

Менеджери пакунків C++ підтримують декларативні маніфести двох форматів: стандартизований документ JSON (`vcpkg.json`) та скриптовий маніфест мовою Python (`conanfile.py`) або спрощений текстовий формат (`conanfile.txt`).

### Специфікація схеми vcpkg.json

Маніфестний режим vcpkg (англ. *vcpkg manifest mode*) використовує кореневий файл `vcpkg.json`, який перевіряється на відповідність офіційній схемі JSON Schema.

```json
{
  "$schema": "https://raw.githubusercontent.com/microsoft/vcpkg-tool/main/docs/vcpkg.json.schema.json",
  "name": "network-telemetry-engine",
  "version-semver": "2.4.1",
  "description": "Високопродуктивний сервіс збору метрик мережевого трафіку",
  "builtin-baseline": "3425a812850a58a74e2d3b2b4129bbd27976e185",
  "dependencies": [
    "fmt",
    {
      "name": "boost-asio",
      "features": ["ssl"]
    },
    {
      "name": "openssl",
      "version>=": "3.1.0"
    }
  ],
  "features": {
    "profiling": {
      "description": "Інструменти трасування та збору статистики продуктивності",
      "dependencies": ["gperftools"]
    }
  }
}
```

#### Семантика полів маніфесту vcpkg.json

* **`name`** (тип `string`, обов'язкове): унікальний ідентифікатор проєкту в реєстрі. Повинен містити лише малі літери латинського алфавіту, цифри та дефіси.
* **`version-semver`** / **`version`** / **`version-date`** (тип `string`, обов'язкове одне з трьох): схема версіонування пакета. Для бібліотек зі стандартним семантичним версіонуванням використовується `version-semver` (формат `X.Y.Z`). Для бібліотек, що версіонуються за датами релізів, використовується `version-date` (`YYYY-MM-DD`). Для довільних рядкових версій застосовується `version`.
* **`builtin-baseline`** (тип `string`, рекомендоване): точний 40-символьний Git-хеш коміту в офіційному репозиторії портів Microsoft vcpkg. Наявність цього поля гарантує, що на будь-якій машині розробника чи CI-сервері менеджер використає абсолютно ідентичні версії рецептів портів.
* **`dependencies`** (тип `array`): перелік прямих залежностей проєкту. Елементами масиву можуть бути як прості рядки з назвами бібліотек (`"fmt"`), так і об'єкти з розширеними властивостями:
  * **`name`**: назва пакета.
  * **`version>=`**: обмеження мінімальної версії. Якщо інша транзитивна залежність вимагає старішу версію, vcpkg автоматично оновить пакет до версії, що задовольняє найжорсткіше обмеження `version>=`.
  * **`features`**: масив назв опціональних компонентів (можливостей), які необхідно зібрати всередині даного пакета (наприклад, увімкнення підтримки SSL для `boost-asio`).
  * **`default-features`** (тип `boolean`, за замовчуванням `true`): чи слід активувати стандартні компоненти, передбачені автором порту.
  * **`platform`** (тип `string`): логічний вираз платформного фільтра (наприклад, `"(windows & x64) | linux"`). Залежність встановлюється лише тоді, коли цільовий триплет задовольняє вираз.
* **`features`** (тип `object`): словник опціональних функцій власного проєкту. Кожна функція містить поле `description` та власний масив `dependencies`, що дозволяє збирати важкі сторонні бібліотеки лише за потреби.

---

### Специфікація маніфесту conanfile.py

Файл `conanfile.py` є повноцінним класом на мові Python, успадкованим від `conan.ConanFile`. Він визначає повний життєвий цикл пакета від опису графа до конфігурації компіляції.

```python
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy

class TelemetryEngineConan(ConanFile):
    name = "network-telemetry-engine"
    version = "2.4.1"
    package_type = "application"

    # Параметри конфігурації двійкового середовища
    settings = "os", "arch", "compiler", "build_type"
    
    # Користувацькі опції та значення за замовчуванням
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": True
    }

    def config_options(self):
        # На платформі Windows позиційно-незалежний код не має сенсу
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def layout(self):
        # Стандартизована структура каталогів для збірки CMake
        cmake_layout(self)

    def requirements(self):
        # Оголошення прямих бібліотечних залежностей
        self.requires("fmt/10.1.1")
        if self.options.with_ssl:
            self.requires("openssl/3.1.4", transitive_headers=True)

    def build_requirements(self):
        # Інструменти, необхідні виключно на етапі збірки на машині-хості
        self.tool_requires("cmake/3.28.1")
        self.tool_requires("ninja/1.11.1")

    def generate(self):
        # Генерація файлів інтеграції для системи збірки
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
```

#### Семантика методів життєвого циклу рецепта Conan

* **`requirements(self)`**: оголошення зв'язків графа. Метод `self.requires()` приймає версійні діапазони та трейти залежностей (англ. *package traits*):
  * `transitive_headers=True`: заголовки залежності потрапляють у публічний інтерфейс поточної бібліотеки й транслюються споживачам вищого рівня.
  * `transitive_libs=True`: необхідність транзитивного компонування бінарного файлу.
  * `headers=True` / `libs=True`: базовий дозвіл на використання заголовків та скомпільованих файлів.
* **`build_requirements(self)`**: інструменти збірки (`tool_requires`), які компілюються або завантажуються для архітектури хоста (`Build Context`), а не для цільового пристрою (`Host Context`).
* **`generate(self)`**: створення файлів зв'язку (`CMakeDeps`, `CMakeToolchain`, `PkgConfigDeps`). Цей метод виконується після розв'язання повного графа й записує дескриптори в каталог генерації збірки.

---

## 2. Контракт профілів збірки та триплетів

Профіль визначає стан апаратної платформи та тулчейна компіляції. Без профілю менеджер пакетів не має змоги обчислити двійкову сумісність або згенерувати правильні прапорці компілятора.

### Специфікація Conan Profile (`[settings]`, `[options]`, `[buildenv]`)

Профіль Conan є текстовим файлом у форматі INI, розділеним на чотири функціональні секції:

```ini
[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=13
compiler.cppstd=gnu20
compiler.libcxx=libstdc++11
build_type=Release

[options]
*:shared=False
*:fPIC=True
openssl/*:no_asm=False

[tool_requires]
cmake/3.28.1

[buildenv]
CC=/usr/bin/gcc-13
CXX=/usr/bin/g++-13
CFLAGS=-O3 -march=native
CXXFLAGS=-O3 -march=native -Wall
```

#### Правила валідації налаштувань у профілі

1. **Ієрархія підключів компілятора:** налаштування `compiler.libcxx` є обов'язковим для компіляторів `gcc`, `clang` та `apple-clang`. Для `gcc` допустимими є значення `libstdc++` (старе C++03 ABI) та `libstdc++11` (нове C++11 Dual ABI). Для `clang` допустимими є `libstdc++11` та `libc++`.
2. **Моделі рантайму MSVC:** якщо обрано `compiler=msvc`, замість `compiler.libcxx` використовується налаштування `compiler.runtime` зі значеннями `dynamic` або `static`, та `compiler.runtime_type` зі значеннями `Release` або `Debug`.
3. **Шаблони опцій:** синтаксис `*:shared=False` встановлює статичне компонування для всіх вузлів графа. Шаблон `openssl/*:no_asm=True` перевизначає опцію виключно для пакета `openssl` незалежно від його версії.

---

### Специфікація vcpkg Triplet

Триплет vcpkg є сценарієм на мові CMake, який розташовується у каталозі `triplets/` або `triplets/community/` і визначає глобальні змінні цільового середовища:

```cmake
# x64-linux-custom.cmake
set(VCPKG_TARGET_ARCHITECTURE x64)
set(VCPKG_CRT_LINKAGE dynamic)
set(VCPKG_LIBRARY_LINKAGE static)
set(VCPKG_CMAKE_SYSTEM_NAME Linux)
set(VCPKG_BUILD_TYPE release)

# Додаткові прапорці компілятора для захисту пам'яті
set(VCPKG_C_FLAGS "-fstack-protector-strong -D_FORTIFY_SOURCE=2")
set(VCPKG_CXX_FLAGS "-fstack-protector-strong -D_FORTIFY_SOURCE=2")
```

#### Ключові змінні триплета vcpkg

* **`VCPKG_TARGET_ARCHITECTURE`**: архітектура цільового процесора (`x86`, `x64`, `arm`, `arm64`, `wasm32`).
* **`VCPKG_CRT_LINKAGE`**: зв'язування з бібліотекою C Runtime (`dynamic` або `static`).
* **`VCPKG_LIBRARY_LINKAGE`**: тип вихідних бібліотек портів (`static` для `.a`/`.lib`, `dynamic` для `.so`/`.dll`).
* **`VCPKG_CMAKE_SYSTEM_NAME`**: системне ім'я операційної системи (`Linux`, `Windows`, `Darwin`, `Android`, `Generic` для систем реального часу).

---

## 3. Контракт імпортованих цілей CMake (Imported Targets)

Генератори (`CMakeDeps` у Conan або механізм `vcpkg.cmake`) транслюють встановлені пакети у конфігураційні файли виду `<Package>Config.cmake` та `<Package>Targets.cmake`.

Усі створені цілі реєструються як глобальні імпортовані цілі (`add_library(Package::Target UNKNOWN IMPORTED GLOBAL)`). Вони інкапсулюють повний набір властивостей використання:

```cmake
# Приклад згенерованого файлу fmt-targets-release.cmake
add_library(fmt::fmt STATIC IMPORTED GLOBAL)

set_target_properties(fmt::fmt PROPERTIES
    IMPORTED_LOCATION_RELEASE "/home/user/.conan2/p/pkg_4a91c78e3b1290ff/p/lib/libfmt.a"
    INTERFACE_INCLUDE_DIRECTORIES "/home/user/.conan2/p/pkg_4a91c78e3b1290ff/p/include"
    INTERFACE_COMPILE_DEFINITIONS "FMT_SHARED=0"
    INTERFACE_COMPILE_FEATURES "cxx_std_17"
    INTERFACE_LINK_LIBRARIES "m"
)
```

### Специфікація властивостей цілей CMake

| Властивість цілі CMake | Тип значення | Семантичний контракт та поведінка |
| :--- | :--- | :--- |
| **`IMPORTED_LOCATION`** / **`IMPORTED_LOCATION_<CONFIG>`** | `FILEPATH` | Абсолютний шлях до двійкового файлу бібліотеки (`.a`, `.so`, `.lib`, `.dylib`) для конкретної конфігурації збірки (`RELEASE`, `DEBUG`). |
| **`IMPORTED_IMPLIB_<CONFIG>`** | `FILEPATH` | На платформі Windows: шлях до бібліотеки імпорту (`.lib`), яка передається лінкувальнику під час збирання з динамічною бібліотекою `.dll`. |
| **`INTERFACE_INCLUDE_DIRECTORIES`** | `LIST(PATH)` | Шляхи до заголовочних файлів бібліотеки. Автоматично додаються компілятору як прапорці `-I` під час компіляції цілей-споживачів. |
| **`INTERFACE_COMPILE_DEFINITIONS`** | `LIST(STRING)` | Препроцесорні макроси (наприклад, `SPDLOG_COMPILED_LIB`), які автоматично передаються споживачам як `-D...`. |
| **`INTERFACE_COMPILE_OPTIONS`** | `LIST(STRING)` | Специфічні прапорці компілятора (наприклад, `-pthread`, `-fexceptions`, `-municode`). |
| **`INTERFACE_COMPILE_FEATURES`** | `LIST(STRING)` | Мінімальні вимоги до стандарту мови C++ (наприклад, `cxx_std_20`). Якщо споживач використовує старіший стандарт, CMake автоматично підвищить стандарт збірки. |
| **`INTERFACE_LINK_LIBRARIES`** | `LIST(TARGET/LIB)` | Список прямих транзитивних залежностей (інших імпортованих цілей `Dependency::Target` або системних бібліотек, як-от `pthread`, `dl`, `ws2_32`). |

---

## 4. Контракт дескрипторів Pkg-Config (`.pc`)

Для середовищ, які не використовують CMake (проєкти на базі GNU Make, Autotools, Meson або кастомні конвеєри), генератори створюють дескриптори стандарту `pkg-config`:

```ini
prefix=/home/user/.conan2/p/pkg_4a91c78e3b1290ff/p
exec_prefix=${prefix}
libdir=${prefix}/lib
includedir=${prefix}/include

Name: fmt
Description: Small, safe and fast formatting library for C++
Version: 10.1.1
Requires:
Requires.private:
Libs: -L${libdir} -lfmt
Libs.private: -lm
Cflags: -I${includedir} -DFMT_SHARED=0
```

### Правила обробки полів у pkg-config

1. **`Libs` проти `Libs.private`:** прапорці, вказані у полі `Libs`, передаються лінкувальнику завжди. Прапорці з поля `Libs.private` (наприклад, системні бібліотеки `-lm`, `-lpthread`) передаються лінкувальнику виключно у режимі статичного компонування (під час виклику `pkg-config --static --libs fmt`). Це запобігає засміченню списку лінкування зайвими транзитивними залежностями під час використання динамічних бібліотек.
2. **`Requires` проти `Requires.private`:** аналогічно, транзитивні пакети, вказані в `Requires.private`, завантажуються парсером `pkg-config` лише у режимі статичної збірки, розгортаючи повне дерево транзитивних залежностей без ручного перелічення кожної бібліотеки.
3. **Релокація префікса (`pc_sysrootdir`):** шляхи у файлі `.pc` повинні формуватися через змінну `${prefix}`. Під час крос-компіляції утиліта `pkg-config` автоматично підставляє шлях до цільового `sysroot` через параметр `--define-prefix`, запобігаючи використанню абсолютних шляхів хостової системи.
