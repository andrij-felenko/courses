# 📋 Інтерфейси та протокол міграції: QMP, libvirt та формат потоку

Керування процесом живої міграції віртуальних машин в операційних системах сімейства Linux спирається на трирівневу ієрархію інтерфейсів: високорівневу систему кластерної оркестрації (libvirt API та утиліта `virsh`), низькорівневий асинхронний протокол керування гіпервізором (QEMU Machine Protocol, QMP) та бінарний формат передачі даних по мережі (QEMU Migration Stream Wire Protocol).

Кожен із цих рівнів визначає власний строгий контракт взаємодії, систему типів, скінченний автомат переходів станів та набір діагностичних кодів помилок.

## Керівний протокол QEMU Machine Protocol (QMP)

Протокол QMP являє собою повнодуплексний JSON-RPC інтерфейс на базі потокового Unix-сокета або TCP-порту. Через нього зовнішні керуючі процеси надсилають команди, змінюють параметри на льоту та отримують асинхронні системні події (QMP Events).

### 1. Команда запуску міграції (`migrate`)

Команда `migrate` ініціює вихідний процес передачі стану віртуальної машини на вказану цільову адресу.

```json
{
  "execute": "migrate",
  "arguments": {
    "uri": "tcp:192.168.10.20:49152",
    "blk": false,
    "inc": false,
    "detach": true,
    "resume": false
  }
}
```

#### Семантика та опис аргументів:
- `uri` (рядок, обов'язковий): Мережевий або системний уніфікований ідентифікатор ресурсу, що визначає цільовий транспортний протокол та адресу приймача.
- `blk` (булеве, застаріле): Примусове копіювання блокових пристроїв разом із пам'яттю (Block Migration). У сучасній інфраструктурі вимкнено на користь механізму NBD Drive Mirror.
- `inc` (булеве): Інкрементна міграція блокових пристроїв поверх спільного базового файлу знімка.
- `detach` (булеве): Виконання команди в асинхронному фоновому режимі (QMP негайно повертає успіх, не блокуючи сокет керування).
- `resume` (булеве): Спеціальний прапорець для відновлення перерваної міграції в режимі `postcopy-paused`.

#### Підтримувані схеми транспорту (URI):
| Схема транспорту | Синтаксис URI | Механізм передачі даних та системні вимоги |
| :--- | :--- | :--- |
| **TCP/IP** | `tcp:<host>:<port>` | Стандартний потоковий сокет TCP. Підтримує взаємну автентифікацію та шифрування через TLS x509. |
| **RDMA** | `rdma:<host>:<port>` | Прямий віддалений доступ до пам'яті через адаптери InfiniBand або RoCE v2. Забезпечує передачу без копіювання (Zero-Copy) та без участі CPU хоста. |
| **Unix Domain** | `unix:<socket-path>` | Локальний міжпроцесний сокет. Застосовується для міграції віртуальних машин між різними демонами або просторами назв на одному фізичному сервері. |
| **Exec pipe** | `exec:<command>` | Перенаправлення вихідного потоку міграції у стандартний ввід зовнішньої утиліти (наприклад, конвеєр `exec:ssh user@host qemu-system-x86_64 ...` або зовнішній компресор `zstd`). |
| **File Descriptor**| `fd:<fdname>` | Використання попередньо переданого дескриптора через команду QMP `getfd`. Дозволяє реалізувати кастомне керування мережевими з'єднаннями у привілейованих демонах. |

### 2. Керування розширеними можливостями (`migrate-set-capabilities`)

Ця команда конфігурує алгоритмічні модулі міграційного рушія. Можливості повинні виставлятися **до** відправки команди `migrate` як на вузлі-джерелі, так і на вузлі-приймачі.

```json
{
  "execute": "migrate-set-capabilities",
  "arguments": {
    "capabilities": [
      { "capability": "postcopy-ram", "state": true },
      { "capability": "auto-converge", "state": true },
      { "capability": "xbzrle", "state": true },
      { "capability": "multifd", "state": true },
      { "capability": "zero-copy-send", "state": true },
      { "capability": "dirty-bitmaps", "state": true },
      { "capability": "late-block-activate", "state": true }
    ]
  }
}
```

#### Детальний опис алгоритмічних прапорців:

1. **`postcopy-ram`:** Дозволяє системі виконувати динамічний перехід до парадигми Post-Copy за допомогою системного виклику ядра Linux `userfaultfd`. На цільовому хості гіпервізор реєструє виділену віртуальну пам'ять у дескрипторі `userfaultfd` та обробляє відсутні сторінки за запитом.
2. **`auto-converge`:** Активує алгоритм автоматичного виявлення стагнації міграції. Якщо протягом ітерації обсяг брудної пам'яті скорочується менш ніж на порогове значення, QEMU примусово знижує доступні процесорні кванти часу гостьових ядер vCPU.
3. **`xbzrle` (XOR-Based Zero Run-Length Encoding):** Вмикає диференційне стиснення сторінок пам'яті. У пам'яті гіпервізора створюється кеш попереднього стану сторінок. При повторному надсиланні обчислюється порозрядна різниця XOR між старою та новою версією сторінки, яка потім стискається RLE-алгоритмом.
4. **`multifd`:** Розбиває потік міграції пам'яті на `M` незалежних паралельних TCP-з'єднань або RDMA-черг. Це усуває вузьке місце однопотокової обробки сокета та дозволяє повністю утилізувати мережеві лінки 40–100 Гбіт/с.
5. **`zero-copy-send`:** Використовує прапорець `MSG_ZEROCOPY` системного виклику `sendmsg()`, дозволяючи мережевій карті вичитувати байти безпосередньо з фізичних сторінок гостя через DMA, минаючи буфери ядра хоста `sk_buff`.
6. **`dirty-bitmaps`:** Забезпечує копіювання збережених бітових масок модифікації віртуальних дисків, що є критично важливим для збереження безперервності інкрементного резервного копіювання СУБД.
7. **`late-block-activate`:** Забороняє цільовому хосту відкривати дискові образи на запис доти, доки джерело повністю не зупинить vCPU та не скине дискові черги, унеможливлюючи пошкодження файлової системи (Split-Brain на сховищі).

### 3. Тонке налаштування числових параметрів (`migrate-set-parameters`)

Команда встановлює ліміти швидкості, таймаути простою, параметри стиснення та конфігурацію процесорного тротлінгу.

```json
{
  "execute": "migrate-set-parameters",
  "arguments": {
    "max-bandwidth": 10737418240,
    "downtime-limit": 50,
    "multifd-channels": 8,
    "multifd-compression": "zstd",
    "multifd-zstd-level": 3,
    "cpu-throttle-initial": 20,
    "cpu-throttle-increment": 10,
    "cpu-throttle-max": 90,
    "xbzrle-cache-size": 1073741824,
    "max-postcopy-bandwidth": 0
  }
}
```

#### Довідник параметрів конфігурації:
| Параметр | Тип даних | Одиниця | За замовчуванням | Опис та правила налаштування |
| :--- | :--- | :--- | :--- | :--- |
| `max-bandwidth` | integer | байти/с | 32 МБ/с (`33554432`) | Верхня межа швидкості передачі даних. Для мереж 10 GbE виставляють `1250000000` (1.25 ГБ/с), для 100 GbE — `11500000000`. |
| `downtime-limit` | integer | мілісекунди | 300 мс | Гранично допустимий розрахунковий час простою у фазі Stop-and-Copy. Гіпервізор переходить до зупинки гостя лише тоді, коли залишок пам'яті можна передати за цей час. |
| `multifd-channels` | integer | кількість | 2 | Кількість паралельних робочих потоків та сокетів (рекомендовано від 4 до 16 залежно від кількості ядер хоста). |
| `multifd-compression` | string | перелік | `"none"` | Алгоритм стиснення сторінок у потоках Multifd: `"none"`, `"zlib"`, `"zstd"`. |
| `multifd-zstd-level` | integer | рівень (1..22) | 1 | Ступінь компресії Zstandard. Значення 1–3 забезпечують оптимальний баланс швидкості та коефіцієнта стиснення. |
| `cpu-throttle-initial`| integer | % | 20 | Початковий відсоток пригнічення процесорного часу гостя при старті Auto-Converge. |
| `cpu-throttle-increment`| integer | % | 10 | Величина, на яку збільшується тротлінг після кожного раунду без збіжності. |
| `cpu-throttle-max` | integer | % | 99 | Верхня межа тротлінгу (залишає гостю мінімум 1% CPU для уникнення падіння сторожових таймерів Watchdog). |
| `xbzrle-cache-size` | integer | байти | 64 МБ | Розмір кільцевого буфера для збереження сторінок попередніх раундів. Для СУБД рекомендується 1–2 ГБ. |
| `max-postcopy-bandwidth`| integer | байти/с | 0 (без ліміту) | Обмеження швидкості фонового потоку в режимі Post-Copy, щоб не забивати канал для on-demand запитів. |

### 4. Опитування телеметрії та стану (`query-migrate`)

Команда повертає поточний статус міграції та детальну статистику лічильників.

```json
{
  "execute": "query-migrate"
}
```

#### Приклад відповіді QMP та розбір полів:
```json
{
  "return": {
    "status": "active",
    "setup-time": 12,
    "total-time": 45210,
    "downtime": 0,
    "expected-downtime": 38,
    "ram": {
      "transferred": 68719476736,
      "remaining": 524288000,
      "total": 68719476736,
      "duplicate": 5242880,
      "skipped": 0,
      "normal": 16252928,
      "normal-bytes": 66571993088,
      "dirty-pages-rate": 14200,
      "mbps": 9850.4,
      "dirty-sync-count": 4,
      "postcopy-requests": 0
    },
    "compression": {
      "pages": 1420500,
      "busy": 0,
      "busy-rate": 0.0,
      "compressed-size": 582490120,
      "compression-rate": 2.44
    }
  }
}
```

- `status`: Поточний стан міграційного скінченного автомата (`setup`, `active`, `postcopy-active`, `postcopy-paused`, `completed`, `failed`, `cancelled`).
- `expected-downtime`: Розрахунковий час простою гостя на основі поточної швидкості мережі та залишку брудної пам'яті.
- `duplicate`: Кількість виявлених та оптимізованих нульових сторінок (Zero Pages), які не передавалися через мережу.
- `dirty-pages-rate`: Поточна швидкість модифікації пам'яті гостем (сторінок на секунду).
- `dirty-sync-count`: Кількість виконаних повних раундів сканування бітової маски пам'яті.
- `postcopy-requests`: Кількість сторінкових збоїв `userfaultfd`, які були запитані цільовим хостом у пріоритетному режимі.

### 5. Асинхронні події QMP (Event Notifications)

Під час виконання міграції гіпервізор відправляє асинхронні повідомлення у керівний сокет для сповіщення оркестратора про зміну стану або завершення чергового раунду:

- `MIGRATION`: Генерується при переході скінченного автомата в новий стан (наприклад, `{"event": "MIGRATION", "data": {"status": "postcopy-active"}}`).
- `MIGRATION_PASS`: Сигналізує про завершення повного проходу по бітовій масці брудних сторінок та початок наступної ітерації (містить номер раунду `pass`).
- `UNPLUG_PRIMARY`: Використовується в архітектурі Failover для відключення первинного фізичного SR-IOV пристрою перед стартом Stop-and-Copy.

### 6. Команди оперативного керування

- `migrate-start-postcopy`: Примусово переводить міграцію з Pre-Copy у режим Post-Copy, зупиняючи гість на джерелі та відновлюючи його на цілі.
- `migrate-cancel`: Скасовує процес міграції та повертає віртуальну машину до нормальної роботи на вихідному хості.
- `migrate-pause`: Призупиняє міграційний потік (переводить у стан `postcopy-paused` при розриві з'єднання).
- `migrate-recover`: Відновлює обірвану міграцію Post-Copy через новий канал передачі даних.

## Високорівневий інтерфейс libvirt та утиліта virsh

Демон `libvirtd` інкапсулює команди QMP у надійний п'ятифазний протокол узгодженої міграції між вузлами кластера:
1. **Begin:** Перевірка сумісності конфігурації, прапорців CPUID та наявності блокових сховищ на вихідному хості.
2. **Prepare:** Виділення порожнього домену на цільовому хості, створення мережевих портів (TAP/veth) та очікування вхідного сокета QEMU (`-incoming`).
3. **Perform:** Запуск передачі даних через QMP-команду `migrate` на вихідному хості.
4. **Finish:** Зупинка домену на джерелі, активація на цілі, запуск vCPU та надсилання Gratuitous ARP.
5. **Confirm:** Видалення тимчасових структур на джерелі після успішного підтвердження старту на цілі.

### Утиліта командного рядка `virsh migrate`

```bash
virsh migrate --live \
  --p2p \
  --postcopy \
  --auto-converge \
  --auto-converge-initial 20 \
  --auto-converge-increment 10 \
  --persistent \
  --undefinesource \
  --bandwidth 10000 \
  --parallel \
  --parallel-connections 8 \
  --verbose \
  production-db-vm qemu+tcp://node2.datacenter.lan/system
```

### Програмний інтерфейс libvirt API (C та C++)

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <libvirt/libvirt.h>

int initiate_vm_migration(virDomainPtr dom, const char *dest_host) {
    virTypedParameter params[4];
    int nparams = 0;

    params[nparams].field = VIR_MIGRATE_PARAM_URI;
    params[nparams].type = VIR_TYPED_PARAM_STRING;
    params[nparams].value.s = (char *)dest_host;
    nparams++;

    params[nparams].field = VIR_MIGRATE_PARAM_BANDWIDTH;
    params[nparams].type = VIR_TYPED_PARAM_ULLONG;
    params[nparams].value.ul = 10000; /* 10 Гбіт/с */
    nparams++;

    params[nparams].field = VIR_MIGRATE_PARAM_PARALLEL_CONNECTIONS;
    params[nparams].type = VIR_TYPED_PARAM_INT;
    params[nparams].value.i = 8;
    nparams++;

    unsigned int flags = VIR_MIGRATE_LIVE | 
                         VIR_MIGRATE_PEER2PEER | 
                         VIR_MIGRATE_POSTCOPY | 
                         VIR_MIGRATE_AUTO_CONVERGE | 
                         VIR_MIGRATE_PERSIST_DEST | 
                         VIR_MIGRATE_UNDEFINE_SOURCE;

    char dconnuri[256];
    snprintf(dconnuri, sizeof(dconnuri), "qemu+tcp://%s/system", dest_host);

    int ret = virDomainMigrateToURI3(dom, dconnuri, params, nparams, flags);
    if (ret < 0) {
        virErrorPtr err = virGetLastError();
        fprintf(stderr, "Помилка міграції: %s\n", err ? err->message : "Невідома помилка");
        return -1;
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <stdexcept>
#include <libvirt/libvirt.h>

namespace cluster {

class LibvirtDomainMigrator {
public:
    static void migrate_live(virDomainPtr dom, const std::string& dest_host) {
        if (!dom) {
            throw std::invalid_argument("Некоректний покажчик домену virDomainPtr");
        }

        std::vector<virTypedParameter> params;
        
        virTypedParameter p_uri{};
        p_uri.field = const_cast<char*>(VIR_MIGRATE_PARAM_URI);
        p_uri.type = VIR_TYPED_PARAM_STRING;
        p_uri.value.s = const_cast<char*>(dest_host.c_str());
        params.push_back(p_uri);

        virTypedParameter p_bw{};
        p_bw.field = const_cast<char*>(VIR_MIGRATE_PARAM_BANDWIDTH);
        p_bw.type = VIR_TYPED_PARAM_ULLONG;
        p_bw.value.ul = 10000; // 10 Гбіт/с
        params.push_back(p_bw);

        virTypedParameter p_par{};
        p_par.field = const_cast<char*>(VIR_MIGRATE_PARAM_PARALLEL_CONNECTIONS);
        p_par.type = VIR_TYPED_PARAM_INT;
        p_par.value.i = 8;
        params.push_back(p_par);

        constexpr unsigned int flags = VIR_MIGRATE_LIVE | 
                                      VIR_MIGRATE_PEER2PEER | 
                                      VIR_MIGRATE_POSTCOPY | 
                                      VIR_MIGRATE_AUTO_CONVERGE | 
                                      VIR_MIGRATE_PERSIST_DEST | 
                                      VIR_MIGRATE_UNDEFINE_SOURCE;

        std::string dconnuri = "qemu+tcp://" + dest_host + "/system";

        int ret = virDomainMigrateToURI3(dom, dconnuri.c_str(),
                                         params.data(), static_cast<int>(params.size()), flags);
        if (ret < 0) {
            virErrorPtr err = virGetLastError();
            std::string msg = err ? err->message : "Невідома помилка libvirt";
            throw std::runtime_error("Збій міграції віртуальної машини: " + msg);
        }
    }
};

} // namespace cluster
```
:::

## Бінарний формат мережевого потоку (QEMU Migration Wire Protocol)

Потік міграції є бінарним упакованим потоком, що передається через TCP/RDMA сокет. Він складається з глобального заголовка, послідовності типізованих секцій та фінального маркера завершення.

```
Структура бінарного потоку міграції QEMU:
┌────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────┐
│ MAGIC (0x5145564d) │ VERSION (0x00000003) │ SECTION_START (RAM)  │ SECTION_PART (Dirty) │ ...      │
├────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────┤
│ 4 байти (Big-Endian)│ 4 байти             │ Заголовок + Дамп     │ Змінені сторінки     │ Секції   │
└────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────┘
```

### 1. Глобальний заголовок файлу
- `QEMU_VM_FILE_MAGIC` (4 байти): `0x5145564d` (ASCII символи `"QEVM"` у порядку байтів Big-Endian);
- `QEMU_VM_FILE_VERSION` (4 байти): `0x00000003` (Поточна 3-я версія структури потоку).

### 2. Типи керуючих секцій (Section Tokens)
Кожна секція починається з 1-байтового маркера, що визначає її роль у життєвому циклі міграції:

| Байт | Символічна назва | Опис та формат корисного навантаження |
| :--- | :--- | :--- |
| `0x01` | `QEMU_VM_SECTION_START` | Початок нової секції (містить 4-байтний `section_id`, рядок імені пристрою, `instance_id`, `version_id` та початкові дані). |
| `0x02` | `QEMU_VM_SECTION_PART` | Інкрементна частина даних існуючої секції (передається під час активних раундів Pre-Copy). |
| `0x03` | `QEMU_VM_SECTION_END` | Фінальний блок даних секції, що передається у фазі Stop-and-Copy. |
| `0x04` | `QEMU_VM_SECTION_FULL` | Повна самодостатня секція для пристроїв, що не підтримують ітеративну передачу і зберігаються лише в момент зупинки гостя. |
| `0x7e` | `QEMU_VM_SECTION_FOOTER`| Маркер коректного закриття секції (містить 4-байтний `section_id` для верифікації цілісності потоку). |

### 3. Формат упакованих сторінок пам'яті (RAM Flags)
Для кожної сторінки передається 64-бітне ціле число. Молодші 12 бітів містять бітові прапорці стану, а старші 52 біти — зміщення сторінки в межах блоку пам'яті (RAMBlock):

| Прапорець | Бітова маска | Семантика корисного навантаження |
| :--- | :--- | :--- |
| `RAM_SAVE_FLAG_FULL` | `0x01` | Повний дескриптор блоку RAMBlock (містить ім'я блоку та його загальну довжину). |
| `RAM_SAVE_FLAG_EMPTY` | `0x02` | Порожній блок пам'яті без даних. |
| `RAM_SAVE_FLAG_PAGE` | `0x08` | Звичайна 4 КБ сторінка даних: безпосередньо за 64-бітним заголовком ідуть 4096 байтів сирих даних. |
| `RAM_SAVE_FLAG_ZERO` | `0x40` | Нульова сторінка: далі байти не передаються, цільовий гіпервізор самостійно очищає сторінку в пам'яті. |
| `RAM_SAVE_FLAG_EOS` | `0x10` | Кінець поточної ітерації передачі пам'яті (End of Iteration Stream). |
| `RAM_SAVE_FLAG_CONTINUE`| `0x20` | Наступна сторінка розташована безпосередньо за адресою попередньої (дозволяє пропускати 64-бітне зміщення). |
| `RAM_SAVE_FLAG_XBZRLE` | `0x40` | Сторінка стиснута алгоритмом XBZRLE: за заголовком іде 2 байти довжини та байти RLE-дельти. |
| `RAM_SAVE_FLAG_HOOK` | `0x80` | Системний виклик хука апаратного транспорту RDMA. |

### 4. Декларативний опис стану віртуальних пристроїв (`VMStateDescription`)

Стан кожного віртуального пристрою описується за допомогою декларативних макросів, що автоматизують серіалізацію полів структури та підтримують зворотну сумісність між різними версіями емуляторів:

:::tabs
```c
#include <stdint.h>

typedef struct SerialState {
    uint16_t divider;
    uint8_t  rbr;
    uint8_t  ier;
    uint8_t  iir;
    uint8_t  lcr;
    uint8_t  mcr;
    uint8_t  lsr;
    uint8_t  msr;
    uint8_t  scr;
} SerialState;

/* Декларативний опис структури серіалізації для QEMU VMState */
typedef struct VMStateField {
    const char *name;
    size_t offset;
    size_t size;
} VMStateField;

typedef struct VMStateDescription {
    const char *name;
    int version_id;
    int minimum_version_id;
    const VMStateField *fields;
} VMStateDescription;

static const VMStateField vmstate_serial_fields[] = {
    { "divider", offsetof(SerialState, divider), sizeof(uint16_t) },
    { "rbr",     offsetof(SerialState, rbr),     sizeof(uint8_t) },
    { "ier",     offsetof(SerialState, ier),     sizeof(uint8_t) },
    { "iir",     offsetof(SerialState, iir),     sizeof(uint8_t) },
    { "lcr",     offsetof(SerialState, lcr),     sizeof(uint8_t) },
    { "mcr",     offsetof(SerialState, mcr),     sizeof(uint8_t) },
    { "lsr",     offsetof(SerialState, lsr),     sizeof(uint8_t) },
    { "msr",     offsetof(SerialState, msr),     sizeof(uint8_t) },
    { "scr",     offsetof(SerialState, scr),     sizeof(uint8_t) },
    { NULL, 0, 0 }
};

static const VMStateDescription vmstate_serial = {
    .name = "serial",
    .version_id = 3,
    .minimum_version_id = 2,
    .fields = vmstate_serial_fields
};
```
```cpp
#include <string_view>
#include <vector>
#include <cstddef>
#include <cstdint>

namespace vmstate {

struct SerialState {
    uint16_t divider{0};
    uint8_t  rbr{0};
    uint8_t  ier{0};
    uint8_t  iir{0};
    uint8_t  lcr{0};
    uint8_t  mcr{0};
    uint8_t  lsr{0};
    uint8_t  msr{0};
    uint8_t  scr{0};
};

struct FieldDescriptor {
    std::string_view name;
    size_t offset;
    size_t size;
};

struct DeviceStateDescription {
    std::string_view name;
    int version_id{1};
    int minimum_version_id{1};
    std::vector<FieldDescriptor> fields;
};

inline const DeviceStateDescription kSerialStateDesc{
    "serial",
    3,
    2,
    {
        { "divider", offsetof(SerialState, divider), sizeof(uint16_t) },
        { "rbr",     offsetof(SerialState, rbr),     sizeof(uint8_t) },
        { "ier",     offsetof(SerialState, ier),     sizeof(uint8_t) },
        { "iir",     offsetof(SerialState, iir),     sizeof(uint8_t) },
        { "lcr",     offsetof(SerialState, lcr),     sizeof(uint8_t) },
        { "mcr",     offsetof(SerialState, mcr),     sizeof(uint8_t) },
        { "lsr",     offsetof(SerialState, lsr),     sizeof(uint8_t) },
        { "msr",     offsetof(SerialState, msr),     sizeof(uint8_t) },
        { "scr",     offsetof(SerialState, scr),     sizeof(uint8_t) }
    }
};

} // namespace vmstate
```
:::

## Скінченний автомат станів міграції (State Machine)

Процес міграції управляється детермінованим скінченним автоматом:

```
Скінченний автомат станів міграції:
  [ none ] ➔ [ setup ] ➔ [ active ] ───────────➔ [ pre-switchover ] ➔ [ device ] ➔ [ completed ]
                             │                            │
                             ├─➔ [ cancelling ] ➔ [ cancelled ]
                             ├─➔ [ postcopy-active ] ────➔ [ postcopy-paused ] ➔ [ postcopy-recover ]
                             └─➔ [ failed ]
```

### Опис та інваріанти станів:
1. `none`: Початковий стан, структури не виділені, міграція не ініційована.
2. `setup`: Встановлення TCP/RDMA з'єднань, TLS-рукостискання, реєстрація слотів пам'яті.
3. `active`: Виконання раундів попереднього копіювання пам'яті (Pre-Copy), гість працює на вихідному хості.
4. `pre-switchover`: Фаза підготовки до зупинки гостя (очікування завершення синхронізації блокових пристроїв).
5. `device`: Фаза Stop-and-Copy. Процесори vCPU призупинені, передаються фінальні залишки пам'яті та стан регістрів віртуальних пристроїв.
6. `postcopy-active`: Віртуальна машина виконується на цільовому вузлі, триває фонова докачка пам'яті та обробка сторінкових збоїв через `userfaultfd`.
7. `postcopy-paused`: Мережеве з'єднання обірвалося під час роботи в режимі Post-Copy; виконання гостя призупинено, очікується команда `migrate-recover`.
8. `completed`: Міграція успішно завершена, домен на вихідному хості знищено.
9. `failed`: Фатальна помилка (розрив мережі, відмова диска, несумісність апаратних прапорців CPUID).
10. `cancelled`: Міграція була коректно перервана адміністратором через виклик `migrate-cancel`.

## Безпека та взаємне шифрування каналів (mTLS)

У хмарних дата-центрах передача гігабайтів відкритої оперативної пам'яті через спільну мережу становить критичну загрозу безпеці (витік паролів, ключів шифрування, сесій СУБД або модифікація пам'яті атакою типу Man-in-the-Middle).

Сучасний протокол міграції QEMU підтримує вбудоване шифрування **mTLS (Mutual TLS)** на основі сертифікатів x509:

1. **Взаємна автентифікація (Mutual Authentication):** І хост-джерело, і хост-приймач перевіряють цифрові підписи сертифікатів один одного через спільний довірений центр сертифікації (Certificate Authority, CA).
2. **Конфігурація об'єкта TLS у QMP:** Перед запуском міграції створюється об'єкт облікових даних:
```json
{
  "execute": "object-add",
  "arguments": {
    "qom-type": "tls-creds-x509",
    "id": "tls_mig",
    "props": {
      "dir": "/etc/pki/qemu",
      "endpoint": "client",
      "verify-peer": true
    }
  }
}
```
3. **Активація у параметрах міграції:**
```json
{
  "execute": "migrate-set-parameters",
  "arguments": {
    "tls-creds": "tls_mig",
    "tls-hostname": "node2.datacenter.lan"
  }
}
```
4. **Апаратне прискорення AES-NI:** Завдяки використанню апаратних інструкцій процесора AES-NI та підтримці Kernel TLS (kTLS) навантаження на CPU при шифруванні потоку 10–40 Гбіт/с знижується до менш ніж 5% процесорного часу.

## П'ятифазний протокол RPC libvirt та обмін куками (Cookies)

Взаємодія між демонами `libvirtd` на двох серверах кластера організована у вигляді строгого п'ятифазного протоколу (libvirt Migration Protocol v3). На кожному етапі демони обмінюються бінарними XML-куками (Migration Cookies), що містять метадані про мережеві порти, топологію сховищ та стан графічних консолей (SPICE/VNC).

```
Послідовність викликів п'ятифазного протоколу libvirt:
  Джерело (Source Node)                     Ціль (Destination Node)
  ─────────────────────                     ───────────────────────
  1. Begin3() ─────────────────────────────➔ [ Перевірка сумісності XML, блокування домену ]
  2. Prepare3() ───────────────────────────➔ [ Створення контейнера ВМ, запуск qemu -incoming ]
     │                                           │ (Повертає Prepare-Cookie з портом QEMU)
  3. Perform3() ➔ [ Старт QMP migrate ] ────➔ [ Прийом потоку RAM ]
  4. Finish3() ────────────────────────────➔ [ Зупинка прийому, активація vCPU, GARP ]
     │                                           │ (Повертає Finish-Cookie про успішний старт)
  5. Confirm3() ➔ [ Знищення домену на джерелі ]
```

### Типи та призначення міграційних кук (Migration Cookies):
- `VIR_MIGRATE_COOKIE_MEMORY`: Містить інформацію про виділені діапазони пам'яті, конфігурацію NUMA-вузлів та параметри HugePages.
- `VIR_MIGRATE_COOKIE_GRAPHICS`: Передає параметри безшовного перемикання графічних клієнтів SPICE/VNC (Seamless Handover), дозволяючи адміністратору не втрачати відкрите вікно консолі під час переїзду.
- `VIR_MIGRATE_COOKIE_NBD`: Передає призначені TCP-порти вбудованого NBD-сервера для паралельної міграції дисків.
- `VIR_MIGRATE_COOKIE_NETWORK`: Передає списки віртуальних мережевих інтерфейсів та стан фільтрів nwfilter.

## Жива міграція без спільного сховища (NBD Storage Migration)

Якщо віртуальна машина використовує локальні NVMe/SATA диски замість спільної SAN/Ceph мережі, міграція виконується у комбінованому режимі за допомогою протоколу **NBD (Network Block Device)** та підсистеми **Drive Mirror**:

1. **Запуск вбудованого NBD-сервера:** На цільовому хості QEMU запускає слухач NBD через команду `nbd-server-start`.
2. **Експорт цільового диска:** Команда `nbd-server-add` експортує порожній цільовий віртуальний диск.
3. **Активація блокового дзеркалювання (Blockdev Mirror):** На вихідному хості QEMU починає копіювання секторів диска на NBD-сервер цілі за допомогою команди `blockdev-mirror`.
4. **Синхронізація брудних блоків:** Поки йде копіювання, нові операції запису гостя записуються одночасно на локальний диск джерела та по мережі на цільовий NBD-сервер.
5. **Фінальне перемикання:** Після завершення копіювання диска починається класична міграція RAM. У фазі Stop-and-Copy обидва потоки (дисковий і сторінковий) синхронно фіксуються.

## Апаратна міграція прокинутих пристроїв (VFIO Migration v2)

Традиційно пряме прокидання обладнання (PCIe Device Passthrough для GPU, FPGA, SmartNIC) робило живу міграцію неможливою, оскільки стан фізичних регістрів кремнієвого чіпа був прихований від гіпервізора.

Стандарт ядра Linux **VFIO Migration v2** (ядро 5.18+) визначив уніфікований апаратний скінченний автомат для драйверів пристроїв вендорів (NVIDIA vGPU, Intel QAT, AMD Instinct):

### Стан апаратного автомата VFIO (`enum vfio_device_mig_state`):
- `VFIO_DEVICE_STATE_RUNNING`: Пристрій активно обслуговує запити гостя; апаратний модуль відстежує брудні сторінки пам'яті через IOMMU dirty logging.
- `VFIO_DEVICE_STATE_STOP`: Пристрій призупинено, черги DMA заморожені.
- `VFIO_DEVICE_STATE_STOP_COPY`: Фаза Stop-and-Copy: драйвер вичитує внутрішній бінарний контекст чіпа (контексти шейдерів, таблиці DMA-трансляцій, регістри) та передає його у міграційний потік через системний виклик `read()`.
- `VFIO_DEVICE_STATE_RESUMING`: Цільовий хост завантажує отриманий бінарний стан у фізичний пристрій через системний виклик `write()`.
- `VFIO_DEVICE_STATE_ERROR`: Апаратний збій відновлення стану, що викликає безпечну аварійну зупинку.

## Міграція вкладеної віртуалізації (Nested KVM State)

Якщо усередині віртуальної машини L1 запущено власний гіпервізор KVM, який виконує вкладеного гостя L2 (Nested Virtualization), звичайної серіалізації регістрів процесора недостатньо: процесор хоста зберігає стан тіньових структур керування віртуальною машиною (**VMCS Shadowing** на Intel або **VMCB Clean Bits** на AMD).

Для підтримки живої міграції вкладених гіпервізорів ядро Linux підтримує спеціальні системні виклики `ioctl`:
- `KVM_GET_NESTED_STATE`: Зчитує з ядра L0 повний бінарний стан вкладеного гіпервізора L1, включаючи активний покажчик `vmcs12`, кешовані тіньові поля VMCS та стан перехоплення переривань гостя L2.
- `KVM_SET_NESTED_STATE`: Завантажує отриманий стан у ядро L0 цільового хоста до виконання першої інструкції `VM-Entry`.

Під час міграції QEMU серіалізує структуру `struct kvm_nested_state` у спеціальну субсекцію `vmstate_nested_state`. Якщо цільовий хост має старішу версію ядра або іншу мікроархітектуру процесора, яка не підтримує відповідні біти VMCS, міграція безпечно відхиляється на етапі валідації з помилкою `KVM_SET_NESTED_STATE failed: Invalid argument`.

## Рецепти конфігурації для мереж 10 GbE, 25 GbE та 100 GbE

Налаштування параметрів міграції повинно строго відповідати пропускній здатності та затримкам мережевої інфраструктури:

### 1. Мережа 10 GbE (MTU 1500 / 9000, 1.1 ГБ/с корисного навантаження):
```bash
# Оптимально: 4 канали Multifd, увімкнений Auto-Converge, початковий тротлінг 20%
virsh migrate-setmaxbandwidth production-vm 1100
# QMP:
# migrate-set-parameters: multifd-channels=4, cpu-throttle-initial=20, downtime-limit=50
```

### 2. Мережа 25 GbE / 40 GbE (MTU 9000 Jumbo Frames, 2.8–4.5 ГБ/с):
```bash
# Оптимально: 8 каналів Multifd з компресією zstd-1, вимкнений тротлінг на перших раундах
# QMP:
# migrate-set-parameters: multifd-channels=8, multifd-compression=zstd, multifd-zstd-level=1, downtime-limit=30
```

### 3. Мережа 100 GbE / 200 GbE RDMA (InfiniBand / RoCE, Zero-Copy):
```bash
# Оптимально: 16 каналів Multifd, увімкнений zero-copy-send, компресія ВИМКНЕНА (CPU не встигає стискати на такій швидкості)
# QMP:
# migrate-set-capabilities: multifd=true, zero-copy-send=true, postcopy-ram=true
# migrate-set-parameters: multifd-channels=16, multifd-compression=none, max-bandwidth=11500000000, downtime-limit=20
```

## Довідник діагностики та кодів помилок

| Помилка / Симптом | Системна причина | Практичні кроки вирішення |
| :--- | :--- | :--- |
| `QERR_MIGRATION_ACTIVE` | Спроба ініціювати міграцію, коли інша міграційна сесія вже перебуває в активному стані. | Дочекатися завершення поточної операції або виконати скасування через `migrate-cancel`. |
| `feature-words mismatch` | Несумісність прапорців CPUID між процесорами хостів (наприклад, наявність AVX-512 на джерелі та відсутність на цілі). | Використовувати узгоджену базову модель процесора у конфігурації XML (наприклад, `<cpu mode='custom' model='Skylake-Server'/>`). |
| `Failed to load VMState` | Розбіжність версій віртуальних пристроїв або непідтримувані субсекції між різними релізами QEMU. | Оновити пакети QEMU на цільовому хості до версії, не старішої за вихідний вузол. |
| `Postcopy not supported` | Ядро цільового сервера зібране без прапорця `CONFIG_USERFAULTFD` або системний вимикач `vm.unprivileged_userfaultfd=0`. | Увімкнути системний прапорець `sysctl -w vm.unprivileged_userfaultfd=1` або запустити QEMU з правами `CAP_SYS_PTRACE`. |
| `Migration network timeout`| Пропускна здатність мережевого каналу менша за швидкість генерації брудної пам'яті (`D > B`). | Збільшити параметр `max-bandwidth`, увімкнути `auto-converge` або переключитися в режим `--postcopy`. |
| `Tls handshake failed` | Розбіжність сертифікатів x509, прострочений термін дії або невідповідність Common Name (CN). | Перевірити актуальність сертифікатів у теці `/etc/pki/qemu/` та синхронізацію системного часу NTP. |
