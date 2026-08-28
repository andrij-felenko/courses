# ⚙️ Створення власного .pc пакета та перевірка лінкування

Коли ви розробляєте власну бібліотеку на C або C++, її споживачі не обов'язково використовуватимуть ту саму систему збірки, що й ви. Хтось збирає проєкти через CMake, хтось через Meson, а хтось пише традиційні `Makefile` для вбудованих Linux-систем.

Єдиним універсальним мостом між різними системами збірки в екосистемі Unix є метадані `pkg-config`. Цей практичний проєкт демонструє повний цикл створення скомпільованої бібліотеки `libgeomcalc`, генерацію переміщуваного файла `geomcalc.pc` засобами CMake та Meson, детальне дослідження таблиць символів через системні утиліти `readelf` і `nm`, а також перевірку коректності динамічного та статичного лінкування.

## 1. Архітектура та вихідний код бібліотеки

Створимо бібліотеку `libgeomcalc`, яка надає функції обчислення площ та кривизни. Для внутрішніх розрахунків бібліотека використовує математичні функції `sin()` і `cos()` із системної бібліотеки `libm`, а для експорту стиснених бінарних звітів — функцію `compress()` із бібліотеки `zlib`.

У публічному інтерфейсі типи `zlib` не розкриваються — залежність є виключно внутрішньою (приватною). Це важливе архітектурне рішення: споживачу нашої бібліотеки непотрібно підключати заголовки `zlib.h` у власному коді, якщо він не викликає функції компресії напряму. Крім того, ми налаштовуємо контроль видимості символів: усі внутрішні допоміжні функції компілюються з прапорцем `-fvisibility=hidden`, а назовні експортуються лише функції з явним модифікатором API.

### Публічний заголовок: include/geomcalc.h / include/geomcalc.hpp

У файлі заголовків оголошуємо структури точок та функції обчислення. Для мови C надаємо класичний процедурний інтерфейс з обов'язковим блоком `extern "C"`, а для C++ — сучасний строго типізований інтерфейс у просторі імен із типами `std::span` та `std::expected`.

:::tabs
:::code proj-pc-authoring/c/geomcalc.h
:::code proj-pc-authoring/cpp/geomcalc.hpp
:::

### Реалізація: src/geomcalc.c / src/geomcalc.cpp

У файлах реалізації виконуємо математичні обчислення через `fabs()` з `<math.h>` та здійснюємо виклик функції `compress()` із бібліотеки `zlib`. Функція розраховує необхідний розмір буфера стиснення за допомогою `compressBound()` і перевіряє коди завершення алгоритму Deflate.

:::tabs
:::code proj-pc-authoring/c/geomcalc.c
:::code proj-pc-authoring/cpp/geomcalc.cpp
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

:::code proj-pc-authoring/cmake/CMakeLists.txt

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
:::code proj-pc-authoring/c/client.c
:::code proj-pc-authoring/cpp/client.cpp
:::

### Складання через Makefile споживача

Напишемо `Makefile`, який демонструє збірку як динамічного клієнта, так і повністю автономного статичного бінарника:

:::code proj-pc-authoring/make/Makefile

Запустимо компіляцію програми:
:::code proj-pc-authoring/sh/main.sh

Перевіримо створені бінарники системною утилітою `file` та `ldd`:
```bash
$ file client_static
client_static: ELF 64-bit LSB executable, x86-64, statically linked, for GNU/Linux 3.2.0, not stripped

$ ldd client_static
	not a dynamic executable
```

Бібліотека успішно скомпільована, інстальована та перевірена в обох режимах компонування. Створений `.pc` файл повністю відповідає стандартам дистрибутивів Linux і готовий до поширення серед розробників на будь-яких системах збірки.
