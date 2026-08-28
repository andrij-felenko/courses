# ⚙️ Практикум: компонентне пакування сервісу телеметрії

Цей практикум демонструє повний інженерний цикл побудови системи компонентного пакування для системного сервісу збору метрик `telemetryd`. Типова проблема промислової розробки полягає в тому, що один проєкт породжує артефакти різного призначення: виконуваний серверний демон, спільну динамічну бібліотеку з публічним ABI, заголовочні файли для розробки сторонніх плагінів, конфігурації компілятора CMake, файли юнітів системного менеджера `systemd` та документацію.

Якщо запакувати всі ці артефакти в єдиний монолітний пакет, користувачі на серверах будуть змушені встановлювати непотрібні заголовки й документацію, а розробники бібліотек отримають конфлікти версій. Мета цього практикуму — створити єдиний сценарій CMake та CPack, який автоматично розділяє артефакти на три ізольовані пакети:
1. `telemetry-runtime` — скомпільований демон `telemetryd`, спільна бібліотека `libtelemetry.so.1`, юніт-файл `systemd` та скрипти постінсталяційного перезавантаження.
2. `telemetry-devel` — заголовки C/C++, символічне посилання `libtelemetry.so` для лінкування та файли експорту цілей CMake (`TelemetryConfig.cmake`).
3. `telemetry-docs` — документація API та системні man-сторінки.

## 1. Архітектура та вихідний код компонентів

Проєкт спроєктовано за модульним принципом: логіка обчислення метрик винесена в окрему спільну бібліотеку з чистим C-сумісним ABI, що дозволяє викликати її з програм будь-якими мовами програмування. Демон `telemetryd` є тонким клієнтом над бібліотекою, який періодично опитує показники та виводить їх у форматі JSON.

### Заголовочний файл бібліотеки (`include/telemetry/metrics.h` / `include/telemetry/metrics.hpp`)

Публічний заголовок визначає структуру знімка метрик та сигнатури функцій збору й форматування.

:::tabs
:::code proj-component-packaging/c/zaholovochnyi-fail.h
:::code proj-component-packaging/cpp/zaholovochnyi-fail.hpp
:::

### Реалізація бібліотеки (`src/metrics.c` / `src/metrics.cpp`)

Реалізація бібліотеки розраховує час безперервної роботи процесу від моменту першого виклику та формує серіалізований рядок JSON. Нижче наведено варіанти реалізації мовами C та сучасним C++ (C++20).

:::tabs
:::code proj-component-packaging/c/realizatsiia-biblioteky.c
:::code proj-component-packaging/cpp/realizatsiia-biblioteky.cpp
:::

### Виконуваний демон (`src/daemon.c` / `src/daemon.cpp`)

Демон запускається як системна служба, ініціалізує буфери пам'яті, опитує бібліотеку метрик і передає результати у стандартний потік виводу (який перехоплюється журналом `systemd-journald`).

:::tabs
:::code proj-component-packaging/c/vykonuvanyi-demon-src.c
:::code proj-component-packaging/cpp/vykonuvanyi-demon-src.cpp
:::

## 2. Системна інтеграція та сценарії життєвого циклу

Системний пакунок Linux повинен не просто розпакувати бінарники на диск, а й зареєструвати службу в підсистемі ініціалізації та оновити кеш динамічного лінкера.

### Юніт-файл systemd (`packaging/telemetryd.service`)

Юніт описує правила запуску демона операційною системою: тип процесу `simple`, автоматичний перезапуск при аварійному завершенні та залежність від мережевого стека.

```ini
[Unit]
Description=Telemetry Monitoring Daemon
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/telemetryd
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### Сценарій постінсталяції (`packaging/postinst.sh`)

Скрипт викликається пакетним менеджером (`dpkg` або `rpm`) після запису всіх файлів на диск. Він виконує дві критичні задачі: викликає `ldconfig` для реєстрації нової бібліотеки `/usr/lib/libtelemetry.so.1` та сповіщає `systemd` про появу нового юніт-файлу через команду `systemctl daemon-reload`.

Для забезпечення ідемпотентності скрипт перевіряє наявність сокета `systemd` у `/run/systemd/system`. Якщо пакунок встановлюється всередині контейнера Docker чи ізольованого середовища `chroot`, де демон `systemd` не запущений як PID 1, скрипт не аварійно перериває інсталяцію, а тихо завершує роботу.

:::code proj-component-packaging/sh/stsenarii-postinstaliatsii.sh

## 3. Повна конфігурація `CMakeLists.txt`

Файл проєкту організовує збірку цілей, пов'язує їх із компонентами інсталяції та конфігурує параметри CPack для генерації DEB, RPM та архівних дистрибутивів.

Зверніть увагу на використання генераторних виразів `$<BUILD_INTERFACE:...>` та `$<INSTALL_INTERFACE:...>` у команді `target_include_directories`. Це гарантує, що під час локальної збірки компілятор шукатиме заголовки у вихідному каталозі `include/`, а при експорті цілей для сторонніх проєктів у згенерований `TelemetryTargets.cmake` буде записано правильний відносний шлях `${_IMPORT_PREFIX}/include`.

:::code proj-component-packaging/cmake/CMakeLists.txt

## 4. Збірка проєкту та створення пакетів

Процес збірки та пакування здійснюється у два етапи: спочатку CMake збирає бінарники у каталозі `build/`, після чого утиліта `cpack` монтує дерево інсталяції та викликає відповідні бекенди генераторів.

:::code proj-component-packaging/sh/4-zbirka-proiektu-ta.sh

## 5. Інспекція та верифікація згенерованих пакетів

Після успішного виконання CPack у каталозі `build/` з'являються готові артефакти:

```text
build/
├── telemetry-1.4.2-Linux-Runtime.deb
├── telemetry-1.4.2-Linux-Development.deb
├── telemetry-1.4.2-Linux-Documentation.deb
├── telemetry-1.4.2-1.x86_64-Runtime.rpm
├── telemetry-1.4.2-1.x86_64-Development.rpm
└── telemetry-1.4.2-Linux.tar.gz
```

### Перевірка метаданих пакета `telemetry-Runtime.deb`

Виконаємо інспекцію файлу `control` всередині згенерованого DEB-пакета за допомогою утиліти `dpkg-deb`:

```bash
dpkg-deb -I telemetry-1.4.2-Linux-Runtime.deb
```

У виводі утиліти видно, що CPack успішно інтегрував параметри з `CMakeLists.txt`, а увімкнений прапорець `CPACK_DEBIAN_PACKAGE_SHLIBDEPS` автоматично визначив системну залежність від версії бібліотеки `libc6` на основі аналізу секції `DT_NEEDED` бінарника `telemetryd`:

```text
 Package: telemetry-runtime
 Version: 1.4.2
 Section: utils
 Priority: optional
 Architecture: amd64
 Maintainer: ops@telemetry.example.com
 Depends: libc6 (>= 2.34)
 Description: Lightweight system telemetry daemon
```

### Перевірка вмісту файлової системи пакета

Переглянемо перелік файлів, запакованих у `telemetry-Runtime.deb`:

```bash
dpkg-deb -c telemetry-1.4.2-Linux-Runtime.deb
```

```text
-rwxr-xr-x root/root     18424 2026-08-21 12:00 ./usr/bin/telemetryd
-rwxr-xr-x root/root     15680 2026-08-21 12:00 ./usr/lib/libtelemetry.so.1.4.2
lrwxrwxrwx root/root         0 2026-08-21 12:00 ./usr/lib/libtelemetry.so.1 -> libtelemetry.so.1.4.2
-rw-r--r-- root/root       210 2026-08-21 12:00 ./lib/systemd/system/telemetryd.service
```

Як видно зі списку, завдяки директиві `NAMELINK_COMPONENT Development`, символічне посилання без версії `libtelemetry.so` та заголовочні файли `include/` потрапили виключно до пакета `telemetry-Development.deb`. Таким чином досягається повна ізоляція середовища виконання від інструментів розробника.

### Інспекція експортованих конфігурацій CMake

Перевіримо вміст пакета розробника `telemetry-Development.deb`:

```bash
dpkg-deb -c telemetry-1.4.2-Linux-Development.deb
```

```text
-rw-r--r-- root/root       730 2026-08-21 12:00 ./usr/include/telemetry/metrics.h
lrwxrwxrwx root/root         0 2026-08-21 12:00 ./usr/lib/libtelemetry.so -> libtelemetry.so.1
-rw-r--r-- root/root      4512 2026-08-21 12:00 ./usr/lib/cmake/Telemetry/TelemetryTargets.cmake
-rw-r--r-- root/root      1280 2026-08-21 12:00 ./usr/lib/cmake/Telemetry/TelemetryTargets-release.cmake
```

Сторонній проєкт, встановивши цей пакет, може безпосередньо підключити бібліотеку у своєму `CMakeLists.txt` за допомогою стандартної команди:

```cmake
find_package(Telemetry REQUIRED)
target_link_libraries(my_plugin PRIVATE Telemetry::telemetry_lib)
```

При цьому CMake автоматично отримає коректні шляхи до заголовочних файлів (`/usr/include`) та прапорці компонування (`-ltelemetry`), гарантуючи повну переносимість і стабільність збірки у системі.

## 6. Порівняння поведінки життєвого циклу в DEB та RPM

Особливу увагу при написанні сценаріїв супроводу слід звертати на аргументи, які передаються операційними менеджерами під час інсталяції та оновлення:

- **У системі Debian (dpkg):** Перший позиційний аргумент `$1` у `postinst` приймає значення `configure` під час початкової інсталяції, або `configure <попередня-версія>` під час оновлення. Сценарій `prerm` викликається з аргументом `remove` або `upgrade <нова-версія>`.
- **У системі Red Hat (RPM):** Перший позиційний аргумент `$1` у секціях `%post` та `%preun` позначає кількість встановлених копій пакета в системі після завершення поточної транзакції. При первинному встановленні `$1 == 1`. При оновленні пакета новою версією `$1 == 2`. При повному видаленні пакета із системи в скрипті `%preun` змінна `$1 == 0`.

Врахування цих аргументів дозволяє писати надійні скрипти, які перезапускають системні служби під час оновлення, але не запускають їх передчасно при розгортанні образу диска під час складання контейнера.
