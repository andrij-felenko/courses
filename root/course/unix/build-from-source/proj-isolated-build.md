# ⚙️ Практичний рецепт: ізольована збірка багатокомпонентного ПЗ та створення DEB-пакунка

Пряме виконання команди `sudo make install` у робочій операційній системі копіює невідстежувані файли безпосередньо у системні каталоги `/usr/local/bin`, `/usr/local/lib` та `/usr/local/include`. З часом це призводить до змішування різних версій бібліотек, неможливості коректного видалення програми, блокування оновлень та ризику пошкодити залежності системного пакетного менеджера (`apt` чи `dnf`). Промисловий стандарт розгортання ПЗ з вихідного коду вимагає ізоляції програми в окремому каталозі `/opt/<app>` або пакування у нативний системний пакунок (`.deb` чи `.rpm`) за допомогою механізму проміжної інсталяції `DESTDIR`.

Нижче наведено покроковий інженерний сценарій: збірка мережевого сервісу з власною ізольованою версією бібліотеки асинхронного введення-виведення, вшивання відносних шляхів завантажувача через `$ORIGIN`, перенаправлення інсталяції у проміжний каталог та генерація чистого DEB-пакунка за допомогою утиліти `fpm`.

---

### 1. Архітектура цільового каталогу та схема залежностей

Наша мета — зібрати мережевий демон `netbridge`, який залежить від сторонньої бібліотеки `libuv` новішої версії, ніж та, що доступна в офіційному репозиторії базового дистрибутива. Фінальний артефакт повинен встановлюватися в каталог `/opt/netbridge` і функціонувати повністю автономно, не вимагаючи глобальної зміни змінної `LD_LIBRARY_PATH` у системі.

Цільова структура ізольованого каталогу `/opt/netbridge`:

```
/opt/netbridge/
├── bin/
│   └── netbridge            # Виконуваний файл ELF із вшитим RUNPATH = $ORIGIN/../lib
├── lib/
│   ├── libuv.so -> libuv.so.1.0.0
│   ├── libuv.so.1 -> libuv.so.1.0.0
│   └── libuv.so.1.0.0       # Ізольована бібліотека залежності
├── etc/
│   └── netbridge.conf       # Файл конфігурації за замовчуванням
└── share/
    └── man/man1/
        └── netbridge.1      # Довідкова сторінка man
```

#### Чому ізоляція через $ORIGIN переважає LD_LIBRARY_PATH

Змінна оточення `LD_LIBRARY_PATH` діє глобально на всі процеси, запущені в поточному сеансі командної оболонки. Якщо додати туди шлях `/opt/netbridge/lib`, усі інші системні утиліти (наприклад, `curl`, `python3` або `git`) можуть випадково завантажити несумісну версію бібліотеки замість системної, що спричиняє падіння через `symbol lookup error`.

На відміну від цього, тег `DT_RUNPATH` зі значенням `$ORIGIN/../lib` записується безпосередньо в заголовок `ELF` виконуваного файлу `netbridge`. Під час запуску програми ядро передає керування динамічному завантажувачу `ld-linux.so`, який розгортає змінну `$ORIGIN` у реальний абсолютний шлях каталогу, де знаходиться двійковий файл (`/opt/netbridge/bin`), і шукає бібліотеки строго у сусідньому каталозі `../lib`.

---

### 2. Крок 1: Підготовка ізольованого робочого середовища

Створюємо тимчасову робочу теку для збірки в оперативній пам'яті (`/tmp`) або у домашньому каталозі користувача. Всі операції виконуються без прав суперкористувача (`root`), що гарантує збереження цілісності операційної системи:

```bash
# Створення робочого простору для збірки
mkdir -p /tmp/build-workspace/{sources,stage}
cd /tmp/build-workspace/sources

# Завантаження та розпакування вихідного коду залежності (libuv)
curl -sSL https://dist.libuv.org/dist/v1.48.0/libuv-v1.48.0.tar.gz | tar -xz
cd libuv-v1.48.0
```

---

### 3. Крок 2: Збірка залежності в автономний префікс

Ми конфігуруємо бібліотеку `libuv` із префіксом `/opt/netbridge`, щоб згенерований файл `libuv.pc` містив правильні шляхи пошуку заголовків і бібліотек. Однак фактичне встановлення виконуємо у тимчасовий каталог інсталяції за допомогою змінної `DESTDIR`:

```bash
# 1. Генерація конфігурації
./autogen.sh
./configure \
    --prefix=/opt/netbridge \
    --enable-shared \
    --disable-static \
    CFLAGS="-O3 -march=native -fPIC"

# 2. Паралельна компіляція з використанням усіх ядер процесора
make -j$(nproc)

# 3. Інсталяція у проміжний каталог stage замість кореня системи
make install DESTDIR=/tmp/build-workspace/stage
```

Після виконання цієї команди структура `/tmp/build-workspace/stage/opt/netbridge` містить скомпільовані файли `.so`, заголовки `.h` та файл метаданих `libuv.pc` у каталозі `lib/pkgconfig`. Зверніть увагу: ми не чіпали реальний системний каталог `/opt/netbridge` — усі артефакти розміщені виключно у пісочниці `stage`.

---

### 4. Крок 3: Вихідний код сервісу та його компіляція

Створюємо вихідний код нашого мережевого демона. Програма ініціалізує цикл подій `libuv`, реєструє асинхронний таймер і демонструє практичне використання стороннього API.

:::tabs
```c
/* netbridge.c — C-реалізація з прямим викликом libuv API */
#include <stdio.h>
#include <stdlib.h>
#include <uv.h>

static void timer_callback(uv_timer_t *handle) {
    int64_t uptime = uv_now(handle->loop);
    printf("[netbridge] Сервіс працює стабільно. Поточний час циклу: %ld мс\n", (long)uptime);
    /* Зупиняємо таймер після першого спрацьовування для чистого виходу */
    uv_timer_stop(handle);
    uv_stop(handle->loop);
}

int main(int argc, char **argv) {
    printf("[netbridge] Ініціалізація демона...\n");
    uv_loop_t *loop = uv_default_loop();
    if (!loop) {
        fprintf(stderr, "Помилка: не вдалося створити uv_loop\n");
        return EXIT_FAILURE;
    }

    uv_timer_t timer_req;
    int status = uv_timer_init(loop, &timer_req);
    if (status < 0) {
        fprintf(stderr, "Помилка ініціалізації таймера: %s\n", uv_strerror(status));
        return EXIT_FAILURE;
    }

    /* Запуск таймера: спрацювати через 100 мс */
    uv_timer_start(&timer_req, timer_callback, 100, 0);

    /* Запуск основного циклу обробки подій */
    uv_run(loop, UV_RUN_DEFAULT);
    uv_loop_close(loop);

    printf("[netbridge] Роботу успішно завершено.\n");
    return EXIT_SUCCESS;
}
```
```cpp
// netbridge.cpp — Ідіоматична C++ реалізація з RAII-обгорткою над uv_loop
#include <iostream>
#include <memory>
#include <expected>
#include <system_error>
#include <uv.h>

class UvLoopRunner {
    uv_loop_t* loop_{nullptr};
public:
    UvLoopRunner() : loop_(uv_default_loop()) {}
    ~UvLoopRunner() noexcept {
        if (loop_) {
            uv_loop_close(loop_);
        }
    }
    UvLoopRunner(const UvLoopRunner&) = delete;
    UvLoopRunner& operator=(const UvLoopRunner&) = delete;
    UvLoopRunner(UvLoopRunner&& other) noexcept : loop_(other.loop_) {
        other.loop_ = nullptr;
    }
    UvLoopRunner& operator=(UvLoopRunner&& other) noexcept {
        if (this != &other) {
            if (loop_) uv_loop_close(loop_);
            loop_ = other.loop_;
            other.loop_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] uv_loop_t* get() const noexcept { return loop_; }
    void run() const noexcept {
        if (loop_) {
            uv_run(loop_, UV_RUN_DEFAULT);
        }
    }
};

static void timer_callback(uv_timer_t* handle) {
    auto uptime = uv_now(handle->loop);
    std::cout << "[netbridge-cpp] Сервіс працює. Час: " << uptime << " мс\n";
    uv_timer_stop(handle);
    uv_stop(handle->loop);
}

int main() {
    std::cout << "[netbridge-cpp] Ініціалізація C++ сервісу...\n";
    UvLoopRunner runner;
    if (!runner.get()) {
        std::cerr << "Не вдалося отримати системний loop\n";
        return 1;
    }

    uv_timer_t timer;
    if (int err = uv_timer_init(runner.get(), &timer); err < 0) {
        std::cerr << "Помилка таймера: " << uv_strerror(err) << "\n";
        return 1;
    }

    uv_timer_start(&timer, timer_callback, 100, 0);
    runner.run();
    std::cout << "[netbridge-cpp] Завершення.\n";
    return 0;
}
```
:::

---

### 5. Крок 4: Складання основного проєкту з вшиванням RUNPATH ($ORIGIN)

Щоб сервіс знайшов бібліотеку `libuv.so` у каталозі `/opt/netbridge/lib` незалежно від глобального системного кешу `/etc/ld.so.cache`, ми передаємо компонувальнику спеціальний прапорець `-Wl,-rpath,'$ORIGIN/../lib'`.

Зв'язування з нашою щойно зібраною залежністю здійснюється через експорт змінної `PKG_CONFIG_PATH`, яка перенаправляє `pkg-config` до створеного у `stage` каталогу:

```bash
cd /tmp/build-workspace/sources

# Спрямовуємо pkg-config на метадані у проміжному каталозі
export PKG_CONFIG_PATH="/tmp/build-workspace/stage/opt/netbridge/lib/pkgconfig"

# Перевірка: чи знаходить pkg-config нашу версію libuv
pkg-config --modversion libuv
# Повинно вивести: 1.48.0

# Компіляція та лінкування з прапорцем RUNPATH
gcc -O3 -Wall \
    $(pkg-config --cflags libuv) \
    netbridge.c \
    $(pkg-config --libs libuv) \
    -Wl,-rpath,'$ORIGIN/../lib' \
    -Wl,--enable-new-dtags \
    -o netbridge

# Перевірка заголовків скомпільованого ELF бінарника
readelf -d netbridge | grep -E '(RUNPATH|NEEDED)'
```

Вивід команди `readelf` підтверджує правильність структури залежностей:

```
 0x0000000000000001 (NEEDED)             Shared library: [libuv.so.1]
 0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
 0x000000000000001d (RUNPATH)            Library runpath: [$ORIGIN/../lib]
```

Прапорець `-Wl,--enable-new-dtags` змушує компонувальник створювати заголовок `DT_RUNPATH` замість застарілого `DT_RPATH`. Це дозволяє у разі крайньої потреби перевизначити шлях пошуку через `LD_LIBRARY_PATH` під час тестування (на відміну від `DT_RPATH`, який ігнорує змінні оточення).

---

### 6. Крок 5: Формування дерева пакунка та конфігурації

Копіюємо скомпільований бінарник та допоміжні системні конфігураційні файли у дерево `stage`:

```bash
# Створення цільових каталогів
mkdir -p /tmp/build-workspace/stage/opt/netbridge/{bin,etc}
mkdir -p /tmp/build-workspace/stage/etc/systemd/system

# Розміщення виконуваного файлу
cp netbridge /tmp/build-workspace/stage/opt/netbridge/bin/
chmod 755 /tmp/build-workspace/stage/opt/netbridge/bin/netbridge

# Створення файлу конфігурації
cat << 'EOF' > /tmp/build-workspace/stage/opt/netbridge/etc/netbridge.conf
# Конфігурація сервісу netbridge
PORT=8080
WORKERS=4
LOG_LEVEL=info
EOF

# Створення systemd сервіс-юніта
cat << 'EOF' > /tmp/build-workspace/stage/etc/systemd/system/netbridge.service
[Unit]
Description=NetBridge Custom Network Gateway
After=network.target

[Service]
Type=simple
ExecStart=/opt/netbridge/bin/netbridge
Restart=on-failure
User=nobody
Group=nogroup
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
EOF
```

---

### 7. Крок 6: Генерація нативного DEB-пакунка за допомогою `fpm`

Утиліта `fpm` (*Effing Package Manager*) дозволяє перетворити довільне дерево каталогів на повноцінний інсталяційний пакунок стандарту Debian (`.deb`) або Red Hat (`.rpm`) без написання складних багаторівневих скриптів `debian/rules` або SPEC-файлів RPM.

Вона пакує вміст каталогу `stage`, зберігаючи всі права доступу до файлів, власників та символічні посилання.

```bash
cd /tmp/build-workspace

# Генерація нативного DEB-пакунка
fpm -s dir -t deb \
    -n netbridge \
    -v 1.0.0 \
    --iteration 1 \
    --architecture x86_64 \
    --maintainer "DevOps Team <admin@example.com>" \
    --description "NetBridge High Performance Network Service" \
    --after-install - << 'EOF'
#!/bin/sh
systemctl daemon-reload
echo "[netbridge] Пакунок успішно встановлено в /opt/netbridge"
EOF \
    -C /tmp/build-workspace/stage \
    .
```

Якщо цільовою платформою є Red Hat Enterprise Linux, Rocky Linux або Fedora, генерація RPM виконується однією зміною цільового прапорця: `-t rpm`.

---

### 8. Крок 7: Тестування інсталяції, валідація та чисте видалення

Перевіряємо створений пакунок у системі, переконуючись у коректності роботи динамічного зв'язування та відсутності конфліктів:

```bash
# 1. Інсталяція через системний менеджер dpkg
sudo dpkg -i netbridge_1.0.0-1_amd64.deb

# 2. Перевірка цілісності та списку встановлених файлів
dpkg -L netbridge

# 3. Перевірка динамічного завантажувача утилітою ldd:
ldd /opt/netbridge/bin/netbridge
```

Зверніть увагу на вивід `ldd`:

```
linux-vdso.so.1 (0x00007ffe345fc000)
libuv.so.1 => /opt/netbridge/bin/../lib/libuv.so.1 (0x00007f59d1a00000)
libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f59d1800000)
/lib64/ld-linux-x86-64.so.2 (0x00007f59d1a40000)
```

Динамічний завантажувач автоматично підставив ізольовану бібліотеку `/opt/netbridge/lib/libuv.so.1` завдяки тегу `$ORIGIN/../lib`. Системна бібліотека `libc.so.6` при цьому використовується зі стандартного системного каталогу `/lib/x86_64-linux-gnu`.

```bash
# 4. Запуск програми
/opt/netbridge/bin/netbridge

# 5. Перевірка системного виклику через strace (перевірка пошуку файлів)
strace -e openat /opt/netbridge/bin/netbridge 2>&1 | grep libuv

# 6. Чисте видалення пакунка без залишку сміття в ОС:
sudo apt remove -y netbridge
```

Команда `apt remove` повністю видаляє всі файли з каталогу `/opt/netbridge` та сервіс із `/etc/systemd/system`, а системний реєстр `dpkg` фіксує видалення. Система повністю повертається у початковий стан, підтверджуючи повну ізоляцію та безпеку створеного артефакту.

---

### 9. Крайові випадки та типові пастки при роботі з $ORIGIN

Під час експлуатації бінарників з відносними шляхами пошуку бібліотек виникають специфічні нюанси, які необхідно враховувати системному інженеру:

1. **Символічні посилання на виконуваний файл:**
   Якщо користувач створює символічне посилання `/usr/local/bin/netbridge -> /opt/netbridge/bin/netbridge` і запускає програму через це посилання, ядро Linux розгортає `$ORIGIN` відносно **реального розташування двійкового файлу** (`/opt/netbridge/bin`), а не відносно шляху симлінка. Бібліотеки завантажуються коректно. Однак якщо програма запускається через шел-скрипт обгортку, яка не робить `exec`, `$ORIGIN` не буде активний для інтерпретатора.

2. **Захищені бінарники з бітом SUID / SGID:**
   З міркувань безпеки динамічний завантажувач `ld-linux.so` повністю ігнорує директиви `$ORIGIN` та `LD_LIBRARY_PATH` для двійкових файлів з активними бітами `setuid` або `setgid`. Якщо сервіс вимагає підвищених привілеїв, замість SUID слід використовувати системні механізми Linux Capabilities (наприклад, `setcap 'cap_net_bind_service=+ep' /opt/netbridge/bin/netbridge`) або налаштування `AmbientCapabilities=` у systemd-юніті.

3. **Створення симлінків SONAME через `ldconfig -n`:**
   Якщо бібліотека встановлюється вручну без використання `make install`, компонувальник може не створити обов'язкові символічні посилання (наприклад, `libuv.so.1 -> libuv.so.1.48.0`). У такому разі в каталозі `/opt/netbridge/lib` слід виконати команду `ldconfig -n /opt/netbridge/lib`, яка просканує файли ELF, зчитає поле `DT_SONAME` і створить необхідні посилання автоматично.
