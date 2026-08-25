# 📋 Програмний та системний інтерфейс керування знімками й клонами

Коли адміністратор, скрипт автоматизації або система хмарної оркестрації створює знімок чи клон віртуальної машини, взаємодія проходить через багаторівневий стек програмних інтерфейсів. На найнижчому рівні гостьове ядро операційної системи забезпечує узгодженість файлових систем через системні виклики блокування вводу-виводу. На проміжному рівні гіпервізор керує графом блокових пристроїв через сокетний протокол керування. На верхньому рівні бібліотека `libvirt` та утиліти командного рядка надають стандартизований маніфест для атомарного маніпулювання дисками та збереженими станами пам'яті. Цей довідник містить вичерпну специфікацію функцій, керуючих структур даних, форматів повідомлень, життєвого циклу обробки помилок та ідіоматичних прикладів коду.

---

## 1. Системні виклики та ioctl ядра Linux для заморозки VFS

Для створення гарантовано узгодженого знімка на рівні файлової системи гостьовий агент взаємодіє з підсистемою віртуальної файлової системи (VFS) ядра Linux через інтерфейс `ioctl(2)`.

Заголовкові файли: `<sys/ioctl.h>`, `<linux/fs.h>`, `<fcntl.h>`, `<unistd.h>`

### Внутрішня трирівнева модель блокування ядра Linux

Під час виклику команди заморозки ядро Linux не просто припиняє обробку запитів, а послідовно активує три рівні блокування у структурі суперблока `struct super_block` за допомогою внутрішньої функції ядра `freeze_super()`:

1. **`SB_FREEZE_WRITE` (Рівень звичайного запису):** блокує всі користувацькі системні виклики модифікації даних (`write(2)`, `pwritev(2)`, `truncate(2)`). Будь-який потік простору користувача, що ініціює новий запис, переводиться планувальником у стан очікування на семафорі `sb->s_writers`.
2. **`SB_FREEZE_PAGEFAULT` (Рівень сторінкових збоїв пам'яті):** блокує обробку викликів запису через файли, відображені в оперативну пам'ять за допомогою системного виклику `mmap(2)`. Спроба процесу змінити байт у сторінці пам'яті викликає сторінковий збій (`page fault`), обробник якого перевіряє статус заморозки суперблока і зупиняє потік до розморожування.
3. **`SB_FREEZE_FS` (Рівень транзакцій файлової системи):** викликає внутрішній метод `freeze_fs` драйвера конкретної файлової системи (ext4, XFS, Btrfs, F2FS). Драйвер примусово скидає всі модифіковані метадані на диск, дописує відкриті транзакції в журнал `jbd2`, позначає суперблок на диску як чистий і блокує створення нових транзакцій.

### Опис операцій ioctl

| Назва запиту ioctl | Числовий макрос | Аргумент | Опис операції та поведінка ядра |
| :--- | :--- | :--- | :--- |
| `FIFREEZE` | `_IOW('X', 119, int)` | `int *` (ігнорується, передається 0) | Примусово скидає всі сторінки буферного кешу на носій, фіксує журнал транзакцій файлової системи, блокує створення нових модифікацій та переводить суперблок у заморожений стан. |
| `FITHAW` | `_IOW('X', 120, int)` | `int *` (ігнорується, передається 0) | Знімає блокування трьох рівнів `SB_FREEZE_*`, викликає внутрішній метод `unfreeze_fs`, пробуджує всі заблоковані процеси та повертає файлову систему до штатного режиму. |

### Коди помилок та обробка крайових випадків

- `EBUSY` — файлова система вже перебуває в замороженому стані під керуванням іншого процесу або на накопичувачі виконується ексклюзивна блокова операція ядра.
- `EINVAL` — переданий файловий дескриптор вказує на звичайний файл або каталог замість кореневої точки монтування розділу, або надіслано команду `FITHAW` до файлової системи, яка не була заморожена.
- `EOPNOTSUPP` — драйвер файлової системи не реалізує методи інтерфейсу заморозки (типово для мережевих файлових систем NFS/CIFS або спеціальних псевдофайлових систем `procfs`, `sysfs`, `devtmpfs`).
- `EPERM` / `EACCES` — викликаючий процес не має адміністративного привілею `CAP_SYS_ADMIN` у просторі назв користувачів.

### Інваріанти надійності при використанні `FIFREEZE`

- **Обмеження часу заморозки (Freeze Timeout):** заборонено утримувати точку монтування в стані `FIFREEZE` понад кілька секунд. Усі прикладні процеси, що намагаються виконати запис у журнал чи скинути кеш, зупиняються у стані ядра `TASK_UNINTERRUPTIBLE` (D-state). Якщо гіпервізор зависне або операція створення знімка на хості зазнає невдачі, сервери всередині гостя зазнають збою за таймаутом дискового вводу-виводу.
- **Відкриття дескриптора:** точка монтування повинна відкриватися в режимі «лише для читання» (`O_RDONLY`) з прапорцем закриття при виклику `exec` (`O_CLOEXEC`).

### Програмна реалізація: безпечний захоплювач із RAII-гарантією

Приклад мовою C демонструє базові виклики системи з ручною обробкою помилок, тоді як приклад мовою C++ реалізує безпечну ідіому RAII (`Resource Acquisition Is Initialization`) з типом `std::expected`, яка гарантує обов'язковий виклик `FITHAW` навіть у разі виникнення виняткових ситуацій.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/fs.h>
#include <errno.h>
#include <string.h>

int freeze_mountpoint(const char *mount_path) {
    int fd = open(mount_path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття шляху монтування %s: %s\n", 
                mount_path, strerror(errno));
        return -1;
    }

    if (ioctl(fd, FIFREEZE, 0) < 0) {
        fprintf(stderr, "Помилка виклику ioctl FIFREEZE для %s: %s\n", 
                mount_path, strerror(errno));
        close(fd);
        return -1;
    }

    return fd;
}

int thaw_mountpoint(int fd, const char *mount_path) {
    int result = 0;
    if (ioctl(fd, FITHAW, 0) < 0) {
        fprintf(stderr, "Критична помилка розморожування FITHAW для %s: %s\n", 
                mount_path, strerror(errno));
        result = -1;
    }
    close(fd);
    return result;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <expected>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/fs.h>

class FsFreezeGuard {
public:
    static std::expected<FsFreezeGuard, std::error_code> acquire(std::string_view mount_path) {
        int fd = ::open(mount_path.data(), O_RDONLY | O_CLOEXEC);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::ioctl(fd, FIFREEZE, 0) < 0) {
            int err = errno;
            ::close(fd);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        return FsFreezeGuard(fd);
    }

    ~FsFreezeGuard() noexcept {
        if (fd_ >= 0) {
            ::ioctl(fd_, FITHAW, 0);
            ::close(fd_);
        }
    }

    FsFreezeGuard(const FsFreezeGuard&) = delete;
    FsFreezeGuard& operator=(const FsFreezeGuard&) = delete;

    FsFreezeGuard(FsFreezeGuard&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    FsFreezeGuard& operator=(FsFreezeGuard&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) {
                ::ioctl(fd_, FITHAW, 0);
                ::close(fd_);
            }
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept {
        return fd_;
    }

private:
    explicit FsFreezeGuard(int fd) noexcept : fd_(fd) {}
    int fd_{-1};
};
```
:::

---

## 2. Специфікація архітектури Microsoft VSS (Volume Shadow Copy Service)

У середовищі операційних систем Microsoft Windows координація знімків реалізується через компонентну модель **VSS (Volume Shadow Copy Service)**. Архітектура VSS об'єднує чотири незалежні ланки взаємодії:

1. **VSS Requestor (Ініціатор):** застосунок резервного копіювання або служба гіпервізора (наприклад, служба `vss` у складі гостьових утиліт Hyper-V Integration Services чи VMware Tools). Ініціює процес створення знімка, задає рівень узгодженості та керує життєвим циклом копії.
2. **VSS Service (Координатор ядра):** центральний системний координатор операційної системи Windows, що транслює команди між ініціатором, прикладними програмами та дисковими драйверами.
3. **VSS Writers (Обробники застосунків):** спеціалізовані модулі, інтегровані в сервери баз даних та системні служби (Microsoft SQL Server Writer, Exchange Writer, Active Directory Domain Services Writer). Обробник гарантує, що при отриманні сигналу підготовки всі активні транзакції в оперативній пам'яті будуть зафіксовані в журналі WAL або тимчасово призупинені.
4. **VSS Provider (Постачальник сховища):** низькорівневий компонент, який безпосередньо створює тіньову копію блоків. Постачальник може бути програмним (системний драйвер `volsnap.sys` у Windows) або апаратним (модуль інтеграції з дисковими масивами SAN / гіпервізором).

### Етапи виконання фаз створення тіньової копії VSS

```
[VSS Requestor] ──> (1. GatherWriterMetadata) ──> [VSS Writers]
[VSS Requestor] ──> (2. PrepareForSnapshot)   ──> [VSS Writers: скидання WAL-буферів]
[VSS Requestor] ──> (3. DoSnapshotSet)        ──> [VSS Service]
                                                        │
                                          (4. Freeze I/O: макс 10 секунд)
                                                        │
                                                  [VSS Provider: створення оверлею]
                                                        │
                                          (5. Thaw I/O: відновлення потоків)
                                                        │
[VSS Requestor] ──> (6. PostSnapshot)         ──> [VSS Writers: відновлення СУБД]
```

Під час фази `DoSnapshotSet` ядро Windows заморожує чергу дискового вводу-виводу на час, що не перевищує жорсткий ліміт у 10 секунд. Якщо постачальник сховища не встигає зафіксувати дельта-шар за цей інтервал, VSS Service автоматично надсилає сигнал скасування `Abort` усім учасникам, а операція створення знімка переривається з помилкою `VSS_E_HOLD_WRITES_TIMEOUT`.

---

## 3. Команди сокетного протоколу керування QEMU (QMP)

QEMU Machine Protocol (QMP) — це протокол керування гіпервізором QEMU через двонаправлений Unix-сокет за допомогою повідомлень у форматі JSON.

### 3.1. Рукостискання та узгодження можливостей

Після встановлення зв'язку з Unix-сокетом гіпервізор надсилає вітальне повідомлення з версією. Керуюча програма зобов'язана надіслати команду активації розширень:

```json
// Запит клієнта на активацію сесії QMP
{
  "execute": "qmp_capabilities"
}

// Успішна відповідь гіпервізора
{
  "return": {}
}
```

### 3.2. Взаємодія з агентом гостя: `guest-fsfreeze`

Команди надсилаються через канал зв'язку `qemu-ga` (гостьовий агент опитує віртуалізований послідовний порт `virtio-serial`):

```json
// Запит на заморозку всіх локальних файлових систем гостя
{
  "execute": "guest-fsfreeze-freeze"
}

// Відповідь: числове значення успішно заморожених розділів
{
  "return": 3
}

// Запит перевірки поточного статусу заморозки
{
  "execute": "guest-fsfreeze-status"
}

// Варіанти відповіді: "thawed" (розморожено) або "frozen" (заморожено)
{
  "return": "frozen"
}

// Запит на розморозку файлових систем
{
  "execute": "guest-fsfreeze-thaw"
}

// Відповідь: кількість розморожених розділів
{
  "return": 3
}
```

### 3.3. Створення зовнішнього знімка диска: `blockdev-snapshot-sync`

Команда виконує підміну активного вузла в дереві блокових пристроїв QEMU, створюючи новий шар оверлею:

```json
{
  "execute": "blockdev-snapshot-sync",
  "arguments": {
    "node-name": "drive-virtio-disk0",
    "snapshot-file": "/var/lib/libvirt/images/vm1-snap1.qcow2",
    "snapshot-node-name": "node-snap1",
    "format": "qcow2",
    "mode": "absolute-paths"
  }
}
```

#### Повний перелік параметрів `blockdev-snapshot-sync`

| Поле аргументу | Тип | Обов'язковість | Опис призначення |
| :--- | :--- | :--- | :--- |
| `device` / `node-name` | string | так | Унікальний ідентифікатор пристрою або вузла графа блокових драйверів у QEMU. |
| `snapshot-file` | string | так | Повний абсолютний шлях до цільового файлу оверлею на файловій системі хоста. |
| `snapshot-node-name` | string | ні | Символьне ім'я нового кореневого вузла графа для подальшої адресації в командах QMP. |
| `format` | string | так | Формат створюваного контейнера (зазвичай `qcow2`). |
| `mode` | string | ні | Режим створення: `absolute-paths` (створити новий файл автоматично) або `existing` (використати попередньо підготовлений файл оверлею). |

### 3.4. Атомарна транзакція для групи дисків: `transaction`

Якщо віртуальна машина містить кілька дисків (наприклад, системний том ОС та окремий масив для журналу транзакцій СУБД), створення знімків окремими послідовними командами неприпустиме, оскільки часовий розрив між викликами призведе до порушення узгодженості даних. Блок `transaction` гарантує атомарне створення оверлеїв для всіх дисків одночасно в межах єдиної мікросекундної паузи vCPU:

```json
{
  "execute": "transaction",
  "arguments": {
    "actions": [
      {
        "type": "blockdev-snapshot-sync",
        "data": {
          "node-name": "drive-virtio-disk0",
          "snapshot-file": "/var/lib/libvirt/images/vm1-os-snap1.qcow2",
          "format": "qcow2"
        }
      },
      {
        "type": "blockdev-snapshot-sync",
        "data": {
          "node-name": "drive-virtio-disk1",
          "snapshot-file": "/var/lib/libvirt/images/vm1-data-snap1.qcow2",
          "format": "qcow2"
        }
      }
    ]
  }
}
```

### 3.5. Фонове злиття шарів: `block-commit` та асинхронні події

Команда `block-commit` запускає фонове фонове перенесення модифікованих кластерів із верхніх оверлеїв у нижчі шари:

```json
{
  "execute": "block-commit",
  "arguments": {
    "device": "drive-virtio-disk0",
    "job-id": "commit-job-01",
    "base": "/var/lib/libvirt/images/vm1-base.qcow2",
    "top": "/var/lib/libvirt/images/vm1-snap1.qcow2",
    "speed": 104857600
  }
}
```

#### Асинхронні події життєвого циклу блокової операції

Під час тривалого фонового злиття гіпервізор надсилає керуючій програмі асинхронні повідомлення про зміну статусу блокової задачі:

```json
// Повідомлення про готовність до фінального перемикання (для активного шару)
{
  "event": "BLOCK_JOB_READY",
  "data": {
    "device": "commit-job-01",
    "type": "commit",
    "len": 53687091200,
    "offset": 53687091200,
    "speed": 104857600
  },
  "timestamp": { "seconds": 1724112000, "microseconds": 500000 }
}

// Повідомлення про успішне завершення задачі
{
  "event": "BLOCK_JOB_COMPLETED",
  "data": {
    "device": "commit-job-01",
    "type": "commit",
    "len": 53687091200,
    "offset": 53687091200,
    "speed": 104857600
  },
  "timestamp": { "seconds": 1724112005, "microseconds": 120000 }
}
```

---

## 4. Специфікація C API бібліотеки `libvirt` та XML-маніфести

Бібліотека `libvirt` надає єдиний API для керування віртуалізацією незалежно від базового гіпервізора.

### Програмна взаємодія з API libvirt

:::tabs
```c
#include <stdio.h>
#include <libvirt/libvirt.h>

int trigger_snapshot_commit(virDomainPtr dom, const char *disk, const char *base, const char *top) {
    unsigned int flags = VIR_DOMAIN_BLOCK_COMMIT_ACTIVE | VIR_DOMAIN_BLOCK_COMMIT_PIVOT;
    int ret = virDomainBlockCommit(dom, disk, base, top, 0, flags);
    if (ret < 0) {
        virErrorPtr err = virGetLastError();
        fprintf(stderr, "Помилка виклику virDomainBlockCommit: %s\n", 
                err ? err->message : "невідома помилка libvirt");
        return -1;
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <expected>
#include <string>
#include <memory>
#include <libvirt/libvirt.h>

struct VirDomainDeleter {
    void operator()(virDomainPtr ptr) const noexcept {
        if (ptr) virDomainFree(ptr);
    }
};
using UniqueVirDomain = std::unique_ptr<virDomain, VirDomainDeleter>;

std::expected<void, std::string> trigger_snapshot_commit(
    virDomainPtr dom,
    std::string_view disk,
    std::string_view base,
    std::string_view top
) {
    unsigned int flags = VIR_DOMAIN_BLOCK_COMMIT_ACTIVE | VIR_DOMAIN_BLOCK_COMMIT_PIVOT;
    int ret = virDomainBlockCommit(dom, disk.data(), base.data(), top.data(), 0, flags);
    if (ret < 0) {
        virErrorPtr err = virGetLastError();
        return std::unexpected(err && err->message ? err->message : "Unknown libvirt error");
    }
    return {};
}
```
:::

#### Прапорці виклику `virDomainSnapshotCreateXML` (`flags`)

- `VIR_DOMAIN_SNAPSHOT_CREATE_DISK_ONLY` (`1 << 4`) — зафіксувати виключно блоковий стан дисків, не зберігаючи дамп оперативної пам'яті.
- `VIR_DOMAIN_SNAPSHOT_CREATE_QUIESCE` (`1 << 6`) — надіслати запит гостьовому агенту для попередньої заморозки файлових систем через `FIFREEZE` / VSS.
- `VIR_DOMAIN_SNAPSHOT_CREATE_ATOMIC` (`1 << 7`) — гарантувати атомарне перемикання для всіх дисків віртуальної машини.
- `VIR_DOMAIN_SNAPSHOT_CREATE_LIVE` (`1 << 8`) — виконати повне збереження пам'яті та стану процесорів без зупинки роботи гостьової ОС.

#### Прапорці виклику `virDomainBlockCommit`

- `VIR_DOMAIN_BLOCK_COMMIT_SHALLOW` (`1 << 0`) — зливати зміни лише у безпосередній батьківський шар замість найглибшої бази.
- `VIR_DOMAIN_BLOCK_COMMIT_ACTIVE` (`1 << 2`) — дозволити злиття активного верхнього шару, в який гість продовжує записувати дані.
- `VIR_DOMAIN_BLOCK_COMMIT_PIVOT` (`1 << 3`) — автоматично перемкнути активний дескриптор віртуального диска на базовий шар після завершення дзеркалювання.

### XML-маніфест опису зовнішнього знімка (`domainsnapshot`)

```xml
<domainsnapshot>
  <name>snap-pre-migration-v3</name>
  <description>Узгоджений зовнішній знімок перед оновленням сервісів</description>
  <state>running</state>
  <creationTime>1724112000</creationTime>
  <memory snapshot='no'/>
  <disks>
    <disk name='vda' snapshot='external' type='file'>
      <driver type='qcow2'/>
      <source file='/var/lib/libvirt/images/vm1-vda-delta1.qcow2'/>
    </disk>
    <disk name='vdb' snapshot='external' type='file'>
      <driver type='qcow2'/>
      <source file='/var/lib/libvirt/images/vm1-vdb-delta1.qcow2'/>
    </disk>
  </disks>
</domainsnapshot>
```

---

## 5. Довідник команд утиліти `qemu-img`

Утиліта `qemu-img` дозволяє автономно створювати оверлеї, перевіряти цілісність ланцюжків та змінювати батьківські зв'язки дисків без запущеного процесу гіпервізора.

### 5.1. Створення зв'язаного оверлею (Linked Clone)

```bash
qemu-img create -f qcow2 \
    -b /var/lib/libvirt/images/golden-master.qcow2 \
    -F qcow2 \
    /var/lib/libvirt/images/clone-node-01.qcow2
```

- `-f qcow2` — формат створюваного файлу оверлею.
- `-b <шлях>` — абсолютний або відносний шлях до незмінного батьківського базового образу.
- `-F qcow2` — явне визначення формату базового образу для запобігання атакам з автовизначенням заголовка.

### 5.2. Інспекція дерева шарів та дельт

```bash
qemu-img info --backing-chain /var/lib/libvirt/images/clone-node-01.qcow2
```

Вивід демонструє повну структуру ланцюжка шарів від активного оверлею до найглибшої бази:

```
image: /var/lib/libvirt/images/clone-node-01.qcow2
file format: qcow2
virtual size: 50 GiB (53687091200 bytes)
disk size: 2.1 MiB
cluster_size: 65536
backing file: /var/lib/libvirt/images/golden-master.qcow2
backing file format: qcow2

image: /var/lib/libvirt/images/golden-master.qcow2
file format: qcow2
virtual size: 50 GiB (53687091200 bytes)
disk size: 5.4 GiB
cluster_size: 65536
```

### 5.3. Переприв'язка базового шару (Rebase)

```bash
# Безпечний ребейз (Safe Rebase): читає розбіжності та переносить кластери
qemu-img rebase -b /new/storage/path/golden-master.qcow2 -F qcow2 clone-node-01.qcow2

# Швидкий небезпечний ребейз (-u, Unsafe): лише оновлює текстовий рядок шляху в заголовку
qemu-img rebase -u -b /new/storage/path/golden-master.qcow2 -F qcow2 clone-node-01.qcow2
```

### 5.4. Автономне злиття та створення повного монолітного клону

```bash
# Офлайн-злиття змін оверлею в його поточний батьківський файл
qemu-img commit clone-node-01.qcow2

# Конвертація ланцюжка шарів у повністю автономний монолітний диск (Flattening)
qemu-img convert -O qcow2 clone-node-01.qcow2 /var/lib/libvirt/images/standalone-vm.qcow2
```

---

## 6. Діагностика та відновлення пошкоджених ланцюжків дисків

Під час аварійних перезавантажень хоста, несподіваного вичерпання дискового простору або збоїв мережевого сховища ланцюжки знімків можуть переходити в неузгоджений або пошкоджений стан.

### 6.1. Аудит цілісності та виправлення помилок кластерів

Утиліта `qemu-img check` аналізує внутрішні таблиці L1/L2 та лічильники посилань кластерів (refcount blocks):

```bash
# Повний аналіз цілісності файлу оверлею
qemu-img check /var/lib/libvirt/images/broken-overlay.qcow2

# Автоматичне виправлення виявлених помилок метаданих та вивільнення висячих кластерів
qemu-img check -r all /var/lib/libvirt/images/broken-overlay.qcow2
```

Коди станів та типові дефекти метаданих QCOW2:
- **Leaked clusters (Витік кластерів):** кластери виділені у фізичному файлі, але на них не посилається жодна таблиця L2. Помилка не загрожує втратою даних і автоматично виправляється очищенням refcount-таблиці.
- **Corrupt cluster offsets (Пошкоджені зміщення):** таблиця L2 вказує на зміщення за межами фізичного розміру файлу або на службові метадані заголовка. Потребує відсікання пошкодженого фрагмента або відновлення з резервної копії.

### 6.2. Відновлення розірваних відносних шляхів (Broken Backing Path)

Якщо базовий файл або каталог образів було переміщено на іншу точку монтування (наприклад, з `/mnt/storage1` на `/mnt/fast-nvme`), спроба запуску ВМ завершується помилкою `Could not open backing file: No such file or directory`.

Для відновлення коректного зв'язку без тривалого поблокового перечитування застосовують команду «швидкого небезпечного» ребейзу:

```bash
# Оновлення абсолютного шляху до базового файлу в заголовку оверлею
qemu-img rebase -u -b /mnt/fast-nvme/golden-master.qcow2 -F qcow2 /mnt/fast-nvme/clone-node-01.qcow2
```

---

## 7. Взаємодія знімків із живою міграцією та блоковим дзеркалюванням

Під час перенесення працюючої віртуальної машини між різними фізичними хостами з локальними сховищами (Non-Shared Storage Live Migration) гіпервізор комбінує механізм знімків із блоковим дзеркалюванням (Block Mirroring) через протокол NBD (Network Block Device).

### Алгоритм підготовки дискового дзеркала через QMP

```
[Хост-Джерело] ───(1. Створення NBD-сервера на Цільовому Хості)───> [Цільовий Хост]
[Хост-Джерело] ───(2. QMP blockdev-mirror: копіювання бази)───────> [NBD Client -> Server]
                                    │
                    (3. Відстеження dirty bitmap при записі)
                                    │
[Хост-Джерело] ───(4. QMP block-job-complete: атомарний півот)───> [Цільовий Хост]
```

1. На цільовому хості створюється порожній цільовий файл диска однакового розміру та запускається вбудований NBD-сервер QEMU.
2. Хост-джерело надсилає команду `blockdev-mirror` (або застарілу `drive-mirror`), яка ініціює фонове потокове копіювання всіх зайнятих кластерів по мережі на цільовий NBD-експорт.
3. Поки триває мережева передача гігабайтів диска, гостьова ОС продовжує активно модифікувати блоки. Усі нові операції запису перехоплюються блоковим драйвером і фіксуються в бітовій карті брудних блоків.
4. Після вирівнювання обсягів джерело надсилає команду фінального перемикання (`block-job-complete`), віртуальний диск атомарно перепідключається до віддаленого вузла, а локальний вихідний ланцюжок оверлеїв заморожується або демонтується.

---

## 8. Структура файлу живого знімка пам'яті (Memory Save State)

Коли створюється живий знімок віртуальної машини зі збереженням оперативної пам'яті (`savevm` або `virsh snapshot-create` без прапорця `--disk-only`), гіпервізор QEMU генерує бінарний потік міграційного стану (Migration Stream Format).

### Структура секцій образу пам'яті та пристроїв

Потік складається з магічного заголовка та послідовності типізованих секцій:

- **Магічний ідентифікатор:** 4 байти `0x51 0x45 0x56 0x4D` (символи `QEVM`) та 4 байти версії формату міграційного потоку.
- **Секція конфігурації пристроїв (`QEMU_VM_SECTION_START`):** опис зареєстрованих віртуальних компонентів материнської плати, контролерів PCI та vCPU.
- **Сторінкові ітерації пам'яті (`QEMU_VM_SECTION_PART`):** неперервний потік сторінок RAM гостя. Для зменшення розміру файлу застосовується стиснення за алгоритмом RLE (Run-Length Encoding) для нульових сторінок або згортка алгоритмами zstd / LZ4.
- **Фінальний зріз стану (`QEMU_VM_SECTION_END`):** бінарні структури регістрів vCPU, стан таймерів TSC, вміст буферів мережевих черг `virtio-net` та внутрішні регістри емульованого контролера переривань APIC.
- **Футер завершення:** маркер `QEMU_VM_EOF` (`0x00`), що сигналізує про коректність збереженого дампа.

Під час відновлення гіпервізор відкриває цей потік, ініціалізує віртуальне залізо за дескрипторами секцій, завантажує сторінки в RAM гостя та відновлює виконання процесорів з точної збереженої інструкції.

---

## 9. Опитування топології розділів через гостьовий сокет JSON-RPC

Перед виконанням операцій заморозки та знімків керівний оркестратор може зчитувати інформацію про змонтовані розділи безпосередньо через сокет гостьового агента на хості (типовий шлях `/var/lib/libvirt/qemu/channel/target/domain-<ім'я>/org.qemu.guest_agent.0`):

```json
// Запит детальної карти файлових систем гостя
{
  "execute": "guest-get-fsinfo"
}

// Структурована відповідь із прив'язкою точок монтування до шин віртуальних дисків
{
  "return": [
    {
      "name": "dm-0",
      "mountpoint": "/",
      "type": "ext4",
      "used-bytes": 14258999296,
      "total-bytes": 52710400000,
      "disk": [
        {
          "serial": "VDA_ROOT_DISK",
          "bus-type": "virtio",
          "bus": 0,
          "unit": 0,
          "target": 0,
          "dev": "/dev/vda1"
        }
      ]
    }
  ]
}
```

Ця інформація дозволяє скриптам автоматизації точно співвіднести точку монтування гостьової операційної системи (`/var/lib/postgresql/data`) з відповідним віртуальним дисковим вузлом QEMU (`drive-virtio-disk1`) для вибіркового та узгодженого створення знімків.

Для захисту від зависання запитів сокетне з'єднання завжди обслуговується через неблокуючий ввід-вивід із системними викликами `poll(2)` або `select(2)` та суворим таймаутом очікування відповіді (зазвичай не більше 3–5 секунд). Перед відправкою важкої команди заморозки оркестратор надсилає діагностичний запит `{"execute": "guest-ping"}`: отримання порожнього об'єкта `{"return": {}}` підтверджує працездатність черги подій гостьового демона, унеможливлюючи блокування дискового конвеєра через завислий процес агента.
