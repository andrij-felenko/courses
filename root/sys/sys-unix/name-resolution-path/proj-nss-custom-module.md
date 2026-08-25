# ⚙️ Практикум: розробка власного NSS-модуля для Linux у C та C++

Підсистема Name Service Switch (NSS) у стандартній C-бібліотеці Linux (`glibc`) надає розробникам системного програмного забезпечення унікальний механізм розширення джерел розв'язання імен без необхідності модифікувати ядро Linux, перекомпільовувати саму C-бібліотеку або змінювати кодову базу прикладних додатків. Коли мережевий додаток або утиліта викликає функцію `getaddrinfo()`, бібліотека `glibc` зчитує конфігураційний файл `/etc/nsswitch.conf`, визначає список активних модулів і за допомогою системних викликів `dlopen()` та `dlsym()` динамічно завантажує shared-бібліотеки вида `libnss_<назва>.so.2` безпосередньо в адресний простір виконуваного процесу.

У цьому практикумі розглянуто покроковий процес розробки, компіляції, встановлення та налагодження власного NSS-модуля з назвою `custom`. Цей модуль перехоплює всі запити на розв'язання доменних імен, які закінчуються на спеціальний локальний суфікс `.lab` (наприклад, `test.lab`, `microservice.lab` або `database.lab`), і миттєво повертає синтетичну IP-адресу `127.0.42.1` без виконання жодного мережевого DNS-запиту та без звернення до зовнішніх DNS-серверів.

## 1. Специфікація ABI та внутрішній устрій NSS-модуля glibc

Щоб стандартна бібліотека `glibc` змогла розпізнати та коректно під'єднати динамічний NSS-модуль, вихідна shared-бібліотека повинна експортувати C-функції з чітко визначеними іменами та сигнатурами. Для підсистеми розв'язання хостів (`hosts:`) основним експортованим символом є функція `_nss_<назва_модуля>_gethostbyname2_r`.

Повна сигнатура цієї функції, визначена у внутрішніх заголовках `glibc` (`<nss.h>`), має такий вигляд:

```c
enum nss_status _nss_custom_gethostbyname2_r(
    const char *name,
    int af,
    struct hostent *result,
    char *buffer,
    size_t buflen,
    int *errnop,
    int *h_errnop
);
```

Під час розробки NSS-модуля необхідно суворо дотримуватися чотирьох фундаментальних правил системи `glibc`:

1. **Сувора заборона динамічного виділення пам'яті в купі (Heap Allocation):** NSS-модуль виконується у контексті довільного прикладного процесу в системі. Використання функцій `malloc()`, `free()`, `realloc()` або оператора `new` категорично не рекомендується або забороняється, оскільки це може призвести до пошкодження купи, витоків пам'яті або взаємного блокування (deadlock) у багатопотокових програмах, які перехоплюють сигнатури виділення пам'яті. Усі необхідні дані, масиви вказівників, текстові рядки та двійкові структури повинні розміщуватися виключно всередині проміжного буфера `buffer`, який передається самою бібліотекою `glibc`, а його доступний розмір у байтах задається параметром `buflen`.
2. **Гарантія потокобезпечності (Reentrancy):** Суфікс `_r` у назві функції вказує на те, що функція зобов'язана бути реінтерабельною та потокобезпечною. Модуль не має права використовувати статичні або глобальні змінні для збереження стану між викликами, оскільки функція може одночасно викликатися з різних потоків того самого процесу.
3. **Обробка переповнення буфера (ERANGE handling):** Якщо розмір наданого буфера `buflen` виявився недостатнім для розміщення структури `struct hostent`, офіційного імені хоста, списку псевдонімів (aliases) та двійкових IP-адрес, модуль зобов'язаний зберегти значення `ERANGE` за вказівником `*errnop`, значення `NETDB_INTERNAL` за вказівником `*h_errnop` і повернути статус `NSS_STATUS_TRYAGAIN`. Отримавши цей статус, `glibc` автоматично виділить буфер більшого розміру в пам'яті й повторно викликає функцію модуля.
4. **Контракт повернення кодів статусу `enum nss_status`:**
   * `NSS_STATUS_SUCCESS` — ім'я хоста успішно розв'язано, структура `result` заповнена коректними вказівниками на дані у наданому буфері.
   * `NSS_STATUS_NOTFOUND` — ім'я хоста не належить до домену відповідальності даного модуля (наприклад, ім'я не закінчується на `.lab`), або запис відсутній. `glibc` передасть запит наступному модулю у `/etc/nsswitch.conf`.
   * `NSS_STATUS_UNAVAIL` — модуль недоступний (наприклад, відсутній критичний конфігураційний файл чи сервіс).
   * `NSS_STATUS_TRYAGAIN` — тимчасова помилка або недостатній розмір буфера пам'яті.

## 2. Повна реалізація модуля мовами C та C++

Нижче наведено повний вихідний код модуля `libnss_custom`. Приклад виконано у двох варіантах: класичний низькорівневий код мовою C з ручним вирівнюванням вказівників та ідіоматичний код мовою C++ з використанням стандартних типів `std::string_view`, `std::span` та RAII-розподільника буфера.

:::tabs
```c
/* libnss_custom.c — C реалізація NSS модуля для розв'язання .lab доменів */
#define _GNU_SOURCE
#include <nss.h>
#include <netdb.h>
#include <string.h>
#include <errno.h>
#include <arpa/inet.h>
#include <stdint.h>

#define LAB_SUFFIX ".lab"
#define SYNTHETIC_IP "127.0.42.1"

enum nss_status _nss_custom_gethostbyname2_r(
    const char *name,
    int af,
    struct hostent *result,
    char *buffer,
    size_t buflen,
    int *errnop,
    int *h_errnop)
{
    /* Модуль обробляє виключно IPv4 адреси (AF_INET) */
    if (af != AF_INET || name == NULL) {
        *h_errnop = HOST_NOT_FOUND;
        return NSS_STATUS_NOTFOUND;
    }

    /* Перевіряємо, чи має ім'я хоста локальний суфікс .lab */
    size_t name_len = strlen(name);
    size_t suffix_len = strlen(LAB_SUFFIX);
    if (name_len < suffix_len || strcmp(name + name_len - suffix_len, LAB_SUFFIX) != 0) {
        *h_errnop = HOST_NOT_FOUND;
        return NSS_STATUS_NOTFOUND;
    }

    /* Обчислюємо точні розміри всіх елементів, які будуть поміщені в буфер */
    size_t name_bytes = name_len + 1;
    size_t addr_bytes = sizeof(struct in_addr);
    size_t addr_list_bytes = 2 * sizeof(char *);
    size_t alias_list_bytes = 1 * sizeof(char *);

    /* Перевіряємо зальний необхідний обсяг з урахуванням вирівнювання */
    size_t total_needed = name_bytes + addr_bytes + addr_list_bytes + alias_list_bytes + 32;
    if (buflen < total_needed) {
        *errnop = ERANGE;
        *h_errnop = NETDB_INTERNAL;
        return NSS_STATUS_TRYAGAIN;
    }

    /* Розміщуємо фрагменти даних у наданому буфері пам'яті */
    char *p = buffer;

    /* 1. Копіюємо текстове ім'я хоста */
    char *h_name = p;
    memcpy(h_name, name, name_bytes);
    p += name_bytes;

    /* Вирівнюємо поточний вказівник до межі sizeof(void *) для запобігання SIGBUS */
    uintptr_t pad = (uintptr_t)p % sizeof(void *);
    if (pad != 0) {
        p += (sizeof(void *) - pad);
    }

    /* 2. Записуємо двійкову структуру IPv4 адреси */
    struct in_addr *addr_ptr = (struct in_addr *)p;
    p += addr_bytes;
    if (inet_pton(AF_INET, SYNTHETIC_IP, addr_ptr) <= 0) {
        *errnop = EINVAL;
        *h_errnop = NETDB_INTERNAL;
        return NSS_STATUS_UNAVAIL;
    }

    /* Вирівнюємо вказівник перед записом масивів вказівників */
    pad = (uintptr_t)p % sizeof(void *);
    if (pad != 0) {
        p += (sizeof(void *) - pad);
    }

    /* 3. Формуємо масив вказівників на IP адреси h_addr_list */
    char **h_addr_list = (char **)p;
    p += addr_list_bytes;
    h_addr_list[0] = (char *)addr_ptr;
    h_addr_list[1] = NULL;

    /* 4. Формуємо порожній масив псевдонімів h_aliases */
    char **h_aliases = (char **)p;
    h_aliases[0] = NULL;

    /* Заповнюємо вихідну структуру hostent вказівниками з наданого буфера */
    result->h_name = h_name;
    result->h_aliases = h_aliases;
    result->h_addrtype = AF_INET;
    result->h_length = sizeof(struct in_addr);
    result->h_addr_list = h_addr_list;

    *h_errnop = NETDB_SUCCESS;
    return NSS_STATUS_SUCCESS;
}

enum nss_status _nss_custom_gethostbyname_r(
    const char *name,
    struct hostent *result,
    char *buffer,
    size_t buflen,
    int *errnop,
    int *h_errnop)
{
    return _nss_custom_gethostbyname2_r(name, AF_INET, result, buffer, buflen, errnop, h_errnop);
}
```
```cpp
// libnss_custom.cpp — Ідіоматична C++20 реалізація з безпечним розподільником буфера
#include <nss.h>
#include <netdb.h>
#include <cerrno>
#include <cstring>
#include <string_view>
#include <span>
#include <arpa/inet.h>
#include <cstdint>

namespace {
    constexpr std::string_view kLabSuffix = ".lab";
    constexpr std::string_view kSyntheticIp = "127.0.42.1";

    // Клас-допоміжник для безпечного розмежування типів у буфері без викликів malloc()
    class PlacementBuffer {
    public:
        explicit PlacementBuffer(std::span<char> buf) : buffer_(buf), offset_(0) {}

        template <typename T>
        T* allocate(size_t count = 1) noexcept {
            size_t align = alignof(T);
            size_t current_addr = reinterpret_cast<size_t>(buffer_.data() + offset_);
            size_t padding = (align - (current_addr % align)) % align;

            size_t total_bytes = padding + count * sizeof(T);
            if (offset_ + total_bytes > buffer_.size()) {
                return nullptr;
            }

            offset_ += padding;
            T* ptr = reinterpret_cast<T*>(buffer_.data() + offset_);
            offset_ += count * sizeof(T);
            return ptr;
        }

        char* copy_string(std::string_view str) noexcept {
            char* dest = allocate<char>(str.size() + 1);
            if (!dest) return nullptr;
            std::memcpy(dest, str.data(), str.size());
            dest[str.size()] = '\0';
            return dest;
        }

    private:
        std::span<char> buffer_;
        size_t offset_;
    };
}

extern "C" {

enum nss_status _nss_custom_gethostbyname2_r(
    const char *name,
    int af,
    struct hostent *result,
    char *buffer,
    size_t buflen,
    int *errnop,
    int *h_errnop) noexcept
{
    if (af != AF_INET || name == nullptr) {
        *h_errnop = HOST_NOT_FOUND;
        return NSS_STATUS_NOTFOUND;
    }

    std::string_view host_name(name);
    if (!host_name.ends_with(kLabSuffix)) {
        *h_errnop = HOST_NOT_FOUND;
        return NSS_STATUS_NOTFOUND;
    }

    PlacementBuffer allocator(std::span<char>(buffer, buflen));

    // 1. Копіюємо текстове ім'я
    char* h_name = allocator.copy_string(host_name);
    if (!h_name) {
        *errnop = ERANGE;
        *h_errnop = NETDB_INTERNAL;
        return NSS_STATUS_TRYAGAIN;
    }

    // 2. Розміщуємо IPv4 адресу
    auto* addr_ptr = allocator.allocate<struct in_addr>();
    if (!addr_ptr) {
        *errnop = ERANGE;
        *h_errnop = NETDB_INTERNAL;
        return NSS_STATUS_TRYAGAIN;
    }

    if (::inet_pton(AF_INET, kSyntheticIp.data(), addr_ptr) <= 0) {
        *errnop = EINVAL;
        *h_errnop = NETDB_INTERNAL;
        return NSS_STATUS_UNAVAIL;
    }

    // 3. Формуємо масив вказівників на адреси
    auto** addr_list = allocator.allocate<char*>(2);
    if (!addr_list) {
        *errnop = ERANGE;
        *h_errnop = NETDB_INTERNAL;
        return NSS_STATUS_TRYAGAIN;
    }
    addr_list[0] = reinterpret_cast<char*>(addr_ptr);
    addr_list[1] = nullptr;

    // 4. Формуємо порожній масив псевдонімів
    auto** alias_list = allocator.allocate<char*>(1);
    if (!alias_list) {
        *errnop = ERANGE;
        *h_errnop = NETDB_INTERNAL;
        return NSS_STATUS_TRYAGAIN;
    }
    alias_list[0] = nullptr;

    // Заповнюємо вихідну структуру hostent
    result->h_name = h_name;
    result->h_aliases = alias_list;
    result->h_addrtype = AF_INET;
    result->h_length = sizeof(struct in_addr);
    result->h_addr_list = addr_list;

    *h_errnop = NETDB_SUCCESS;
    return NSS_STATUS_SUCCESS;
}

enum nss_status _nss_custom_gethostbyname_r(
    const char *name,
    struct hostent *result,
    char *buffer,
    size_t buflen,
    int *errnop,
    int *h_errnop) noexcept
{
    return _nss_custom_gethostbyname2_r(name, AF_INET, result, buffer, buflen, errnop, h_errnop);
}

} // extern "C"
```
:::

## 3. Збірка, встановлення та реєстрація модуля в системі

Для компіляції вихідного коду у динамічно завантажувану shared-бібліотеку `libnss_custom.so.2` виконуються такі команди компілятора:

```bash
# Збірка C-версії модуля:
gcc -O2 -fPIC -shared -Wl,-soname,libnss_custom.so.2 -o libnss_custom.so.2 libnss_custom.c

# Або збірка C++20 версії модуля:
g++ -O2 -std=c++20 -fPIC -shared -Wl,-soname,libnss_custom.so.2 -o libnss_custom.so.2 libnss_custom.cpp
```

Прапор `-fPIC` (Position Independent Code) є обов'язковим для створення спільно використовуваного коду, який може завантажуватися за довільною адресою в пам'яті. Прапор `-Wl,-soname,libnss_custom.so.2` фіксує внутрішнє ім'я SONAME у заголовках ELF-файла.

Після компіляції бінарний файл необхідно скопіювати до системного каталогу розпізнавання бібліотек `glibc` (наприклад, `/lib/x86_64-linux-gnu/` у дистрибутивах Ubuntu/Debian або `/usr/lib64/` у RHEL/Fedora) та оновити кеш динамічного лінкера:

```bash
sudo cp libnss_custom.so.2 /lib/x86_64-linux-gnu/
sudo ldconfig
```

Для активації модуля відредагуйте файл `/etc/nsswitch.conf`, додавши ідентифікатор `custom` у рядок база даних `hosts:` перед модулем `dns`:

```text
hosts: files custom dns myhostname
```

## 4. Верифікація та інструментальний траблшутинг

Для перевірки коректності роботи нового модуля використовується системна утиліта `getent`, яка здійснює виклики безпосередньо через підсистему NSS бібліотеки `glibc`:

```bash
# Тестування розв'язання імені з суфіксом .lab (обробляється нашим модулем):
$ getent hosts service.lab
127.0.42.1      service.lab

# Тестування традиційного імені (пропускається нашим модулем і передається в dns/resolve):
$ getent hosts kernel.org
198.145.29.83   kernel.org
```

Щоб переконатися, що `glibc` дійсно динамічно завантажує створену бібліотеку `libnss_custom.so.2`, можна простежити системні виклики за допомогою `strace`:

```bash
$ strace -e trace=openat,open,dlopen getent hosts test.lab
openat(AT_FDCWD, "/etc/nsswitch.conf", O_RDONLY|O_CLOEXEC) = 3
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libnss_custom.so.2", O_RDONLY|O_CLOEXEC) = 3
127.0.42.1      test.lab
```

## 5. Типові пастки та потенційні дефекти

* **Помилки вирівнювання пам'яті (Alignment Faults):** На архітектурах ARM64 або RISC-V примусове приведення довільних вказівників `char*` до типів `char**` або `struct in_addr*` без вирівнювання за межею 4 або 8 байтів викликає апаратне виключення й аварійне завершення процесу сигналом `SIGBUS`.
* **Побічні ефекти операторів розгалуження в `nsswitch.conf`:** Якщо після вашого модуля вказати мову реакцій `custom [NOTFOUND=return] dns`, то будь-який запит до доменів, які не закінчуються на `.lab`, поверне статус `NOTFOUND` і негайно припинить обробку, повністю заблокувавши доступ до зовнішнього інтернету.
* **Блокування міжпроцесної взаємодії (IPC Deadlocks) в контейнерах:** Якщо написати NSS-модуль, який звертається до зовнішнього демона через Unix-сокет, додатки у закритих `chroot`-контейнерах або ізольованих `mount namespace` зависнуть або впадуть через відсутність файлу сокета у їхній файловій системі.
