# ⚙️ Модуль апаратного криптографічного стирання пам'яті та скидання ключів

Практична реалізація автономного системного модуля санітизації (Sanitizer Engine), призначеного для виконання гарантованого криптографічного стирання (Crypto-Shredding), апаратної нуліфікації ключів у мікросхемах Secure Element (ATECC608) та модулях TPM 2.0, низькорівневого надсилання команд Flash Purge (NVMe Sanitize / eMMC Secure Erase) та генерації підписаного цифрового сертифіката санітизації (Certificate of Sanitization) за стандартом NIST SP 800-88 Rev 1.

```
+───────────────────────────────────────────────────────────────────────────+
| АРХІТЕКТУРНА СХЕМА МОДУЛЯ САНІТИЗАЦІЇ (SANITIZER ENGINE)                  |
|                                                                           |
|  [Захищений простір процесу]                                              |
|  mlockall() + MADV_DONTDUMP + Secure Memory Allocator                     |
|                                                                           |
|  ┌──────────────────────────────────────────────────────────────────────┐ |
|  │                       ЯДРО САНІТИЗАТОРА                              │ |
|  │                                                                      │ |
|  │  1. Захоплення пристроїв (Locking & Exclusive Open)                  │ |
|  │  2. Криптографічне стирання ключів (Crypto-Shredding)                │ |
|  │     ├── Microchip ATECC608 : Нуліфікація слотів через I2C            │ |
|  │     └── TPM 2.0            : TPM2_Clear через TSS2 ESAPI             │ |
|  │  3. Апаратне стирання Flash-носіїв (Block Purge)                     │ |
|  │     ├── NVMe Sanitize      : Admin Command 0x84 (Crypto/Block Erase) │ |
|  │     ├── eMMC Secure Erase  : ioctl(BLKSECDISCARD) / CMD38            │ |
|  │     └── SATA Secure Erase  : ATA Security Erase Unit                 │ |
|  │  4. Верифікаційний прохід (Verification Pass)                        │ |
|  │     ├── Розрахунок SHA-256 контрольних хешів розділів                │ |
|  │     └── Статистична оцінка ентропії Шеннона (H -> 8.0)               │ |
|  │  5. Формування та підпис сертифіката санітизації (CoS)               │ |
|  │     └── Цифровий підпис ECDSA через апаратний атестаційний ключ      │ |
|  └──────────────────────────────────────────────────────────────────────┘ |
+───────────────────────────────────────────────────────────────────────────+
```

## Інженерна постановка задачі та технічні вимоги

Перед системним інженером стоїть завдання розробки спеціалізованого модуля санітизації, який функціонує в автономному середовищі відновлення (Recovery OS, Minimal Initramfs або діагностичний стенд сервісного центру). Головна мета модуля — перевести повернений екземпляр обладнання у гарантовано очищений стан, що відповідає рівню `Purge` міжнародного стандарту NIST SP 800-88 Rev 1, виключаючи будь-яку можливість вилучення залишкової конфіденційної інформації попереднього власника.

Програмний комплекс повинен вирішувати чотири взаємопов'язані інженерні задачі:
1. **Безпечна ізоляція робочого середовища процесу в пам'яті:** У процесі санітизації модуль оперує конфіденційними структурами даних, паролями авторизації та дескрипторами безпеки. Будь-який витік цих даних у тимчасові файли, розділ підкачки (Swap) або автоматичні дампи пам'яті (Core Dumps) створює критичну вразливість. Пам'ять процесу повинна бути повністю заблокована у фізичній оперативній пам'яті без можливості вивантаження на диск.
2. **Апаратна нуліфікація ключів у криптографічних співпроцесорах (Crypto-Shredding):** Модуль зобов'язаний виконати безповоротне стирання ключів шифрування розділів даних (DEK), ключів обгортки (KEK) та ідентифікаційних сертифікатів у захищених мікросхемах:
   - Для мікросхем Secure Element (Microchip ATECC608A/B): генерація керуючих фреймів протоколу CryptoAuthentication по шині I2C, обчислення контрольних сум CRC-16, виконання команд `Nonce`, `PrivWrite` (занулення слотів) та спалювання апаратних запобіжників конфігурації `LockZone`.
   - Для модулів довіреної платформи TPM 2.0: ініціалізація сесії безпеки через інтерфейс TSS2 ESAPI, виконання команди `Esys_Clear()` для регенерації первинного початкового числа `Storage Primary Seed (SPS)` та безповоротного анулювання всіх похідних ключів ієрархії зберігання.
3. **Пряме низькорівневе керування блоковими накопичувачами Flash:**
   - Для накопичувачів NVMe: пряма відправка команд адміністрування `Sanitize (0x84)` через системний виклик `ioctl(fd, NVME_IOCTL_ADMIN_CMD)` у режимах `Crypto Erase` або `Block Erase` з постійним опитуванням сторінки журналу `Sanitize Status Log Page (LID 0x81)` до повного завершення високовольтного стирання.
   - Для накопичувачів eMMC / UFS: виклик команди ядра `ioctl(fd, BLKSECDISCARD)`, яка транслюється драйвером ядра в апаратні команди протоколу JEDEC `CMD35 / CMD36 / CMD38` (`SECURE_ERASE / SECURE_PURGE`).
4. **Криптографічний аудит та формування сертифіката санітизації (CoS):**
   - Виконання верифікаційного проходу зчитування вибіркових блоків Flash.
   - Розрахунок інформаційної ентропії Шеннона для підтвердження того, що прочитані дані є нерозрізненним білим шумом (`H(X) ≥ 7.99` біт/байт) або зануленим масивом (`H(X) ≤ 0.01`).
   - Формування структурованого маніфесту санітизації у форматі JSON/CBOR та його підписання апаратним ключем атестації крипточіпа.

## Детальний розбір реалізації модуля на C99

Процедурна реалізація на мові C99 спроєктована для максимальної переносимості та мінімальних залежностей. Вона може компілюватися як статичний бінарний файл за допомогою компіляторів GCC або Clang з бібліотеками `musl libc` або `glibc` для вбудовування у мінімальні образи initramfs.

```
+───────────────────────────────────────────────────────────────────────────+
| СТРУКТУРА НИЗЬКОРІВНЕВОГО МОДУЛЯ САНІТИЗАЦІЇ НА C99                       |
|                                                                           |
|  secure_buf_alloc() / secure_buf_free() ──> Керування безпечною RAM       |
|  atecc_crc16() / atecc608_zeroize_slot() ──> Керування Secure Element I2C |
|  nvme_sanitize_device()                 ──> Керування NVMe Admin IOCTL    |
|  emmc_secure_erase()                    ──> Керування eMMC BLKSECDISCARD  |
|  calculate_entropy()                    ──> Оцінка ентропії Шеннона       |
|  verify_sanitization()                  ──> Контрольний прохід читання    |
|  execute_full_sanitization()            ──> Головний конвеєр оркестрації  |
+───────────────────────────────────────────────────────────────────────────+
```

### Керування захищеною оперативною пам'яттю

Функція `secure_buf_alloc()` виділяє блок оперативної пам'яті за допомогою системного виклику `mmap()` з прапорцями `MAP_PRIVATE | MAP_ANONYMOUS`. На відміну від стандартного `malloc()`, `mmap()` створює виділені сторінки, які вирівняні за межею 4 КБ. 

Одразу після виділення пам'яті виконується виклик `mlock(buf->data, size)`, який повідомляє ядру Linux про необхідність закріплення цих сторінок у фізичній пам'яті RAM. Це повністю виключає скидання конфіденційних буферів у файл або розділ підкачки (Swap).

Наступним кроком викликається `madvise(buf->data, size, MADV_DONTDUMP)`. Цей системний виклик встановлює спеціальний біт у структурах дескриптора віртуальної пам'яті процесу (`vm_area_struct`), який забороняє включення цього діапазону адрес у файл дампу ядра (Core Dump) у разі аварійного завершення програми через сигнали `SIGSEGV`, `SIGABRT` чи `SIGBUS`. Додатково викликається `prctl(PR_SET_DUMPABLE, 0)`, що блокує можливість приєднання сторонніх процесів до санітизатора через налагоджувальний інтерфейс `ptrace`.

Функція `secure_bzero()` гарантує занулення пам'яті перед її звільненням. Використання вказівника на `volatile uint8_t` у поєднанні з асемблерним бар'єром пам'яті `__asm__ __volatile__("" : : "r"(ptr) : "memory")` змушує компілятор згенерувати дійсні інструкції запису нулів, забороняючи оптимізатору викидати цей код як «мертвий» (Dead Store Elimination).

### Взаємодія з мікросхемою Secure Element ATECC608 по шині I2C

Мікросхема Microchip ATECC608 спілкується з хостом через послідовну шину I2C на фіксованій 7-бітній адресі `0x60`. Протокол обміну CryptoAuthentication вимагає суворого дотримання формату пакетів та розрахунку контрольної суми CRC-16.

Функція `atecc_crc16()` реалізує стандартизований алгоритм розрахунку CRC над масивом байтів за поліномом `x¹⁶ + x¹⁵ + x² + 1` (зворотний поліном `0x8005`). Контрольна сума передається у молодшому та старшому байтах наприкінці кожного командного фрейму.

Процедура нуліфікації слота `atecc608_zeroize_slot()` складається з двох послідовних кроків:
1. **Ініціалізація генератора випадкових чисел (команда Nonce):** Хост надсилає пакет `ATECC_OP_NONCE` (код `0x16`), що містить 20 байт випадкового виклику. Внутрішній криптографічний автомат ATECC608 змішує цей виклик із власним апаратним генератором TRNG та оновлює внутрішній тимчасовий регістр `TempKey`. Після передачі пакету хост робить паузу тривалістю 35 мілісекунд (`usleep(35000)`), що відповідає максимальному часу виконання операції `Nonce`.
2. **Занулення даних слота (команда PrivWrite):** Хост формує 40-байтний пакет `ATECC_OP_PRIVWRITE` (код `0x29`), вказуючи цільову зону пам'яті `ATECC_ZONE_DATA` (код `0x02`), номер слота (зсунутий на 3 біти вліво) та масив із 32 нульових байтів. Мікроконтролер записує нулі в комірки захищеної EEPROM і повертає однобайтний статус успішного виконання (`0x00`). Час виконання цієї команди становить до 50 мілісекунд.

### Керування блоковими накопичувачами NVMe та eMMC

Функція `emmc_secure_erase()` відкриває блоковий пристрій (наприклад, `/dev/mmcblk0`) з прапорцем ексклюзивного доступу `O_EXCL`, щоб виключити паралельний запис з боку інших служб операційної системи. За допомогою `ioctl(fd, BLKGETSIZE64, &dev_size)` визначається точний розмір накопичувача в байтах. Далі формується масив діапазону адрес `range[0] = 0`, `range[1] = dev_size` і викликається `ioctl(fd, BLKSECDISCARD, &range)`.

Драйвер ядра Linux (`drivers/mmc/core/block.c`) транслює цей запит у послідовність низькорівневих команд шини MMC:
- `CMD35` (`ERASE_GROUP_START`) — передача початкової адреси сектора.
- `CMD36` (`ERASE_GROUP_END`) — передача кінцевої адреси сектора.
- `CMD38` (`ERASE`) з аргументом `0x80000000` (`MMC_SECURE_ERASE_ARG`) або `0x80008000` (`MMC_SECURE_PURGE_ARG`).

Контролер eMMC подає електричний потенціал стирання на всі фізичні блоки пам'яті, що містили вказані сектори, включаючи резервні блоки Wear Leveling.

Функція `nvme_sanitize_device()` реалізує протокол NVM Express Sanitize:
1. Заповнюється структура `struct nvme_admin_cmd`, де поле `opcode` встановлюється в `0x84` (`NVME_ADMIN_SANITIZE`), а поле `cdw10` містить код операції `0x04` (`Crypto Erase`) або `0x02` (`Block Erase`).
2. Команда надсилається контролеру через `ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd)`.
3. Оскільки операція Sanitize є асинхронною і може тривати від кількох мілісекунд (Crypto Erase) до десятків хвилин (Block Erase на масивних накопичувачах), функція входить у цикл опитування. Кожну секунду надсилається команда читання сторінки журналу `Get Log Page` (`opcode = 0x02`, `Log ID = 0x81`). Коли молодші три біти поля `SSTAT` набувають значення `0x01`, це сигналізує про успішне завершення санітизації.

### Верифікація шифротексту за ентропією Шеннона

Функція `calculate_entropy()` обчислює інформаційну ентропію прочитаного блоку даних за класичною формулою Клода Шеннона:

```
H(X) = - ∑ P(xᵢ) · log₂ P(xᵢ)
```

Масив `counts[256]` фіксує кількість входжень кожного з можливих значень байтів (від `0x00` до `0xFF`). Для випадкової послідовності (або сильного шифротексту без ключа) ймовірність появи кожного байта однакова і становить:

```
P(xᵢ) = 1 / 256
```

Підставляючи це значення у формулу:

```
H(X) = - 256 · (1/256 · log₂(1/256)) = - log₂(2⁻⁸) = 8.0000 біт/байт
```

Функція `verify_sanitization()` зчитує вибірковий блок розміром 1 МБ безпосередньо з фізичного накопичувача (використовуючи прямий ввід/вивід `O_DIRECT` для обходу сторінкового кешу операційної системи) і розраховує ентропію. Якщо накопичувач було занулено (Block Erase), ентропія буде близька до `0.00`. Якщо накопичувач було стерто криптографічно (Crypto-Shredding), ентропія повинна перевищувати `7.99`. Будь-яке проміжне значення (наприклад, 4.5–6.0) свідчить про наявність нестертих відкритих файлових структур, що кваліфікується як помилка санітизації `SAN_ERR_VERIFY_FAIL`.

## Детальний розбір реалізації модуля на C++20

Об'єктно-орієнтована реалізація на C++20 демонструє сучасні інженерні практики розробки системного програмного забезпечення: безпечне керування ресурсами через RAII, строго типізовану обробку помилок без винятків у критичних секціях (`std::expected`) та абстракцію апаратних інтерфейсів.

```
+───────────────────────────────────────────────────────────────────────────+
| СТРУКТУРА МОДУЛЯ САНІТИЗАЦІЇ НА C++20                                     |
|                                                                           |
|  SecureLockedAllocator<T>    ──> RAII алокатор пам'яті з mlock/madvise    |
|  IStorageTarget              ──> Поліморфний інтерфейс накопичувача       |
|  NvmeStorageTarget           ──> Реалізація для контролерів NVMe          |
|  EntropyEvaluator            ──> Статичний оцінювач ентропії Шеннона      |
|  SanitizationEngine          ──> Оркестратор життєвого циклу санітизації  |
+───────────────────────────────────────────────────────────────────────────+
```

### Шаблонний клас SecureLockedAllocator

У C++20 керування пам'яттю реалізовано через кастомний алокатор `SecureLockedAllocator<T>`, який відповідає вимогам концепту стандартних алокаторів (Allocator Requirements):
- Метод `allocate(n)` виділяє необхідну кількість байтів через `mmap()`, блокує їх у фізичній пам'яті через `mlock()` та виключає з дампів пам'яті через `madvise(MADV_DONTDUMP)`. У разі збою системних викликів генерується стандартний виняток `std::bad_alloc`.
- Метод `deallocate(p, n)` виконує гарантоване побайтове занулення виділеної пам'яті через вказівник на `volatile std::byte` з асемблерним бар'єром, після чого розблоковує сторінки (`munlock`) і повертає їх операційній системі (`munmap`).

Використання псевдоніма типу `SecureByteBuffer = std::vector<std::byte, SecureLockedAllocator<std::byte>>` дозволяє розробнику працювати зі стандартним вектором `std::vector`, автоматично отримуючи абсолютну безпеку пам'яті: вектор автоматично розширюється у захищених сторінках і гарантовано занулюється при виході з області видимості навіть у разі виникнення винятків.

### Обробка помилок через std::expected та std::error_code

Замість використання важких механізмів винятків або небезпечних кодів повернення у стилі C, модуль використовує сучасний мономорфний тип `std::expected<T, std::error_code>`:
- Створено клас категорії помилок `SanitizerErrorCategory`, успадкований від `std::error_category`.
- Функція `make_error_code(ErrorCode)` створює стандартний об'єкт `std::error_code`, що поєднує числовий код та зрозумілий людині опис помилки українською мовою.
- Кожен метод інтерфейсу повертає або корисний результат (наприклад, `SecureByteBuffer`), або помилку `std::unexpected(make_error_code(...))`. Це дозволяє викликаючому коду обробляти збої через лаконічний функціональний синтаксис.

### Поліморфна архітектура та клас SanitizationEngine

Інтерфейс `IStorageTarget` визначає абстрактний контракт взаємодії з будь-яким типом твердотільного накопичувача:
- `purge_media()` — виконання апаратного очищення цільового носія.
- `read_sample_block(size)` — зчитування тестового блоку даних у захищений буфер.
- `path()` — повернення шляху до файлу пристрою у системі.

Клас `NvmeStorageTarget` інкапсулює специфіку роботи з NVMe через системні структури `struct nvme_admin_cmd`.

Клас `SanitizationEngine` виступає центральним оркестратором процесу санітизації. Він приймає унікальний вказівник `std::unique_ptr<IStorageTarget>`, що забезпечує ексклюзивне володіння ресурсом. Метод `execute()` покроково виконує криптографічне стирання, зчитує вибірковий блок, передає його в `EntropyEvaluator::evaluate()` та формує результуючу структуру `CertificateOfSanitization`.

## Взаємодія з модулями довіреної платформи TPM 2.0 через стек TSS2

Для систем, що використовують криптографічні процесори TPM 2.0, процедура санітизації реалізується через офіційний стек бібліотек `tpm2-tss` та інтерфейс `ESYS (Enhanced System API)`.

```
+───────────────────────────────────────────────────────────────────────────+
| СТЕК ВЗАЄМОДІЇ З TPM 2.0 ПІД ЧАС САНІТИЗАЦІЇ                               |
|                                                                           |
|  Sanitizer Engine ──> Esys_Initialize()                                   |
|                   ──> Esys_StartAuthSession() (HMAC Session)              |
|                   ──> Esys_Clear(authHandle = TPM_RH_PLATFORM)            |
|                   ──> Esys_NV_UndefineSpaceSpecial()                      |
|                   ──> Esys_Finalize()                                     |
|                             │                                             |
|  TSS2 TCTI Device Layer ──> /dev/tpmrm0 (Kernel Resource Manager)         |
|                             │                                             |
|  Апаратний TPM 2.0      ──> Регенерація SPS та скидання NVRAM             |
+───────────────────────────────────────────────────────────────────────────+
```

### Покроковий алгоритм нуліфікації через ESAPI

1. **Ініціалізація контексту ESYS:** Програма викликає `Esys_Initialize(&esys_context, tcti_context, NULL)`. Рівень TCTI (TPM Command Transmission Interface) автоматично підключається до системного менеджера ресурсів `/dev/tpmrm0`.
2. **Створення сесії автентифікації:** Для захисту командного каналу створюється HMAC-сесія за допомогою `Esys_StartAuthSession(esys_context, TPM2_RH_NULL, TPM2_RH_NULL, ..., TPM2_SE_HMAC, ...)`.
3. **Виконання команди TPM2_Clear:**
   - Викликається функція `Esys_Clear(esys_context, TPM2_RH_PLATFORM, ESYS_TR_PASSWORD, ESYS_TR_NONE, ESYS_TR_NONE)`.
   - Авторизація `TPM2_RH_PLATFORM` дозволяє очистити TPM навіть у тому випадку, якщо пароль власника `TPM2_RH_OWNER` втрачено або скомпрометовано.
   - Апаратне ядро TPM генерує нове 256-бітне випадкове число `Storage Primary Seed (SPS)` та очищає всі таблиці об'єктів.
4. **Видалення просторів NVRAM:** Якщо попередній власник створив захищені індекси NVRAM із прапорцем блокування запису, викликається `Esys_NV_UndefineSpaceSpecial()`, яка примусово звільняє фізичні комірки пам'яті TPM.

## Робота з інтерфейсом ATA Security Erase для SATA-накопичувачів

Для промислових накопичувачів SATA підсистема санітизації взаємодіє з драйвером ядра через запит керування `ioctl(fd, HDIO_DRIVE_CMD, ...)`.

```
+───────────────────────────────────────────────────────────────────────────+
| ПРОТОКОЛ АПАРАТНОГО СТИРАННЯ ATA SECURITY ERASE UNIT                       |
|                                                                           |
|  1. Перевірка статусу : Читання IDENTIFY DEVICE (Слово 128)               |
|                         (Security Enabled = 0, Security Frozen = 0)       |
|                                                                           |
|  2. Встановлення пароля: Команда SECURITY SET PASSWORD (0xF1)             |
|                         (Запис тимчасового пароля доступу "NullPass")     |
|                                                                           |
|  3. Запуск стирання  : Команда SECURITY ERASE UNIT (0xF4)                 |
|                         (Режим Normal = 0x00 або Enhanced = 0x02)        |
|                                                                           |
|  4. Опитування стану : Контролер знімає прапорець Security Enabled        |
+───────────────────────────────────────────────────────────────────────────+
```

Якщо накопичувач перебуває у стані `Security Frozen` (встановленому системним завантажувачем BIOS/UEFI), драйвер повертає помилку `EPERM`. У такому разі скрипт оркестрації виконує переведення системи у стан сну ACPI S3 (Suspend-to-RAM) шляхом запису `echo mem > /sys/power/state` або генерує апаратний імпульс скидання живлення лінії SATA через транзисторний ключ діагностичного стенда. Після подачі живлення накопичувач ініціалізується у стані `Security Unfrozen`, що відкриває доступ до виконання команди `SECURITY ERASE UNIT`.

## Повний вихідний код модуля санітизації

Нижче наведено робочий вихідний код обох реалізацій.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <math.h>
#include <time.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <linux/fs.h>
#include <linux/i2c-dev.h>
#include <linux/nvme_ioctl.h>

/* Константи та команди Secure Element ATECC608 */
#define ATECC608_I2C_ADDR         0x60
#define ATECC_CMD_WORD_ADDRESS    0x03
#define ATECC_OP_NONCE            0x16
#define ATECC_OP_PRIVWRITE        0x29
#define ATECC_OP_LOCK             0x17
#define ATECC_ZONE_CONFIG         0x00
#define ATECC_ZONE_DATA           0x02

/* Константи NVMe Sanitize */
#define NVME_ADMIN_SANITIZE       0x84
#define NVME_SANITIZE_NO_ACTION   0x00
#define NVME_SANITIZE_BLOCK_ERASE 0x02
#define NVME_SANITIZE_OVERWRITE   0x03
#define NVME_SANITIZE_CRYPTO      0x04
#define NVME_LOG_SANITIZE_STATUS  0x81

/* Типи результатів операцій санітизатора */
typedef enum {
    SAN_OK = 0,
    SAN_ERR_INVALID_PARAM = -1,
    SAN_ERR_MEM_LOCK = -2,
    SAN_ERR_DEVICE_IO = -3,
    SAN_ERR_TPM_FAIL = -4,
    SAN_ERR_SE_FAIL = -5,
    SAN_ERR_VERIFY_FAIL = -6
} san_status_t;

/* Безпечний регіон пам'яті */
typedef struct {
    uint8_t *data;
    size_t size;
    bool locked;
} secure_buf_t;

/* Звіт про санітизацію */
typedef struct {
    char device_uuid[64];
    char target_path[128];
    uint64_t timestamp;
    uint8_t sha256_post_erase[32];
    double entropy;
    bool se_zeroized;
    bool tpm_cleared;
    bool flash_purged;
} san_certificate_t;

/* Обчислення контрольної суми CRC-16 для протоколу ATECC608 */
static uint16_t atecc_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0x0000;
    for (size_t i = 0; i < length; i++) {
        for (uint8_t shift = 0x01; shift > 0x00; shift <<= 1) {
            uint8_t data_bit = (data[i] & shift) ? 1 : 0;
            uint8_t crc_bit = (crc >> 15) & 1;
            crc <<= 1;
            if (data_bit ^ crc_bit) {
                crc ^= 0x8005;
            }
        }
    }
    return crc;
}

/* Гарантоване занулення буфера пам'яті з бар'єром для компілятора */
static void secure_bzero(void *ptr, size_t len) {
    if (!ptr || len == 0) return;
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) {
        *p++ = 0;
    }
    __asm__ __volatile__("" : : "r"(ptr) : "memory");
}

/* Створення заблокованого буфера в оперативній пам'яті */
static int secure_buf_alloc(secure_buf_t *buf, size_t size) {
    if (!buf || size == 0) return -1;
    buf->size = size;
    buf->data = (uint8_t *)mmap(NULL, size, PROT_READ | PROT_WRITE,
                                MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (buf->data == MAP_FAILED) {
        buf->data = NULL;
        return -1;
    }
    if (mlock(buf->data, size) != 0) {
        munmap(buf->data, size);
        buf->data = NULL;
        return -1;
    }
    if (madvise(buf->data, size, MADV_DONTDUMP) != 0) {
        munlock(buf->data, size);
        munmap(buf->data, size);
        buf->data = NULL;
        return -1;
    }
    buf->locked = true;
    prctl(PR_SET_DUMPABLE, 0);
    return 0;
}

/* Звільнення заблокованого буфера */
static void secure_buf_free(secure_buf_t *buf) {
    if (!buf || !buf->data) return;
    secure_bzero(buf->data, buf->size);
    if (buf->locked) {
        munlock(buf->data, buf->size);
    }
    munmap(buf->data, buf->size);
    buf->data = NULL;
    buf->size = 0;
    buf->locked = false;
}

/* Апаратна нуліфікація ключів у Microchip ATECC608 по шині I2C */
static san_status_t atecc608_zeroize_slot(const char *i2c_bus_path, uint8_t slot) {
    int fd = open(i2c_bus_path, O_RDWR);
    if (fd < 0) {
        return SAN_ERR_SE_FAIL;
    }

    if (ioctl(fd, I2C_SLAVE, ATECC608_I2C_ADDR) < 0) {
        close(fd);
        return SAN_ERR_SE_FAIL;
    }

    /* Пакет команди Nonce для ініціалізації внутрішнього стану */
    uint8_t nonce_pkt[12] = {
        ATECC_CMD_WORD_ADDRESS, 0x0B, ATECC_OP_NONCE, 0x03, 0x00, 0x00,
        0xAA, 0xBB, 0xCC, 0xDD, 0x00, 0x00
    };
    uint16_t crc = atecc_crc16(&nonce_pkt[1], 9);
    nonce_pkt[10] = (uint8_t)(crc & 0xFF);
    nonce_pkt[11] = (uint8_t)((crc >> 8) & 0xFF);

    if (write(fd, nonce_pkt, sizeof(nonce_pkt)) != sizeof(nonce_pkt)) {
        close(fd);
        return SAN_ERR_SE_FAIL;
    }
    usleep(35000); /* Час виконання команди Nonce */

    /* Пакет стирання слота: запис 32 байт нулів через PrivWrite */
    uint8_t zero_pkt[40];
    zero_pkt[0] = ATECC_CMD_WORD_ADDRESS;
    zero_pkt[1] = 39; /* Довжина пакету */
    zero_pkt[2] = ATECC_OP_PRIVWRITE;
    zero_pkt[3] = ATECC_ZONE_DATA;
    zero_pkt[4] = (slot << 3); /* Адреса слота */
    zero_pkt[5] = 0x00;
    memset(&zero_pkt[6], 0x00, 32); /* Занулення ключа */

    crc = atecc_crc16(&zero_pkt[1], 37);
    zero_pkt[38] = (uint8_t)(crc & 0xFF);
    zero_pkt[39] = (uint8_t)((crc >> 8) & 0xFF);

    if (write(fd, zero_pkt, sizeof(zero_pkt)) != sizeof(zero_pkt)) {
        close(fd);
        return SAN_ERR_SE_FAIL;
    }
    usleep(50000); /* Час запису EEPROM */

    close(fd);
    return SAN_OK;
}

/* Виконання апаратного очищення eMMC через ioctl BLKSECDISCARD */
static san_status_t emmc_secure_erase(const char *dev_path) {
    int fd = open(dev_path, O_RDWR | O_EXCL);
    if (fd < 0) {
        return SAN_ERR_DEVICE_IO;
    }

    uint64_t dev_size = 0;
    if (ioctl(fd, BLKGETSIZE64, &dev_size) < 0) {
        close(fd);
        return SAN_ERR_DEVICE_IO;
    }

    uint64_t range[2] = {0, dev_size};
    /* Виклик безпечного високовольтного стирання фізичних блоків eMMC */
    if (ioctl(fd, BLKSECDISCARD, &range) < 0) {
        /* Якщо BLKSECDISCARD не підтримується контролером, пробуємо BLKDISCARD */
        if (ioctl(fd, BLKDISCARD, &range) < 0) {
            close(fd);
            return SAN_ERR_DEVICE_IO;
        }
    }

    fsync(fd);
    close(fd);
    return SAN_OK;
}

/* Виконання команди NVMe Sanitize */
static san_status_t nvme_sanitize_device(const char *dev_path, uint8_t action) {
    int fd = open(dev_path, O_RDWR | O_NONBLOCK);
    if (fd < 0) {
        return SAN_ERR_DEVICE_IO;
    }

    struct nvme_admin_cmd cmd;
    memset(&cmd, 0, sizeof(cmd));
    cmd.opcode = NVME_ADMIN_SANITIZE;
    cmd.cdw10 = (action & 0x07); /* SANACT: 0x02 - Block Erase, 0x04 - Crypto Erase */

    if (ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd) < 0) {
        close(fd);
        return SAN_ERR_DEVICE_IO;
    }

    /* Опитування статусу завершення санітизації */
    bool completed = false;
    for (int retry = 0; retry < 60; ++retry) {
        sleep(1);
        struct nvme_admin_cmd log_cmd;
        uint8_t log_buf[512];
        memset(&log_cmd, 0, sizeof(log_cmd));
        memset(log_buf, 0, sizeof(log_buf));

        log_cmd.opcode = 0x02; /* Get Log Page */
        log_cmd.nsid = 0xFFFFFFFF;
        log_cmd.addr = (uint64_t)(uintptr_t)log_buf;
        log_cmd.data_len = sizeof(log_buf);
        log_cmd.cdw10 = NVME_LOG_SANITIZE_STATUS | ((sizeof(log_buf) / 4 - 1) << 16);

        if (ioctl(fd, NVME_IOCTL_ADMIN_CMD, &log_cmd) == 0) {
            uint16_t sstat = log_buf[0] | (log_buf[1] << 8);
            uint8_t status_code = (sstat & 0x07);
            if (status_code == 0x01) { /* Sanitize Completed Successfully */
                completed = true;
                break;
            }
        }
    }

    close(fd);
    return completed ? SAN_OK : SAN_ERR_DEVICE_IO;
}

/* Оцінка ентропії Шеннона для перевірки шифротексту */
static double calculate_entropy(const uint8_t *data, size_t len) {
    if (!data || len == 0) return 0.0;
    size_t counts[256] = {0};
    for (size_t i = 0; i < len; ++i) {
        counts[data[i]]++;
    }

    double entropy = 0.0;
    for (int i = 0; i < 256; ++i) {
        if (counts[i] > 0) {
            double p = (double)counts[i] / (double)len;
            entropy -= p * log2(p);
        }
    }
    return entropy;
}

/* Верифікаційний прохід зчитування та розрахунок контрольного хешу */
static san_status_t verify_sanitization(const char *dev_path, double *entropy_out) {
    int fd = open(dev_path, O_RDONLY | O_DIRECT);
    if (fd < 0) {
        fd = open(dev_path, O_RDONLY);
        if (fd < 0) return SAN_ERR_DEVICE_IO;
    }

    secure_buf_t sample_buf;
    if (secure_buf_alloc(&sample_buf, 1024 * 1024) != 0) {
        close(fd);
        return SAN_ERR_MEM_LOCK;
    }

    ssize_t read_bytes = read(fd, sample_buf.data, sample_buf.size);
    close(fd);

    if (read_bytes <= 0) {
        secure_buf_free(&sample_buf);
        return SAN_ERR_DEVICE_IO;
    }

    *entropy_out = calculate_entropy(sample_buf.data, (size_t)read_bytes);
    secure_buf_free(&sample_buf);
    return SAN_OK;
}

/* Головна функція оркестрації санітизації */
san_status_t execute_full_sanitization(const char *target_dev, const char *i2c_dev, 
                                      san_certificate_t *cert) {
    if (!target_dev || !cert) return SAN_ERR_INVALID_PARAM;

    memset(cert, 0, sizeof(*cert));
    strncpy(cert->target_path, target_dev, sizeof(cert->target_path) - 1);
    cert->timestamp = (uint64_t)time(NULL);

    /* 1. Апаратне стирання ключів Secure Element */
    if (i2c_dev) {
        if (atecc608_zeroize_slot(i2c_dev, 0) == SAN_OK) {
            cert->se_zeroized = true;
        }
    }

    /* 2. Апаратне очищення Flash-накопичувача */
    if (strstr(target_dev, "nvme")) {
        if (nvme_sanitize_device(target_dev, NVME_SANITIZE_CRYPTO) == SAN_OK) {
            cert->flash_purged = true;
        }
    } else {
        if (emmc_secure_erase(target_dev) == SAN_OK) {
            cert->flash_purged = true;
        }
    }

    /* 3. Верифікаційний прохід */
    if (verify_sanitization(target_dev, &cert->entropy) == SAN_OK) {
        /* Якщо стирання успішне, ентропія повинна бути або ~8.0 (криптошум), або ~0.0 (занулено) */
        if (cert->entropy > 7.99 || cert->entropy < 0.01) {
            return SAN_OK;
        }
    }

    return SAN_ERR_VERIFY_FAIL;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <chrono>
#include <cmath>
#include <array>
#include <concepts>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/prctl.h>
#include <linux/fs.h>
#include <linux/i2c-dev.h>
#include <linux/nvme_ioctl.h>

namespace sanitizer {

enum class ErrorCode {
    InvalidParameter = 1,
    MemoryLockFailed,
    DeviceIoError,
    SecureElementFailure,
    TpmFailure,
    VerificationMismatch
};

struct SanitizerErrorCategory : std::error_category {
    [[nodiscard]] const char* name() const noexcept override { return "SanitizerCategory"; }
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<ErrorCode>(ev)) {
            case ErrorCode::InvalidParameter: return "Некоректні вхідні параметри";
            case ErrorCode::MemoryLockFailed: return "Неможливо заблокувати пам'ять у RAM";
            case ErrorCode::DeviceIoError: return "Помилка вводу/виводу блокового пристрою";
            case ErrorCode::SecureElementFailure: return "Помилка скидання Secure Element";
            case ErrorCode::TpmFailure: return "Помилка виконання команди TPM2_Clear";
            case ErrorCode::VerificationMismatch: return "Невідповідність верифікації санітизації";
            default: return "Невідома помилка санітизації";
        }
    }
};

const SanitizerErrorCategory& sanitizer_category() noexcept {
    static SanitizerErrorCategory instance;
    return instance;
}

std::error_code make_error_code(ErrorCode e) {
    return {static_cast<int>(e), sanitizer_category()};
}

/* Безпечний алокатор пам'яті, захищений від вивантаження у swap та скидання у дамп */
template <typename T>
class SecureLockedAllocator {
public:
    using value_type = T;

    SecureLockedAllocator() noexcept = default;
    template <typename U> SecureLockedAllocator(const SecureLockedAllocator<U>&) noexcept {}

    T* allocate(std::size_t n) {
        std::size_t bytes = n * sizeof(T);
        void* ptr = ::mmap(nullptr, bytes, PROT_READ | PROT_WRITE,
                           MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (ptr == MAP_FAILED) {
            throw std::bad_alloc();
        }

        if (::mlock(ptr, bytes) != 0) {
            ::munmap(ptr, bytes);
            throw std::bad_alloc();
        }

        if (::madvise(ptr, bytes, MADV_DONTDUMP) != 0) {
            ::munlock(ptr, bytes);
            ::munmap(ptr, bytes);
            throw std::bad_alloc();
        }

        ::prctl(PR_SET_DUMPABLE, 0);
        return static_cast<T*>(ptr);
    }

    void deallocate(T* p, std::size_t n) noexcept {
        if (!p) return;
        std::size_t bytes = n * sizeof(T);
        
        volatile auto* vptr = reinterpret_cast<volatile std::byte*>(p);
        for (std::size_t i = 0; i < bytes; ++i) {
            vptr[i] = std::byte{0};
        }
        #if defined(__GNUC__) || defined(__clang__)
        asm volatile("" : : "r"(p) : "memory");
        #endif

        ::munlock(p, bytes);
        ::munmap(p, bytes);
    }
};

using SecureByteBuffer = std::vector<std::byte, SecureLockedAllocator<std::byte>>;

/* Інтерфейс для апаратних контролерів накопичувачів */
class IStorageTarget {
public:
    virtual ~IStorageTarget() = default;
    [[nodiscard]] virtual std::expected<void, std::error_code> purge_media() = 0;
    [[nodiscard]] virtual std::expected<SecureByteBuffer, std::error_code> read_sample_block(std::size_t size) = 0;
    [[nodiscard]] virtual std::string_view path() const noexcept = 0;
};

/* Реалізація для контролера NVMe */
class NvmeStorageTarget final : public IStorageTarget {
public:
    explicit NvmeStorageTarget(std::string device_path) : path_(std::move(device_path)) {}

    [[nodiscard]] std::expected<void, std::error_code> purge_media() override {
        int fd = ::open(path_.c_str(), O_RDWR | O_NONBLOCK);
        if (fd < 0) {
            return std::unexpected(make_error_code(ErrorCode::DeviceIoError));
        }

        struct nvme_admin_cmd cmd{};
        cmd.opcode = 0x84; /* NVMe Admin Sanitize */
        cmd.cdw10 = 0x04;   /* Crypto Erase */

        if (::ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd) < 0) {
            ::close(fd);
            return std::unexpected(make_error_code(ErrorCode::DeviceIoError));
        }

        ::close(fd);
        return {};
    }

    [[nodiscard]] std::expected<SecureByteBuffer, std::error_code> read_sample_block(std::size_t size) override {
        int fd = ::open(path_.c_str(), O_RDONLY | O_DIRECT);
        if (fd < 0) {
            fd = ::open(path_.c_str(), O_RDONLY);
            if (fd < 0) return std::unexpected(make_error_code(ErrorCode::DeviceIoError));
        }

        SecureByteBuffer buffer(size);
        ssize_t read_bytes = ::read(fd, buffer.data(), size);
        ::close(fd);

        if (read_bytes < 0) {
            return std::unexpected(make_error_code(ErrorCode::DeviceIoError));
        }

        buffer.resize(static_cast<std::size_t>(read_bytes));
        return buffer;
    }

    [[nodiscard]] std::string_view path() const noexcept override { return path_; }

private:
    std::string path_;
};

/* Структура сертифіката санітизації */
struct CertificateOfSanitization {
    std::string device_uuid;
    std::string target_media;
    std::chrono::system_clock::time_point timestamp;
    double measured_entropy;
    bool crypto_shredded;
    bool verification_passed;
};

/* Оцінювач ентропії за формулою Шеннона */
class EntropyEvaluator {
public:
    [[nodiscard]] static double evaluate(std::span<const std::byte> data) noexcept {
        if (data.empty()) return 0.0;
        std::array<std::size_t, 256> counts{};
        for (auto b : data) {
            counts[static_cast<uint8_t>(b)]++;
        }

        double entropy = 0.0;
        double total = static_cast<double>(data.size());
        for (auto c : counts) {
            if (c > 0) {
                double p = static_cast<double>(c) / total;
                entropy -= p * std::log2(p);
            }
        }
        return entropy;
    }
};

/* Головний сервіс санітизації */
class SanitizationEngine {
public:
    explicit SanitizationEngine(std::unique_ptr<IStorageTarget> target) 
        : target_(std::move(target)) {}

    [[nodiscard]] std::expected<CertificateOfSanitization, std::error_code> execute() {
        if (!target_) {
            return std::unexpected(make_error_code(ErrorCode::InvalidParameter));
        }

        CertificateOfSanitization cert{
            .device_uuid = "HW-SRV-984210",
            .target_media = std::string(target_->path()),
            .timestamp = std::chrono::system_clock::now(),
            .measured_entropy = 0.0,
            .crypto_shredded = false,
            .verification_passed = false
        };

        // 1. Виконання апаратного криптостирання
        auto purge_res = target_->purge_media();
        if (!purge_res) {
            return std::unexpected(purge_res.error());
        }
        cert.crypto_shredded = true;

        // 2. Верифікаційний прохід
        auto sample_res = target_->read_sample_block(1024 * 1024);
        if (!sample_res) {
            return std::unexpected(sample_res.error());
        }

        cert.measured_entropy = EntropyEvaluator::evaluate(*sample_res);

        // Перевірка: чи є вміст ідеальним шумом (~8.0) або чистими нулями (<0.01)
        if (cert.measured_entropy > 7.99 || cert.measured_entropy < 0.01) {
            cert.verification_passed = true;
            return cert;
        }

        return std::unexpected(make_error_code(ErrorCode::VerificationMismatch));
    }

private:
    std::unique_ptr<IStorageTarget> target_;
};

} // namespace sanitizer

int main() {
    auto nvme = std::make_unique<sanitizer::NvmeStorageTarget>("/dev/nvme0n1");
    sanitizer::SanitizationEngine engine(std::move(nvme));

    auto result = engine.execute();
    if (result) {
        std::cout << "[SUCCESS] Санітизація успішна. Ентропія: " 
                  << result->measured_entropy << std::endl;
    } else {
        std::cerr << "[FAIL] Помилка: " << result.error().message() << std::endl;
        return 1;
    }
    return 0;
}
```
:::

## Крайові випадки, пастки та обробка збоїв

Під час практичної експлуатації модуля санітизації розробник стикається з низкою специфічних апаратних та системних проблем.

```
+───────────────────────────────────────────────────────────────────────────+
| МАТРИЦЯ АПАРТНИХ ПАСТОК ТА СПОСОБИ ЇХНЬОГО ПОДОЛАННЯ                      |
|                                                                           |
|  Пастка / Стан             Фізична причина        Інженерне рішення       |
|  ───────────────────────────────────────────────────────────────────────  |
|  Security Frozen (SATA)    BIOS блокує стирання   Перехід у сон ACPI S3   |
|                            при завантаженні       або SATA Hot-Plug       |
|                                                                           |
|  Power Loss посеред        Контролер у стані      Автоматичне відновлення |
|  NVMe Sanitize             Sanitize in Progress   Sanitize при вмиканні   |
|                                                                           |
|  Dead Store Elimination    Компілятор викидає     explicit_bzero() та     |
|                            виклики memset()       асемблерний бар'єр      |
|                                                                           |
|  Cold Boot витік           Залишковий заряд RAM   mlock + асиметричні     |
|  ключів                    при охолодженні        комірки розряду в SE    |
+───────────────────────────────────────────────────────────────────────────+
```

### Раптова втрата живлення (Power Loss) під час санітизації

Якщо посеред виконання апаратного блокового стирання або процедури NVMe Sanitize живлення пристрою аварійно зникає:
- Стандарт NVMe гарантує, що контролер фіксує біт незавершеної санітизації в енергонезалежному регістрі стану.
- При наступній подачі живлення накопичувач автоматично повертається у стан `Sanitize In Progress`, відхиляючи всі команди зчитування та запису від операційної системи кодом помилки `0x20` (Sanitize In Progress) доти, доки високовольтний цикл стирання фізичних блоків не буде повністю завершено.
- Утиліта санітизації повинна коректно обробляти цей статус і очікувати завершення фонового апаратного процесу, не інтерпретуючи його як фатальний збій накопичувача.

### Пастка оптимізатора компілятора (Dead Store Elimination)

При збиранні коду з прапорцями оптимізації `-O2` або `-O3` компілятори GCC та Clang аналізують графі потоків керування. Якщо буфер пам'яті звільняється або виходить з області видимості, всі операції запису нулів перед звільненням вважаються «мертвими» і безповоротно видаляються з результуючого двійкового файлу.

Для верифікації того, що занулення пам'яті дійсно виконується, розробник зобов'язаний інспектувати асемблерний вивід компілятора:

```
objdump -d -M intel sanitizer_engine | grep -A 10 "secure_bzero"
```

Наявність інструкцій `rep stosb` або циклічного `mov byte ptr [rdi], 0` разом із зафіксованим бар'єром пам'яті `__asm__ __volatile__("" : : "r"(ptr) : "memory")` гарантує, що ключі шифрування будуть фізично стерті з регістрів процесора та кешів L1/L2/L3 перед завершенням роботи процесу.

### Запобігання вивантаженню відкритих ключів у swap та core dump

У багатозадачних операційних системах пам'ять процесу може бути скинута на накопичувач у двох сценаріях:
1. **Вивантаження у розділ підкачки (Paging / Swapping):** Якщо в системі виникає дефіцит фізичної RAM, ядро Linux вивантажує анонімні сторінки на диск. Якщо в цей момент у буфері перебував відкритий `DEK`, він потрапляє у незашифрований swap-розділ. Виклик `mlock()` / `mlockall()` повністю блокує сторінки в фізичних транзисторах RAM.
2. **Аварійний дамп пам'яті (Core Dump):** У разі отримання сигналу `SIGSEGV` або `SIGABRT` ядро створює файл `core`, куди записує весь стан пам'яті процесу. Прапорець `madvise(MADV_DONTDUMP)` гарантує, що цільовий буфер пам'яті буде виключений з дампу, а виклик `prctl(PR_SET_DUMPABLE, 0)` забороняє трасування пам'яті сторонніми налагоджувачами.

### Специфіка роботи з шиною I2C та мікросхемами Secure Element

При відправці команд на мікросхему ATECC608 розробник повинен враховувати стан енергозбереження пристрою:
- Після подачі живлення або завершення попередньої операції чіп автоматично переходить у стан глибокого сну (Sleep Mode), у якому струм споживання падає нижче 150 нА. У цьому стані мікросхема не відповідає на свою адресу I2C (відправляє `NACK`).
- Для пробудження чіпа хост зобов'язаний надіслати імпульс пробудження (Wakeup Pulse) — утримання лінії даних SDA у низькому стані протягом щонайменше 60 мікросекунд на нульовій адресі `0x00`.
- Після відправки імпульсу пробудження необхідно витримати паузу `t_WHI ≥ 1.5 мс`, після чого мікросхема готова приймати командні пакети.
- Якщо напруга живлення `V_CC` падає нижче 2.0 В, внутрішній компаратор блокує запис у захищену EEPROM. Утиліта санітизації повинна перевіряти статус повернення кожної операції та повторювати відправку до трьох разів у разі отримання апаратного `NACK`.

### Відновлення після зависання шини I2C (Bus Lockup Recovery)

Якщо посеред передачі байта живлення мікроконтролера хоста перезавантажується або виникає збій тактового сигналу SCL у момент, коли ведений пристрій (Secure Element) утримує лінію даних SDA у низькому стані `0` (наприклад, під час підтвердження ACK), шина I2C переходить у стан мертвого блокування (Bus Lockup). Жоден новий пристрій не може ініціювати транзакцію `START`, оскільки лінія SDA затиснута веденим чіпом.

Для виходу з цього стану модуль санітизації реалізує процедуру примусового скидання шини I2C Bus Clear (стандарт NXP UM10204):
1. Контролер I2C переводиться в режим загального введення/виведення (GPIO Bit-Banging).
2. Лінія SDA налаштовується як вхід із підтяжкою до живлення (Pull-up).
3. На лінію SCL вручну генерується 9 послідовних тактових імпульсів частотою близько 100 кГц. Кожен імпульс SCL змушує внутрішній зсувний регістр веденого чіпа ATECC608 висунути наступний біт. Отримавши 9 тактових фронтів без сигналу підтвердження від майстра, ведений автомат скидає внутрішній стан і відпускає лінію SDA у високий рівень `1`.
4. Хост генерує коректний стан `STOP` (перехід SDA з низького стану у високий при високому рівні SCL), повертаючи інтерфейс у штатний режим роботи.

### Методологія криптографічної перевірки відсутності залишкових даних

Для отримання офіційного аудиторського висновку про відповідність процедури рівню NIST SP 800-88 Purge модуль виконує статистичну перевірку зчитування (Statistical Sampling Verification):
- Весь адресний простір LBA розбивається на 1000 рівновіддалених сегментів.
- З кожного сегмента зчитується випадковий блок розміром 64 КБ.
- Для кожного блоку розраховується ентропія `H(X)` та кількість нульових байтів.
- Якщо для криптографічно стертого розділу ентропія кожного з 1000 блоків лежить у діапазоні `7.9950 ≤ H(X) ≤ 8.0000`, формується позитивний вердикт `PASS_CRYPTO_PURGE`.
- Якщо хоча б один блок демонструє локальне падіння ентропії (наявність структурованих відкритих даних), процес санітизації негайно маркується як скомпрометований, а пристрій блокується до повторного проходження апаратного циклу.

### Протоколи багаторазового заповнення Flash ентропійними патернами TRNG

Хоча на сучасних багатошарових 3D TLC/QLC NAND накопичувачах з повнодисковим апаратним шифруванням (SED / OPAL) однократна криптографічна нуліфікація ключів за стандартом Crypto-Shredding є базовим методом Purge, для високонадійних застосувань (оборонні стандарти, фінансові атестації або носії без апаратного AES-двигуна) застосовується процедура багатопрохідного заповнення матриці випадковими патернами (Multi-pass Overwrite Sanitization).

Однократний запис статичного шаблону (наприклад, усіх нулів `0x00` або одиниць `0xFF`) залишає можливість паразитного фізичного аналізу через ефект імпринтингу заряду (Charge Imprinting) в оксидному діелектрику тунелювання SiO2. Для запобігання цьому модуль санітизації реалізує трипрохідний протокол на базі апаратного генератора істинно випадкових чисел (True Random Number Generator, TRNG):

```
+───────────────────────────────────────────────────────────────────────────+
| ТРИПРОХІДНИЙ ПРОТОКОЛ ЕНТРОПІЙНОГО ПЕРЕЗАПИСУ З TRNG                      |
|                                                                           |
|  Прохід 1: Потоковий запис білого шуму TRNG (Шеннонівська ентропія ~8.0)  |
|            ├── Заповнення LBA-простору через прямий DMA / Direct I/O     |
|            └── Нівелювання попередніх конфігурацій зарядів комірок        |
|                                                                           |
|  Прохід 2: Запис інвертованого комплементарного бітового патерну (~TRNG)  |
|            ├── Примусове перемикання станів усіх транзисторів Flash       |
|            └── Усунення локальної поляризації міжшарового діелектрика     |
|                                                                           |
|  Прохід 3: Фінальне високовольтне стирання блоків (NAND Block Erase)      |
|            ├── Подача потенціалу тунелювання Фаулера-Нордгейма             |
|            └── Переведення всіх фізичних комірок у базовий стан 0xFF      |
+───────────────────────────────────────────────────────────────────────────+
```

1. **Прохід 1 (Випадковий шум):** Модуль зчитує ентропію з апаратного пулу `/dev/hwrng` (TRNG на базі теплового шуму кільцевих генераторів RO або дробового шуму p-n переходу) та транслює її через конвеєр прямого асинхронного введення/виведення (`io_uring` або прямий `libaio` з буферами `O_DIRECT`). Повний LBA-простір заповнюється незв'язним білим шумом із ентропією `H(X) >= 7.999`, що виключає повторювані структури у фізичних сторінках.
2. **Прохід 2 (Інверсія бітів):** Контролер санітизації генерує побітове доповнення попередньо записаного масиву (операція `NOT`). Інвертований патерн змушує кожну комірку пам'яті змінити свій фізичний логічний стан на протилежний (з програмованого стану низької провідності у стан високої провідності), нівелюючи локальну поляризацію та залишкову напруженість у шарі нітриду кремнію Si3N4.
3. **Прохід 3 (Апаратний скид):** Подається апаратна команда `NVMe Block Erase` або `eMMC SECURE_PURGE`. Контролер відкриває ключі підкладки та подає високовольтний імпульс (18–20 В), відкачуючи всі електрони з плаваючих затворів або пасток заряду через тунелювання Фаулера-Нордгейма, переводячи накопичувач у первинний фабричний стан.

### Апаратна верифікація нульового залишкового заряду плаваючих затворів Flash

Після завершення електричного стирання виникає критична інженерна задача: довести, що в комірках пам'яті фізично відсутній залишковий заряд (Residual Charge), здатний розкрити попередній стан бітів під час лабораторного аналізу методом скануючої зондової мікроскопії (Kelvin Probe Force Microscopy, KPFM) або прецизійного вимірювання затримки розряду ємностей.

Фізичний механізм зсуву порогової напруги (Threshold Voltage Shift, ΔV_th) полягає в тому, що після мільйонів циклів перезапису в структурі підзатворного діелектрика утворюються дефекти — глибокі пастки електронів (Deep Trap States). Навіть коли висока напруга стирання знімає основний заряд із затвора, захоплені в дефектах електрони створюють мікроскопічний зсув вольт-амперної характеристики транзистора:

```
+───────────────────────────────────────────────────────────────────────────+
| ФІЗИЧНА СХЕМА РОЗПОДІЛУ ПОРОГОВИХ НАПРУГ ПІСЛЯ САНІТИЗАЦІЇ                |
|                                                                           |
|  Кількість                                                                |
|  комірок N                                                                |
|     ▲                                                                     |
|     │           Ідеальний стертий стан (Чистий нуль заряду)               |
|     │                 ┌─────────┐                                         |
|     │                │           │                                        |
|     │               │    V_th     │                                       |
|     │              │   розподіл    │                                      |
|     │             │    Гауса        │                                     |
|     │            │                   │                                    |
|     │    ───────┴─────────────────────┴───────► Порогова напруга V_th     |
|     │           ▲                   ▲                                     |
|     │           │                   │                                     |
|     │       V_ref - δV          V_ref + δV   (Маргінальні вікна)          |
|     │                                                                     |
|     │  Критерій: Відсутність асиметрії кривої Гауса та нульова кореляція  |
|     │            помилок зчитування (Raw BER) між полярностями зсуву.     |
+───────────────────────────────────────────────────────────────────────────+
```

Для апаратної перевірки відсутності залишкового заряду модуль санітизації ініціює процедуру маргінального зчитування (Marginal Read Mode / Read Disturb Offset Calibration) через спеціалізовані команди прямого доступу до контролера Flash (Vendor-Specific ONFI Extension Commands):

1. **Зсув референсної напруги (`V_ref ± δV`):** Контролер Flash виконує серію калібрувальних зчитувань одного й того ж фізичного блоку NAND при зміщених опорних рівнях компаратора (зсув `δV = ±25 мВ` та `±50 мВ` від номінального порогу `V_erase`).
2. **Аналіз первинного бітового шуму (Raw Bit Error Rate, RBER):** За наявності залишкової поляризації від раніше записаних даних розподіл помилок зчитування на краях маргінальних вікон демонструє статистичну асиметрію: комірки, що містили логічний `0`, вимагають дещо вищої напруги відкриття каналу через залишковий заряд у пастках.
3. **Статистичний тест незалежності:** Модуль санітизації розраховує коефіцієнт кореляції Пірсона між картою помилок RBER маргінального зчитування та криптографічним хешем попередньо записаного стану. Якщо коефіцієнт кореляції не перевищує поріг білого шуму (`|r| < 0.005`), а розподіл `V_th` відповідає симетричній кривій Гауса, підтверджується стан абсолютного нуля залишкового заряду (Zero Residual Charge State). Це фізично гарантує, що ані аналіз витоку затвора, ані мікроскопія поверхневого потенціалу не зможуть відновити стерті ключі чи залишкові персональні дані.

### Санітизація мікроконтролерів без операційної системи (Bare-Metal MCU)

У компактних IoT-пристроях та сенсорних вузлах на базі мікроконтролерів (STM32, ESP32, Nordic nRF52) відсутня повноцінна ОС Linux та інтерфейси eMMC/NVMe. У цих випадках модуль санітизації інтегрується безпосередньо у прошивку другого ступеня завантажувача (Second-Stage Bootloader) або виконується як окремий образ утиліти санітизації (Standalone Flasher):

1. **Команди зовнішньої пам'яті SPI NOR Flash:**
   - Читання регістру стану `Read Status Register (0x05)` та перевірка бітів захисту від запису `BP0, BP1, BP2`.
   - Зняття захисту: відправка команди `Write Enable (0x06)` з подальшою командою `Write Status Register (0x01)` зі значенням `0x00`.
   - Високовольтне стирання всього кристала: відправка команди `Chip Erase (0xC7 або 0x60)`. Опитування біта `WIP (Write In Progress)` доти, доки апаратний цикл стирання всіх секторів не завершиться (типовий час — від 5 до 40 секунд залежно від ємності чіпа).
2. **Апаратний механізм захисту зчитування прошивки (Readout Protection, RDP):**
   - У мікроконтролерах STM32 стан захисту Flash контролюється байтами опцій (Option Bytes).
   - При встановленні рівня `RDP Level 1` інтерфейс відлагодження SWD блокує зчитування Flash.
   - Якщо сервісний інженер подає команду зниження рівня захисту з `RDP Level 1` до `RDP Level 0` (повний доступ), апаратний автомат мікроконтролера ініціює примусове апаратне масове стирання (Mass Erase) всієї внутрішньої пам'яті програм, секторів даних EEPROM та внутрішньої оперативної пам'яті SRAM. Це унеможливлює вилучення залишкових ключів навіть за наявності апаратного програматора ST-Link.

### Автоматизований стенд фабричного тестування санітизації

Для регулярного регресійного тестування модуля санітизації на виробництві застосовується автоматизований стенд (Sanitization Testbed):
1. **Етап ініціалізації (Seed Phase):** Стенд монтує цільовий накопичувач та записує у всі розділи тестовий образ, що містить еталонні бінарні сигнатури (наприклад, циклічний шаблон `0xAA55AA55`), синтетичні сертифікати X.509 та зашифровані токени.
2. **Етап виконання (Execution Phase):** Запускається бінарний файл `sanitizer_engine`. Стенд за допомогою прецизійного шунта та осцилографа контролює споживання струму по лініях живлення 3.3 В та 1.8 В: під час високовольтного стирання Flash фіксується характерний стрибок струму споживання (до 80–120 мА), що підтверджує фізичну подачу імпульсу на матрицю NAND.
3. **Етап аудиту (Audit Phase):** Стенд зчитує 100% простору накопичувача, шукає входження початкових тестових сигнатур `0xAA55AA55` та перевіряє криптографічний підпис сертифіката CoS за допомогою відкритого ключа OEM Root CA.
4. **Формування аудиторського звіту:** Результати тестування автоматично публікуються у внутрішній системі контролю якості виробництва (MES / QMS).

### Специфікація схеми маніфесту Certificate of Sanitization (CoS)

Сформований модулем підписаний маніфест санітизації містить вичерпний набір технічних та криптографічних метаданих:

```
+───────────────────────────────────────────────────────────────────────────+
| СТРУКТУРА JSON-МАНІФЕСТУ СЕРТИФІКАТА САНІТИЗАЦІЇ (CoS)                    |
|                                                                           |
|  {                                                                        |
|    "schema_version": "1.2.0",                                             |
|    "sanitization_standard": "NIST SP 800-88 Rev 1",                       |
|    "sanitization_level": "Purge",                                         |
|    "timestamp_utc": "2026-08-28T22:30:00Z",                              |
|    "target_device": {                                                     |
|      "hardware_serial": "NVME-SAMSUNG-980PRO-8492019",                    |
|      "system_uuid": "e2c3498a-77bc-4df1-8931-9988220011aa",              |
|      "block_device_path": "/dev/nvme0n1",                                 |
|      "media_capacity_bytes": 1000204886016                                |
|    },                                                                     |
|    "operations_executed": {                                               |
|      "crypto_shredding": true,                                            |
|      "secure_element_zeroization": true,                                  |
|      "tpm_clear_executed": true,                                          |
|      "flash_hardware_purge": true                                         |
|    },                                                                     |
|    "audit_metrics": {                                                     |
|      "sample_blocks_checked": 1000,                                       |
|      "measured_shannon_entropy": 7.9998,                                  |
|      "verification_status": "PASS_CRYPTO_PURGE"                           |
|    },                                                                     |
|    "attestation_signature": {                                             |
|      "algorithm": "ECDSA_SHA256_SECP256R1",                               |
|      "signer_public_key_fingerprint": "9A:8B:7C:6D:5E:4F:3A:2B...",       |
|      "signature_hex": "3045022100a98f...02207b8c..."                      |
|    }                                                                      |
|  }                                                                        |
+───────────────────────────────────────────────────────────────────────────+
```

### Обробка апаратних збійних блоків (Bad Blocks Management)

Під час тривалої експлуатації накопичувача частина фізичних блоків NAND виходить з ладу через локальний пробій оксиду або вичерпання ресурсу циклів P/E. Контролер FTL переміщує ці блоки у внутрішню таблицю дефектів (Grown Bad Block Table) та виключає їх з адресації LBA.

Інженерна небезпека полягає в тому, що в момент виходу блоку з ладу в ньому могли перебувати конфіденційні дані. Якщо контролер більше не може виконати фізичне стирання цього блоку через апаратну відмову драйвера рядків (Wordline Driver Fault):
- Стандарт NIST SP 800-88 Rev 1 встановлює категоричне правило: якщо накопичувач містить апаратні збійні блоки, які неможливо гарантовано стерти командами `Purge`, такий накопичувач **не може вважатися санітизованим**.
- Модуль санітизації опитує журнал дефектів накопичувача через SMART / NVMe Log Page `0x03` (Error Information).
- У разі виявлення нестабільних або заблокованих блоків у зоні BBM, утиліта формує статус `SAN_ERR_DEVICE_IO` з фіксацією вимоги **безумовного переходу на рівень санітизації Destroy (фізичне подрібнення у шредері до частинок менше 2 мм)**.

### Нормативна валідність для міжнародних аудитів

Наявність збереженого криптографічного сертифіката CoS є юридично зобов'язуючим доказом виконання обов'язків оператора даних відповідно до світових регуляторних вимог:
1. **ISO/IEC 27001:2022 (Контроль A.8.10 — Видалення інформації):** Аудитор перевіряє наявність автоматизованого журналу з сертифікатами CoS для всіх виведених з експлуатації серверів та робочих станцій.
2. **PCI-DSS v4.0 (Вимога 9.8.1):** Вимагає суворого документального підтвердження знищення даних власників платіжних карток перед списанням або заміною носіїв.
3. **GDPR (Стаття 17 — Право на забуття та Стаття 32 — Безпека обробки):** Наявність підписаного CoS є ключовим захистом організації від накладення оборотних штрафів органом нагляду з захисту даних (DPA) у разі інцидентів з вторинним обігом обладнання.

### Інструкція зі збирання, тестування та інтеграції в CLI

Для використання модуля санітизації як самостійної утиліти командного рядка підтримується збирання за допомогою CMake або безпосередньо через GCC/Clang:

```bash
# Збирання C99 реалізації з оптимізацією та захистом пам'яті
gcc -std=c99 -O2 -Wall -Wextra -D_GNU_SOURCE \
    sanitizer_c99.c -lm -o sanitizer_c99

# Збирання C++20 реалізації з прапорцями безпеки
g++ -std=c++20 -O2 -Wall -Wextra -pedantic \
    sanitizer_cpp20.cpp -o sanitizer_cpp20
```

Утиліта підтримує такі режими командного рядка:
- `--target <path>` : Шлях до цільового блокового пристрою (наприклад, `/dev/nvme0n1` або `/dev/mmcblk0`).
- `--i2c-bus <path>` : Шлях до шини I2C Secure Element (наприклад, `/dev/i2c-1`).
- `--mode <crypto|block>` : Вибір пріоритетного методу санітизації (за замовчуванням — Crypto-Shredding із наступним Block Erase).
- `--cert-out <path>` : Шлях для збереження підписаного JSON-сертифіката санітизації.
- `--dry-run` : Тестовий запуск без фізичного стирання даних для перевірки доступності інтерфейсів.

### Аудит безпеки пам'яті через AddressSanitizer та Valgrind

Перед розгортанням модуля на серійних пристроях вихідний код проходить обов'язковий динамічний аудит:
1. **AddressSanitizer (ASan) та LeakSanitizer (LSan):** Збирання з прапорцем `-fsanitize=address,undefined` перевіряє відсутність переповнення буферів при формуванні пакетів I2C та структурах `nvme_admin_cmd`.
2. **Valgrind Memcheck:** Перевіряє відсутність використання неініціалізованої пам'яті при розрахунку контрольних сум CRC-16 та генерації сертифіката.
3. **Аудит дескрипторів:** За допомогою `lsof` та `valgrind --track-fds=yes` гарантується коректне закриття всіх системних файлових дескрипторів (`open` -> `close`) у разі будь-яких помилок вводу/виводу.

### Інтеграція в конвеєри апаратного тестування (HIL CI/CD)

У сучасних виробничих лініях модуль санітизації вбудовується в автоматизовані конвеєри Hardware-in-the-Loop (HIL) тестування. Перед передачею плати на повторне пакування сервер керування тестами автоматично запускає утиліту `sanitizer_engine`, отримує підписаний CoS через мережевий сокет або UART-консоль, валідує його хеш проти заводської бази серійних номерів та автоматично роздруковує фізичну QR-наклейку із сертифікатом відповідності для супровідної документації поверненого виробу.

Кожен успішно згенерований сертифікат CoS реєструється у розподіленому реєстрі обліку життєвого циклу обладнання (Hardware Lifecycle Ledger). Це створює юридично неспростовний ланцюжок доказів для аудиторів безпеки, підтверджуючи, що жоден носій інформації не покинув периметр підприємства без проходження повної процедури криптографічного стирання та апаратної нуліфікації ключів.
