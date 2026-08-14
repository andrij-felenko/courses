# ⚙️ Практична реалізація P2PDMA: ядровий модуль та утиліта користувача

У цій практичній вставці наведено повноцінні прикладні фрагменти коду для роботи з підсистемою PCIe Peer-to-Peer DMA (P2PDMA) у ядрі Linux та просторі користувача. У першій частині розібрано архітектуру модуля ядра на мові C, який виконує пошук пристроїв за ідентифікаторами Bus:Device:Function (BDF), аналізує топологічну відстань між ними, виділяє буфер у регіоні Controller Memory Buffer (CMB) та налаштовує таблицю розсіяного передавання (`scatterlist`). У другій частині наведено утиліту простору користувача для тестування P2P-пам'яті через символьний пристрій `/dev/p2pmemX`, написану у двох ідіоматичних реалізаціях на мовах C та C++.

## 1. Архітектура та логіка ядрового DMA-драйвера

Розробка ядрових драйверів для роботи з P2PDMA вимагає чіткого дотримання життєвого циклу ресурсів PCIe. Модуль ядра оперує безпосередньо апаратними BAR-регістрами, тому будь-яка помилка у виправленні посилань на пристрої (`refcounting`) або передчасне вилучення модуля може призвести до системної паніки ядра (Kernel Panic).

У просторі ядра Linux використовується виключно мова C. Використання C++ у середовищі ядра є неможливим, оскільки ядро не несе в собі бібліотеки `libstdc++`, не підтримує динамічне виділення пам'яті через `new`/`delete` з класичними конструкторами, не підтримує механізми розгортання стеку при винятках (`exceptions`) та таблиці віртуальних методів RTTI.

### Етапи виконання в ядрі

1. **Отримання посилань на пристрої:** Модуль приймає BDF-імена провайдера (наприклад, NVMe SSD) та клієнта (наприклад, FPGA або SmartNIC). За допомогою функцій PCI-підсистеми ядро знаходить відповідні структури `struct pci_dev` та збільшує їхні лічильники посилань.
2. **Перевірка сумісності топології:** Виклик `pci_p2pdma_distance_many()` аналізує всі проміжні PCIe Switches та Root Complex. Якщо на шляху між пристроями виявлено міст із примусовим перенаправленням ACS, функція повертає від'ємне значення, і драйвер зобов'язаний коректно перервати ініціалізацію.
3. **Виділення P2P-пам'яті:** За допомогою `pci_alloc_p2pmem()` ядро виділяє сторінки пам'яті з пулу провайдера. На відміну від стандартного `kmalloc()`, ця пам'ять фізично знаходиться в MMIO BAR периферійного пристрою, але має відповідні структури `struct page` у зоні `ZONE_DEVICE`.
4. **Мапування `scatterlist`:** Створення елемента `struct scatterlist` та його підготовка через `pci_p2pdma_map_sg()`. Функція розраховує шинну DMA-адресу, яку драйвер записує в регістри контролера клієнтського пристрою для початку апаратного прямого доступ.

### Повний вихідний код модуля ядра

```c
/*
 * p2p_dma_demo.c — Приклад модуля ядра Linux для тестування pci-p2pdma
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/pci.h>
#include <linux/pci-p2pdma.h>
#include <linux/dma-mapping.h>
#include <linux/scatterlist.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Antigravity Engineer");
MODULE_DESCRIPTION("PCIe P2PDMA Mapping Demo Driver");

// BDF пристроїв для прикладу (передаються як параметри модуля при insmod)
static char *provider_bdf = "0000:03:00.0"; // NVMe SSD з CMB
static char *client_bdf   = "0000:04:00.0"; // Ініціатор DMA (FPGA / SmartNIC)

module_param(provider_bdf, charp, 0644);
MODULE_PARM_DESC(provider_bdf, "PCI BDF of Provider Device (e.g. 0000:03:00.0)");
module_param(client_bdf, charp, 0644);
MODULE_PARM_DESC(client_bdf, "PCI BDF of Client Device (e.g. 0000:04:00.0)");

static struct pci_dev *provider_dev;
static struct pci_dev *client_dev;
static void *p2p_vaddr;
static struct scatterlist sg;

static int __init p2p_demo_init(void)
{
    int ret = 0;
    int dist;
    int nents;
    dma_addr_t dma_bus_addr;
    struct device *clients[1];

    pr_info("P2PDMA Demo: Початок ініціалізації драйвера\n");

    // 1. Пошук пристроїв за їхніми BDF в ірархії PCI
    provider_dev = pci_get_pfnblock(provider_bdf);
    if (!provider_dev) {
        pr_err("P2PDMA Demo: Не знайдено пристрій-провайдер %s\n", provider_bdf);
        return -ENODEV;
    }

    client_dev = pci_get_pfnblock(client_bdf);
    if (!client_dev) {
        pr_err("P2PDMA Demo: Не знайдено пристрій-клієнт %s\n", client_bdf);
        pci_dev_put(provider_dev);
        return -ENODEV;
    }

    // 2. Перевірка топологічної відстані та ACS сумісності
    clients[0] = &client_dev->dev;
    dist = pci_p2pdma_distance_many(provider_dev, clients, 1, true);
    if (dist < 0) {
        pr_err("P2PDMA Demo: P2P DMA НЕМОЖЛИВИЙ між %s та %s (dist=%d)\n",
               provider_bdf, client_bdf, dist);
        ret = -EIO;
        goto err_put;
    }

    pr_info("P2PDMA Demo: Обчислена топологічна відстань P2P: %d\n", dist);

    // 3. Виділення 4 КіБ пам'яті з P2P пулу провайдера
    p2p_vaddr = pci_alloc_p2pmem(provider_dev, PAGE_SIZE);
    if (!p2p_vaddr) {
        pr_err("P2PDMA Demo: Не вдалося виділити P2P пам'ять із пулу провайдера\n");
        ret = -ENOMEM;
        goto err_put;
    }

    pr_info("P2PDMA Demo: Виділено P2P буфер: vaddr=%px\n", p2p_vaddr);

    // 4. Ініціалізація структури scatterlist
    sg_init_table(&sg, 1);
    sg_set_page(&sg, virt_to_page(p2p_vaddr), PAGE_SIZE, 0);

    // 5. Мапування P2PDMA для клієнтського пристрою
    nents = pci_p2pdma_map_sg(&client_dev->dev, &sg, 1, DMA_BIDIRECTIONAL);
    if (nents <= 0) {
        pr_err("P2PDMA Demo: pci_p2pdma_map_sg повернув помилку (%d)\n", nents);
        ret = -EIO;
        goto err_free_mem;
    }

    // 6. Отримання шинної DMA-адреси для програмування регістрів апаратного DMA-контролера
    dma_bus_addr = sg_dma_address(&sg);
    pr_info("P2PDMA Demo: Успішно замаповано! Bus DMA Address = %pad\n", &dma_bus_addr);

    // Тут зазвичай виконується запис dma_bus_addr в регістри апаратного DMA-рушія client_dev
    return 0;

err_free_mem:
    pci_free_p2pmem(provider_dev, p2p_vaddr, PAGE_SIZE);
err_put:
    pci_dev_put(client_dev);
    pci_dev_put(provider_dev);
    return ret;
}

static void __exit p2p_demo_exit(void)
{
    pr_info("P2PDMA Demo: Завершення роботи та розвантаження модуля\n");
    if (p2p_vaddr) {
        pci_p2pdma_unmap_sg(&client_dev->dev, &sg, 1, DMA_BIDIRECTIONAL);
        pci_free_p2pmem(provider_dev, p2p_vaddr, PAGE_SIZE);
    }
    if (client_dev)
        pci_dev_put(client_dev);
    if (provider_dev)
        pci_dev_put(provider_dev);
}

module_init(p2p_demo_init);
module_exit(p2p_demo_exit);
```

---

## 2. Тестова утиліта простору користувача (User-Space Test Utility)

Утиліта простору користувача дозволяє безпосередньо взаємодіяти з P2P-пам'яттю пристрою через символьний пристрій `/dev/p2pmemX`. Драйвер ядра експонує цей пристрій, дозволяючи процесу виконувати виклик `mmap()` для відображення регіону MMIO прямо в адресний простір користувацького процесу.

### Особлівості відображення пам'яті MMIO

При виконанні `mmap()` на пристрій `/dev/p2pmemX` ядро налаштовує таблиці сторінок процесу (Page Tables) з атрибутами `pgprot_noncached` або `pgprot_writecombine`. Це означає, що доступ до цієї пам'яті обходить кеш-пам'ять CPU (L1/L2/L3). Читання та запис проходять безпосередньо по шині PCIe у вигляді TLP-пакетів. З цієї причини розробник повинен пам'ятати про бар'єри пам'яті (`memory barriers`), щоб запобігти зміні порядку записів процесором.

Нижче наведено дві повноцінні ідіоматичні реалізації цієї утиліти.

:::tabs
```c
/* C Implementation: Системні виклики POSIX та mmap */

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <string.h>
#include <errno.h>

#define P2P_DEV_PATH "/dev/p2pmem0"
#define TEST_SIZE 4096

int main(void)
{
    int fd = -1;
    char *buf = NULL;
    int ret = 0;

    printf("[C] Відкриття символьного пристрою P2PMEM: %s\n", P2P_DEV_PATH);
    fd = open(P2P_DEV_PATH, O_RDWR);
    if (fd < 0) {
        fprintf(stderr, "[C] Помилка відкриття %s: %s\n", P2P_DEV_PATH, strerror(errno));
        return 1;
    }

    // Відображення P2P MMIO пам'яті в адресний простір процесу
    buf = (char *)mmap(NULL, TEST_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (buf == MAP_FAILED) {
        fprintf(stderr, "[C] Помилка mmap P2P буфера: %s\n", strerror(errno));
        close(fd);
        return 1;
    }

    printf("[C] Успішно замаповано P2P буфер за адресою %p\n", (void *)buf);

    // Запис тестового патерну безпосередньо в CMB контролера
    const char *test_str = "P2PDMA direct write payload";
    memcpy(buf, test_str, strlen(test_str) + 1);

    printf("[C] Прочитано з P2P буфера: '%s'\n", buf);

    munmap(buf, TEST_SIZE);
    close(fd);
    printf("[C] Тест завершено успішно.\n");
    return 0;
}
```
```cpp
// C++ Implementation: Ідіоматичний C++20 із RAII та std::span

#include <iostream>
#include <string_view>
#include <span>
#include <system_error>
#include <memory>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <cstring>

namespace {
    constexpr std::string_view p2p_dev_path = "/dev/p2pmem0";
    constexpr size_t test_size = 4096;

    // RAII обгортка для файлового дескриптора
    class ScopedFd {
        int m_fd{-1};
    public:
        explicit ScopedFd(int fd) : m_fd(fd) {}
        ~ScopedFd() {
            if (m_fd >= 0) {
                ::close(m_fd);
            }
        }
        ScopedFd(const ScopedFd&) = delete;
        ScopedFd& operator=(const ScopedFd&) = delete;
        [[nodiscard]] int get() const noexcept { return m_fd; }
        [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
    };

    // RAII обгортка для mmap відображення P2P пам'яті
    class P2PBufferMapping {
        void* m_addr{MAP_FAILED};
        size_t m_size{0};
    public:
        P2PBufferMapping(int fd, size_t size) : m_size(size) {
            m_addr = ::mmap(nullptr, m_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
            if (m_addr == MAP_FAILED) {
                throw std::system_error(errno, std::generic_category(), "Не вдалося виконати mmap P2P буфера");
            }
        }
        ~P2PBufferMapping() {
            if (m_addr != MAP_FAILED) {
                ::munmap(m_addr, m_size);
            }
        }
        P2PBufferMapping(const P2PBufferMapping&) = delete;
        P2PBufferMapping& operator=(const P2PBufferMapping&) = delete;

        [[nodiscard]] std::span<char> as_span() noexcept {
            return std::span<char>{static_cast<char*>(m_addr), m_size};
        }
    };
}

int main() {
    try {
        std::cout << "[C++] Відкриття P2PMEM пристрою: " << p2p_dev_path << "\n";
        ScopedFd dev_file{::open(p2p_dev_path.data(), O_RDWR)};
        if (!dev_file.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити пристрій");
        }

        P2PBufferMapping mapping{dev_file.get(), test_size};
        auto buffer = mapping.as_span();

        std::cout << "[C++] Успішно замаповано P2P буфер за адресою "
                  << static_cast<void*>(buffer.data()) << "\n";

        constexpr std::string_view payload = "P2PDMA C++20 idiomatic payload";
        std::ranges::copy(payload, buffer.begin());
        buffer[payload.size()] = '\0';

        std::cout << "[C++] Зчитано з P2P буфера: '" << buffer.data() << "'\n";
        std::cout << "[C++] Роботу з P2P буфером завершено чисто за допомогою RAII.\n";

    } catch (const std::exception& ex) {
        std::cerr << "[C++] Помилка виконання: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

## 3. Відмінності C та C++ підходів при роботі з ресурсами I/O

Порівняння двох реалізацій тестової утиліти демонструє фундаментальну різницю стилів програмування:

1. **Управління ресурсами (RAII):** У C-версії розробник змушений вручну контролювати кожен шлях виходу з функції, викликаючи `close(fd)` та `munmap()` до повернення значення. Будь-який пропущений `return` викликає витік ресурсів. У C++20 варіанті обгортки `ScopedFd` та `P2PBufferMapping` автоматично звільняють файловий дескриптор та скасовують відображення `mmap` у деструкторах навіть у випадку виникнення винятку.
2. **Типобезпека буферів:** У C-версії повернений з `mmap` вказівник є сирим `void*`, який примусово кастується до `char*`. Випадковий вихід за межі виділеної довжини `TEST_SIZE` призводить до краху `SIGSEGV`. У C++ версії клас `std::span<char>` обгортає пам'ять у типобезпечний контейнер із відомою довжиною, що дозволяє використовувати безпечні алгоритми `std::ranges::copy`.
3. **Обробка помилок:** C-версія використовує повернення коду помилки та перевірку глобальної змінної `errno` через `strerror()`. C++ версія конвертує системні помилки в стандартний виняток `std::system_error`, централізуючи обробку помилок у блоці `catch`.

---

## 4. Сценарії помилок та крайові випадки при розробці P2P-драйверів

При практичному впровадженні P2PDMA розробники драйверів найчастіше стикаються з трьома категоріями помилок:

### Невирівняний доступ до пам'яті (Unaligned BAR Access)

Більшість апаратних контролерів PCIe BAR (зокрема SRAM у NVMe CMB) вимагають строгого вирівнювання адрес для DMA-транзакцій на межу 4, 8 або 64 байтів (розмір строчки кешу). Якщо драйвер передає в `pci_p2pdma_map_sg()` зсув, не кратний розміру сектора чи строчки кешу, контролер PCIe повертає помилку `Completer Abort` (CA) або генерує переривання шини.

### Перепереповнення пулу провайдера

Обсяг CMB на накопичувачах NVMe рідко перевищує 16–64 Мегабайти. Якщо кілька клієнтських пристроїв одночасно запитують великі буфери через `pci_alloc_p2pmem()`, функція повертає `NULL`. Драйвер повинен мати запасний шлях (`fallback mechanism`) — у разі браку P2P-пам'яті переходити на стандартне мапування через системну оперативну пам'ять хоста за допомогою `dma_map_sg()`.

### Гаряче вилучення пристрою (Hot Unplug Races)

Якщо пристрій-провайдер P2P-пам'яті (NVMe SSD) вилучається з системи (наприклад, раптове відключення NVMe-накопичувача з гарячої заміни) у момент, коли клієнтський пристрій ще виконує DMA-запис у його CMB, транзакція TLP падає у "порожнечу" (Master Abort). Драйвер клієнта повинен підписуватися на події вилучення PCI-пристроїв (`pci_driver.remove`) і негайно скасовувати активні DMA-транзакцій через `pci_p2pdma_unmap_sg()`.

---

## 5. Інструкція зі збірки та тестування

Для компіляції модуля ядра та двох варіантів клієнтських утиліт використовується наступний `Makefile`:

```makefile
obj-m += p2p_dma_demo.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all: module client_c client_cpp

module:
	make -C $(KDIR) M=$(PWD) modules

client_c: client.c
	gcc -O2 -Wall client.c -o client_c

client_cpp: client.cpp
	g++ -O2 -Wall -std=c++20 client.cpp -o client_cpp

clean:
	make -C $(KDIR) M=$(PWD) clean
	rm -f client_c client_cpp
```
