# ⚙️ Практика вендорингу: побудова hermetic-пайплайну в CMake з патчами та ізоляцією

У цій практичній роботі реалізовано повний інженерний конвеєр вендорингу сторонніх бібліотек у проєкті на C та C++ під керуванням CMake. Конвеєр забезпечує 100% герметичність збірки (можливість компіляції в повністю ізольованому air-gapped середовищі без доступу до зовнішньої мережі Інтернет), автоматичне накладання локальних патчів та ізоляцію глобального простору імен цілей.

---

## 1. Постановка інженерної задачі

Розробляється вбудований сервіс збору та стиснення телеметрії `telemetry_node`. Архітектура проєкту має задовольняти чотири фундаментальні інженерні вимоги:

1. **Повна автономність файлового дерева:** вихідні тексти всіх зовнішніх компонентів зберігаються безпосередньо у репозиторії проєкту в каталозі `third_party/`. Збірка не повинна залежати від наявності зовнішніх утиліт (Conan, vcpkg) або мережевих з'єднань під час фази конфігурації.
2. **Ізоляція діагностики компілятора:** власні файли проєкту компілюються з найсуворішим рівнем перевірки (`-Wall -Wextra -Wpedantic -Werror` для компіляторів GCC/Clang або `/W4 /WX` для MSVC). Проте сторонній код, що містить застарілі синтаксичні конструкції або неявні перетворення типів C, не повинен призводити до аварійної зупинки збірки.
3. **Захист від колізій імен цілей у CMake:** усі сторонні бібліотеки повинні надавати стандартизовані псевдоніми цілей із простором імен виду `Vendor::<Name>`.
4. **Підтримка локальних патчів під цільову платформу:** якщо стороння бібліотека вимагає виправлень для роботи на специфічній вбудованій архітектурі, ці виправлення повинні зберігатися у вигляді версіонованих файлів `.patch` та автоматично накатуватися під час оновлення версії бібліотеки.

### Файлова структура проєкту

```text
telemetry_service/
├── CMakeLists.txt
├── patches/
│   └── 0001-tinyxml2-disable-warnings.patch
├── scripts/
│   └── vendor-sync.sh
├── src/
│   ├── main.c
│   └── main.cpp
└── third_party/
    ├── CMakeLists.txt
    ├── miniz/
    │   ├── miniz.c
    │   └── miniz.h
    └── tinyxml2/
        ├── CMakeLists.txt
        ├── tinyxml2.cpp
        └── tinyxml2.h
```

---

## 2. Скрипт синхронізації та оновлення залежностей

Скрипт `scripts/vendor-sync.sh` автоматизує процес завантаження чистих вихідних текстів бібліотек з офіційних релізів, очищення від непотрібного баласту (документації, тестів, бінарних ассетів) та накладання локальних патчів.

```bash
#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
THIRD_PARTY_DIR="${PROJECT_ROOT}/third_party"
PATCHES_DIR="${PROJECT_ROOT}/patches"

echo "[1/3] Оновлення бібліотеки TinyXML2..."
TINYXML2_TAG="10.0.0"
TINYXML2_DIR="${THIRD_PARTY_DIR}/tinyxml2"
rm -rf "${TINYXML2_DIR}"

# Завантажуємо чистий стан релізу з глибиною 1
git clone --depth 1 --branch "${TINYXML2_TAG}" https://github.com/leethomason/tinyxml2.git "${TINYXML2_DIR}"

# Очищуємо каталог від службових файлів Git, документації та важких тестів
rm -rf "${TINYXML2_DIR}/.git" "${TINYXML2_DIR}/docs" "${TINYXML2_DIR}/test"

# Накладання локального патчу за наявності
if [ -f "${PATCHES_DIR}/0001-tinyxml2-disable-warnings.patch" ]; then
    echo "  -> Накладання локального патчу на TinyXML2..."
    git -C "${PROJECT_ROOT}" apply --directory="third_party/tinyxml2" "${PATCHES_DIR}/0001-tinyxml2-disable-warnings.patch"
fi

echo "[2/3] Оновлення однофайлової бібліотеки Miniz (C-джерело та заголовок)..."
MINIZ_TAG="3.0.2"
MINIZ_DIR="${THIRD_PARTY_DIR}/miniz"
mkdir -p "${MINIZ_DIR}"
curl -sSL "https://raw.githubusercontent.com/richgel999/miniz/${MINIZ_TAG}/miniz.c" -o "${MINIZ_DIR}/miniz.c"
curl -sSL "https://raw.githubusercontent.com/richgel999/miniz/${MINIZ_TAG}/miniz.h" -o "${MINIZ_DIR}/miniz.h"

echo "[3/3] Синхронізацію завершено успішно. Усі файли зафіксовано в каталозі third_party/."
```

### Анатомія роботи скрипта синхронізації

1. **Клонування з `--depth 1`:** завантажує виключно цільовий реліз без багаторічної історії комітів, що скорочує час виконання до кількох секунд.
2. **Видалення службового каталогу `.git`:** усуває ризик випадкового перетворення каталогу на неініціалізований підмодуль Git, що зламало б індексування файлів батьківським репозиторієм.
3. **Застосування `git apply --directory`:** дозволяє накладати патчі з єдиного каталогу `patches/` відносно кореня проєкту, зберігаючи повну історію модифікацій під контролем версій. Якщо накладання патчу завершується конфліктом, скрипт негайно зупиняється завдяки прапорцю `set -e`, сигналізуючи інженеру про несумісність нової версії коду.

---

## 3. Модуль ізоляції third_party/CMakeLists.txt

Файл `third_party/CMakeLists.txt` відіграє роль захисного архітектурного бар'єра. Він керує підключенням як бібліотек із власними скриптами збірки (TinyXML2), так і бібліотек, що складаються з сирих C-файлів без власного `CMakeLists.txt` (Miniz).

```cmake
# third_party/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

# Політика CMP0077: локальні змінні set() перемагають чужі option() без FORCE
if(POLICY CMP0077)
    cmake_policy(SET CMP0077 NEW)
endif()

# 1. Попереднє перекриття опцій кешу стороннього підпроєкту
set(BUILD_TESTS OFF)
set(BUILD_TESTING OFF)
set(TINYXML2_BUILD_TESTING OFF)
set(BUILD_SHARED_LIBS OFF)

# 2. Підключення бібліотеки TinyXML2
# EXCLUDE_FROM_ALL: відсікає всі сторонні цілі від дефолтної збірки all
# SYSTEM: позначає відкриті заголовки як системні (-isystem), придушуючи попередження
add_subdirectory(tinyxml2 EXCLUDE_FROM_ALL SYSTEM)

# Створюємо стандартизований псевдонім простору імен, якщо бібліотека його не створила
if(TARGET tinyxml2 AND NOT TARGET Vendor::TinyXML2)
    add_library(Vendor::TinyXML2 ALIAS tinyxml2)
endif()

# 3. Підключення Miniz (чисті C-файли без власного CMakeLists.txt)
# Створюємо власну статичну ціль з інкапсульованими вимогами вжитку
add_library(miniz_static STATIC
    "${CMAKE_CURRENT_SOURCE_DIR}/miniz/miniz.c"
)

# Експортуємо системні каталоги заголовків для споживачів
target_include_directories(miniz_static
    SYSTEM PUBLIC
        "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/miniz>"
)

# Вимикаємо діагностику компілятора для старої кодової бази C
if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(miniz_static PRIVATE -w)
elseif(MSVC)
    target_compile_options(miniz_static PRIVATE /w)
endif()

# Реєструємо псевдонім простору імен
add_library(Vendor::Miniz ALIAS miniz_static)
```

### Інженерне обґрунтування застосованих директив

* **Політика `CMP0077`:** у стані `NEW` дозволяє звичайній локальній команді `set(TINYXML2_BUILD_TESTING OFF)` автоматично перевизначити команду `option(TINYXML2_BUILD_TESTING ... ON)` усередині чужого файлу без необхідності небезпечного запису у файл глобального кешу з модифікатором `FORCE`.
* **Флаг `EXCLUDE_FROM_ALL`:** гарантує, що допоміжні цілі підпроєкту (наприклад, тестові утиліти) не компілюватимуться під час виклику команди `cmake --build build`.
* **Модифікатор `SYSTEM`:** автоматично транслює відкриті каталоги заголовків цілей через прапорець `-isystem` замість `-I`, наказуючи препроцесору придушувати всі діагностичні попередження компілятора у чужих файлах.
* **Генераторний вираз `$<BUILD_INTERFACE:...>`:** обмежує видимість каталогу включення виключно деревом збірки проєкту, запобігаючи витоку некоректних абсолютних шляхів під час генерації пакетів інсталяції.

### Керування транзитивними залежностями вендореного коду

Якщо одна вендорена бібліотека залежить від іншої (наприклад, власний парсер залежить від вендореного `miniz`), зв'язок між ними описується суворо через псевдоніми цілей:

```cmake
# Внутрішній зв'язок між вендореними компонентами
target_link_libraries(Vendor::TinyXML2 PRIVATE Vendor::Miniz)
```

Специфікатор `PRIVATE` інкапсулює заголовки `miniz` усередині реалізації `tinyxml2`, запобігаючи неконтрольованому витоку внутрішніх типів у головну програму.

---

## 4. Кореневий файл конфігурації CMakeLists.txt

Головний файл проєкту описує правила складання цільового бінарного образу та активує максимальний рівень суворості компілятора для власного коду.

```cmake
# Головний CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(telemetry_service LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Вмикаємо суворі прапорці якості коду для ВЛАСНИХ файлів проєкту
if(MSVC)
    add_compile_options(/W4 /WX)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -Werror)
endif()

# Включаємо вендорений каталог
add_subdirectory(third_party)

# Головний бінарний виконуваний файл
add_executable(telemetry_node
    src/main.cpp
)

# Лінкуємося виключно до псевдонімів простору імен
target_link_libraries(telemetry_node
    PRIVATE
        Vendor::TinyXML2
        Vendor::Miniz
)
```

---

## 5. Вихідний код програми

:::tabs
@tab C
```c
/* src/main.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "miniz.h"

int main(void) {
    const char *payload = "<telemetry version=\"1.0\"><sensor id=\"temp\" val=\"24.5\"/></telemetry>";
    size_t payload_len = strlen(payload);

    uLong bound_len = compressBound((uLong)payload_len);
    unsigned char *compressed = (unsigned char *)malloc(bound_len);
    if (!compressed) {
        fprintf(stderr, "Помилка виділення пам'яті під буфер стиснення\n");
        return 1;
    }

    uLong comp_len = bound_len;
    int status = compress(compressed, &comp_len, (const unsigned char *)payload, (uLong)payload_len);
    if (status != Z_OK) {
        fprintf(stderr, "Помилка стиснення даних: %d\n", status);
        free(compressed);
        return 1;
    }

    printf("Розмір початковий: %zu байтів, розмір стиснений: %lu байтів\n", payload_len, comp_len);
    free(compressed);
    return 0;
}
```
@tab C++
```cpp
// src/main.cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <memory>
#include <tinyxml2.h>
#include "miniz.h"

int main() {
    constexpr std::string_view raw_xml = 
        "<telemetry version=\"1.0\">\n"
        "    <sensor name=\"temperature\" value=\"24.5\" unit=\"celsius\"/>\n"
        "    <sensor name=\"pressure\" value=\"1013.25\" unit=\"hPa\"/>\n"
        "</telemetry>";

    tinyxml2::XMLDocument doc;
    const tinyxml2::XMLError err = doc.Parse(raw_xml.data(), raw_xml.size());
    if (err != tinyxml2::XML_SUCCESS) {
        std::cerr << "Помилка розбору XML: " << doc.ErrorStr() << "\n";
        return 1;
    }

    const auto* root = doc.FirstChildElement("telemetry");
    if (!root) {
        std::cerr << "Відсутній кореневий елемент telemetry\n";
        return 1;
    }

    std::cout << "Успішно розібрано пакет телеметрії версії: " 
              << root->Attribute("version") << "\n";

    // Демонстрація стиснення через вендорений Miniz
    const uLong bound = compressBound(static_cast<uLong>(raw_xml.size()));
    std::vector<unsigned char> compressed_buffer(bound);
    uLong compressed_size = bound;

    const int status = compress(
        compressed_buffer.data(),
        &compressed_size,
        reinterpret_cast<const unsigned char*>(raw_xml.data()),
        static_cast<uLong>(raw_xml.size())
    );

    if (status != Z_OK) {
        std::cerr << "Помилка стиснення: " << status << "\n";
        return 1;
    }

    compressed_buffer.resize(compressed_size);
    std::cout << "Стиснено: " << raw_xml.size() << " байтів -> " 
              << compressed_buffer.size() << " байтів.\n";

    return 0;
}
```
:::

---

## 6. Перевірка герметичності та практичні рекомендації

Для верифікації герметичності на машині розробника або в конвеєрі CI рекомендується виконати тестовий запуск у повністю ізольованому оточенні:

```bash
# Симуляція air-gapped середовища без доступу до Інтернету
# 1. Створення каталогу збірки
cmake -B build -S . -G Ninja

# 2. Компіляція бінарного виконуваного файлу
cmake --build build --config Release

# 3. Запуск верифікаційного тесту
./build/telemetry_node
```

### Підводні камені під час експлуатації:

1. **Конфлікти інсталяції (`install()`):**
   Якщо стороння бібліотека містить директиви `install(TARGETS ... EXPORT ...)`, виклик команди `cmake --install build` скопіює чужі файли у загальний каталог інсталяції програми. Використання прапорця `EXCLUDE_FROM_ALL` у виклику `add_subdirectory()` запобігає включенню інсталяційних правил підпроєкту до загальної цілі інсталяції.
2. **Абсолютні шляхи у `CMAKE_SOURCE_DIR`:**
   Якщо чужий `CMakeLists.txt` звертається до власних заголовків через `${CMAKE_SOURCE_DIR}/include` замість `${CMAKE_CURRENT_SOURCE_DIR}/include`, скрипт впаде під час вкладення в підкаталог `third_party/`. Такі скрипти вимагають обов'язкового накладання патчу або заміни на чистий мінімальний файл опису цілі.
3. **Глобальний стан змінної `BUILD_SHARED_LIBS`:**
   Вендорені статичні бібліотеки повинні явно вказувати ключове слово `STATIC` у виклику `add_library()`. Це захищає проєкт від випадкового перетворення внутрішніх залежностей на спільні динамічні бібліотеки (`.so` / `.dll`), якщо у кореневому проєкті випадково буде встановлено `set(BUILD_SHARED_LIBS ON)`.
4. **Скидання налаштувань компілятора у підпроєктах:**
   Деякі застарілі сторонні скрипти виконують `set(CMAKE_CXX_FLAGS "...")`, перезаписуючи системні прапорці. У сучасному CMake такі конструкції замінюють на виклики `target_compile_options()`, що ізолює специфічні прапорці в межах конкретної цілі та унеможливлює пошкодження параметрів компіляції батьківського проєкту.
5. **Розрив сумісності ABI через різні стандарти C++:**
   Якщо сторонній підпроєкт не задає вимогу стандарту `target_compile_features(lib PUBLIC cxx_std_20)`, а компілюється зі старішим стандартом C++14, передавання стандартних типів (наприклад, `std::string_view` або `std::span`) через межу інтерфейсу бібліотеки може призвести до помилок компіляції. Завжди контролюйте транзитивні вимоги стандарту мови для кожної імпортованої цілі.
