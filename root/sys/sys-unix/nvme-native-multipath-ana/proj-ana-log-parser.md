# ⚙️ Практикум: парсер журналу ANA Log Page через ioctl мовами C та C++

Утиліти керування простором користувача високого рівня (зокрема `nvme-cli`) надають зручні команди на кшталт `nvme ana-log /dev/nvme0`, проте для глибокого розуміння протоколу або інтеграції у власні високонавантажені сервіси збереження даних виникає потреба безпосередньої взаємодії з драйвером ядра. 

У цьому практичному проекті ми розробляємо утиліту для прямого зчитування та розбору журналу Asymmetric Namespace Access (ANA Log Page, ідентифікатор сторінки `LID = 0x0C`) через символьний вузол керування контролером `/dev/nvme0`. Програма взаємодіє з драйвером NVMe через системний виклик `ioctl` із командою `NVME_IOCTL_ADMIN_CMD`, оминаючи проміжні бібліотеки, здійснює двійковий розбір динамічних дескрипторів змінної довжини та виводить актуальну карту маршрутизації для всіх логічних томів.

---

## 1. Архітектура утиліти та взаємодія з драйвером

Для взаємодії з апаратним контролером безпосередньо з простору користувача використовується протокол прямих адміністративних команд Passthrough. Послідовність дій складається з чотирьох чітких кроків:

1. **Відкриття символьного вузла контролера:** файл `/dev/nvme0` (або `/dev/nvme1`) відкривається системним викликом `open()` у режимі лише для читання (`O_RDONLY`). Слід звернути особливу увагу на те, що адміністративні команди надсилаються до символьного вузла контролера, а не до блокового пристрою простору назв (`/dev/nvme0n1`). Спроба виконати `NVME_IOCTL_ADMIN_CMD` над блоковим пристроєм завершиться помилкою `ENOTTY` (*Inappropriate ioctl for device*).
2. **Формування командної структури `nvme_passthru_cmd`:**
   - Поле `opcode = 0x02` відповідає команді `Get Log Page` відповідно до базової специфікації NVMe.
   - Поле `nsid = 0xFFFFFFFF` вказує на запит загальносистемного журналу, що охоплює всі групи просторів назв.
   - Поле `cdw10` кодує ідентифікатор сторінки `LID = 0x0C` у молодших 8 бітах та молодшу частину розміру буфера у 32-бітних подвійних словах (`(data_len / 4) - 1`) у бітах `31:16`.
   - Поле `cdw11` за необхідності передає старші 16 бітів розміру буфера.
   - Поле `addr` містить віртуальну адресу користувацького буфера в пам'яті, приведеного до типу `uintptr_t`.
3. **Виконання системного виклику:** системний виклик `ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd)` передає запит у драйвер ядра, де функція `nvme_user_cmd()` формує апаратну команду в адміністративній черзі відправки (Admin Submission Queue), сповіщає контролер через регістр Doorbell та переводить процес у стан очікування переривання.
4. **Розбір двійкових структур у пам'яті:** після успішного повернення з ядра утиліта зчитує 16-байтний заголовок `struct nvme_ana_log`, перевіряє лічильник змін `chgcnt`, обчислює кількість груп `ngrps` та послідовно ітерує дескриптори груп `struct nvme_ana_group_desc`, враховуючи наявність динамічного масиву ідентифікаторів томів `nsids[]`.

---

## 2. Реалізація утиліти (C та C++)

:::tabs
```c
/* ana_dump.c — зчитування та розбір журналу NVMe ANA мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

#define NVME_LOG_ANA_LID 0x0c
#define BUFFER_SIZE 4096

/* Двійкові структури специфікації NVMe 1.4 / 2.0 */
struct nvme_ana_group_desc {
    uint32_t grpid;
    uint32_t nnsids;
    uint64_t chgcnt;
    uint8_t  state;
    uint8_t  rsvd17[15];
    uint32_t nsids[];
};

struct nvme_ana_log {
    uint64_t chgcnt;
    uint16_t ngrps;
    uint8_t  rsvd10[6];
};

static const char *ana_state_to_str(uint8_t state) {
    switch (state & 0x0f) {
        case 0x01: return "OPTIMIZED (AO)";
        case 0x02: return "NON-OPTIMIZED (ANO)";
        case 0x03: return "INACCESSIBLE (AI)";
        case 0x04: return "PERSISTENT LOSS (PL)";
        case 0x0f: return "CHANGE STATE (TRANSITION)";
        default:   return "UNKNOWN";
    }
}

int main(int argc, char *argv[]) {
    const char *dev_path = (argc > 1) ? argv[1] : "/dev/nvme0";
    int fd = open(dev_path, O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття NVMe пристрою");
        return 1;
    }

    uint8_t buffer[BUFFER_SIZE];
    memset(buffer, 0, sizeof(buffer));

    uint32_t numd = (sizeof(buffer) / 4) - 1;
    struct nvme_passthru_cmd cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.opcode       = 0x02; /* Get Log Page */
    cmd.nsid         = 0xFFFFFFFF;
    cmd.addr         = (uintptr_t)buffer;
    cmd.data_len     = sizeof(buffer);
    cmd.cdw10        = ((numd & 0xFFFF) << 16) | NVME_LOG_ANA_LID;
    cmd.cdw11        = (numd >> 16) & 0xFFFF;
    cmd.timeout_ms   = 5000;

    if (ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd) < 0) {
        perror("Помилка виконання NVME_IOCTL_ADMIN_CMD");
        close(fd);
        return 1;
    }

    struct nvme_ana_log *log = (struct nvme_ana_log *)buffer;
    printf("=== ЖУРНАЛ СТАНІВ NVMe ANA (%s) ===\n", dev_path);
    printf("Глобальний лічильник змін (Change Counter): %lu\n", (unsigned long)log->chgcnt);
    printf("Кількість груп ANA (Number of Groups):     %u\n\n", (unsigned int)log->ngrps);

    uint8_t *ptr = buffer + sizeof(struct nvme_ana_log);
    uint8_t *end = buffer + sizeof(buffer);

    for (uint16_t i = 0; i < log->ngrps; i++) {
        if (ptr + sizeof(struct nvme_ana_group_desc) > end) {
            fprintf(stderr, "Попередження: буфер переповнено, журнал усічено.\n");
            break;
        }

        struct nvme_ana_group_desc *desc = (struct nvme_ana_group_desc *)ptr;
        size_t desc_size = sizeof(struct nvme_ana_group_desc) + (desc->nnsids * sizeof(uint32_t));

        if (ptr + desc_size > end) {
            fprintf(stderr, "Попередження: неповний дескриптор групи %u.\n", desc->grpid);
            break;
        }

        printf("Група ANA ID: %u\n", desc->grpid);
        printf("  Стан маршруту:       %s (0x%02X)\n", ana_state_to_str(desc->state), desc->state);
        printf("  Лічильник змін:      %lu\n", (unsigned long)desc->chgcnt);
        printf("  Кількість томів:     %u\n", desc->nnsids);
        printf("  Прив'язані томи NSID: ");

        for (uint32_t n = 0; n < desc->nnsids; n++) {
            printf("%u%s", desc->nsids[n], (n + 1 < desc->nnsids) ? ", " : "");
        }
        printf("\n\n");

        ptr += desc_size;
    }

    close(fd);
    return 0;
}
```
```cpp
// ana_dump.cpp — ідіоматичний парсер NVMe ANA мовою C++20
#include <iostream>
#include <vector>
#include <string_view>
#include <memory>
#include <span>
#include <format>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

namespace nvme {

inline constexpr uint8_t LOG_ANA_LID = 0x0c;
inline constexpr size_t DEFAULT_BUFFER_SIZE = 4096;

struct [[gnu::packed]] AnaGroupDesc {
    uint32_t grpid;
    uint32_t nnsids;
    uint64_t chgcnt;
    uint8_t  state;
    uint8_t  rsvd17[15];
    uint32_t nsids[];
};

struct [[gnu::packed]] AnaLogHeader {
    uint64_t chgcnt;
    uint16_t ngrps;
    uint8_t  rsvd10[6];
};

constexpr std::string_view stateToString(uint8_t state) noexcept {
    switch (state & 0x0f) {
        case 0x01: return "OPTIMIZED (AO)";
        case 0x02: return "NON-OPTIMIZED (ANO)";
        case 0x03: return "INACCESSIBLE (AI)";
        case 0x04: return "PERSISTENT LOSS (PL)";
        case 0x0f: return "CHANGE STATE (TRANSITION)";
        default:   return "UNKNOWN";
    }
}

class Device {
    int fd_{-1};
public:
    explicit Device(std::string_view path) {
        fd_ = ::open(path.data(), O_RDONLY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити пристрій");
        }
    }

    ~Device() noexcept {
        if (fd_ >= 0) ::close(fd_);
    }

    Device(const Device&) = delete;
    Device& operator=(const Device&) = delete;

    [[nodiscard]] std::vector<uint8_t> fetchAnaLog(size_t bufferSize = DEFAULT_BUFFER_SIZE) const {
        std::vector<uint8_t> buffer(bufferSize, 0);
        const auto numd = static_cast<uint32_t>((buffer.size() / 4) - 1);

        nvme_passthru_cmd cmd{};
        cmd.opcode     = 0x02; // Get Log Page
        cmd.nsid       = 0xFFFFFFFF;
        cmd.addr       = reinterpret_cast<uintptr_t>(buffer.data());
        cmd.data_len   = static_cast<uint32_t>(buffer.size());
        cmd.cdw10      = ((numd & 0xFFFF) << 16) | LOG_ANA_LID;
        cmd.cdw11      = (numd >> 16) & 0xFFFF;
        cmd.timeout_ms = 5000;

        if (::ioctl(fd_, NVME_IOCTL_ADMIN_CMD, &cmd) < 0) {
            throw std::system_error(errno, std::generic_category(), "ioctl(NVME_IOCTL_ADMIN_CMD) зазнав невдачі");
        }

        return buffer;
    }
};

void parseAndPrint(std::span<const uint8_t> buffer, std::string_view devPath) {
    if (buffer.size() < sizeof(AnaLogHeader)) {
        std::cerr << "Буфер замалий для заголовка ANA\n";
        return;
    }

    const auto* header = reinterpret_cast<const AnaLogHeader*>(buffer.data());
    std::cout << std::format("=== ЖУРНАЛ СТАНІВ NVMe ANA ({}) ===\n", devPath);
    std::cout << std::format("Глобальний лічильник змін (Change Counter): {}\n", header->chgcnt);
    std::cout << std::format("Кількість груп ANA (Number of Groups):     {}\n\n", header->ngrps);

    size_t offset = sizeof(AnaLogHeader);
    for (uint16_t i = 0; i < header->ngrps; ++i) {
        if (offset + sizeof(AnaGroupDesc) > buffer.size()) {
            std::cerr << "Попередження: неочікуваний кінець буфера дескрипторів.\n";
            break;
        }

        const auto* desc = reinterpret_cast<const AnaGroupDesc*>(buffer.data() + offset);
        const size_t descSize = sizeof(AnaGroupDesc) + (desc->nnsids * sizeof(uint32_t));

        if (offset + descSize > buffer.size()) {
            std::cerr << std::format("Попередження: обрізаний дескриптор для групи {}.\n", desc->grpid);
            break;
        }

        std::cout << std::format("Група ANA ID: {}\n", desc->grpid);
        std::cout << std::format("  Стан маршруту:       {} (0x{:02X})\n", stateToString(desc->state), desc->state);
        std::cout << std::format("  Лічильник змін:      {}\n", desc->chgcnt);
        std::cout << std::format("  Кількість томів:     {}\n", desc->nnsids);
        std::cout << "  Прив'язані томи NSID: ";

        std::span<const uint32_t> nsids(desc->nsids, desc->nnsids);
        for (size_t n = 0; n < nsids.size(); ++n) {
            std::cout << nsids[n] << (n + 1 < nsids.size() ? ", " : "");
        }
        std::cout << "\n\n";

        offset += descSize;
    }
}

} // namespace nvme

int main(int argc, char* argv[]) {
    const std::string_view devPath = (argc > 1) ? argv[1] : "/dev/nvme0";
    try {
        const nvme::Device device(devPath);
        const auto buffer = device.fetchAnaLog();
        nvme::parseAndPrint(buffer, devPath);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

---

## 3. Детальний аналіз реалізації та обробки помилок

Під час взаємодії з низькорівневим інтерфейсом NVMe необхідно враховувати кілька важливих системних аспектів:

### Безпека меж пам'яті під час ітерування
Оскільки розмір дескриптора залежить від поля `desc->nnsids`, зловмисно модифікований або пошкоджений кадр журналу може містити неправдоподібно велике число просторів назв. Програма виконує подвійну перевірку:
1. Перевірка наявності місця для базового тіла дескриптора: `ptr + sizeof(struct nvme_ana_group_desc) <= end`.
2. Перевірка наявності всього масиву `nsids`: `ptr + desc_size <= end`.

Якщо дескриптор виходить за межі виділеного буфера, цикл негайно переривається з повідомленням про обрізаний журнал, запобігаючи читанню невиділеної пам'яті (*heap out-of-bounds read*).

### Права доступу та привілеї
Виконання системного виклику `ioctl(NVME_IOCTL_ADMIN_CMD)` вимагає адміністративних привілеїв у системі (наявності можливості `CAP_SYS_ADMIN`). Спроба запуску утиліти від імені звичайного непривілейованого користувача призведе до помилки `EPERM` (*Operation not permitted*) на етапі відкриття пристрою або `EACCES` під час виконання виклику керування.

### Вирівнювання буфера та робота DMA
Драйвер ядра Linux під час обробки `NVME_IOCTL_ADMIN_CMD` викликає внутрішню функцію `blk_rq_map_user()`, яка будує список сторінок для прямого доступу контролера до пам'яті (Direct Memory Access). Для уникнення додаткового копіювання через проміжні системні буфери (*bounce buffers*) користувацький буфер повинен бути вирівняний у пам'яті мінімум по межі 4 байтів, що в реалізації C++ автоматично забезпечується стандартним контейнером `std::vector<uint8_t>`.

### Врахування порядку байтів (Endianness)
Специфікація NVMe суворо визначає, що всі цілочисельні поля дескрипторів та заголовків журналу передаються у форматі з прямим порядком байтів (Little-Endian). На архітектурах x86_64 порядок байтів процесора збігається з форматом протоколу, проте під час портування на архітектури зі зворотним порядком байтів (Big-Endian, наприклад, IBM s390x або SPARC) читання 32-бітних та 64-бітних полів вимагає явного виклику макросів перетворення типу `le32toh()` та `le64toh()`.

### Обробка багатосторінкових журналів та зміщення (Log Page Offset)
Якщо цільовий дисковий масив містить десятки груп ANA або тисячі логічних просторів назв, розмір журналу легко перевищує розмір фіксованого буфера 4096 байтів. У таких корпоративних конфігураціях утиліта повинна спочатку зчитати 16-байтний заголовок, визначити точну кількість груп `ngrps`, обчислити сумарний розмір буфера з урахуванням усіх дескрипторів, та виконати цикл послідовного зчитування частин журналу, передаючи зміщення через командні слова `cdw12` (молодші 32 біти зсуву) та `cdw13` (старші 32 біти).

### Шлях виконання виклику в ядрі Linux
Коли процес користувача викликає `ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd)`:
1. Ядро входить у точку входу `nvme_dev_ioctl()` підсистеми NVMe.
2. Функція `nvme_user_cmd()` перевіряє права процесу (`capable(CAP_SYS_ADMIN)`), копіює командну структуру з простору користувача та виділяє запит блокового рівня `struct request` в адміністративній черзі контролера.
3. Функція `blk_rq_map_user()` будує сторінковий вектор DMA для безпосереднього запису відповіді контролера у віртуальну пам'ять користувацького буфера без проміжного копіювання в пам'яті ядра.
4. Драйвер встановлює біт у регістрі Doorbell контролера; процесор контролера зчитує команду, готує двійковий кадр журналу та надсилає сигнал завершення через чергу Admin Completion Queue.
5. Після отримання апаратного переривання ядро пробуджує сплячий процес користувача та повертає керування з кодом `0`.

---

## 4. Збірка та очікуваний вивід утиліти

Збірка утиліти здійснюється стандартними компіляторами GNU Toolchain:

```bash
# Збірка версії мовою C
gcc -O2 -Wall -Wextra ana_dump.c -o ana_dump_c

# Збірка версії мовою C++20
g++ -O2 -std=c++20 -Wall -Wextra ana_dump.cpp -o ana_dump_cpp
```

Приклад запуску над підключеним контролером дискового масиву NVMe-oF:

```bash
sudo ./ana_dump_cpp /dev/nvme0
```

Типовий результат виконання програми:

```
=== ЖУРНАЛ СТАНІВ NVMe ANA (/dev/nvme0) ===
Глобальний лічильник змін (Change Counter): 42
Кількість груп ANA (Number of Groups):     2

Група ANA ID: 1
  Стан маршруту:       OPTIMIZED (AO) (0x01)
  Лічильник змін:      18
  Кількість томів:     2
  Прив'язані томи NSID: 1, 2

Група ANA ID: 2
  Стан маршруту:       NON-OPTIMIZED (ANO) (0x02)
  Лічильник змін:      24
  Кількість томів:     2
  Прив'язані томи NSID: 3, 4
```

Отримані дані повністю узгоджуються з топологією масиву: для першої групи просторів назв (томи 1 та 2) поточний контролер є прямим власником (стан Optimized), тоді як для другої групи (томи 3 та 4) доступ здійснюється через міжконтролерну шину в режимі проксі (стан Non-Optimized).
