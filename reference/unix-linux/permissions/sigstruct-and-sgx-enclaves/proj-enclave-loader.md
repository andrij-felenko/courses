# ⚙️ Практичне завантаження енклава через /dev/sgx_enclave

Ця вставка демонструє практичну реалізацію низькорівневого завантажувача енклавів Intel SGX у системному середовищі Linux з використанням інтерфейсу `ioctl` символьного пристрою `/dev/sgx_enclave`, висвітлюючи послідовність системних викликів, керування віртуальними адресами та пастки вирівнювання пам'яті.

## Архітектура інтерфейсу ioctl /dev/sgx_enclave

Ядро Linux (починаючи з версії 5.11) надає пристрій `/dev/sgx_enclave` для взаємодії користувацького простору з підсистемою SGX. Створення та ініціалізація енклава вимагають строго визначеної послідовності із чотирьох фаз:

1. **Створення контексту енклава (`SGX_IOC_ENCLAVE_CREATE`):** Передача драйверу структури `secs` (SGX Enclave Control Structure). Драйвер виділяє сторінку EPC під SECS та повертає внутрішній стан.
2. **Резервування віртуальної пам'яті (`mmap`):** Запит до ядра на виділення лінійного діапазону віртуальних адрес (ELRANGE) відповідного розміру на файловому дескрипторі `/dev/sgx_enclave`.
3. **Завантаження сторінок коду та даних (`SGX_IOC_ENCLAVE_ADD_PAGES`):** Додавання сторінок у циклі. Драйвер виконує інструкції `EADD` для копіювання даних та `EEXTEND` для оновлення вимірювання `MRENCLAVE`.
4. **Фінальна ініціалізація (`SGX_IOC_ENCLAVE_INIT`):** Передача бінарного макету `SIGSTRUCT`. Драйвер виконує інструкцію `EINIT`. Якщо верифікація підпису та вимірювань успішна, енклав переходить у стан готовності до виконання (`VALID = 1`).

## Деталізація параметрів викликів ioctl

При взаємодії з драйвером ядра користувацький процес заповнює спеціалізовані структури, визначені у заголовному файлі `<asm/sgx.h>`:

- **`struct sgx_enclave_create`:** Містить єдине поле `src` — 64-бітну покажчикову адресу джерела, яка вказує на підготовлену користувацьку сторінку SECS. Сторінка SECS задає розмір енклава, атрибути `ATTRIBUTES` та атрибути винятків.
- **`struct sgx_enclave_add_pages`:** Містить поля `src` (адреса даних джерела), `offset` (зсув відносно початку енклава), `length` (розмір масиву, кратний 4096 байтам), `secinfo` (покажчик на структуру `struct sgx_secinfo` з правами доступу), `flags` (біт `SGX_PAGE_MEASURE` вмикає виконання `EEXTEND` драйвером) та `count` — поле, у яке драйвер повертає кількість фактично доданих байтів.
- **`struct sgx_enclave_init`:** Містить поле `sigstruct` — покажчик на 1808-байтовий масив підпису розробника `SIGSTRUCT`.

## Реалізація завантажувача енклавів

Нижче наведено робочі приклади реалізації процесу створення та ініціалізації енклава. Приклад на мові C демонструє безпосереднє використання системних структур ядра `<asm/sgx.h>`, а приклад на мові C++ реалізує безпечну концепцію RAII для автоматичного управління ресурсами дескрипторів та закриттям відображень пам'яті.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <asm/sgx.h>

#define PAGE_SIZE 4096

/* Функція створення та ініціалізації порожнього енклава */
int load_sgx_enclave(const char *sigstruct_path, size_t enclave_size) {
    int sgx_fd = -1;
    void *enclave_addr = MAP_FAILED;
    struct sgx_enclave_create create_req;
    struct sgx_enclave_add_pages add_req;
    struct sgx_enclave_init init_req;
    struct sgx_secinfo secinfo;
    uint8_t sigstruct_buf[1808];
    uint8_t dummy_page[PAGE_SIZE];

    /* 1. Відкриття символьного пристрою SGX */
    sgx_fd = open("/dev/sgx_enclave", O_RDWR);
    if (sgx_fd < 0) {
        perror("Помилка відкриття /dev/sgx_enclave");
        return -1;
    }

    /* 2. Завантаження структури SIGSTRUCT з файлу */
    int sig_fd = open(sigstruct_path, O_RDONLY);
    if (sig_fd < 0) {
        perror("Помилка відкриття SIGSTRUCT файлу");
        close(sgx_fd);
        return -1;
    }
    if (read(sig_fd, sigstruct_buf, sizeof(sigstruct_buf)) != sizeof(sigstruct_buf)) {
        perror("Помилка читання SIGSTRUCT");
        close(sig_fd);
        close(sgx_fd);
        return -1;
    }
    close(sig_fd);

    /* 3. Ініціалізація та виклик SGX_IOC_ENCLAVE_CREATE */
    memset(&create_req, 0, sizeof(create_req));
    /* Потрібно підготувати вирівняну SECS структуру */
    uint8_t secs_buf[4096] __attribute__((aligned(4096)));
    memset(secs_buf, 0, sizeof(secs_buf));

    /* Налаштування полів SECS: розмір енклава повинен бути ступенем двійки */
    *(uint64_t *)(secs_buf + 8) = enclave_size; /* size */
    create_req.src = (uint64_t)secs_buf;

    if (ioctl(sgx_fd, SGX_IOC_ENCLAVE_CREATE, &create_req) < 0) {
        perror("Помилка SGX_IOC_ENCLAVE_CREATE");
        close(sgx_fd);
        return -1;
    }

    /* 4. Відображення пам'яті енклава у віртуальний простір */
    enclave_addr = mmap(NULL, enclave_size, PROT_READ | PROT_WRITE | PROT_EXEC,
                        MAP_SHARED, sgx_fd, 0);
    if (enclave_addr == MAP_FAILED) {
        perror("Помилка mmap енклава");
        close(sgx_fd);
        return -1;
    }

    /* 5. Додавання сторінки коду/даних через SGX_IOC_ENCLAVE_ADD_PAGES */
    memset(&secinfo, 0, sizeof(secinfo));
    secinfo.flags = SGX_SECINFO_REG | SGX_SECINFO_R | SGX_SECINFO_W | SGX_SECINFO_X;

    memset(dummy_page, 0x90, sizeof(dummy_page)); /* NOP інструкції */

    memset(&add_req, 0, sizeof(add_req));
    add_req.src = (uint64_t)dummy_page;
    add_req.offset = 0; /* Перша сторінка за адресою enclave_addr */
    add_req.length = PAGE_SIZE;
    add_req.secinfo = (uint64_t)&secinfo;
    add_req.flags = SGX_PAGE_MEASURE; /* Драйвер виконає EEXTEND для кожного 256-байтового блоку */

    if (ioctl(sgx_fd, SGX_IOC_ENCLAVE_ADD_PAGES, &add_req) < 0) {
        perror("Помилка SGX_IOC_ENCLAVE_ADD_PAGES");
        munmap(enclave_addr, enclave_size);
        close(sgx_fd);
        return -1;
    }

    /* 6. Активація енклава через SGX_IOC_ENCLAVE_INIT */
    memset(&init_req, 0, sizeof(init_req));
    init_req.sigstruct = (uint64_t)sigstruct_buf;

    if (ioctl(sgx_fd, SGX_IOC_ENCLAVE_INIT, &init_req) < 0) {
        perror("Помилка SGX_IOC_ENCLAVE_INIT (EINIT)");
        munmap(enclave_addr, enclave_size);
        close(sgx_fd);
        return -1;
    }

    printf("Енклав успішно створено та ініціалізовано за адресою: %p\n", enclave_addr);
    
    /* Очищення ресурсів після завершення демонстрації */
    munmap(enclave_addr, enclave_size);
    close(sgx_fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <memory>
#include <fstream>
#include <stdexcept>
#include <system_error>
#include <cerrno>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <asm/sgx.h>

constexpr std::size_t kPageSize = 4096;
constexpr std::size_t kSigstructSize = 1808;

/* RAII обгортка для файлового дескриптора SGX */
class SgxDevice {
public:
    explicit SgxDevice(const char* device_path = "/dev/sgx_enclave") {
        fd_ = ::open(device_path, O_RDWR);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити SGX пристрій");
        }
    }

    ~SgxDevice() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SgxDevice(const SgxDevice&) = delete;
    SgxDevice& operator=(const SgxDevice&) = delete;

    [[nodiscard]] int get() const noexcept { return fd_; }

private:
    int fd_{-1};
};

/* RAII обгортка для відображення пам'яті mmap */
class EnclaveMemory {
public:
    EnclaveMemory(int sgx_fd, std::size_t size) : size_(size) {
        addr_ = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE | PROT_EXEC,
                        MAP_SHARED, sgx_fd, 0);
        if (addr_ == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "Помилка mmap пам'яті енклава");
        }
    }

    ~EnclaveMemory() {
        if (addr_ != MAP_FAILED) {
            ::munmap(addr_, size_);
        }
    }

    EnclaveMemory(const EnclaveMemory&) = delete;
    EnclaveMemory& operator=(const EnclaveMemory&) = delete;

    [[nodiscard]] void* data() const noexcept { return addr_; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }

private:
    void* addr_{MAP_FAILED};
    std::size_t size_{0};
};

/* Клас завантажувача енклавів */
class EnclaveLoader {
public:
    static void load(const std::string& sigstruct_path, std::size_t enclave_size) {
        SgxDevice device;

        // 1. Читання бінарної структури SIGSTRUCT
        std::array<std::uint8_t, kSigstructSize> sigstruct_buf{};
        std::ifstream sig_file(sigstruct_path, std::ios::binary);
        if (!sig_file.read(reinterpret_cast<char*>(sigstruct_buf.data()), kSigstructSize)) {
            throw std::runtime_error("Помилка читання файлу SIGSTRUCT");
        }

        // 2. Створення SECS та виклик SGX_IOC_ENCLAVE_CREATE
        alignas(kPageSize) std::array<std::uint8_t, kPageSize> secs_buf{};
        *reinterpret_cast<std::uint64_t*>(secs_buf.data() + 8) = enclave_size;

        sgx_enclave_create create_req{};
        create_req.src = reinterpret_cast<std::uint64_t>(secs_buf.data());

        if (::ioctl(device.get(), SGX_IOC_ENCLAVE_CREATE, &create_req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl SGX_IOC_ENCLAVE_CREATE");
        }

        // 3. Резервування віртуальної пам'яті через mmap RAII
        EnclaveMemory enclave_mem(device.get(), enclave_size);

        // 4. Додавання початкової сторінки
        alignas(kPageSize) std::array<std::uint8_t, kPageSize> code_page{};
        code_page.fill(0x90); // Заповнення NOP інструкціями

        sgx_secinfo secinfo{};
        secinfo.flags = SGX_SECINFO_REG | SGX_SECINFO_R | SGX_SECINFO_W | SGX_SECINFO_X;

        sgx_enclave_add_pages add_req{};
        add_req.src = reinterpret_cast<std::uint64_t>(code_page.data());
        add_req.offset = 0;
        add_req.length = kPageSize;
        add_req.secinfo = reinterpret_cast<std::uint64_t>(&secinfo);
        add_req.flags = SGX_PAGE_MEASURE;

        if (::ioctl(device.get(), SGX_IOC_ENCLAVE_ADD_PAGES, &add_req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl SGX_IOC_ENCLAVE_ADD_PAGES");
        }

        // 5. Ініціалізація енклава
        sgx_enclave_init init_req{};
        init_req.sigstruct = reinterpret_cast<std::uint64_t>(sigstruct_buf.data());

        if (::ioctl(device.get(), SGX_IOC_ENCLAVE_INIT, &init_req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl SGX_IOC_ENCLAVE_INIT");
        }

        std::cout << "Енклав C++ успішно завантажено за адресою: " << enclave_mem.data() << std::endl;
    }
};
```
:::

## Опис розширених операцій SGX2 та налаштування /dev/sgx_provision

Окрім базових викликів створення та наповнення, ядро Linux надає розширені виклики `ioctl` для систем з підтримкою SGX2:

- **`SGX_IOC_ENCLAVE_RESTRICT_PERMISSIONS`:** Звуження прав доступу сторінки EPCM з боку самого енклава через виконання апаратної інструкції `EMODPR`.
- **`SGX_IOC_ENCLAVE_MODIFY_TYPES`:** Зміна типу сторінки (наприклад, перетворення звичайної сторінки даних `REG` у структуру `TCS` або `TRIM`).

Окремий символьний пристрій `/dev/sgx_provision` використовується виключно для доступу до ключів атестації та провізіонінгу (`Provisioning Key`). Викликаючи `SGX_IOC_ENCLAVE_PROVISION`, процес передає драйверу не токен, а відкритий файловий дескриптор `/dev/sgx_provision` — саме право відкрити цей файл і є дозволом. Права доступу до `/dev/sgx_provision` вимагають привілеїв суперкористувача або членства у спеціалізованій групі `sgx`, оскільки доступ до цих ключів дозволяє енклаву генерувати сертифікати атестації, що зв'язують обчислення з унікальним апаратним ID процесора.

## Багатопотоковість та керування структурами TCS

Для підтримки паралельного виконання декількох потоків усередині одного енклава завантажувач зобов'язаний виділити окремі сторінки типу `TCS` (Thread Control Structure) для кожного потоку. Кожна сторінка `TCS` описує унікальну точку входу, покажчик на стек SSA (State Save Area) та локальний стек потоку.

Якщо два системних потоки користувацького процесу спробують одночасно виконати інструкцію `EENTER`, звертаючись до однієї і тієї самої сторінки `TCS`, другий `EENTER` завершиться винятком `#GP` — структура TCS уже позначена як зайнята. Для запобігання цьому завантажувачі створюють пули `TCS`-сторінок і синхронізують їх розподіл між POSIX-потоками додатка-хоста.

## Критичні вимоги та пастки реалізації

Під час роботи з пристроєм `/dev/sgx_enclave` необхідно враховувати наступні низькорівневі обмеження ядра та апаратури:

1. **Кратно-степеневе вирівнювання розміру енклава (ELRANGE Alignment):** Поле розміру енклава `size` у структурі SECS повинно бути степенем двійки (2ⁿ). Віртуальна адреса, отримана через `mmap`, також має бути вирівняна на кордон свого власного розміру (наприклад, енклав розміром 16 МБ повинен починатися з віртуальної адреси, кратної 16 МБ).
2. **Права доступу сторінок SECINFO:** Прапори `secinfo.flags` при виконанні `SGX_IOC_ENCLAVE_ADD_PAGES` визначають апаратні права в EPCM. Якщо програма додасть сторінку без прапора `SGX_SECINFO_X`, спроба виконати з неї код обірветься сторінковим збоєм `#PF` із виставленим бітом `SGX` у коді помилки.
3. **Послідовність виконання EEXTEND:** Драйвер ядра автоматично розбиває 4096-байтову сторінку на шістнадцять 256-байтових блоків і викликає апаратну інструкцію `EEXTEND` для кожного з них. Будь-яка зміна порядку додавання сторінок або вмісту джерела `src` змінить підсумковий SHA-256 хеш `MRENCLAVE`, і `EINIT` відмовить із кодом `SGX_INVALID_MEASUREMENT`.
4. **Обробка винятку EPCM Fault:** Якщо у процесі виконання енклав звертається до сторінки, яка вивантажена ядром у swap через `EWB`, ядро перехоплює сторінковий збій `#PF`, виконує `ELDU` для повернення сторінки в EPC і відновлює виконання інструкції через `ERESUME`.
5. **Санітизація покажчиків при викликах OCALL:** Оскільки додаток-хост виконується у недовіреній пам'яті, код всередині енклава повинен суворо санітизувати будь-які покажчики та буфери, що повертаються з недовіреного світу при виконанні OCALL (Out-call). Використання недовіреного покажчика без перевірки його знаходження поза межами діапазону ELRANGE відкриває можливість атак типу Iago Attack, коли ОС змушує енклав перезаписати власну захищену пам'ять.
