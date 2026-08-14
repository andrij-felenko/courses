# ⚙️ Практичне пакування: створення DEB та RPM для C/C++ сервісу

Цей практичний керівник демонструє повний цикл автоматизованої збірки бінарних пакунків `.deb` та `.rpm` для системного демона спостереження, написаного на C та C++. Тут детально розглянуто структуру вихідних файлів, конфігурацію системи збірки `Make`, специфікаційні файли каталогу `debian/` та спек-файли `.spec`, а також правила управління системними службами через утиліти `systemd`.

Головна мета практичного пакування полягає у перетворенні сирого вихідного коду програми на автономний пакет, який можна безпечно встановити у файлову систему Linux без пошкодження наявних компонентів системи. Для цього розробник пакунка повинен правильно налаштувати ізоляцію шляхів встановлення за допомогою змінної `DESTDIR` та гарантувати очищення тимчасових ресурсів.

## 1. Системний демон спостереження (sysmon)

Розглянемо вихідний код системної утиліти `sysmon`, яка записує статус роботи у системний журнал `syslog`. Демон обробляє POSIX-сигнали `SIGINT` та `SIGTERM` для коректного завершення роботи без залишення пошкоджених тимчасових ресурсів чи заблокованих дескрипторів файлів.

:::tabs
```c
/* sysmon.c — Системний демон фонового моніторингу на C */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <syslog.h>
#include <signal.h>

static volatile int keep_running = 1;

void handle_signal(int sig) {
    if (sig == SIGINT || sig == SIGTERM) {
        keep_running = 0;
    }
}

int main(void) {
    openlog("sysmon", LOG_PID | LOG_CONS, LOG_DAEMON);
    syslog(LOG_INFO, "Демон sysmon успішно запущено.");

    struct sigaction sa;
    sa.sa_handler = handle_signal;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    while (keep_running) {
        syslog(LOG_INFO, "sysmon: системний статус OK");
        sleep(5);
    }

    syslog(LOG_INFO, "Демон sysmon зупинено за сигналом.");
    closelog();
    return 0;
}
```
```cpp
// sysmon.cpp — Системний демон фонового моніторингу на C++
#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <csignal>
#include <syslog.h>

namespace {
    std::atomic<bool> g_keep_running{true};
}

void signal_handler(int signal) {
    if (signal == SIGINT || signal == SIGTERM) {
        g_keep_running = false;
    }
}

class SyslogGuard {
public:
    explicit SyslogGuard(const char* ident) {
        openlog(ident, LOG_PID | LOG_CONS, LOG_DAEMON);
    }
    ~SyslogGuard() {
        syslog(LOG_INFO, "Демон sysmon зупинено за сигналом (RAII).");
        closelog();
    }
};

int main() {
    SyslogGuard log_guard("sysmon");
    syslog(LOG_INFO, "Демон sysmon (C++) успішно запущено.");

    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    while (g_keep_running) {
        syslog(LOG_INFO, "sysmon: системний статус OK");
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }

    return 0;
}
```
:::

### 1.1. Складальний файл `Makefile`

Для компіляції та розміщення файлів у структурі каталогів тимчасового кореня використовується наступний `Makefile`. Всі шляхи встановлення задаються через змінні `PREFIX` та `DESTDIR`. Прапорець `DESTDIR` використовується обома пакетними менеджерами для ізоляції файлів у тимчасових каталогах збірки без пошкодження реальної файлової системи розробника.

Під час збірки пакетний менеджер передає свій каталог тимчасового монтування (наприклад, `debian/sysmon/` або `BUILDROOT/`), куди `make install` копіює бінарні файли та юніти `systemd`. Використання команд `install -d` та `install -m` гарантує точне дотримання прав доступу (POSIX mode `0755` для бінарних файлів та `0644` для службових конфігурацій).

```makefile
PREFIX ?= /usr
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/share/man/man1
SYSTEMDDIR ?= /lib/systemd/system

CC ?= gcc
CXX ?= g++
CFLAGS += -Wall -Wextra -O2
CXXFLAGS += -Wall -Wextra -O2 -std=c++17

TARGET = sysmon

all: $(TARGET)

$(TARGET): sysmon.c
	$(CC) $(CFLAGS) $< -o $@

cpp-build: sysmon.cpp
	$(CXX) $(CXXFLAGS) $< -o $(TARGET)

install: $(TARGET)
	install -d $(DESTDIR)$(BINDIR)
	install -m 0755 $(TARGET) $(DESTDIR)$(BINDIR)/$(TARGET)
	install -d $(DESTDIR)$(SYSTEMDDIR)
	install -m 0644 sysmon.service $(DESTDIR)$(SYSTEMDDIR)/sysmon.service

clean:
	rm -f $(TARGET)

.PHONY: all cpp-build install clean
```

---

## 2. Збірка DEB-пакунка (`dpkg-buildpackage` та Debhelper)

Для створення `.deb` пакунка в корені вихідного коду створюється каталог `debian/`. Інструментарій Debhelper серії `dh` автоматизує виклики `configure`, `make`, `make install`, а також вилучення символів налагодження (`dh_strip`) та генерацію залежностей від динамічних бібліотек (`dh_shlibdeps`).

Система `debhelper` послідовно виконує серію стандартних утиліт (`dh_auto_configure`, `dh_auto_build`, `dh_auto_install`), що позбавляє пейкеджера від необхідності вручну прописувати кожну команду компіляції та копіювання файлів.

### 2.1. Конвеєр виконання Debhelper

За лаштунками утиліта `dh $@` викликає суворо визначену послідовність кроків:

1. `dh_testdir`: Перевіряє, чи знаходиться почний виклик у корені вихідного коду програми.
2. `dh_auto_configure`: Автоматично визначає систему збірки (Autotools, CMake, Meson або Makefile) та викликає її з правильними системними прапорцями компіляції (`--prefix=/usr`).
3. `dh_auto_build`: Запускає команду компіляції `make -jN`.
4. `dh_auto_install`: Виконує інсталяцію в ізольований каталог `debian/sysmon/` через `make install DESTDIR=...`.
5. `dh_installsystemd`: Виявляє юніт-файли `.service` і створює відповідні виклики `systemctl` у скриптлетах `postinst` та `prerm`.
6. `dh_strip`: Вилучає налагоджувальні символи з бінарних ELF файлів для зменшення розміру підсумкового пакунка.
7. `dh_shlibdeps`: Аналізує за допомогою `ldd` або `objdump` список динамічних бібліотек та будує рядок `${shlibs:Depends}`.
8. `dh_gencontrol`: Ґенерує остаточний файл `control` у `debian/sysmon/DEBIAN/`.
9. `dh_builddeb`: Запаковує вміст за допомогою `dpkg-deb --build` у файл `.deb`.

### 2.2. Механізм виявлення залежностей `dpkg-shlibdeps`

Під час виконання етапу `binary-arch` інструмент `dpkg-shlibdeps` зчитує згенеровані бінарні файли ELF у каталозі `debian/sysmon/usr/bin/sysmon`. Він аналізує динамічну секцію заголовка ELF на наявність тегів `DT_NEEDED`, які вказують, які саме спільні об'єкти (наприклад, `libc.so.6`) потрібні бінарному файлу.

Після цього `dpkg-shlibdeps` звертається до системних баз даних `/var/lib/dpkg/info/*.symbols` та `/var/lib/dpkg/info/*.shlibs` для визначення мінімальних версій пакетів (наприклад, `libc6 (>= 2.34)`), що надають ці бібліотеки, і підставляє підсумковий рядок у підстановку `${shlibs:Depends}` файлу `debian/control`.

### 2.3. Конфігурація `debian/control`

Файл визначає джерельний пакунок `Source: sysmon` та підсумковий бінарний пакунок `Package: sysmon`. Змінна `${shlibs:Depends}` буде автоматично замінена інструментом `dpkg-shlibdeps` на списки конкретних версій системної бібліотеки `libc6`.

```text
Source: sysmon
Section: utils
Priority: optional
Maintainer: System Engineer <admin@example.com>
Build-Depends: debhelper-compat (= 13), gcc, make
Standards-Version: 4.6.2

Package: sysmon
Architecture: any
Depends: ${shlibs:Depends}, ${misc:Depends}
Description: Simple system monitoring daemon
 Sysmon is a lightweight daemon that periodically logs health check
 statistics to the system logger (syslog).
```

### 2.4. Файл правил `debian/rules`

Завдяки Debhelper v13 файл правил є лаконічним і перевизначає етапи збірки лише за необхідності виклику нестандартних цілей `Makefile`:

```makefile
#!/usr/bin/make -f
%:
	dh $@
```

### 2.5. Журнал змін `debian/changelog`

Формат журнала є суворо стандартизованим для парсингу версії інструментами `dpkg-parsechangelog`. Перший рядок визначає назву пакунка, його версію та цільову гілку дистрибутиву (`unstable` або `main`):

```text
sysmon (1.0.0-1) unstable; urgency=medium

  * Initial release of sysmon daemon package.

 -- System Engineer <admin@example.com>  Fri, 14 Aug 2026 12:00:00 +0300
```

### 2.6. Виконання збірки DEB

Команда `dpkg-buildpackage` з прапорцями `-us -uc` (без цифрового підпису GPG для локального тестування) збирає бінарний `.deb` файл у батьківському каталозі:

```bash
$ dpkg-buildpackage -us -uc -b
```

---

## 3. Збірка RPM-пакунка (`rpmbuild` та `.spec`)

Для збірки `.rpm` створюється рецепт `sysmon.spec`. Утиліта `rpmbuild` виконує розпакування тарифного архіву джерел, компіляцію у тимчасовому каталозі `BUILD`, встановлення у `BUILDROOT` і формування cpio-пакунка.

### 3.1. Ієрархія каталогів `~/rpmbuild` та фази збірки

Для ізольованої збірки пакунків у домашньому каталозі користувача створюється стандартне дерево каталогів:

- `SOURCES/`: Містить тарифні архіви вихідного коду (`sysmon-1.0.0.tar.gz`) та патчі.
- `SPECS/`: Містить файли рецептів збірки (`.spec`).
- `BUILD/`: Тимчасовий каталог, у якому розпаковуються вихідні файли і виконується компіляція.
- `BUILDROOT/`: Тимчасовий каталог мока файлової системи (chroot root), куди виконується `make install`.
- `RPMS/`: Каталог для готових бінарних RPM-пакунків, розкладених по архітектурах (`x86_64`, `noarch`).
- `SRPMS/`: Каталог для згенерованих пакунків вихідного коду Source RPM (`.src.rpm`).

Утиліта `rpmbuild` послідовно виконує секції spec-файлу:

- `%prep`: Розпаковує архіви за допомогою `%autosetup` та накладає необхідні системні патчі.
- `%build`: Запускає компіляцію за допомогою макросу `%make_build`, який передає апстрімні прапорці оптимізації дистрибутиву (`RPM_OPT_FLAGS`).
- `%install`: Очищує `%buildroot` і виконує команду `%make_install DESTDIR=%{buildroot}`, розміщуючи бінарні файли у тимчасовому пеленальному каталозі.
- `%check`: Виконує прогін модульних тестів (якщо ціль `test` або `check` присутня в Makefile).
- `%files`: Перевіряє, чи всі створені у `%buildroot` файли явним чином перелічені в секції. Якщо в каталозі збірки знайдено незареєстрований файл, `rpmbuild` припиняє роботу з помилкою `Unpackaged file(s) found`.

### 3.2. Файл рецепта `sysmon.spec`

Макроси `%systemd_post` та `%systemd_preun` автоматично генерують скриптлети для перезапуску служб `systemd` після оновлення або видалення пакунка, забезпечуючи коректну інтеграцію з системним менеджером ініціалізації без залишення сирітських процесів.

Конфігураційні файли в секції `%files` часто позначаються макросом `%config(noreplace)`. Це гарантує, що під час оновлення RPM-пакунка змінений адміністратором конфігураційний файл не буде перезаписано; новий конфіг з пакунка буде збережено поруч із розширенням `.rpmnew`.

```spec
Name:           sysmon
Version:        1.0.0
Release:        1%{?dist}
Summary:        Simple system monitoring daemon

License:        MIT
URL:            https://example.com/sysmon
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  gcc, make, systemd-rpm-macros
Requires(post): systemd
Requires(preun): systemd

%description
Sysmon is a lightweight daemon that periodically logs health check
statistics to the system logger (syslog).

%prep
%autosetup

%build
%make_build

%install
%make_install DESTDIR=%{buildroot} PREFIX=/usr

%post
%systemd_post sysmon.service

%preun
%systemd_preun sysmon.service

%postun
%systemd_postun_with_restart sysmon.service

%files
%license LICENSE
%{_bindir}/sysmon
/lib/systemd/system/sysmon.service

%changelog
* Fri Aug 14 2026 System Engineer <admin@example.com> - 1.0.0-1
- Initial release of sysmon daemon.
```

### 3.3. Виконання збірки RPM

Перед викликом `rpmbuild` необхідно розмістити архів джерел `sysmon-1.0.0.tar.gz` у каталозі `~/rpmbuild/SOURCES/`. Після цього запускається процедура комбінованої збірки бінарного пакунка та пакунка джерел SRPM:

```bash
$ rpmbuild -ba sysmon.spec
```
