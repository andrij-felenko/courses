# 📋 Інтерфейс системних повноважень Capsicum та seL4

Цей технічний довідник описує системні інтерфейси, структури ядра, системні виклики, бітові маски прав, коди помилок та інваріанти двох провідних систем контролю доступу на основі повноважень: гібридного фреймворку **Capsicum** (FreeBSD) та верифікованого мікроядра **seL4**.

---

## 1. Системний інтерфейс Capsicum (FreeBSD)

Підсистема Capsicum розширює традиційне середовище POSIX у ядрі FreeBSD, надаючи інструменти для добровільної ізоляції процесів та гранулярного обмеження операцій над файловими дескрипторами. Системні оголошення, прототипи функцій та константи масок прав розташовані в заголовному файлі `<sys/capsicum.h>`.

### Внутрішня організація маски прав у ядрі

У ядрі FreeBSD маска повноважень інкапсульована у структурі `cap_rights_t`. Для підтримки розширюваності та забезпечення понад 64 незалежних атомарних прав структура реалізована як масив 64-бітних слів із контролем версії ABI:

:::tabs
```c
#include <stdint.h>

#define CAP_RIGHTS_VERSION_00  0
#define CAP_RIGHTS_VERSION     CAP_RIGHTS_VERSION_00

struct cap_rights {
    uint64_t cr_rights[2];
};
typedef struct cap_rights cap_rights_t;
```
```cpp
#include <cstdint>
#include <array>

namespace capsicum {

inline constexpr uint32_t RightsVersion00 = 0;
inline constexpr uint32_t CurrentRightsVersion = RightsVersion00;

struct alignas(uint64_t) InternalRightsLayout {
    std::array<uint64_t, 2> raw_bits{};
};

} // namespace capsicum
```
:::

Старші біти першого слова `cr_rights[0]` зарезервовані під бітові прапорці версії формату (`CAP_RIGHTS_VERSION`). Коли системний виклик отримує покажчик на `cap_rights_t`, ядро спершу верифікує номер версії. Якщо простір користувача передає структуру з невідомою ядру версією, системний виклик негайно повертає помилку `EINVAL`. Це гарантує стабільність бінарного інтерфейсу (ABI) при додаванні нових категорій прав у майбутніх версіях операційної системи.

### Керування режимом виконання процесу

Фундаментальним елементом ізоляції є переведення процесу в замкнений режим повноважень за допомогою виклику `cap_enter()` та перевірка поточного стану через `cap_getmode()`.

:::tabs
```c
#include <sys/capsicum.h>

/* Безповоротний перехід у режим повноважень */
int cap_enter(void);

/* Отримання поточного стану ізоляції процесу */
int cap_getmode(u_int *modep);
```
```cpp
#include <sys/capsicum.h>
#include <system_error>
#include <cerrno>

namespace capsicum {

inline void enter() {
    if (::cap_enter() < 0) {
        throw std::system_error(errno, std::generic_category(), "cap_enter failed");
    }
}

[[nodiscard]] inline bool is_capability_mode() {
    u_int mode = 0;
    if (::cap_getmode(&mode) < 0) {
        throw std::system_error(errno, std::generic_category(), "cap_getmode failed");
    }
    return mode != 0;
}

} // namespace capsicum
```
:::

#### Семантика, інваріанти та блокування системних викликів

1. **Односторонній перехід (One-way Trapdoor):** Виклик `cap_enter()` є незворотним. У структурі процесу `struct proc` ядро встановлює прапорець `P_CAPMODE`. Після цього жоден системний виклик, включно з викликами суперкористувача (`root`), не може скинути цей прапорець назад. Усі нащадки процесу, створені через `fork()` або дескрипторні процеси `pdfork()`, автоматично успадковують цей прапорець.
2. **Повна ліквідація глобального простору VFS:** Усі системні виклики, які приймають рядковий шлях до файлу без прив'язки до відкритого дескриптора каталогу, безумовно блокуються диспетчером викликів ядра. До списку заблокованих викликів належать `open`, `creat`, `mkdir`, `link`, `symlink`, `unlink`, `rmdir`, `chdir`, `chroot`, `access`, `stat`, `lstat`, `mknod`, `rename`, `truncate`, `chmod`, `chown`. При спробі виклику процес отримує значення `-1`, а змінна `errno` встановлюється в `ECAPMODE`.
3. **Блокування глобальних мережевих операцій:** Спроба прив'язати сокет до глобальної мережевої адреси через `bind()` або ініціювати нове з'єднання через `connect()` у режимі capability mode завершується помилкою `ECAPMODE`, якщо ці операції не були виконані до ізоляції.
4. **Управління дескрипторами процесів:** У замкненому режимі прямі операції над PID (наприклад, `kill(pid, sig)`) заборонені. Замість цього Capsicum вимагає використання дескрипторів процесів (*Process Descriptors*): процес породжується викликом `pdfork(&pd, ...)` і керується через функції `pdkill(pd, sig)` та `pdwait(pd)`.

---

### Маніпуляція масками прав файлових дескрипторів

Capsicum розширює кожен запис таблиці файлових дескрипторів процесу полем прав. Процес може ініціалізувати маску, обмежити права існуючого дескриптора, отримати поточну маску або перевірити наявність необхідних повноважень.

:::tabs
```c
#include <sys/capsicum.h>
#include <stdbool.h>

/* Ініціалізація структури списком прав; список завершується 0 */
cap_rights_t *cap_rights_init(cap_rights_t *rights, ...);

/* Обмеження прав дескриптора fd вказаною маскою */
int cap_rights_limit(int fd, const cap_rights_t *rights);

/* Отримання поточної маски прав дескриптора */
int cap_rights_get(int fd, cap_rights_t *rights);

/* Перевірка, чи маска big містить усі права маски little */
bool cap_rights_contains(const cap_rights_t *big, const cap_rights_t *little);
```
```cpp
#include <sys/capsicum.h>
#include <system_error>
#include <cerrno>

namespace capsicum {

class Rights {
public:
    template <typename... Args>
    explicit Rights(Args... args) noexcept {
        ::cap_rights_init(&raw_, args..., 0);
    }

    [[nodiscard]] const cap_rights_t* get() const noexcept { return &raw_; }
    [[nodiscard]] cap_rights_t* get() noexcept { return &raw_; }

    [[nodiscard]] bool contains(const Rights& sub) const noexcept {
        return ::cap_rights_contains(&raw_, sub.get());
    }

    void apply_to(int fd) const {
        if (::cap_rights_limit(fd, &raw_) < 0) {
            throw std::system_error(errno, std::generic_category(), "cap_rights_limit failed");
        }
    }

    [[nodiscard]] static Rights from_fd(int fd) {
        Rights r;
        if (::cap_rights_get(fd, r.get()) < 0) {
            throw std::system_error(errno, std::generic_category(), "cap_rights_get failed");
        }
        return r;
    }

private:
    cap_rights_t raw_{};
};

} // namespace capsicum
```
:::

#### Інваріант монотонного звуження прав (Monotonicity Invariant)

Функція `cap_rights_limit()` реалізує суворе правило монотонності: **права можна лише зменшувати, але ніколи не розширювати**. 

Коли процес викликає `cap_rights_limit(fd, &new_rights)`, ядро зчитує поточну маску прав дескриптора `cur_rights` і перевіряє умову включення:
```
cap_rights_contains(cur_rights, new_rights) == true
```
Якщо в `new_rights` встановлено хоча б один біт, якого не було в `cur_rights`, ядро відхиляє операцію з кодом помилки `ENOTCAPABLE`. Якщо перевірка успішна, ядро замінює маску дескриптора на `new_rights`. Будь-яка подальша спроба додати раніше знятий біт буде відхилена.

---

### Класифікація категорій прав Capsicum

| Прапорець права | Дозволені системні виклики | Інженерне призначення та семантика |
|---|---|---|
| `CAP_READ` | `read`, `readv`, `pread`, `preadv` | Читання потоку байтів із файлу, каналу IPC (pipe) або сокета. |
| `CAP_WRITE` | `write`, `writev`, `pwrite`, `pwritev` | Запис потоку байтів у дескриптор. Без права `CAP_SEEK` запис відбувається строго послідовно. |
| `CAP_SEEK` | `lseek` | Дозвіл на довільну зміну файлового покажчика (зміщення). |
| `CAP_FSTAT` | `fstat`, `fstatat` | Зчитування метаданих об'єкта (розмір, власник, часові мітки, номер інода). |
| `CAP_FTRUNCATE` | `ftruncate` | Дозвіл на обрізання або розширення розміру файлу до вказаної довжини. |
| `CAP_FSYNC` | `fsync`, `fdatasync` | Примусовий скид буферів файлової системи на фізичний накопичувач. |
| `CAP_MMAP` | `mmap` | Загальний дозвіл на відображення вмісту дескриптора у віртуальну пам'ять. |
| `CAP_MMAP_R` | `mmap(PROT_READ)` | Гранулярний дозвіл на створення сторінок пам'яті виключно для читання. |
| `CAP_MMAP_W` | `mmap(PROT_WRITE)` | Гранулярний дозвіл на створення сторінок пам'яті, доступних для модифікації. |
| `CAP_MMAP_X` | `mmap(PROT_EXEC)` | Гранулярний дозвіл на відображення виконуваного машинного коду. |
| `CAP_FCNTL` | `fcntl` | Дозвіл на керування прапорцями дескриптора (потребує списку команд `cap_fcntls_limit`). |
| `CAP_IOCTL` | `ioctl` | Дозвіл на низькорівневі запити драйвера (потребує списку команд `cap_ioctls_limit`). |
| `CAP_LOOKUP` | `openat`, `fstatat`, `unlinkat` | Дозвіл на пошук імен у підкаталогах відкритого каталогового дескриптора. |
| `CAP_ACCEPT` | `accept`, `accept4` | Прийом вхідних з'єднань на мережевому сокеті, переведеному в стан прослуховування. |
| `CAP_BIND` | `bind` | Прив'язка мережевого сокета до локального порту чи адреси. |
| `CAP_CONNECT` | `connect` | Ініціалізація вихідного мережевого з'єднання. |
| `CAP_EVENT` | `kqueue`, `kevent` | Реєстрація дескриптора в системі моніторингу подій введення-виведення. |

---

## 2. Системний інтерфейс маніпуляції CNode у мікроядрі seL4

У мікроядрі seL4 весь простір адрес повноважень представлений таблицями вузлів **CNode**. Кожен системний виклик у seL4 є операцією над певним слотом CNode, який адресується комбінацією покажчика `CPtr` та глибини адресації `depth`.

### Базові маски прав доступу seL4

У seL4 права доступу до об'єкта кодуються 4-бітним полем `seL4_CapRights_t`:

:::tabs
```c
#include <stdint.h>

typedef uintptr_t seL4_Word;
typedef seL4_Word seL4_CapRights_t;

#define seL4_CanRead        (1 << 0)  /* 0x1: читання даних або отримання IPC-повідомлень */
#define seL4_CanWrite       (1 << 1)  /* 0x2: запис даних або надсилання IPC-повідомлень */
#define seL4_CanGrant       (1 << 2)  /* 0x4: право передавати інші повноваження через IPC */
#define seL4_CanGrantReply  (1 << 3)  /* 0x8: право передавати одноразовий токен відповіді */
#define seL4_AllRights      (seL4_CanRead | seL4_CanWrite | seL4_CanGrant | seL4_CanGrantReply)
```
```cpp
#include <cstdint>

namespace sel4 {

enum class CapRights : uint32_t {
    None        = 0,
    CanRead     = 1U << 0, /* Читання / отримання IPC */
    CanWrite    = 1U << 1, /* Запис / надсилання IPC */
    CanGrant    = 1U << 2, /* Передача повноважень через IPC */
    CanGrantReply = 1U << 3, /* Одноразова відповідь */
    AllRights   = CanRead | CanWrite | CanGrant | CanGrantReply
};

[[nodiscard]] constexpr CapRights operator|(CapRights a, CapRights b) noexcept {
    return static_cast<CapRights>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

[[nodiscard]] constexpr CapRights operator&(CapRights a, CapRights b) noexcept {
    return static_cast<CapRights>(static_cast<uint32_t>(a) & static_cast<uint32_t>(b));
}

} // namespace sel4
```
:::

Право `seL4_CanGrant` є критичним для запобігання несанкціонованому поширенню повноважень (Confinement Problem): якщо процес не має біта `seL4_CanGrant` на каналі зв'язку, ядро апаратно блокує спробу вкласти дескриптор іншого об'єкта в IPC-повідомлення.

---

### Операції над слотами CNode

Маніпуляція простором повноважень здійснюється через виклики методів кореневого CNode.

:::tabs
```c
#include <sel4/sel4.h>

/* Створення нового повноваження зі звуженням прав та бейджем */
seL4_Error seL4_CNode_Mint(
    seL4_CNode service,        /* CNode, у якому виконується операція */
    seL4_Word dest_index,      /* Індекс цільового слота */
    seL4_Uint8 dest_depth,     /* Глибина адресації цільового слота */
    seL4_CNode src_root,       /* Кореневий CNode джерела */
    seL4_Word src_index,       /* Індекс слота джерела */
    seL4_Uint8 src_depth,      /* Глибина адресації джерела */
    seL4_CapRights_t rights,   /* Нова (звужена) маска прав */
    seL4_CapData_t badge       /* Ідентифікатор (бейдж) для розрізнення клієнтів */
);

/* Копіювання повноваження без зміни бейджа */
seL4_Error seL4_CNode_Copy(
    seL4_CNode service, seL4_Word dest_index, seL4_Uint8 dest_depth,
    seL4_CNode src_root, seL4_Word src_index, seL4_Uint8 src_depth,
    seL4_CapRights_t rights
);

/* Переміщення повноваження зі слота в слот із вивільненням джерела */
seL4_Error seL4_CNode_Move(
    seL4_CNode service, seL4_Word dest_index, seL4_Uint8 dest_depth,
    seL4_CNode src_root, seL4_Word src_index, seL4_Uint8 src_depth
);

/* Каскадне відкликання: рекурсивне видалення всіх похідних копій */
seL4_Error seL4_CNode_Revoke(
    seL4_CNode service, seL4_Word index, seL4_Uint8 depth
);

/* Очищення окремого слота CNode */
seL4_Error seL4_CNode_Delete(
    seL4_CNode service, seL4_Word index, seL4_Uint8 depth
);
```
```cpp
#include <sel4/sel4.h>
#include <expected>
#include <cstdint>

namespace sel4 {

enum class Error : int {
    NoError = seL4_NoError,
    InvalidArgument = seL4_InvalidArgument,
    InvalidCapability = seL4_InvalidCapability,
    IllegalOperation = seL4_IllegalOperation,
    RangeError = seL4_RangeError,
    DeleteFirst = seL4_DeleteFirst,
    RevokeFirst = seL4_RevokeFirst,
    NotEnoughMemory = seL4_NotEnoughMemory
};

struct SlotRef {
    seL4_CNode root;
    seL4_Word index;
    seL4_Uint8 depth;
};

class CNodeManager {
public:
    explicit CNodeManager(seL4_CNode service_cnode) noexcept : service_{service_cnode} {}

    [[nodiscard]] std::expected<void, Error> mint(
        const SlotRef& dest, const SlotRef& src,
        seL4_CapRights_t rights, seL4_CapData_t badge) const noexcept
    {
        int res = ::seL4_CNode_Mint(
            service_, dest.index, dest.depth,
            src.root, src.index, src.depth,
            rights, badge);
        if (res != seL4_NoError) {
            return std::unexpected(static_cast<Error>(res));
        }
        return {};
    }

    [[nodiscard]] std::expected<void, Error> revoke(const SlotRef& target) const noexcept {
        int res = ::seL4_CNode_Revoke(service_, target.index, target.depth);
        if (res != seL4_NoError) {
            return std::unexpected(static_cast<Error>(res));
        }
        return {};
    }

    [[nodiscard]] std::expected<void, Error> remove(const SlotRef& target) const noexcept {
        int res = ::seL4_CNode_Delete(service_, target.index, target.depth);
        if (res != seL4_NoError) {
            return std::unexpected(static_cast<Error>(res));
        }
        return {};
    }

private:
    seL4_CNode service_;
};

} // namespace sel4
```
:::

#### Механізм бейджів (Badges) та дерево похідних (CDT)

1. **Ідентифікаційні бейджі (Badges):** Операція `seL4_CNode_Mint` дозволяє прикріпити до повноваження на IPC Endpoint 28-бітне число — **бейдж**. Коли клієнт надсилає повідомлення через забейджене повноваження, ядро доставляє це число серверу в системному регістрі `seL4_GetBadge(0)`. Сервер достовірно знає ідентифікатор клієнта, не запитуючи його ім'я чи автентифікаційні токени. Клієнт не може змінити свій бейдж, оскільки не володіє батьківським повноваженням без бейджа.
2. **Дерево похідних прав (Capability Derivation Tree, CDT):** Кожен виклик `Mint` або `Copy` автоматично фіксується у внутрішньому дереві похідних прав ядра. Дерево організоване як зв'язаний список вузлів ядра. Коли володар первинного повноваження викликає `seL4_CNode_Revoke`, ядро виконує рекурсивний обхід дерева нащадків і атомарно анулює всі дочірні слоти в адресних просторах інших процесів. Це унеможливлює завислі посилання (dangling capabilities) та витоки прав.

---

## 3. Системний інтерфейс дескрипторів Fuchsia Zircon

В операційній системі Fuchsia ядро Zircon реалізує об'єктний контроль доступу через **дескриптори** (*Handles*). На відміну від дескрипторів Unix, які посилаються лише на файли та сокети, дескриптори Zircon є універсальними повноваженнями на будь-які ресурси операційної системи: канали комунікації (Channels), процеси (Processes), потоки (Threads), пам'ять (VMO), події (Events) та завдання (Jobs).

### Базові системні виклики Zircon

1. `zx_handle_close(zx_handle_t handle)`: закриття дескриптора та видалення відповідного запису з таблиці поточного процесу. Якщо це було останнє активне повноваження на об'єкт ядра, ядро знищує сам об'єкт та звільняє виділену під нього фізичну пам'ять.
2. `zx_handle_duplicate(zx_handle_t handle, zx_rights_t rights, zx_handle_t* out)`: створення копії дескриптора з можливістю монотонного звуження прав (параметр `rights` повинен бути підмножиною прав вихідного дескриптора або мати спеціальне значення `ZX_RIGHT_SAME_RIGHTS`). Вимагає наявності права `ZX_RIGHT_DUPLICATE`.
3. `zx_handle_replace(zx_handle_t handle, zx_rights_t rights, zx_handle_t* out)`: атомарна заміна дескриптора новим дескриптором зі звуженими правами з одночасним закриттям старого. Ця операція не потребує наявності права `ZX_RIGHT_DUPLICATE`, оскільки загальна кількість дескрипторів у системі не збільшується.

### Таблиця фундаментальних прав Zircon

| Прапорець права | Числове значення | Семантичне призначення |
|---|---|---|
| `ZX_RIGHT_READ` | `1 << 0` (0x00000001) | Читання байтів або отримання повідомлень з об'єкта. |
| `ZX_RIGHT_WRITE` | `1 << 1` (0x00000002) | Запис байтів або надсилання повідомлень в об'єкт. |
| `ZX_RIGHT_EXECUTE` | `1 << 2` (0x00000004) | Дозвіл на виконання коду з об'єкта пам'яті (VMO). |
| `ZX_RIGHT_MAP` | `1 << 3` (0x00000008) | Дозвіл на відображення об'єкта VMO у віртуальний адресний простір. |
| `ZX_RIGHT_DUPLICATE` | `1 << 4` (0x00000010) | Право розмножувати дескриптор через `zx_handle_duplicate`. |
| `ZX_RIGHT_TRANSFER` | `1 << 5` (0x00000020) | Право передавати дескриптор іншому процесу через Zircon Channel. |
| `ZX_RIGHT_WAIT` | `1 << 6` (0x00000040) | Право очікувати на сигнали зміни стану об'єкта через порти подій. |
| `ZX_RIGHT_INSPECT` | `1 << 7` (0x00000080) | Дозвіл на отримання базової діагностичної інформації про об'єкт. |
| `ZX_RIGHT_MANAGE_JOB` | `1 << 8` (0x00000100) | Керування дочірніми процесами та політиками безпеки завдання. |

---

## 4. Діагностичні коди помилок та інженерні винятки

| Код помилки | Число | Підсистема | Причина виникнення та спосіб усунення |
|---|---|---|---|
| `ECAPMODE` | `94` | Capsicum | Спроба виконати заборонений системний виклик (наприклад, `open` замість `openat`) після входу в режим пісочниці. Необхідно відкривати дескриптори до виклику `cap_enter()`. |
| `ENOTCAPABLE` | `93` | Capsicum | Запитана операція виходить за межі поточної маски прав дескриптора (наприклад, виклик `write()` для дескриптора без `CAP_WRITE`). Необхідно перевірити маску `cap_rights_init`. |
| `seL4_IllegalOperation` | `3` | seL4 | Спроба розширення прав під час `seL4_CNode_Mint` або виконання непідтримуваної операції над типом об'єкта ядра. |
| `seL4_InvalidCapability` | `2` | seL4 | Числовий індекс `CPtr` вказує на порожній, неініціалізований або раніше видалений слот у CNode. |
| `seL4_RevokeFirst` | `6` | seL4 | Спроба видалити або перетипізувати батьківський об'єкт пам'яті, коли на нього все ще існують активні дочірні повноваження. Спершу слід викликати `seL4_CNode_Revoke`. |
| `ZX_ERR_ACCESS_DENIED` | `-30` | Zircon | Спроба виконати операцію над дескриптором, у якого відсутній необхідний біт права (наприклад, `ZX_RIGHT_WRITE` під час запису в канал). |
