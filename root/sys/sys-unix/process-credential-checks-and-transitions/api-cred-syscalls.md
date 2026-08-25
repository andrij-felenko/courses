# 📋 Системні виклики та API управління креденшелями процесів

Цей довідник описує низькорівневий POSIX та Linux-специфічний API системних викликів для читання й модифікації ідентифікаторів користувача та груп (UID/GID) процесу, що необхідно при розробці системних служб та систем розмежування привілеїв.

При роботі з креденшелями у мовах C та C++ ключовим є розуміння відмінностей між стандартними POSIX-викликами (`setuid`, `seteuid`) та розширеними атомарними викликами Linux (`setresuid`, `setfsuid`), а також правил роботи з додатковими групами (`setgroups`).

## Системні виклики читання ідентифікаторів

Отримання поточних ідентифікаторів здійснюється безпривілейованими викликами, які завжди виконуються успішно.

### getuid, geteuid, getgid, getegid

:::tabs
```c
#include <unistd.h>
#include <sys/types.h>

void print_basic_uids(void) {
    uid_t ruid = getuid();   // Повертає Real UID
    uid_t euid = geteuid();  // Повертає Effective UID
    gid_t rgid = getgid();   // Повертає Real GID
    gid_t egid = getegid();  // Повертає Effective GID
}
```
```cpp
#include <unistd.h>
#include <sys/types.h>
#include <iostream>

void print_basic_uids() {
    const uid_t ruid = ::getuid();   // Повертає Real UID
    const uid_t euid = ::geteuid();  // Повертає Effective UID
    const gid_t rgid = ::getgid();   // Повертає Real GID
    const gid_t egid = ::getegid();  // Повертає Effective GID
    std::cout << "RUID: " << ruid << ", EUID: " << euid << '\n';
}
```
:::

- **Опис**: Повертають відповідний ідентифікатор викликаючого процесу.
- **Помилки**: Системні виклики завжди успішні та не повертають помилок.

### getresuid, getresgid

:::tabs
```c
#define _GNU_SOURCE
#include <unistd.h>
#include <stdio.h>

int read_all_uids(uid_t *ruid, uid_t *euid, uid_t *suid) {
    return getresuid(ruid, euid, suid);
}
```
```cpp
#include <unistd.h>
#include <expected>
#include <system_error>
#include <cerrno>

struct UserIDs {
    uid_t ruid;
    uid_t euid;
    uid_t suid;
};

std::expected<UserIDs, std::error_code> read_all_uids() noexcept {
    UserIDs ids{};
    if (::getresuid(&ids.ruid, &ids.euid, &ids.suid) != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }
    return ids;
}
```
:::

- **Опис**: Записує за наданими вказівниками всі три ідентифікатори (Real, Effective, Saved). Це розширення Linux та BSD.
- **Повертане значення**: `0` у разі успіху, `-1` у разі помилки.
- **Помилки**:
  - `EFAULT`: один із вказівників вказує за межі адресованості пам'яті процесу.

---

## Системні виклики модифікації UID

Зміна UID суворо регламентується ядром залежно від наявності привілею `CAP_SETUID` у поточному середовищі креденшелів.

### setuid

:::tabs
```c
#include <unistd.h>

int apply_setuid(uid_t uid) {
    return setuid(uid);
}
```
```cpp
#include <unistd.h>
#include <system_error>
#include <expected>
#include <cerrno>

std::expected<void, std::error_code> apply_setuid(uid_t uid) noexcept {
    if (::setuid(uid) != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }
    return {};
}
```
:::

- **Привілейований процес (`CAP_SETUID` або `euid == 0`)**: Встановлює **всі три** ідентифікатори (`ruid`, `euid`, `suid`) та `fsuid` у значення `uid`. Це незворотна операція скидання привілеїв.
- **Непривілейований процес**: Встановлює **лише** `euid` у значення `uid`. При цьому `uid` мусить дорівнювати поточному `ruid` або `suid`.
- **Повертане значення**: `0` при успіху, `-1` при помилці (`errno` встановлюється).
- **Помилки**:
  - `EPERM`: процес не має привілеїв, а аргумент `uid` не збігається з `ruid` чи `suid`.
  - `EAGAIN`: аргумент `uid` відповідає іншому користувачу, і процес досяг ліміту ресурсів `NPROC` для цього UID.

### seteuid

:::tabs
```c
#include <unistd.h>

int apply_seteuid(uid_t euid) {
    return seteuid(euid);
}
```
```cpp
#include <unistd.h>
#include <system_error>
#include <expected>
#include <cerrno>

std::expected<void, std::error_code> apply_seteuid(uid_t euid) noexcept {
    if (::seteuid(euid) != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }
    return {};
}
```
:::

- **Опис**: Модифікує **виключно** Effective UID процесу (а також `fsuid`).
- **Привілейований процес**: Може встановити `euid` у будь-яке значення.
- **Непривілейований процес**: Може встановити `euid` лише у значення поточного `ruid`, `euid` або `suid`.
- **Повертане значення**: `0` при успіху, `-1` при помилці.
- **Помилки**:
  - `EPERM`: запитане значення `euid` недозволене для непривілейованого процесу.

### setreuid

:::tabs
```c
#include <unistd.h>

int apply_setreuid(uid_t ruid, uid_t euid) {
    return setreuid(ruid, euid);
}
```
```cpp
#include <unistd.h>
#include <system_error>
#include <expected>
#include <cerrno>

std::expected<void, std::error_code> apply_setreuid(uid_t ruid, uid_t euid) noexcept {
    if (::setreuid(ruid, euid) != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }
    return {};
}
```
:::

- **Опис**: Атомарно встановлює Real UID та Effective UID. Якщо аргумент дорівнює `-1`, відповідний ідентифікатор залишається без змін.
- **Правила для Saved UID**: Якщо `ruid` задано (аргумент не `-1`) або якщо `euid` встановлюється у значення, відмінне від попереднього `ruid`, Saved UID отримує нове значення `euid`.
- **Помилки**: `EPERM`, `EAGAIN`.

### setresuid (Рекомендований виклик у Linux)

:::tabs
```c
#define _GNU_SOURCE
#include <unistd.h>

int apply_setresuid(uid_t ruid, uid_t euid, uid_t suid) {
    return setresuid(ruid, euid, suid);
}
```
```cpp
#include <unistd.h>
#include <system_error>
#include <expected>
#include <cerrno>

std::expected<void, std::error_code> apply_setresuid(uid_t ruid, uid_t euid, uid_t suid) noexcept {
    if (::setresuid(ruid, euid, suid) != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }
    return {};
}
```
:::

- **Опис**: Явно і атомарно встановлює Real UID, Effective UID та Saved Set-UID. Значення `-1` означає «залишити без змін».
- **Привілейований процес**: Встановлює довільні значення для кожного з полів.
- **Непривілейований процес**: Кожен із трьох аргументів мусить дорівнювати одному з поточних полів (`ruid`, `euid` або `suid`).
- **Перевага**: Усуває будь-яку побічну або непередбачувану поведінку щодо Saved UID, яка присутня в POSIX `setuid`/`setreuid`.
- **Помилки**: `EPERM`, `EAGAIN`.

---

## Системні виклики модифікації GID та додаткових груп

### setgid, setegid, setregid, setresgid

Дзеркальні до викликів UID, але контролюються наявністю привілею `CAP_SETGID`.

:::tabs
```c
#define _GNU_SOURCE
#include <unistd.h>

int apply_group_credentials(gid_t rgid, gid_t egid, gid_t sgid) {
    return setresgid(rgid, egid, sgid);
}
```
```cpp
#include <unistd.h>
#include <system_error>
#include <expected>
#include <cerrno>

std::expected<void, std::error_code> apply_group_credentials(gid_t rgid, gid_t egid, gid_t sgid) noexcept {
    if (::setresgid(rgid, egid, sgid) != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }
    return {};
}
```
:::

- **Помилки**:
  - `EPERM`: відсутність `CAP_SETGID` при спробі встановити недозволений GID.

### getgroups, setgroups

:::tabs
```c
#include <unistd.h>
#include <grp.h>

int clear_supplementary_groups(void) {
    return setgroups(0, NULL);
}
```
```cpp
#include <unistd.h>
#include <grp.h>
#include <system_error>
#include <expected>
#include <cerrno>

std::expected<void, std::error_code> clear_supplementary_groups() noexcept {
    if (::setgroups(0, nullptr) != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }
    return {};
}
```
:::

- **getgroups**: Записує додаткові групи у масив `list`. Якщо `size == 0`, повертає кількість додаткових груп без модифікації масиву.
- **setgroups**: Замінює список додаткових груп процесу новим масивом `list` довжиною `size`.
- **Вимоги до привілеїв**: `setgroups` вимагає привілею `CAP_SETGID`.
- **Очищення груп**: Для повного видалення всіх додаткових груп при скиданні привілеїв викликається `setgroups(0, NULL)`.
- **Помилки**:
  - `EPERM`: відсутність `CAP_SETGID` при виклику `setgroups`.
  - `EINVAL`: `size` перевищує `NGROUPS_MAX` (системна константа, зазвичай 65536 у Linux).
  - `EFAULT`: некоректна адреса масиву `list`.

---

## Специфічні виклики Linux: fsuid та fsgid

:::tabs
```c
#include <sys/fsuid.h>

int change_fsuid(uid_t fsuid) {
    return setfsuid(fsuid);
}
```
```cpp
#include <sys/fsuid.h>

uid_t change_fsuid(uid_t fsuid) noexcept {
    return ::setfsuid(fsuid);
}
```
:::

- **Опис**: Задають Filesystem UID/GID. Вживаються майже виключно демонами файлових систем (наприклад, NFS-серверами чи Samba).
- **Особливість сигнатури**: На відміну від більшості POSIX викликів, `setfsuid` повертає **попередній** `fsuid` у разі успіху або помилки. При помилці значення `fsuid` не змінюється.
- **Автоматична синхронізація**: Будь-який виклик `setuid`, `seteuid`, `setreuid` або `setresuid`, що змінює `euid`, беззастережно переставляє `fsuid` на те саме нове значення — навіть якщо перед цим `fsuid` було навмисно розведено викликом `setfsuid`.

---

## Зведена таблиця системних викликів та вимог привілеїв

| Системний виклик | Впливає на | Вимога привілею для довільної зміни | Дійсний для непривілейованого процесу |
| :--- | :--- | :--- | :--- |
| `setuid(id)` | ruid, euid, suid (при root) / euid | `CAP_SETUID` | Якщо `id ∈ {ruid, suid}` |
| `seteuid(id)` | euid | `CAP_SETUID` | Якщо `id ∈ {ruid, euid, suid}` |
| `setreuid(r, e)` | ruid, euid, suid | `CAP_SETUID` | Якщо `r, e ∈ {ruid, euid, suid}` |
| `setresuid(r, e, s)`| ruid, euid, suid | `CAP_SETUID` | Якщо кожен з `r, e, s ∈ {ruid, euid, suid}` |
| `setgroups(n, lst)` | supplementary groups | `CAP_SETGID` | Заборонено (`EPERM`) |
| `setfsuid(id)` | fsuid | `CAP_SETUID` | Якщо `id ∈ {ruid, euid, suid, fsuid}` |
