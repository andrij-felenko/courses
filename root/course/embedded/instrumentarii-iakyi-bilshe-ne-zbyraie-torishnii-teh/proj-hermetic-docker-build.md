# ⚙️ Герметичний контейнерний конвеєр: збірка прошивки із зафіксованими хешами

Герметична збірка гарантує, що процес компіляції прошивки спирається виключно на зафіксовані вхідні файли, не має доступу до зовнішньої мережі під час компіляції та видає криптографічно тотожний бінарний образ на будь-якому хості. Нижче наведено завершену реалізацію контейнеризованого інструментарію з повною фіксацією версій, захистом від мовного дрейфу та автоматизованою верифікацією детермінізму.

### Архітектура та структура проєкту

Проєкт складається з п'яти взаємопов'язаних компонентів, що повністю усувають залежність від хостової операційної системи розробника та стану зовнішніх серверів:

1. `Dockerfile.builder` — декларація контейнера з фіксацією базового образу через OCI SHA-256 дайджест, перевіркою контрольної суми крос-компілятора та створенням автономного Python virtualenv.
2. `requirements.lock` — маніфест допоміжних Python-пакетів із хешами кожного двійкового архіву (`--require-hashes`), що унеможливлює підміну залежностей або неявне оновлення модулів.
3. `Makefile` — складальний сценарій із прапорцями нормалізації файлових шляхів, фіксованою часовою міткою `SOURCE_DATE_EPOCH` та детермінованим сортуванням списків файлів.
4. `build.sh` — хостовий скрипт-обгортка, який автоматично витягує дату останнього коміту в Git, монтує каталог проєкту та запускає збірку з повністю відключеним мережевим інтерфейсом (`--network none`).
5. `verify.sh` — утиліта верифікації детермінізму, яка виконує дві повністю незалежні збірки у різних тимчасових каталогах і порівнює хеші релізних файлів.

Така структура дозволяє ізолювати кожен шар складального процесу: операційну систему, крос-компілятор, інтерпретатор та сирцевий код. Якщо через кілька років збірку запускають на новій робочій станції або іншому сервері CI, образ контейнера завантажується з архіву або локального кешу й виконує компіляцію у тотожних умовах.

### 1. Декларація контейнера: `Dockerfile.builder`

Усі зовнішні бінарні пакети встановлюються з суворою перевіркою криптографічної цілісності. Використання символічних імен базових образів (наприклад, `ubuntu:22.04`) заборонено, оскільки вендори дистрибутивів періодично оновлюють їхній вміст, змінюючи версії системного `glibc` або інтерпретаторів.

Змінні середовища `LC_ALL=C.UTF-8` та `LANG=C.UTF-8` гарантують стабільну локаль, запобігаючи несподіваній зміні формату кодування символів або сортування рядків у системних утилітах. Крос-компілятор `arm-none-eabi-gcc` завантажується з перевіркою контрольної суми SHA-256 за допомогою `sha256sum -c`, що блокує збірку у разі пошкодження архіву або підміни джерела.

```dockerfile
# Фіксація базового образу через OCI digest замість плаваючого тегу
FROM ubuntu:22.04@sha256:3fbc632167424a6d997e7492beeb788b8aa9cc52c80309995537e477e54f073e

ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Встановлення мінімальних хостових утиліт без рекомендованих пакетів
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    xz-utils \
    make \
    ninja-build \
    python3 \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Встановлення крос-компілятора ARM GNU Toolchain 13.2.Rel1 із перевіркою хешу
ARG TOOLCHAIN_URL="https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-x86_64-arm-none-eabi.tar.xz"
ARG TOOLCHAIN_SHA256="6cd1bbc523e2b90be084ffcf6352b4337d331859400aa628905ba6157920545f"

RUN curl -fsSL -o /tmp/toolchain.tar.xz "${TOOLCHAIN_URL}" \
    && echo "${TOOLCHAIN_SHA256}  /tmp/toolchain.tar.xz" | sha256sum -c - \
    && mkdir -p /opt/toolchain \
    && tar -xf /tmp/toolchain.tar.xz -C /opt/toolchain --strip-components=1 \
    && rm /tmp/toolchain.tar.xz

ENV PATH="/opt/toolchain/bin:${PATH}"

# Створення ізольованого Python-середовища з фіксованими хешами
WORKDIR /opt/build-env
COPY requirements.lock /opt/build-env/
RUN python3 -m venv /opt/build-env/venv \
    && /opt/build-env/venv/bin/pip install --no-cache-dir --require-hashes -r requirements.lock

ENV PATH="/opt/build-env/venv/bin:${PATH}"

# Робочий каталог проєкту
WORKDIR /workspace
ENTRYPOINT ["/bin/bash", "-c"]
```

### 2. Маніфест Python-пакетів: `requirements.lock`

Кожен допоміжний пакет (генератор коду, утиліта злиття образів, парсер конфігурацій) фіксується точним хешем двійкового коліщатка (`wheel`). Прапорець `--require-hashes` змушує утиліту `pip` відмовитися від встановлення будь-якого пакета, якщо його хеш відрізняється від зазначеного в маніфесті хоча б на один біт. Це виключає підміну коду в мережі або оновлення мінорних залежностей.

```text
kconfiglib==14.1.0 \
    --hash=sha256:7e307775a7c29be60dd7bb6d3bb91c9ff6a9e1e7912bc097a8e7e1f5ce01878b
intelhex==2.3.0 \
    --hash=sha256:a6a575a6c11d04ebae33ebcaab0d03221b2bb502a9bca5e396eb5e6d0a7a3db0
jinja2==3.1.4 \
    --hash=sha256:bc377d907016146ae38047f4535a013c49e29f70eb6ed34f141607118b3d3732
markupsafe==2.1.5 \
    --hash=sha256:06e2012579a4da25f3de2e16c5144c3301b87932a3802d31041bcae637b88f95
```

### 3. Детермінований Makefile

Складальний файл налаштовує прапорці компіляції для усунення локальних шляхів розробника з об'єктних файлів, передає часову мітку `SOURCE_DATE_EPOCH` та вмикає стабільне сортування вихідних файлів. Використання функції `$(sort ...)` утиліти GNU Make усуває залежність від порядку зчитування вузлів файлової системи `readdir()`.

Прапорець `ARFLAGS := Dcr` вмикає детермінований режим створення статичних бібліотек `ar`, записуючи нулі замість UID/GID розробника та фіксовану дату Jan 1 1970 у заголовок кожного архіву `.a`.

```makefile
# Визначення часу збірки через SOURCE_DATE_EPOCH або фіксований дефолт
SOURCE_DATE_EPOCH ?= 1700000000

CC      := arm-none-eabi-gcc
OBJCOPY := arm-none-eabi-objcopy
AR      := arm-none-eabi-ar

# Нормалізація шляхів до файлів у DWARF та макросах
SRCDIR  := $(CURDIR)
CFLAGS  += -ffile-prefix-map=$(SRCDIR)=.
CFLAGS  += -fmacro-prefix-map=$(SRCDIR)=.
CFLAGS  += -fdebug-prefix-map=$(SRCDIR)=.
CFLAGS  += -Wl,--build-id=none
CFLAGS  += -DSOURCE_DATE_EPOCH=$(SOURCE_DATE_EPOCH)
CFLAGS  += -O2 -g -Wall -Wextra -Werror

# Детермінований режим архівації бібліотек
ARFLAGS := Dcr

# Стабільне сортування списку об'єктних файлів
SRCS    := $(sort $(wildcard src/*.c))
OBJS    := $(SRCS:.c=.o)

all: build/firmware.bin

build/firmware.elf: $(OBJS) | build
	$(CC) $(CFLAGS) -T linker.ld $(OBJS) -o $@

build/firmware.bin: build/firmware.elf
	$(OBJCOPY) -O binary $< $@

build:
	mkdir -p build

clean:
	rm -rf build src/*.o
```

### 4. Вбудована перевірка метаданих збірки у прошивці

Прошивка має містити секцію метаданих, що дозволяє runtime-коду повідомити, з яким саме хешем середовища та конфігурацією її було скомпільовано. Завдяки розміщенню у спеціальній секції пам'яті `.meta` діагностична утиліта або завантажувач перевіряють автентичність образу без необхідності розбирати повний ELF-файл.

:::tabs
```c
#include <stdint.h>
#include <string.h>

/* Структура детермінованих метаданих прошивки у фіксованій секції Flash */
typedef struct {
    uint32_t magic;
    uint32_t build_timestamp;
    char     git_commit[16];
    char     toolchain_id[16];
    uint32_t image_crc32;
} __attribute__((packed)) firmware_meta_t;

#define META_MAGIC 0x544F4F4C /* 'TOOL' */

#ifndef SOURCE_DATE_EPOCH
#define SOURCE_DATE_EPOCH 0U
#endif

/* Розміщення у спеціальній секції .meta для аудиту без розбору всього ELF */
__attribute__((section(".meta"), used))
const firmware_meta_t g_firmware_meta = {
    .magic           = META_MAGIC,
    .build_timestamp = (uint32_t)SOURCE_DATE_EPOCH,
    .git_commit      = "a1b2c3d4e5f60718",
    .toolchain_id    = "gcc-13.2.arm",
    .image_crc32     = 0xDEADBEEFU
};

int verify_build_metadata(const firmware_meta_t *meta) {
    if (meta == NULL || meta->magic != META_MAGIC) {
        return -1;
    }
    /* Перевірка, що дата збірки є коректною міткою епохи */
    if (meta->build_timestamp == 0U) {
        return -2;
    }
    return 0;
}
```
```cpp
#include <cstdint>
#include <string_view>
#include <span>

/* Безпечна C++ типізація детермінованих метаданих прошивки */
struct alignas(4) FirmwareMeta {
    uint32_t magic;
    uint32_t build_timestamp;
    char     git_commit[16];
    char     toolchain_id[16];
    uint32_t image_crc32;

    static constexpr uint32_t ExpectedMagic = 0x544F4F4CU; /* 'TOOL' */

    [[nodiscard]] constexpr bool isValid() const noexcept {
        return (magic == ExpectedMagic) && (build_timestamp != 0U);
    }

    [[nodiscard]] constexpr std::string_view getGitCommit() const noexcept {
        return std::string_view(git_commit, 16);
    }
};

#ifndef SOURCE_DATE_EPOCH
#define SOURCE_DATE_EPOCH 0U
#endif

[[gnu::section(".meta"), gnu::used]]
constexpr FirmwareMeta g_firmware_meta{
    .magic           = FirmwareMeta::ExpectedMagic,
    .build_timestamp = static_cast<uint32_t>(SOURCE_DATE_EPOCH),
    .git_commit      = {'a','1','b','2','c','3','d','4','e','5','f','6','0','7','1','8'},
    .toolchain_id    = {'g','c','c','-','1','3','.','2','.','a','r','m', 0, 0, 0, 0},
    .image_crc32     = 0xDEADBEEFU
};

static_assert(g_firmware_meta.isValid(), "Metadata structure must be valid at compile time");

int verify_metadata(std::span<const uint8_t> meta_bytes) noexcept {
    if (meta_bytes.size() < sizeof(FirmwareMeta)) {
        return -1;
    }
    const auto* meta = reinterpret_cast<const FirmwareMeta*>(meta_bytes.data());
    return meta->isValid() ? 0 : -2;
}
```
:::

### 5. Скрипт запуску з повною ізоляцією: `build.sh`

Скрипт отримує часову мітку з Git, монтує каталог проєкту як том, зіставляє UID/GID поточного користувача Linux і повністю блокує доступ до мережі під час компіляції. Параметр `--network none` гарантує, що жоден допоміжний скрипт або утиліта збірки не зможе непомітно завантажити оновлення з Інтернету.

```bash
#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG="embedded-builder:v1.4.2"
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Отримання часу останнього коміту в форматі UNIX Epoch
if [ -d ".git" ]; then
    SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"
else
    SOURCE_DATE_EPOCH="1700000000"
fi

echo "=== Запуск герметичної збірки (SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}) ==="

# Запуск збірки з вимкненою мережею та ізольованим середовищем
docker run --rm \
    --network none \
    --user "$(id -u):$(id -g)" \
    --env SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH}" \
    --volume "${WORKSPACE_DIR}:/workspace" \
    "${IMAGE_TAG}" \
    "make clean && make -j$(nproc)"

echo "=== Збірку завершено. Хеш релізу: ==="
sha256sum build/firmware.bin
```

### 6. Автоматизована перевірка детермінізму: `verify.sh`

Скрипт перевіряє, чи дві абсолютно незалежні збірки в різних тимчасових каталогах видають ідентичний бінарний хеш. Використання двох окремих каталогів у `/tmp` усуває вплив кешу файлової системи та залишкових об'єктних файлів, підтверджуючи повну незалежність результату.

```bash
#!/usr/bin/env bash
set -euo pipefail

DIR1="/tmp/build_test_1"
DIR2="/tmp/build_test_2"

rm -rf "${DIR1}" "${DIR2}"
mkdir -p "${DIR1}" "${DIR2}"

cp -r . "${DIR1}"
cp -r . "${DIR2}"

echo "Запуск збірки 1..."
(cd "${DIR1}" && ./build.sh > /dev/null)
HASH1=$(sha256sum "${DIR1}/build/firmware.bin" | awk '{print $1}')

echo "Запуск збірки 2..."
(cd "${DIR2}" && ./build.sh > /dev/null)
HASH2=$(sha256sum "${DIR2}/build/firmware.bin" | awk '{print $1}')

rm -rf "${DIR1}" "${DIR2}"

if [ "${HASH1}" = "${HASH2}" ]; then
    echo "УСПІХ: Збірки бінарно ідентичні!"
    echo "SHA-256: ${HASH1}"
    exit 0
else
    echo "ПОМИЛКА: Виявлено розбіжність бінарників!"
    echo "Build 1: ${HASH1}"
    echo "Build 2: ${HASH2}"
    exit 1
fi
```

### Діагностика розбіжностей бінарників

Якщо контрольні суми двох збірок відрізняються, для пошуку джерела недетермінізму використовують спеціалізовану утиліту `diffoscope`:

```bash
diffoscope build1/firmware.elf build2/firmware.elf
```

Утиліта рекурсивно розбирає ELF-структури та наочно показує, що саме викликало розбіжність:
- **Розбіжність у секції `.rodata`:** Зазвичай свідчить про наявність макросів `__DATE__` або `__TIME__`, які не були замінені на `SOURCE_DATE_EPOCH`.
- **Розбіжність у секціях `.debug_info` або `.debug_line`:** Вказує на те, що прапорець `-ffile-prefix-map` не покрив якісь сторонні бібліотеки або каталоги заголовків, і в об'єктний файл потрапив абсолютний хостовий шлях.
- **Розбіжність у порядку функцій у секції `.text`:** Свідчить про невідсортований список об'єктних файлів під час виклику компонувальника.

### Типові пастки реалізації

1. **Несумісність UID/GID розробника:** Якщо всередині контейнера збірка запускається під `root`, скомпільовані файли у хостовій теці `build/` отримують права `root:root`, блокуючи подальші дії без `sudo`. Прапорець `--user "$(id -u):$(id -g)"` вирішує цю проблему, змушуючи контейнер створювати файли від імені поточного користувача хоста.
2. **Незмивний Git-стан:** Наявність незакомічених локальних змін (`git status --porcelain`) призводить до генерації випадкових прапорців утилітами на зразок `git describe --dirty`. Релізний конвеєр має суворо блокувати збірку за наявності незбереженого стану.
3. **Недетерміноване компонування бібліотек:** Використання звичайного `ar` замість `ar D` призводить до збереження часу створення файлу `.a`, що змінює фінальний хеш ELF-файлу при кожному виклику.
