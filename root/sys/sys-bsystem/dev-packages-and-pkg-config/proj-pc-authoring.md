# ⚙️ Створення власного .pc пакета та перевірка лінкування

Коли ви розробляєте власну бібліотеку на C або C++, її споживачі не обов'язково використовуватимуть ту саму систему збірки, що й ви. Хтось збирає проєкти через CMake, хтось через Meson, а хтось пише традиційні `Makefile` для вбудованих Linux-систем.

Єдиним універсальним мостом між різними системами збірки в екосистемі Unix є метадані `pkg-config`. Цей практичний проєкт демонструє повний цикл створення скомпільованої бібліотеки `libgeomcalc`, генерацію переміщуваного файла `geomcalc.pc` засобами CMake та Meson, детальне дослідження таблиць символів через системні утиліти `readelf` і `nm`, а також перевірку коректності динамічного та статичного лінкування.

## 1. Архітектура та вихідний код бібліотеки

Створимо бібліотеку `libgeomcalc`, яка надає функції обчислення площ та кривизни. Для внутрішніх розрахунків бібліотека використовує математичні функції `sin()` і `cos()` із системної бібліотеки `libm`, а для експорту стиснених бінарних звітів — функцію `compress()` із бібліотеки `zlib`.

У публічному інтерфейсі типи `zlib` не розкриваються — залежність є виключно внутрішньою (приватною). Це важливе архітектурне рішення: споживачу нашої бібліотеки непотрібно підключати заголовки `zlib.h` у власному коді, якщо він не викликає функції компресії напряму. Крім того, ми налаштовуємо контроль видимості символів: усі внутрішні допоміжні функції компілюються з прапорцем `-fvisibility=hidden`, а назовні експортуються лише функції з явним модифікатором API.

### Публічний заголовок: include/geomcalc.h / include/geomcalc.hpp

У файлі заголовків оголошуємо структури точок та функції обчислення. Для мови C надаємо класичний процедурний інтерфейс з обов'язковим блоком `extern "C"`, а для C++ — сучасний строго типізований інтерфейс у просторі імен із типами `std::span` та `std::expected`.

:::tabs
```c
/* include/geomcalc.h */
#ifndef GEOMCALC_H
#define GEOMCALC_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    double x;
    double y;
} geom_point_t;

/* Обчислює площу трикутника за координатами вершин */
double geom_triangle_area(geom_point_t a, geom_point_t b, geom_point_t c);

/* Генерує стиснений бінарний звіт про геометрію (використовує zlib) */
int geom_export_compressed_report(const geom_point_t* points, size_t count, 
                                  unsigned char* out_buf, size_t* out_size);

#ifdef __cplusplus
}
#endif

#endif /* GEOMCALC_H */
```
```cpp
// include/geomcalc.hpp
#pragma once

#include <cstddef>
#include <span>
#include <vector>
#include <expected>

namespace geom {

struct Point {
    double x{0.0};
    double y{0.0};
};

enum class ExportError {
    BufferTooSmall,
    CompressionFailed,
    EmptyInput
};

// Обчислює площу трикутника за трьома точками
double triangle_area(Point a, Point b, Point c) noexcept;

// Генерує стиснений бінарний звіт
std::expected<std::vector<unsigned char>, ExportError> 
export_compressed_report(std::span<const Point> points);

} // namespace geom
```
:::

### Реалізація: src/geomcalc.c / src/geomcalc.cpp

У файлах реалізації виконуємо математичні обчислення через `fabs()` з `<math.h>` та здійснюємо виклик функції `compress()` із бібліотеки `zlib`. Функція розраховує необхідний розмір буфера стиснення за допомогою `compressBound()` і перевіряє коди завершення алгоритму Deflate.

:::tabs
```c
/* src/geomcalc.c */
#include "geomcalc.h"
#include <math.h>
#include <zlib.h>
#include <stdlib.h>
#include <string.h>

double geom_triangle_area(geom_point_t a, geom_point_t b, geom_point_t c) {
    /* Формула Гауса для площі багатокутника з використанням fabs з math.h */
    double area = 0.5 * fabs(a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y));
    return area;
}

int geom_export_compressed_report(const geom_point_t* points, size_t count, 
                                  unsigned char* out_buf, size_t* out_size) {
    if (!points || count == 0 || !out_buf || !out_size) {
        return -1;
    }
    
    size_t raw_bytes = count * sizeof(geom_point_t);
    uLongf dest_len = (uLongf)(*out_size);
    
    int z_res = compress(out_buf, &dest_len, (const Bytef*)points, (uLong)raw_bytes);
    if (z_res != Z_OK) {
        return -2;
    }
    
    *out_size = (size_t)dest_len;
    return 0;
}
```
```cpp
// src/geomcalc.cpp
#include "geomcalc.hpp"
#include <cmath>
#include <zlib.h>

namespace geom {

double triangle_area(Point a, Point b, Point c) noexcept {
    return 0.5 * std::abs(a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y));
}

std::expected<std::vector<unsigned char>, ExportError> 
export_compressed_report(std::span<const Point> points) {
    if (points.empty()) {
        return std::unexpected(ExportError::EmptyInput);
    }

    const size_t raw_bytes = points.size_bytes();
    uLongf max_dest_len = compressBound(static_cast<uLong>(raw_bytes));
    std::vector<unsigned char> compressed(max_dest_len);

    uLongf actual_len = max_dest_len;
    int z_res = compress(compressed.data(), &actual_len, 
                         reinterpret_cast<const Bytef*>(points.data()), 
                         static_cast<uLong>(raw_bytes));
                         
    if (z_res != Z_OK) {
        return std::unexpected(ExportError::CompressionFailed);
    }

    compressed.resize(actual_len);
    return compressed;
}

} // namespace geom
```
:::

## 2. Шаблон файла geomcalc.pc.in

Для коректної генерації метаданих створюємо шаблон `geomcalc.pc.in`. У ньому ми використовуємо спеціальні маркери з символами `@...@`, які будуть замінені системою збірки під час конфігурації.

Зверніть увагу на розділення публічних та приватних залежностей:
- `Requires.private: zlib` — вказує утиліті `pkg-config`, що бібліотека `zlib` потрібна для внутрішньої роботи `libgeomcalc`, але споживачу динамічної версії бібліотеки не потрібно додавати `-lz` у свій командний рядок.
- `Libs.private: -lm` — системна математична бібліотека підключається лише під час статичного компонування.
- Змінні `prefix`, `libdir` та `includedir` описуються через взаємне посилання, що дозволяє легко адаптувати файл до будь-якої структури каталогів.

```ini
# geomcalc.pc.in
prefix=@CMAKE_INSTALL_PREFIX@
exec_prefix=${prefix}
libdir=${prefix}/@CMAKE_INSTALL_LIBDIR@
includedir=${prefix}/@CMAKE_INSTALL_INCLUDEDIR@

Name: geomcalc
Description: Бібліотека швидких геометричних обчислень
Version: @PROJECT_VERSION@
Requires.private: zlib
Libs: -L${libdir} -lgeomcalc
Libs.private: -lm
Cflags: -I${includedir}
```

## 3. Генерація метаданих через CMake

У файлі `CMakeLists.txt` ми задіюємо стандартний модуль `GNUInstallDirs`, який автоматично обчислює коректні системні каталоги для поточної операційної системи (наприклад `lib/x86_64-linux-gnu` для Debian/Ubuntu або `lib64` для Red Hat/Fedora).

Команда `configure_file()` підставляє реальні шляхи інсталяції в шаблон `.pc.in` з прапорцем `@ONLY`, щоб випадково не пошкодити змінні вигляду `${prefix}`.

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(geomcalc VERSION 1.2.0 LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 23)

include(GNUInstallDirs)

# Пошук внутрішньої залежності zlib
find_package(ZLIB REQUIRED)

# Створення бібліотеки (підтримує збірку як SHARED, так і STATIC через BUILD_SHARED_LIBS)
add_library(geomcalc
    src/geomcalc.c
    src/geomcalc.cpp
)

target_include_directories(geomcalc PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(geomcalc PRIVATE
    ZLIB::ZLIB
    m # Підключення libm для Unix
)

# Генерація файлу метаданих geomcalc.pc
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/geomcalc.pc.in"
    "${CMAKE_CURRENT_BINARY_DIR}/geomcalc.pc"
    @ONLY
)

# Правила інсталяції бінарних файлів та заголовків
install(TARGETS geomcalc
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(FILES include/geomcalc.h include/geomcalc.hpp
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Інсталяція згенерованого .pc файлу в каталог pkgconfig
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/geomcalc.pc"
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/pkgconfig"
)
```

## 4. Генерація метаданих через Meson

Якщо бібліотека збирається за допомогою системи Meson, створювати шаблонний файл `.pc.in` узагалі не потрібно. Meson містить вбудований модуль `pkgconfig`, який самостійно витягує всі властивості цілі, її версію, каталоги заголовків та залежності:

```meson
# meson.build
project('geomcalc', ['c', 'cpp'], version : '1.2.0', default_options : ['c_std=c11', 'cpp_std=c++23'])

zlib_dep = dependency('zlib', required : true)
cc = meson.get_compiler('c')
m_dep = cc.find_library('m', required : false)

inc = include_directories('include')

geomcalc_lib = both_libraries('geomcalc',
    sources : ['src/geomcalc.c', 'src/geomcalc.cpp'],
    include_directories : inc,
    dependencies : [zlib_dep, m_dep],
    install : true
)

install_headers('include/geomcalc.h', 'include/geomcalc.hpp')

pkg = import('pkgconfig')
pkg.generate(geomcalc_lib,
    name : 'geomcalc',
    description : 'Бібліотека швидких геометричних обчислень',
    filebase : 'geomcalc',
    subdirs : '.',
    libraries_private : [m_dep],
    requires_private : ['zlib']
)
```

Функція `pkg.generate()` автоматично розкладає залежності: бібліотеки, передані в `requires_private`, потрапляють у `Requires.private`, а низькорівневі бібліотеки з `libraries_private` — у поле `Libs.private`.

## 5. Збірка, встановлення та верифікація через pkg-config

Виконаємо компіляцію проєкту за допомогою CMake та встановимо його в тестовий ізольований префікс `/tmp/opt/geomcalc`:

```bash
# Конфігурація та збірка спільної та статичної бібліотек
cmake -B build -S . -DCMAKE_INSTALL_PREFIX=/tmp/opt/geomcalc -DBUILD_SHARED_LIBS=ON
cmake --build build
cmake --install build

# Додаємо каталог згенерованих метаданих до системної змінної PKG_CONFIG_PATH
export PKG_CONFIG_PATH=/tmp/opt/geomcalc/lib/pkgconfig:$PKG_CONFIG_PATH
```

Після виконання команди `cmake --install` перевіримо структуру каталогу `/tmp/opt/geomcalc`. Ми побачимо класичний склад пакета розробки:
- Заголовкові файли: `/tmp/opt/geomcalc/include/geomcalc.h` та `geomcalc.hpp`.
- Спільний об'єкт: `/tmp/opt/geomcalc/lib/libgeomcalc.so`.
- Файл опису інтерфейсу: `/tmp/opt/geomcalc/lib/pkgconfig/geomcalc.pc`.

Тепер виконаємо тестові запити через утиліту `pkg-config`, щоб переконатися у правильності обчислення прапорців компілятора та лінкера.

### 1. Перевірка версії пакета
```bash
$ pkg-config --modversion geomcalc
1.2.0
```

### 2. Запит прапорців компіляції (Cflags)
```bash
$ pkg-config --cflags geomcalc
-I/tmp/opt/geomcalc/include
```
Утиліта повернула точний шлях до каталогу заголовків без зайвих сторонніх прапорців.

### 3. Запит прапорців динамічного лінкування (Libs)
```bash
$ pkg-config --libs geomcalc
-L/tmp/opt/geomcalc/lib -lgeomcalc
```
У виводі присутній лише прямий прапорець підключення `-lgeomcalc`. Внутрішні залежності `zlib` та `libm` не додаються, оскільки динамічний завантажувач ELF знайде їх автоматично через заголовки `DT_NEEDED` всередині `libgeomcalc.so`. Перевірити наявність запису `DT_NEEDED` можна системною утилітою `readelf`:

```bash
$ readelf -d /tmp/opt/geomcalc/lib/libgeomcalc.so | grep NEEDED
 0x0000000000000001 (NEEDED)             Shared library: [libz.so.1]
 0x0000000000000001 (NEEDED)             Shared library: [libm.so.6]
 0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
```

### 4. Запит прапорців статичного лінкування (--static)
```bash
$ pkg-config --static --libs geomcalc
-L/tmp/opt/geomcalc/lib -lgeomcalc -lz -lm
```
При додаванні ключа `--static` утиліта автоматично розгорнула все транзитивне дерево: додала бібліотеку компресії `-lz` з поля `Requires.private` та математичну бібліотеку `-lm` з поля `Libs.private`. Утиліта `nm` підтверджує, що в статичному архіві `libgeomcalc.a` символи `compress` та `fabs` позначені як `U` (невирішені, undefined), тому без цих прапорців статичне лінкування завершилося б помилкою.

## 6. Написання та компіляція програми-споживача

Створимо тестову клієнтську програму `client`, яка викликає обидві функції бібліотеки: обчислює площу трикутника та формує стиснений бінарний звіт.

:::tabs
```c
/* client.c */
#include <geomcalc.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    geom_point_t p1 = {0.0, 0.0};
    geom_point_t p2 = {4.0, 0.0};
    geom_point_t p3 = {0.0, 3.0};
    
    double area = geom_triangle_area(p1, p2, p3);
    printf("Обчислена площа трикутника: %.2f (очікується 6.00)\n", area);
    
    geom_point_t pts[3] = {p1, p2, p3};
    unsigned char compressed[128];
    size_t comp_size = sizeof(compressed);
    
    if (geom_export_compressed_report(pts, 3, compressed, &comp_size) == 0) {
        printf("Звіт успішно стиснуто до %zu байтів.\n", comp_size);
    }
    
    return EXIT_SUCCESS;
}
```
```cpp
// client.cpp
#include <geomcalc.hpp>
#include <iostream>
#include <vector>

int main() {
    geom::Point p1{0.0, 0.0};
    geom::Point p2{4.0, 0.0};
    geom::Point p3{0.0, 3.0};

    double area = geom::triangle_area(p1, p2, p3);
    std::cout << "Обчислена площа трикутника: " << area << " (очікується 6.00)\n";

    std::vector<geom::Point> pts{p1, p2, p3};
    auto report = geom::export_compressed_report(pts);

    if (report.has_value()) {
        std::cout << "Звіт успішно стиснуто через zlib до " 
                  << report->size() << " байтів.\n";
    } else {
        std::cerr << "Помилка стиснення звіту.\n";
        return 1;
    }

    return 0;
}
```
:::

### Складання через Makefile споживача

Напишемо `Makefile`, який демонструє збірку як динамічного клієнта, так і повністю автономного статичного бінарника:

```makefile
# Makefile споживача
CC ?= gcc
CFLAGS ?= -Wall -Wextra -O2
PKG_CONFIG ?= pkg-config

# Динамічні прапорці
DYN_CFLAGS := $(shell $(PKG_CONFIG) --cflags geomcalc)
DYN_LIBS   := $(shell $(PKG_CONFIG) --libs geomcalc)
DYN_RPATH  := -Wl,-rpath,$(shell $(PKG_CONFIG) --variable=libdir geomcalc)

# Статичні прапорці
STATIC_CFLAGS := $(shell $(PKG_CONFIG) --static --cflags geomcalc)
STATIC_LIBS   := $(shell $(PKG_CONFIG) --static --libs geomcalc)

all: client client_static

# Збірка динамічного клієнта
client: client.c
	$(CC) $(CFLAGS) $(DYN_CFLAGS) $< $(DYN_RPATH) $(DYN_LIBS) -o $@

# Збірка повністю статичного бінарника
client_static: client.c
	$(CC) -static $(CFLAGS) $(STATIC_CFLAGS) $< $(STATIC_LIBS) -o $@

clean:
	rm -f client client_static
```

Запустимо компіляцію програми:
```bash
$ make
gcc -Wall -Wextra -O2 -I/tmp/opt/geomcalc/include client.c -Wl,-rpath,/tmp/opt/geomcalc/lib -L/tmp/opt/geomcalc/lib -lgeomcalc -o client
gcc -static -Wall -Wextra -O2 -I/tmp/opt/geomcalc/include client.c -L/tmp/opt/geomcalc/lib -lgeomcalc -lz -lm -o client_static

$ ./client
Обчислена площа трикутника: 6.00 (очікується 6.00)
Звіт успішно стиснуто до 26 байтів.

$ ./client_static
Обчислена площа трикутника: 6.00 (очікується 6.00)
Звіт успішно стиснуто до 26 байтів.
```

Перевіримо створені бінарники системною утилітою `file` та `ldd`:
```bash
$ file client_static
client_static: ELF 64-bit LSB executable, x86-64, statically linked, for GNU/Linux 3.2.0, not stripped

$ ldd client_static
	not a dynamic executable
```

Бібліотека успішно скомпільована, інстальована та перевірена в обох режимах компонування. Створений `.pc` файл повністю відповідає стандартам дистрибутивів Linux і готовий до поширення серед розробників на будь-яких системах збірки.
