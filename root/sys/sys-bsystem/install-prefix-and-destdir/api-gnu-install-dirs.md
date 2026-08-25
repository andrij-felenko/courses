# 📋 Довідник змінних розміщення: GNU Coding Standards, CMake та Meson

Управління розміщенням двійкових файлів, заголовків, бібліотек та конфігурацій у Unix-подібних операційних системах спирається на суворо стандартизовану систему змінних каталогів. Первинний стандарт було закладено на початку 1990-х років у документі **GNU Coding Standards** для системи збірки GNU Autotools. Згодом цю конвенцію без змін адаптували сучасні системи збірки — **CMake** (через стандартний модуль `GNUInstallDirs`) та **Meson** (через набір вбудованих параметрів каталогу).

Стандартизація назв змінних гарантує, що системні пакувальники (`rpmbuild`, `debhelper`, `abuild`, `makepkg`) можуть викликати конфігурацію будь-якого проєкту за єдиним шаблоном, перевизначаючи потрібні каталоги без ручного редагування вихідних сценаріїв збірки.

## Зведена матриця стандартних змінних розміщення

Усі відносні шляхи за замовчуванням обчислюються відносно префікса встановлення (`PREFIX` в Autotools, `CMAKE_INSTALL_PREFIX` у CMake, `--prefix` у Meson).

| Змінна GNU (Autotools) | Змінна CMake (`GNUInstallDirs`) | Опція Meson | Типове значення відносно PREFIX | Призначення каталогу за стандартом FHS |
| :--- | :--- | :--- | :--- | :--- |
| `bindir` | `CMAKE_INSTALL_BINDIR` | `bindir` | `bin` | Виконувані файли програм загального призначення для користувачів |
| `sbindir` | `CMAKE_INSTALL_SBINDIR` | `sbindir` | `sbin` | Системні виконувані файли для системного адміністратора (`root`) |
| `libexecdir` | `CMAKE_INSTALL_LIBEXECDIR` | `libexecdir` | `libexec` (або `lib`) | Внутрішні допоміжні бінарники, які викликаються іншими програмами й не призначені для `$PATH` |
| `libdir` | `CMAKE_INSTALL_LIBDIR` | `libdir` | `lib` / `lib64` / `lib/<triplet>` | Об'єктний двійковий код: спільні (`.so`, `.dylib`) та статичні (`.a`) бібліотеки |
| `includedir` | `CMAKE_INSTALL_INCLUDEDIR` | `includedir` | `include` | Публічні заголовкові файли мов C та C++ (`.h`, `.hpp`) |
| `datarootdir` | `CMAKE_INSTALL_DATAROOTDIR` | `datadir` | `share` | Кореневий каталог архітектурно-незалежних даних тільки для читання |
| `datadir` | `CMAKE_INSTALL_DATADIR` | `datadir` | `share` (або `share/<project>`) | Статичні дані застосунків (іконки, теми, схеми, звуки, шрифти) |
| `sysconfdir` | `CMAKE_INSTALL_SYSCONFDIR` | `sysconfdir` | `etc` | Системні конфігураційні файли хоста, доступні для редагування адміністратором |
| `sharedstatedir` | `CMAKE_INSTALL_SHAREDSTATEDIR` | — | `com` (або `var/lib`) | Архітектурно-незалежні змінні дані, спільні для кількох комп'ютерів мережі |
| `localstatedir` | `CMAKE_INSTALL_LOCALSTATEDIR` | `localstatedir` | `var` | Локальні змінні дані конкретного хоста (бази даних, черги spool, журнали) |
| `runstatedir` | `CMAKE_INSTALL_RUNSTATEDIR` | — | `var/run` (або `run`) | Тимчасові дані часу виконання процесу (PID-файли, UNIX-сокети, блокування) |
| `localedir` | `CMAKE_INSTALL_LOCALEDIR` | `localedir` | `share/locale` | Скомпільовані бінарні каталоги повідомлень локалізації `gettext` (`.mo`) |
| `mandir` | `CMAKE_INSTALL_MANDIR` | `mandir` | `share/man` | Сторінки системної документації утиліти `man` (секції 1–8) |
| `infodir` | `CMAKE_INSTALL_INFODIR` | `infodir` | `share/info` | Гіпертекстова документація у форматі GNU Info |
| `docdir` | `CMAKE_INSTALL_DOCDIR` | — | `share/doc/<project>` | Додаткова документація пакета (файли README, ліцензії, PDF, HTML) |

## Анатомія змінних модуля GNUInstallDirs у CMake

Після підключення модуля `include(GNUInstallDirs)` у просторі CMake стають доступними два взаємодоповнюючі набори змінних для кожного типу каталогу:

### 1. Відносні змінні (`CMAKE_INSTALL_<DIR>`)
Містять відносний шлях без префікса (наприклад `bin`, `lib`, `share/myapp`, `include/mylib`).

Ці змінні призначені **виключно** для використання як значення параметра `DESTINATION` у командах встановлення:
- `install(TARGETS ... RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})`
- `install(DIRECTORY ... DESTINATION ${CMAKE_INSTALL_DATADIR}/myapp)`
- `install(FILES ... DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/mylib)`

Використання відносних змінних гарантує, що система збірки автоматично об'єднає їх із поточним значенням `CMAKE_INSTALL_PREFIX` під час генерації коду встановлення `cmake_install.cmake`, дозволяючи змінювати префікс через команду `cmake --install build --prefix /new/prefix`.

### 2. Абсолютні змінні (`CMAKE_INSTALL_FULL_<DIR>`)
Містять повний абсолютний шлях до каталогу у файловій системі, сформований шляхом автоматичного об'єднання `${CMAKE_INSTALL_PREFIX}` та `${CMAKE_INSTALL_<DIR>}` (наприклад `/usr/local/share/myapp` або `/opt/company/etc`).

Ці змінні використовуються:
- Для передачі абсолютних шляхів у макроси компілятора через `target_compile_definitions`:
  ```cmake
  target_compile_definitions(myapp PRIVATE
      DEFAULT_CONFIG_FILE="${CMAKE_INSTALL_FULL_SYSCONFDIR}/myapp.conf"
      LOCALEDIR="${CMAKE_INSTALL_FULL_LOCALEDIR}"
  )
  ```
- Для підстановки у конфігураційні шаблони `.pc.in` для `pkg-config` або системні юніти systemd через команду `configure_file`.

## Дистрибутивні відмінності у значенні CMAKE_INSTALL_LIBDIR

Розміщення динамічних бібліотек у 64-бітних архітектурах Linux є найбільш гетерогенною частиною системного пакування:

```
Linux x86_64 / AArch64
 ├── Red Hat / Fedora / RHEL / SUSE  ──>  lib64  (/usr/lib64)
 ├── Debian / Ubuntu (Multiarch)     ──>  lib/x86_64-linux-gnu (/usr/lib/x86_64-linux-gnu)
 ├── Arch Linux / Alpine Linux (musl) ─>  lib    (/usr/lib)
 └── macOS / Windows                 ──>  lib    (<prefix>/lib)
```

1. **Сімейство Red Hat / Fedora / SUSE:** 64-бітні бібліотеки розміщуються в каталозі `/usr/lib64`, тоді як каталог `/usr/lib` зарезервовано для 32-бітної сумісності. Модуль `GNUInstallDirs` автоматично визначає 64-бітну систему і встановлює `CMAKE_INSTALL_LIBDIR=lib64`, якщо префікс дорівнює `/usr` або `/usr/local`.
2. **Сімейство Debian / Ubuntu:** використовує концепцію **Multiarch**, де бібліотеки розміщуються у підкаталогах із назвою системного кортежу архітектури (`lib/x86_64-linux-gnu`, `lib/aarch64-linux-gnu`, `lib/arm-linux-gnueabihf`). Це дозволяє одночасно встановлювати бібліотеки для різних процесорних архітектур на один спільний диск. Інструменти складання Debian передають прапорець `-DCMAKE_INSTALL_LIBDIR=lib/${DEB_HOST_MULTIARCH}`.
3. **Arch Linux та Alpine Linux:** відмовилися від дублювання `lib64` і монтують єдиний каталог `/usr/lib` для всіх системних бібліотек.

## Специфіка системних каталогів SYSCONFDIR та LOCALSTATEDIR

Каталоги системної конфігурації (`sysconfdir`) та змінних даних (`localstatedir`) мають особливу логіку поведінки залежно від значення `PREFIX`:

1. **Дистрибутивні пакети (`PREFIX=/usr`):**
   Конфігураційні файли дистрибутива ніколи не повинні потрапляти у `/usr/etc`. Згідно зі стандартом FHS, системні налаштування хоста мають перебувати виключно в кореневому каталозі `/etc`. Тому під час збірки дистрибутивних пакетів пакувальники передають:
   - Autotools: `./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var`
   - CMake: `cmake -B build -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_INSTALL_SYSCONFDIR=/etc -DCMAKE_INSTALL_LOCALSTATEDIR=/var`
   - Meson: `meson setup build --prefix=/usr --sysconfdir=/etc --localstatedir=/var`
2. **Локальні інсталяції адміністратора (`PREFIX=/usr/local`):**
   Якщо програма встановлюється вручну в `/usr/local`, вона не має права перезаписувати глобальні конфігурації дистрибутива в `/etc`. Тому конфігурація за замовчуванням встановлюється у `/usr/local/etc`, а змінні дані — у `/usr/local/var`.

## Механізм LIBEXECDIR проти BINDIR: де ховаються внутрішні помічники

Каталог `CMAKE_INSTALL_LIBEXECDIR` (типово `libexec` або `lib/<project>`) займає особливе місце в ієрархії FHS. У той час як `bindir` призначений виключно для утиліт, які користувач викликає вручну або які знаходяться в системній змінній `$PATH`, `libexecdir` призначений для внутрішніх бінарних програм, допоміжних демонів та плагінів, які викликаються іншими програмами.

Типові приклади артефактів, що належать до `LIBEXECDIR`:
- Допоміжні агенти автентифікації SSH (`ssh-pkcs11-helper`).
- Внутрішні помічники демонів Polkit (`polkit-agent-helper-1`), які мають спеціальні атрибути безпеки (setuid root).
- Генератори середовища systemd (`systemd-sysv-generator`).
- Внутрішні обробники компіляторів (наприклад `cc1`, `cc1plus` у надрах каталогу `/usr/libexec/gcc`).

Розміщення таких двійкових файлів у загальному каталозі `bindir` вважається грубим порушенням архітектури пакування, оскільки це засмічує автодоповнення командної оболонки та створює ризики випадкового запуску службових процесів без належного контексту оточення.

## Генерація конфігураційних файлів (.pc, .service) за допомогою змінних шляхів

Під час побудови бібліотек та системних служб розробник стикається з необхідністю підставляти шляхи розміщення у шаблони файлів метаданих. Найпоширенішими є описи для менеджера пакетів `pkg-config` (`.pc.in`) та описи служб systemd (`.service.in`).

Для коректної генерації таких файлів у CMake використовують команду `configure_file(@ONLY)`:

```ini
# Шаблон mylib.pc.in для pkg-config
prefix=@CMAKE_INSTALL_PREFIX@
exec_prefix=${prefix}
libdir=@CMAKE_INSTALL_FULL_LIBDIR@
includedir=@CMAKE_INSTALL_FULL_INCLUDEDIR@

Name: mylib
Description: Високопродуктивна бібліотека C++
Version: @PROJECT_VERSION@
Libs: -L${libdir} -lmylib
Cflags: -I${includedir}
```

У шаблонах служб systemd (`myapp.service.in`) використовують повні абсолютні шляхи до виконуваного файлу та робочого каталогу:

```ini
[Unit]
Description=Служба фонової обробки даних MyApp
After=network.target

[Service]
Type=simple
ExecStart=@CMAKE_INSTALL_FULL_BINDIR@/myapp-daemon
WorkingDirectory=@CMAKE_INSTALL_FULL_LOCALSTATEDIR@/lib/myapp
ConfigurationDirectory=myapp
RuntimeDirectory=myapp
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Використання змінних `CMAKE_INSTALL_FULL_*` гарантує, що у згенерованому сервісному юніті шлях `ExecStart` автоматично перетвориться на точний рядок `/usr/bin/myapp-daemon` або `/usr/local/bin/myapp-daemon` залежно від обраного префікса конфігурації.

## Крос-компіляція: взаємодія PREFIX, SYSROOT та PKG_CONFIG_SYSROOT_DIR

Під час крос-компіляції для вбудованих пристроїв (наприклад збірка під ARM64 на робочій станції x86_64) виникає критичне розрізнення між трьома сутностями:

1. **`CMAKE_SYSROOT` (або `--sysroot`):** фізичний каталог на комп'ютері розробника, де лежать заголовки та бібліотеки цільової плати (наприклад `/opt/toolchains/aarch64-linux-gnu/libc`).
2. **`CMAKE_INSTALL_PREFIX`:** логічний шлях у файловій системі цільової плати, куди програма потрапить після прошивання образу (наприклад `/usr` або `/opt/app`).
3. **`PKG_CONFIG_SYSROOT_DIR`:** змінна середовища, яку читає утиліта `pkg-config` під час крос-компіляції. Якщо `pkg-config` повертає шлях `-I/usr/include/glib-2.0`, утиліта автоматично додає значення `PKG_CONFIG_SYSROOT_DIR` на початку, формуючи валідний для крос-компілятора шлях `-I/opt/toolchains/aarch64-linux-gnu/libc/usr/include/glib-2.0`.

Якщо розробник помилково вказує шлях `sysroot` як префікс встановлення (`-DCMAKE_INSTALL_PREFIX=/opt/toolchains/...`), програма після прошивання на мікрокомп'ютер не зможе знайти свої конфігурації, оскільки шукатиме каталог тулчейна хост-машини, якого на реальному пристрої фізично не існує.

## Інтеграція зі спеціалізованими підсистемами Linux

Крім стандартних змінних FHS, сучасні програми в екосистемі Linux встановлюють файли інтеграції з системними службами. Модуль `GNUInstallDirs` або системні файли `pkg-config` надають такі загальноприйняті змінні:

- **Служби systemd:**
  - Системні юніти дистрибутива: `${CMAKE_INSTALL_PREFIX}/lib/systemd/system` (або `/usr/lib/systemd/system`).
  - Користувацькі юніти: `${CMAKE_INSTALL_PREFIX}/lib/systemd/user`.
- **Шина D-Bus:**
  - Системні служби D-Bus: `${CMAKE_INSTALL_DATADIR}/dbus-1/system-services`.
  - Сесійні служби D-Bus: `${CMAKE_INSTALL_DATADIR}/dbus-1/services`.
  - Політики безпеки D-Bus: `${CMAKE_INSTALL_DATADIR}/dbus-1/system.d` (або `/etc/dbus-1/system.d`).
- **Правила udev:**
  - Системні правила пристроїв: `${CMAKE_INSTALL_PREFIX}/lib/udev/rules.d`.
- **Політики Polkit:**
  - Декларації дій: `${CMAKE_INSTALL_DATADIR}/polkit-1/actions`.
- **Ярлики робочого столу та MIME-типи:**
  - Файли запуску `.desktop`: `${CMAKE_INSTALL_DATADIR}/applications`.
  - Іконки інтерфейсу: `${CMAKE_INSTALL_DATADIR}/icons/hicolor`.
  - Описи MIME-типів: `${CMAKE_INSTALL_DATADIR}/mime/packages`.

## Типові помилки та антипатерни використання змінних

1. **Жорстке кодування `DESTINATION lib` або `DESTINATION include`:**
   Пряме зазначення рядка `lib` у правилах `install(TARGETS myapp LIBRARY DESTINATION lib)` ламає пакування на 64-бітних системах Fedora/RHEL (де потрібен `lib64`) та Debian Multiarch. Завжди використовуйте `${CMAKE_INSTALL_LIBDIR}`.
2. **Змішування відносних та абсолютних змінних у `DESTINATION`:**
   Зазначення `install(FILES config.json DESTINATION ${CMAKE_INSTALL_FULL_DATADIR}/myapp)` робить шлях абсолютним. Якщо користувач спробує встановити пакет в інший каталог через `cmake --install build --prefix /opt/new`, CMake проігнорує новий префікс для цього файлу і спробує записати його за старим абсолютним шляхом.
3. **Забування створення підкаталогу для проєкту в `DATADIR`:**
   Копіювання файлу безпосередньо у `${CMAKE_INSTALL_DATADIR}` призводить до того, що файл опиняється прямо в корені спільної системної теки `/usr/share`. Статичні ресурси програми завжди повинні встановлюватися у підкаталог імені проєкту: `${CMAKE_INSTALL_DATADIR}/<project_name>`.
