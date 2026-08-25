# ⚙️ Налаштування вкладеної трансляції через IOMMUFD у C та C++

Взаємодія з новим фреймворком IOMMUFD у ядрі Linux дозволяє гіпервізору L0 виділити апаратну таблицю сторінок Стадії 2 (Stage 2 HWPT) та прив'язати до неї вкладену таблицю сторінок Стадії 1 (Nested Stage 1 HWPT), якою керує гостьова операційна система L1. Це позбавляє гіпервізор необхідності емулювати тіньові таблиці сторінок (Shadow Page Tables) та обробляти тисячі виходів у гіпервізор (VM-exits) на секунду під час інтенсивного вводу-виводу.

## Архітектурний механізм IOMMUFD для вкладеної трансляції

У класичному фреймворку `vfio_iommu_type1` керування IOMMU здійснювалося через монолітні контейнери, що робило неможливим пряме прокидання гостьових таблиць сторінок у фізичний контролер IOMMU. Підсистема IOMMUFD представляє ресурси IOMMU у вигляді окремих файлових дескрипторів та об'єктів у просторі користувача.

Головними об'єктами IOMMUFD є:
1. **IOAS (IO Address Space):** Абстракція адресного простору вводу-виводу, яка визначає мапінг між віртуальними адресами DMA та фізичними сторінками оперативної пам'яті.
2. **HWPT (Hardware Page Table):** Об'єкт, що відповідає реальній апаратній таблиці сторінок IOMMU. Для вкладеної трансляції створюється базова HWPT Стадії 2 (L1 GPA → HPA), а поверх неї конфігурується вкладена HWPT Стадії 1 (L2 GPA → L1 GPA).
3. **IOMMUFD Device:** Об'єкт, що зв'язує фізичний PCI-пристрій з відповідним файловим дескриптором IOMMUFD.

Процес налаштування вкладеного домену складається з послідовних кроків:
- Відкриття файлового дескриптора `/dev/iommufd`.
- Отримання інформації про можливості фізичного IOMMU командою `ioctl(IOMMU_GET_HW_INFO)`.
- Виділення базового простору IOAS (`IOMMU_IOAS_ALLOC`) та створення HWPT Стадії 2.
- Виклик `ioctl(IOMMU_HWPT_ALLOC)` для вкладеної HWPT Стадії 1: батьківським `pt_id` вказано HWPT Стадії 2 (її виділено з прапорцем `IOMMU_HWPT_ALLOC_NEST_PARENT`), а `data_type`/`data_uptr` описують гостьовий формат Стадії 1 разом з адресою кореня таблиць L1 у просторі L1 GPA.
- Прив'язка PCI-пристрою до новоствореної вкладеної HWPT.

Гіпервізор L0 виступає арбітром між фізичним залізом і гостем L1. Гіпервізор L0 відповідає за валідацію форматів та перевірку того, що гостьова адреса кореня знаходиться в межах дозволеного адресного простору L1.

## Життєвий цикл файлового дескриптора /dev/iommufd

Коли процес гіпервізора QEMU ініціалізує прокидання пристрою, він відкриває псевдопристрій `/dev/iommufd` та отримує анонімний файловий дескриптор. Усі наступні маніпуляції здійснюються за допомогою системних викликів `ioctl()` над цим дескриптором:

1. **`IOMMU_GET_HW_INFO`:** Повертає структуру `struct iommu_hw_info`, яка містить тип апаратного забезпечення (`IOMMU_HW_INFO_TYPE_INTEL_VTD` або `IOMMU_HW_INFO_TYPE_ARM_SMMUV3`), версію специфікації, ширину підтримуваних адрес та підтримувані прапорці інвалідації.
2. **`IOMMU_IOAS_ALLOC`:** Створює порожній простір IOAS і повертає його `ioas_id`.
3. **`IOMMU_IOAS_MAP`:** Заповнює Стадію 2 — прив'язує діапазон IOVA (для гостя L1 це його L1 GPA) до сторінок у пам'яті процесу QEMU. Усі фізичні сторінки пам'яті гостя L1 запінюються у ядрі L0 за допомогою виклику `pin_user_pages_fast()` з прапорцем `FOLL_LONGTERM`.
4. **`IOMMU_HWPT_ALLOC`:** Створює апаратну таблицю сторінок. Якщо `pt_id` вказує на вже наявну HWPT Стадії 2, а `data_type` описує гостьовий формат, ядро створює зв'язану пару HWPT, де Стадія 1 читає гостьові таблиці L1, а Стадія 2 транслює L1 GPA у HPA.

## Детальний розбір структури IOMMU_GET_HW_INFO

Перед створенням HWPT Стадії 1 програма зобов'язана запитати апаратні характеристики конкретного PCI-пристрою та контролера IOMMU. Нижче наведено описи відповідної структури мовами C та C++:

:::tabs
```c
/* Структура запиту апаратних можливостей пристрою у C */
struct iommu_hw_info {
    __u32 size;            /* Розмір структури для зворотної сумісності */
    __u32 flags;           /* Бітове поле прапорців */
    __u32 dev_id;          /* Ідентифікатор пристрою у системі IOMMUFD */
    __u32 data_len;        /* Довжина буфера специфічних даних */
    __u64 data_uptr;       /* Вказівник на буфер у пам'яті користувача */
    __u32 out_data_type;   /* Повернений тип апаратного забезпечення */
};
```
```cpp
/* Ідіоматичне представлення структури запиту можливостей пристрою у C++20 */
struct IommuHardwareInfo {
    std::uint32_t size{sizeof(IommuHardwareInfo)};
    std::uint32_t flags{0};
    std::uint32_t dev_id{0};
    std::uint32_t data_len{0};
    std::uint64_t data_uptr{0};
    std::uint32_t out_data_type{0};
};
```
:::

Поле `out_data_type` повертає один із підтримуваних типів вкладеної трансляції:
- `IOMMU_HW_INFO_TYPE_INTEL_VTD`: апаратний контролер Intel VT-d з підтримкою Scalable Mode та двох стадій трансляції.
- `IOMMU_HW_INFO_TYPE_ARM_SMMUV3`: апаратний контролер ARM SMMUv3 з підтримкою Stream Table Entry (STE) та Context Descriptors (CD).

Якщо поле `data_uptr` заповнене вказівником на буфер, ядро поверне специфічну для архітектури маску можливостей. Наприклад, для Intel VT-d ядро повертає регістр capabilities (CAP_REG) та extended capabilities (ECAP_REG), що дозволяє гіпервізору перевірити підтримку 5-рівневого пейджингу та підтримку версій специфікації PASID.

## Створення мапінгів простору IOAS та HugePages

Для налаштування Стадії 2 гіпервізор L0 заповнює простір IOAS за допомогою системного виклику `IOMMU_IOAS_MAP`. Цей виклик зв'язує гостьові фізичні адреси (L1 GPA) з віртуальними адресами процесу QEMU (HVA):

:::tabs
```c
/* Створення мапінгу IOAS у C */
int map_ioas_region_c(int iommufd_fd, uint32_t ioas_id, uint64_t hva_address,
                     uint64_t l1_gpa_address, uint64_t memory_region_size)
{
    struct iommu_ioas_map map_cmd;
    memset(&map_cmd, 0, sizeof(map_cmd));
    map_cmd.size = sizeof(map_cmd);
    map_cmd.ioas_id = ioas_id;
    map_cmd.flags = IOMMU_IOAS_MAP_READABLE | IOMMU_IOAS_MAP_WRITEABLE |
                    IOMMU_IOAS_MAP_FIXED_IOVA; /* IOVA задає викликач, а не ядро */
    map_cmd.user_va = hva_address;
    map_cmd.iova = l1_gpa_address;
    map_cmd.length = memory_region_size;

    if (ioctl(iommufd_fd, IOMMU_IOAS_MAP, &map_cmd) < 0) {
        perror("Помилка створення мапінгу IOAS");
        return -1;
    }
    return 0;
}
```
```cpp
/* Ідіоматична реалізація створення мапінгу IOAS у C++20 */
[[nodiscard]] std::expected<void, std::error_code> map_ioas_region_cpp(
    int iommufd_fd,
    std::uint32_t ioas_id,
    std::uint64_t hva_address,
    std::uint64_t l1_gpa_address,
    std::uint64_t memory_region_size) noexcept
{
    iommu_ioas_map map_cmd{};
    map_cmd.size = sizeof(map_cmd);
    map_cmd.ioas_id = ioas_id;
    map_cmd.flags = IOMMU_IOAS_MAP_READABLE | IOMMU_IOAS_MAP_WRITEABLE |
                    IOMMU_IOAS_MAP_FIXED_IOVA; // IOVA задає викликач, а не ядро
    map_cmd.user_va = hva_address;
    map_cmd.iova = l1_gpa_address;
    map_cmd.length = memory_region_size;

    if (::ioctl(iommufd_fd, IOMMU_IOAS_MAP, &map_cmd) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
```
:::

Використання великих сторінок пам'яті (HugePages 2 МБ або 1 ГБ) у системі L0 значно спрощує структуру Стадії 2. Апаратний IOMMU покриває регіон HugePage одним великим записом на рівні каталогу замість сотень дрібних, що мінімізує кількість промахів у внутрішньому кеші IOTLB хоста під час тривалих операцій DMA.

При виникненні помилок створення мапінгу ядро повертає стандартні коди системних помилок: `EFAULT` у разі передачі некоректного віртуального покажчика HVA, `EOPNOTSUPP` якщо апаратний IOMMU не підтримує запитаний розмір сторінки, або `ENOMEM` при недостатності фізичної оперативної пам'яті для запінювання буферів. Гіпервізор зобов'язаний коректно обробляти ці помилки та переривати завантаження вкладеного гостя L2.

При видаленні або динамічному зменшенні обсягу пам'яті віртуальної машини використовується виклик `IOMMU_IOAS_UNMAP`, який скасовує мапінг та вивільняє раніше запінені сторінки RAM. Структура `struct iommu_ioas_unmap` передає діапазон IOVA та повертає фактично скасований обсяг у байтах. У разі виявлення спроб розпінування задіяних сторінок система повертає `EBUSY`. Це гарантує цілісність пам'яті під час динамічного перерозподілу ресурсів хоста.

## Практична реалізація створення вкладеного HWPT мовами C та C++

Нижче наведено робочий приклад конфігурації вкладеної HWPT Стадії 1 для архітектури Intel VT-d (Scalable Mode) мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/iommufd.h>

/* Структура конфігурації Intel VT-d Stage 1 для передачі в ядро */
struct iommu_hwpt_vtd_s1_config {
    __u64 flags;
    __u64 pgtbl_pptr; /* Фізичний покажчик на корінь таблиці сторінок L1 */
    __u32 addr_width; /* Ширина адреси (48 або 57 біт для 4/5-рівневого пейджингу) */
    __u32 pad;
};

/* Створення вкладеної HWPT Стадії 1 у C */
int create_nested_stage1_hwpt_c(int iommufd_fd, uint32_t dev_id, 
                                uint32_t stage2_hwpt_id, 
                                uint64_t l1_pgtbl_root,
                                uint32_t *out_nested_hwpt_id) 
{
    if (iommufd_fd < 0 || !out_nested_hwpt_id) {
        errno = EINVAL;
        return -1;
    }

    struct iommu_hwpt_vtd_s1_config vtd_s1_cfg;
    memset(&vtd_s1_cfg, 0, sizeof(vtd_s1_cfg));
    vtd_s1_cfg.flags = 0;
    vtd_s1_cfg.pgtbl_pptr = l1_pgtbl_root;
    vtd_s1_cfg.addr_width = 48; /* Стандартний 4-рівневий пейджинг x86_64 */

    struct iommu_hwpt_alloc alloc_cmd;
    memset(&alloc_cmd, 0, sizeof(alloc_cmd));
    alloc_cmd.size = sizeof(alloc_cmd);
    alloc_cmd.flags = 0; /* вкладеність задає не прапорець, а батьківський pt_id */
    alloc_cmd.dev_id = dev_id;
    alloc_cmd.pt_id = stage2_hwpt_id; /* Базовий батьківський HWPT Стадії 2 */
    alloc_cmd.data_type = IOMMU_HWPT_DATA_VTD_S1; /* Режим Intel VT-d Stage 1 */
    alloc_cmd.data_len = sizeof(vtd_s1_cfg);
    alloc_cmd.data_uptr = (uint64_t)(uintptr_t)&vtd_s1_cfg;

    if (ioctl(iommufd_fd, IOMMU_HWPT_ALLOC, &alloc_cmd) < 0) {
        perror("[C-API] Помилка виконання ioctl(IOMMU_HWPT_ALLOC)");
        return -1;
    }

    *out_nested_hwpt_id = alloc_cmd.out_hwpt_id;
    printf("[C-API] Успішно створено вкладений HWPT Stage 1 ID: %u\n", alloc_cmd.out_hwpt_id);
    return 0;
}
```
```cpp
#include <iostream>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <utility>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/iommufd.h>

/* RAII-обгортка для управління файловим дескриптором IOMMUFD */
class UniqueFd {
    int fd_ = -1;
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = std::exchange(other.fd_, -1);
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }
};

/* Специфічна конфігурація Intel VT-d Stage 1 */
struct VtdStage1Config {
    std::uint64_t flags{0};
    std::uint64_t pgtbl_pptr{0};
    std::uint32_t addr_width{48};
    std::uint32_t pad{0};
};

/* Ідіоматична реалізація створення вкладеної HWPT Стадії 1 у C++20 */
[[nodiscard]] std::expected<std::uint32_t, std::error_code> create_nested_stage1_hwpt_cpp(
    int iommufd,
    std::uint32_t dev_id,
    std::uint32_t stage2_hwpt_id,
    std::uint64_t l1_page_table_root) noexcept
{
    if (iommufd < 0) {
        return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
    }

    VtdStage1Config vtd_cfg{
        .flags = 0,
        .pgtbl_pptr = l1_page_table_root,
        .addr_width = 48,
        .pad = 0
    };

    iommu_hwpt_alloc alloc_cmd{};
    alloc_cmd.size = sizeof(alloc_cmd);
    alloc_cmd.flags = 0; // вкладеність задає не прапорець, а батьківський pt_id
    alloc_cmd.dev_id = dev_id;
    alloc_cmd.pt_id = stage2_hwpt_id;
    alloc_cmd.data_type = IOMMU_HWPT_DATA_VTD_S1;
    alloc_cmd.data_len = sizeof(vtd_cfg);
    alloc_cmd.data_uptr = reinterpret_cast<std::uint64_t>(&vtd_cfg);

    if (::ioctl(iommufd, IOMMU_HWPT_ALLOC, &alloc_cmd) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return alloc_cmd.out_hwpt_id;
}
```
:::

## Інвалідація кешу IOTLB з простору користувача

При апаратній вкладеній трансляції модифікація таблиць сторінок L1 здійснюється безпосередньо у віртуальній пам'яті L1 без генерування VM-exits. Однак фізичний контролер IOMMU кешує записи трансляції у своєму внутрішньому кеші IOTLB. Коли гостьова ОС L1 видаляє або змінює записи у своїх таблицях, вона відправляє команду інвалідації до vIOMMU.

Гіпервізор L0 (QEMU) перехоплює цю команду та виконує системний виклик `IOMMU_HWPT_INVALIDATE` через IOMMUFD. Це змушує ядро L0 видалити застарілі записи безпосередньо з апаратного кешу IOTLB фізичного IOMMU.

Нижче подано порівняльну реалізацію виклику інвалідації IOTLB мовами C та C++:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/iommufd.h>

/* Інвалідація IOTLB у C */
int invalidate_stage1_iotlb_c(int iommufd_fd, uint32_t nested_hwpt_id,
                              uint64_t *inv_entries_array, uint32_t num_entries)
{
    struct iommu_hwpt_invalidate inv_cmd;
    memset(&inv_cmd, 0, sizeof(inv_cmd));
    inv_cmd.size = sizeof(inv_cmd);
    inv_cmd.hwpt_id = nested_hwpt_id;
    inv_cmd.data_type = IOMMU_HWPT_INVALIDATE_DATA_VTD_S1;
    inv_cmd.entry_len = sizeof(struct iommu_hwpt_vtd_s1_invalidate);
    inv_cmd.entry_num = num_entries;
    inv_cmd.inv_data_uptr = (uint64_t)(uintptr_t)inv_entries_array;

    if (ioctl(iommufd_fd, IOMMU_HWPT_INVALIDATE, &inv_cmd) < 0) {
        perror("[C] Помилка інвалідації IOTLB для вкладеного HWPT");
        return -1;
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <expected>
#include <system_error>
#include <cstdint>
#include <span>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/iommufd.h>

/* Інвалідація IOTLB у C++20 з використанням std::span */
[[nodiscard]] std::expected<void, std::error_code> invalidate_stage1_iotlb_cpp(
    int iommufd_fd, 
    std::uint32_t nested_hwpt_id,
    std::span<const iommu_hwpt_vtd_s1_invalidate> entries) noexcept
{
    iommu_hwpt_invalidate inv_cmd{};
    inv_cmd.size = sizeof(inv_cmd);
    inv_cmd.hwpt_id = nested_hwpt_id;
    inv_cmd.data_type = IOMMU_HWPT_INVALIDATE_DATA_VTD_S1;
    inv_cmd.entry_len = sizeof(iommu_hwpt_vtd_s1_invalidate);
    inv_cmd.entry_num = static_cast<std::uint32_t>(entries.size());
    inv_cmd.inv_data_uptr = reinterpret_cast<std::uint64_t>(entries.data());

    if (::ioctl(iommufd_fd, IOMMU_HWPT_INVALIDATE, &inv_cmd) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
```
:::

## Опис структур даних інвалідації Intel VT-d

Кожен елемент масиву інвалідації `struct iommu_hwpt_vtd_s1_invalidate` описує конкретну операцію скидання кешу:
- **`addr`:** Початкова віртуальна адреса DMA, для якої видаляється трансляція.
- **`npages`:** Кількість 4-кілобайтних сторінок, які треба видалити з IOTLB.
- **`flags`:** Бітове поле прапорців. Прапорець `IOMMU_VTD_INV_FLAGS_LEAF` вказує, що треба інвалідувати лише кінцеву сторінку, а не самі міжрівневі каталоги сторінок.

При виконанні `IOMMU_HWPT_INVALIDATE` ядро Linux бере масив цих структур, перевіряє їхні межі у пам'яті користувача, а потім відправляє відповідні команди до інвалідаційної черги фізичного IOMMU (Invalidation Queue).

## Специфіка реалізації для ARM SMMUv3

Для архітектури ARM64 вкладена трансляція описується відповідною конфігураційною структурою:

:::tabs
```c
/* Структура конфігурації ARM SMMUv3 Stage 1 у C */
struct iommu_hwpt_arm_smmuv3_s1 {
    __u64 s1ctxptr; /* Фізична адреса Context Descriptor (CD) у пам'яті L1 */
};
```
```cpp
/* Конфігурація ARM SMMUv3 Stage 1 у C++20 */
struct IommuHwptArmSmmuV3S1 {
    std::uint64_t s1ctxptr{0}; /* Фізична адреса Context Descriptor (CD) у пам'яті L1 */
};
```
:::

На відміну від Intel VT-d, де передається безпосередньо корінь таблиці сторінок, в ARM SMMUv3 передається покажчик на Context Descriptor, який містить не лише корінь TTB0/TTB1, але й ідентифікатор ASID (Address Space ID) та параметри атрибутів пам'яті (MAIR). Це надає гіпервізору L1 повну свободу конфігурування режимів кешування для пристроїв L2.

## Демонтаж та руйнування ресурсів (Teardown Lifecycle)

При завершенні роботи віртуальної машини L2 або при відв'язуванні пристрою, гіпервізор L0 зобов'язаний виконати чисту процедуру демонтажу об'єктів IOMMUFD у зворотному порядку:

1. **Припинення DMA:** Гіпервізор надсилає сигнал пристрою зупинити всі активні DMA-транзакції через конфігураційний простір PCI (Command Register Bit 2: Bus Master Disable).
2. **Звільнення вкладеного HWPT:** Закриття дескриптора або виклик `ioctl(IOMMU_DESTROY)` над `nested_hwpt_id` знищує зв'язок з гостьовою Стадією 1. Фізичний IOMMU припиняє читати таблиці сторінок з пам'яті L1.
3. **Звільнення HWPT Стадії 2:** Знищення батьківської таблиці Стадії 2 розформовує мапінг L1 GPA → HPA.
4. **Розпінування пам'яті (Unpinning):** Ядро L0 знижує лічильники посилань на фізичні сторінки пам'яті `unpin_user_page()`, роблячи їх доступними для звичайного підкачування та перерозподілу ядра.

## Типові підводні камені та практичні рекомендації

1. **Перевірка апаратних можливостей (Capability Check):** Перед створенням вкладеної HWPT необхідно викликати `ioctl(IOMMU_GET_HW_INFO)`. Якщо апаратне забезпечення чи драйвер хоста не підтримують двостадійну трансляцію, системний виклик поверне помилку `EOPNOTSUPP`. Гіпервізор повинен бути готовим відкотитися до емуляції Shadow IOMMU.
2. **Узгодження глибини пейджингу (4-level vs 5-level):** Значення `addr_width` у конфігураційній структурі має чітко відповідати конфігурації ядра L1. Якщо L1 використовує 57-бітний адресний простір (5-level paging), а хост налаштований на 48-бітний, спроби DMA-доступу спричинять `DMAR Fault`.
3. **Синхронізація ATS (Address Translation Services):** Якщо прокинутий PCI-пристрій підтримує кешування записів у власному DevTLB, команди інвалідації повинні поширюватися не лише на IOTLB контролера IOMMU, але й на DevTLB самого пристрою — окремими пакетами PCIe ATS `Invalidate Request`, на які пристрій відповідає `Invalidate Completion`.
4. **Вирівнювання сторінок (Alignment):** Адреса кореня таблиці сторінок `pgtbl_pptr` повинна бути суворо вирівняна по межі 4 КБ (`0x1000`), інакше апаратний IOMMU згенерує помилку конфігурації контекстного запису.
5. **Безпека живого мігрування (Live Migration):** Під час міграції віртуальної машини L1 на інший хост, гіпервізор L0 повинен повністю зупинити вкладену HWPT Стадії 1, очистити кеш IOTLB і заново зареєструвати таблиці на цільовому хості.
