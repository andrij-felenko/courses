# ⚙️ Атомарна заміна файлів та порятунок відкритих дескрипторів

Коли програма записує оновлений конфігураційний файл безпосередньо через `open(..., O_WRONLY | O_TRUNC)`, вона створює небезпечне часове вікно: файл обнуляється, і будь-який паралельний читач отримує порожні або напів-записані дані. Якщо ж посеред запису станеться збій живлення чи падіння процесу, старі дані вже знищені, а нові ще не зафіксовані. Цей проєкт розбирає дві критичні системні задачі, що безпосередньо спираються на поділ імені та інода: виробничий патерн гарантовано безпечної атомарної заміни файлів через `rename()` з повним скиданням кешів на диск, а також утиліту виявлення та порятунку видалених (unlinked) файлів, які все ще утримуються відкритими дескрипторами процесів у `/proc`.

## 1. Патерн атомарної заміни файлу (Safe Atomic Replace)

Щоб сторонні процеси за жодних умов не бачили частково записаного файлу, запис завжди виконується у проміжний тимчасовий файл у тому самому каталозі, після чого викликається системний виклик `rename()`. Оскільки обидва записи знаходяться в одній файловій системі, перейменування зводиться до атомарної заміни покажчика в таблиці каталогу.

### Чому прямий запис руйнує виробничі системи

Розгляньмо, що відбувається на рівні системних викликів, коли розробник наївно оновлює критичний конфігураційний файл `/etc/app/config.json` стандартною операцією перезапису:

:::tabs
```c
/* НАЇВНИЙ ПІДХІД: високий ризик збою */
int fd = open("/etc/app/config.json", O_WRONLY | O_TRUNC);
write(fd, new_payload, size);
close(fd);
```
```cpp
#include <fcntl.h>
#include <unistd.h>
#include <string_view>

// Наївний прямий перезапис: обнуляє інод перед записом
void unsafe_write(std::string_view payload) {
    int fd = ::open("/etc/app/config.json", O_WRONLY | O_TRUNC);
    if (fd >= 0) {
        ::write(fd, payload.data(), payload.size());
        ::close(fd);
    }
}
```
:::

У цій послідовності закладено три критичні точки відмови:

1. **Миттєве обнулення довжини (`i_size = 0`):** Системний виклик `open()` з прапорцем `O_TRUNC` негайно очищає карту блоків у поточному іноді та виставляє розмір файлу в нуль. Якщо в цей же момент фоновий робочий потік читає конфігурацію, його виклик `read()` поверне `0` (кінець файлу) або прочитає напів-згенерований JSON/YAML, викликавши аварійне завершення або непередбачувану поведінку програми.
2. **Втрата даних при аварійному вимкненні:** Якщо посеред виконання циклу `write()` зникне електроживлення або процес буде примусово зупинено сигналом `SIGKILL` (наприклад, через OOM-killer), старий вміст файлу вже безповоротно втрачено, а новий записаний лише частково. Після перезавантаження система не зможе запустити сервіс через синтаксичну помилку в конфігурації.
3. **Блокування виконуваних бінарників (`ETXTBSY`):** Якщо цільовим об'єктом є виконуваний файл працюючого сервісу (наприклад, `/usr/bin/daemon`), прямий виклик `open(..., O_WRONLY)` поверне помилку ядра `ETXTBSY` (*Text file busy*). Linux блокує запис у блоки файлу, якщо хоча б один процес у системі виконує код із цього інода через відображення пам'яті `mmap()`.

### П'ятикрокова архітектура надійного збереження

Виробничий патерн безпечного оновлення (відомий як *Safe Save* або *Atomic File Replacement*) розв'язує ці проблеми шляхом повного розділення старого та нового інодів:

```
Процес оновлення
  │
  ├── 1. open(".config.json.tmp.1042", O_WRONLY | O_CREAT | O_EXCL, mode)
  │      └── Створення нового інода (Inode #599) поруч зі старим (Inode #501)
  │
  ├── 2. write(fd, buffer, size)  [у циклі з обробкою EINTR]
  │      └── Запис усіх нових даних виключно у новий інод
  │
  ├── 3. fsync(fd)
  │      └── Примусове скидання сторінок пам'яті та метаданих Inode #599 на диск
  │
  ├── 4. close(fd)
  │
  ├── 5. rename(".config.json.tmp.1042", "config.json")
  │      └── Атомарна підміна запису dirent: "config.json" тепер вказує на Inode #599.
  │          Старий Inode #501 відв'язується (unlink), але активні читачі тримають його до закриття!
  │
  └── 6. dir_fd = open(".", O_RDONLY | O_DIRECTORY) ──> fsync(dir_fd) ──> close(dir_fd)
         └── Фіксація зміненого блоку каталогу в журналі файлової системи
```

Кожен крок цього алгоритму несе строго визначену функцію:

* **Створення поруч у тому самому каталозі:** Тимчасовий файл зобов'язаний створюватися в тому самому каталозі (або принаймні на тій самій файловій системі). Якщо створити тимчасовий файл у загальному каталозі `/tmp` (який зазвичай змонтовано як віртуальну пам'ять `tmpfs`), виклик `rename()` поверне помилку `EXDEV` (*Invalid cross-device link*), оскільки перейменування не здатне переміщати іноди між різними суперблоками.
* **Прапорець `O_EXCL`:** Запобігає випадковому перезапису чужого тимчасового файлу, якщо два процеси спробують зберегти файл одночасно.
* **Успадкування прав (`fchmod` / `fchown`):** Якщо цільовий файл уже існував, тимчасовий файл повинен отримати його точну бітову маску дозволів (`st_mode & 07777`) та власника, інакше новий файл буде створено з правами за замовчуванням відповідно до `umask` поточного процесу.
* **Синхронізація файлу `fsync()`:** Гарантує, що дані блоків фізично записані на енергонезалежний носій до того, як ім'я буде підмінено в каталозі. Без цього виклику сучасні кеші ядра з відкладеним записом (write-back page cache) можуть записати змінені метадані каталогу раніше за дані самого файлу, і у разі раптового збою живлення після перезавантаження користувач отримає файл, заповнений нульовими байтами.
* **Синхронізація батьківського каталогу `fsync(dir_fd)`:** Каталог у файловій системі сам по собі є файлом, чиї блоки кешуються в пам'яті. Виклик `fsync()` на дескрипторі каталогу гарантує, що транзакція перейменування в журналі ФС (наприклад, JBD2 в Ext4) зафіксована на диску.

### Подвійне споживання простору (Double Space Requirement) та оптимізація через CoW

Важливим практичним наслідком патерну Safe Save є необхідність тимчасового подвоєння дискового простору під час збереження. Якщо файл конфігурації чи бази даних має розмір 10 ГБ, у процесі створення нового файлу на диску одночасно існують і старий Inode #501 (10 ГБ), і новий Inode #599 (10 ГБ). Якщо на розділі залишається менше ніж 10 ГБ вільного місця, операція запису поверне помилку `ENOSPC`.

У сучасних файлових системах із підтримкою копіювання при записі (Btrfs, XFS, ZFS) це обмеження обходять за допомогою системного виклику клонування блоків `ioctl(FICLONE)` або `copy_file_range()`:

:::tabs
```c
#include <sys/ioctl.h>
#include <linux/fs.h>
#include <fcntl.h>
#include <unistd.h>

/* Швидке клонування метаданих без дублювання фізичних блоків даних (CoW) */
int clone_file_blocks(int src_fd, int dest_fd) {
    if (ioctl(dest_fd, FICLONE, src_fd) < 0) {
        return -1; /* ФС не підтримує reflink */
    }
    return 0;
}
```
```cpp
#include <sys/ioctl.h>
#include <linux/fs.h>
#include <expected>
#include <system_error>
#include <cerrno>

[[nodiscard]] std::expected<void, std::error_code>
clone_file_blocks(int src_fd, int dest_fd) {
    if (::ioctl(dest_fd, FICLONE, src_fd) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
```
:::

Виклик `FICLONE` миттєво створює новий інод, який посилається на ті самі фізичні екстенти старого файлу без виділення нового дискового простору. Нові дискові блоки виділятимуться лише для тих секторів, які будуть реально модифіковані.

### Реалізація атомарної заміни

Нижче наведено повну виробничу реалізацію функції безпечного запису мовами C та C++ з коректною обробкою переривань сигналів, збереженням атрибутів та обов'язковим очищенням тимчасових ресурсів у разі виникнення помилок.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <libgen.h>

/* Безпечний атомарний запис буфера даних у цільовий файл */
int atomic_write_file(const char *target_path, const void *data, size_t size, mode_t default_mode) {
    char dir_buf[1024];
    char temp_path[1024];
    struct stat st;
    mode_t target_mode = default_mode;
    uid_t target_uid = (uid_t)-1;
    gid_t target_gid = (gid_t)-1;
    int has_original = 0;

    if (!target_path || !data) {
        errno = EINVAL;
        return -1;
    }

    /* Отримуємо шлях до каталогу цільового файлу */
    strncpy(dir_buf, target_path, sizeof(dir_buf) - 1);
    dir_buf[sizeof(dir_buf) - 1] = '\0';
    char *dir_name = dirname(dir_buf);

    /* Якщо цільовий файл уже існує, зчитуємо його права та власника */
    if (stat(target_path, &st) == 0) {
        target_mode = st.st_mode & 07777;
        target_uid = st.st_uid;
        target_gid = st.st_gid;
        has_original = 1;
    }

    /* Формуємо унікальний шлях до тимчасового файлу поруч із цільовим */
    snprintf(temp_path, sizeof(temp_path), "%s/.tmp_atomic_%d_%lu", dir_name, (int)getpid(), (unsigned long)size);

    /* Створюємо новий інод з обов'язковою перевіркою відсутності колізій */
    int fd = open(temp_path, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, target_mode);
    if (fd < 0) {
        return -1;
    }

    /* Якщо запускаємося від привілейованого користувача, відновлюємо UID/GID */
    if (has_original && geteuid() == 0) {
        if (fchown(fd, target_uid, target_gid) < 0) {
            int err = errno;
            close(fd);
            unlink(temp_path);
            errno = err;
            return -1;
        }
    }

    /* Повний запис даних з обов'язковим врахуванням часткових записів та сигналів */
    const char *ptr = (const char *)data;
    size_t remaining = size;
    while (remaining > 0) {
        ssize_t written = write(fd, ptr, remaining);
        if (written < 0) {
            if (errno == EINTR) continue;
            int err = errno;
            close(fd);
            unlink(temp_path);
            errno = err;
            return -1;
        }
        ptr += written;
        remaining -= (size_t)written;
    }

    /* Примусово вимиваємо сторінки кешу та метадані інода на диск */
    if (fsync(fd) < 0) {
        int err = errno;
        close(fd);
        unlink(temp_path);
        errno = err;
        return -1;
    }

    /* Закриваємо дескриптор перед фінальною операцією підміни */
    if (close(fd) < 0) {
        int err = errno;
        unlink(temp_path);
        errno = err;
        return -1;
    }

    /* Атомарно замінюємо ім'я файлу на новий інод */
    if (rename(temp_path, target_path) < 0) {
        int err = errno;
        unlink(temp_path);
        errno = err;
        return -1;
    }

    /* Фіксуємо змінений запис каталогу на накопичувачі */
    int dir_fd = open(dir_name, O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    if (dir_fd >= 0) {
        fsync(dir_fd);
        close(dir_fd);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <expected>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

class ScopedFileDescriptor {
    int fd_{-1};
public:
    explicit ScopedFileDescriptor(int fd) noexcept : fd_(fd) {}
    ~ScopedFileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    
    ScopedFileDescriptor(const ScopedFileDescriptor&) = delete;
    ScopedFileDescriptor& operator=(const ScopedFileDescriptor&) = delete;
    ScopedFileDescriptor(ScopedFileDescriptor&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    ScopedFileDescriptor& operator=(ScopedFileDescriptor&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }
    int release() noexcept { int tmp = fd_; fd_ = -1; return tmp; }
};

[[nodiscard]] std::expected<void, std::error_code> 
atomic_write_file(const fs::path& target_path, std::string_view payload, mode_t default_mode = 0644) {
    std::error_code ec;
    const fs::path parent_dir = target_path.parent_path().empty() ? fs::current_path() : target_path.parent_path();
    
    mode_t target_mode = default_mode;
    uid_t target_uid = static_cast<uid_t>(-1);
    gid_t target_gid = static_cast<gid_t>(-1);
    bool has_original = false;

    struct stat st{};
    if (::stat(target_path.c_str(), &st) == 0) {
        target_mode = st.st_mode & 07777;
        target_uid = st.st_uid;
        target_gid = st.st_gid;
        has_original = true;
    }

    const fs::path temp_path = parent_dir / (".tmp_atomic_" + std::to_string(::getpid()) + "_" + std::to_string(payload.size()));

    ScopedFileDescriptor fd{::open(temp_path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, target_mode)};
    if (!fd.is_valid()) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // Лямбда-охоронець для автоматичного прибирання тимчасового файлу при помилці
    bool success = false;
    auto auto_cleanup = [&temp_path, &success]() {
        if (!success) {
            ::unlink(temp_path.c_str());
        }
    };
    struct CleanupGuard {
        decltype(auto_cleanup)& cleaner;
        ~CleanupGuard() { cleaner(); }
    } guard{auto_cleanup};

    if (has_original && ::geteuid() == 0) {
        if (::fchown(fd.get(), target_uid, target_gid) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
    }

    const char* ptr = payload.data();
    size_t remaining = payload.size();
    while (remaining > 0) {
        ssize_t written = ::write(fd.get(), ptr, remaining);
        if (written < 0) {
            if (errno == EINTR) continue;
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        ptr += written;
        remaining -= static_cast<size_t>(written);
    }

    if (::fsync(fd.get()) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // Закриваємо файл перед викликом rename
    int raw_fd = fd.release();
    if (::close(raw_fd) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (::rename(temp_path.c_str(), target_path.c_str()) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    success = true; // Успішно перейменовано, прибирати тимчасовий файл не потрібно

    // Скидаємо блок батьківського каталогу на носій
    ScopedFileDescriptor dir_fd{::open(parent_dir.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC)};
    if (dir_fd.is_valid()) {
        ::fsync(dir_fd.get());
    }

    return {};
}
```
:::

### Сучасні розширення: системний виклик `renameat2()`

У ядрі Linux, починаючи з версії 3.15, з'явився розширений системний виклик `renameat2()`, який дозволяє передавати прапорці контролю атомарності:

* **`RENAME_NOREPLACE`:** гарантує, що операція перейменування завершиться успіхом лише в тому випадку, якщо цільового файлу `target` ще не існує. Якщо ціль існує, ядро повертає помилку `EEXIST`. Це забезпечує ідеальний примітив для реалізації атомарного захоплення блокувань (file locking primitives) без стану гонитви між перевіркою та створенням.
* **`RENAME_EXCHANGE`:** атомарно обмінює місцями два існуючі файли або каталоги в системі. Обидва шляхи мають існувати. За одну транзакцію файлової системи покажчик першого імені починає вести на другий інод, а покажчик другого імені — на перший інод. Це дозволяє реалізувати миттєвий відкат (instant rollback) або чергування буферів без створення третіх тимчасових імен.
* **`RENAME_WHITEOUT`:** спеціалізований прапорець для шаруватих файлових систем (OverlayFS), який під час перейменування створює на місці старого імені спеціальний символ видалення (whiteout device).

:::tabs
```c
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

/* Атомарний обмін місцями активної конфігурації та резервної */
int swap_configurations(const char *active_path, const char *backup_path) {
    if (renameat2(AT_FDCWD, active_path, AT_FDCWD, backup_path, RENAME_EXCHANGE) < 0) {
        perror("Помилка атомарного обміну файлів");
        return -1;
    }
    return 0;
}
```
```cpp
#include <filesystem>
#include <expected>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>

namespace fs = std::filesystem;

[[nodiscard]] std::expected<void, std::error_code>
swap_configurations(const fs::path& active_path, const fs::path& backup_path) {
    if (::renameat2(AT_FDCWD, active_path.c_str(), AT_FDCWD, backup_path.c_str(), RENAME_EXCHANGE) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
```
:::

## 2. Утиліта порятунку видалених файлів через `/proc/[pid]/fd`

Коли файл видалено викликом `unlink()`, але фоновий демон усе ще тримає його відкритим, ядро підтримує інод у «живому» стані. Поки процес не завершився і не закрив дескриптор, увесь вміст файлу залишається доступним для читання через псевдопосилання `/proc/[PID]/fd/[FD]`.

### Як влаштоване вікно `/proc/[pid]/fd`

У псевдофайловій системі `procfs` каталог кожного процесу `/proc/[pid]/fd/` містить список числових файлових дескрипторів. Кожен елемент цього каталогу є особливим символьним посиланням ядра — так званим «магічним посиланням» (*magic link*).

Якщо цільове ім'я файлу було вилучено з файлової системи командою `rm`, системний виклик `readlink()` для такого запису повертає вихідний рядок шляху з приписаним суфіксом:

```
/var/log/database.log (deleted)
```

Магічна природа цього посилання полягає в тому, що коли прикладний процес викликає `open("/proc/1042/fd/3", O_RDONLY)`, ядро не починає звичайний пошук файлу за текстовим шляхом у каталозі `/var/log`. Воно бере покажчик безпосередньо з таблиці відкритих файлів процесу `current->files->fdt->fd[3]->f_inode` і створює новий опис відкритого файлу на той самий інод. Це дозволяє прочитати всі збережені байти навіть тоді, коли у файловій системі не залишилося жодного імені цього файлу.

### Політика безпеки та права доступу

Зчитування дескрипторів чужого процесу регулюється підсистемою прав доступу ядра:

1. **Користувацькі обмеження:** Процес може відкривати файли через `/proc/[pid]/fd/` лише тих процесів, які належать тому самому користувачеві (`EUID`), або якщо він володіє системною можливістю `CAP_SYS_PTRACE` чи `CAP_DAC_READ_SEARCH` (запуск від імені `root`).
2. **Прапорці доступу:** Відкриття `/proc/[pid]/fd/[fd]` створює новий `struct file` з правами, які не можуть перевищувати початковий режим відкриття вихідного дескриптора (якщо файл було відкрито тільки на запис `O_WRONLY`, спроба відкрити його на читання через `/proc` на деяких ядрах поверне помилку `EACCES`). У таких випадках для порятунку даних читають безпосередньо системну пам'ять процесу або використовують засоби налагодження `ptrace`.

### Особливості мережевих файлових систем (NFS Silly Renaming)

У розподілених мережевих файлових системах (NFS) сервер не підтримує концепцію неіменованих інодів для клієнтів. Якщо клієнтський процес відкриває файл на NFS і викликає `unlink()`, клієнтський драйвер NFS у ядрі Linux не видаляє файл негайно, а прозоро перейменовує його у спеціальний прихований файл вигляду:

```
.nfs000000000000421100000001
```

Цей механізм називається *Silly Renaming*. Файл зникне з сервера лише після того, як останній процес на клієнті виконає виклик `close()`. Якщо ж клієнт аварійно перезавантажиться, такі `.nfs*` файли залишаються на сервері як «сміття», яке потребує періодичного ручного очищення.

Якщо файл було видалено безпосередньо на стороні NFS-сервера іншим клієнтом, локальний процес при черговій спробі читання свого відкритого дескриптора отримає специфічну мережеву помилку ядра `ESTALE` (*Stale file handle*).

### Робота з розрідженими файлами (Sparse files) при порятунку

Багато баз даних та образів віртуальних дисків створюють файли з «дірками» — нерозподіленими блоками, які не займають місця на накопичувачі, але при читанні повертають нульові байти. Якщо просто копіювати такий файл через звичайний цикл `read()`/`write()`, усі нерозподілені дірки перетворяться на фізичні нульові блоки, що може миттєво переповнити цільовий диск.

Для коректного порятунку розріджених файлів використовують системний виклик `lseek()` з прапорцями швидкого пошуку дірок та даних:

* `lseek(fd, offset, SEEK_DATA)`: миттєво переміщує файловий покажчик на початок наступного непорожнього блоку даних.
* `lseek(fd, offset, SEEK_HOLE)`: переміщує покажчик на початок наступної нерозподіленої дірки.

Використовуючи ці виклики, утиліта порятунку копіює лише реальні блоки даних, пропускаючи дірки за допомогою виклику `lseek(out_fd, hole_size, SEEK_CUR)` або розширення `fallocate()`.

### Реалізація інспектора та порятунку

Нижче наведено повний код діагностичної утиліти, яка сканує всі запущені процеси або вказаний PID, знаходить усі відкриті дескриптори на видалені файли та копіює їхній вміст у безпечне місце на диску.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>

/* Копіювання вмісту відкритого дескриптора у новий файл */
static int rescue_descriptor(pid_t pid, int fd, const char *target_name, const char *dest_directory) {
    char proc_link[256];
    char out_path[512];
    char clean_name[256];

    snprintf(proc_link, sizeof(proc_link), "/proc/%d/fd/%d", pid, fd);

    /* Очищаємо суфікс " (deleted)" з отриманого шляху */
    strncpy(clean_name, target_name, sizeof(clean_name) - 1);
    clean_name[sizeof(clean_name) - 1] = '\0';
    char *del_marker = strstr(clean_name, " (deleted)");
    if (del_marker) *del_marker = '\0';

    /* Витягуємо базове ім'я файлу */
    char *base = strrchr(clean_name, '/');
    const char *filename = base ? base + 1 : clean_name;
    if (strlen(filename) == 0) filename = "unnamed_rescued_file";

    snprintf(out_path, sizeof(out_path), "%s/rescued_pid%d_fd%d_%s", dest_directory, pid, fd, filename);

    /* Відкриваємо дескриптор напряму через magic link */
    int in_fd = open(proc_link, O_RDONLY | O_CLOEXEC);
    if (in_fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", proc_link, strerror(errno));
        return -1;
    }

    int out_fd = open(out_path, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0640);
    if (out_fd < 0) {
        fprintf(stderr, "Не вдалося створити цільовий файл %s: %s\n", out_path, strerror(errno));
        close(in_fd);
        return -1;
    }

    char buffer[65536];
    ssize_t bytes_read;
    size_t total_rescued = 0;

    while ((bytes_read = read(in_fd, buffer, sizeof(buffer))) > 0) {
        char *ptr = buffer;
        ssize_t to_write = bytes_read;
        while (to_write > 0) {
            ssize_t written = write(out_fd, ptr, to_write);
            if (written < 0) {
                if (errno == EINTR) continue;
                fprintf(stderr, "Помилка запису даних у %s: %s\n", out_path, strerror(errno));
                close(in_fd);
                close(out_fd);
                return -1;
            }
            ptr += written;
            to_write -= written;
        }
        total_rescued += (size_t)bytes_read;
    }

    close(in_fd);
    close(out_fd);

    printf("✓ [ВРЯТОВАНО] PID %d, FD %d -> %s (розмір: %lu байтів)\n", pid, fd, out_path, (unsigned long)total_rescued);
    return 0;
}

/* Сканування таблиці дескрипторів конкретного процесу */
int scan_process_descriptors(pid_t pid, const char *dest_directory) {
    char fd_dir_path[256];
    snprintf(fd_dir_path, sizeof(fd_dir_path), "/proc/%d/fd", pid);

    DIR *dir = opendir(fd_dir_path);
    if (!dir) {
        return -1;
    }

    struct dirent *entry;
    int rescued_count = 0;

    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') continue;

        int fd_num = atoi(entry->d_name);
        char link_path[512];
        char target_buf[1024];

        snprintf(link_path, sizeof(link_path), "%s/%s", fd_dir_path, entry->d_name);
        ssize_t len = readlink(link_path, target_buf, sizeof(target_buf) - 1);
        if (len < 0) continue;
        target_buf[len] = '\0';

        /* Перевіряємо наявність мітки (deleted) у розв'язаному шляху */
        if (strstr(target_buf, "(deleted)") != NULL) {
            printf("! Знайдено відкритий видалений файл: PID %d, FD %d -> %s\n", pid, fd_num, target_buf);
            if (rescue_descriptor(pid, fd_num, target_buf, dest_directory) == 0) {
                rescued_count++;
            }
        }
    }

    closedir(dir);
    return rescued_count;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <filesystem>
#include <expected>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

struct GhostFileEntry {
    pid_t pid;
    int fd;
    std::string original_path;
    size_t file_size;
};

class ProcRescueManager {
public:
    static std::vector<GhostFileEntry> scan_process(pid_t pid) {
        std::vector<GhostFileEntry> results;
        const fs::path fd_path = fs::path("/proc") / std::to_string(pid) / "fd";

        std::error_code ec;
        if (!fs::exists(fd_path, ec)) {
            return results;
        }

        for (const auto& entry : fs::directory_iterator(fd_path, ec)) {
            if (ec) break;

            std::string link_target = fs::read_symlink(entry.path(), ec).string();
            if (ec) { ec.clear(); continue; }

            if (link_target.find("(deleted)") != std::string::npos) {
                int fd_num = -1;
                try {
                    fd_num = std::stoi(entry.path().filename().string());
                } catch (...) {
                    continue;
                }

                struct stat st{};
                size_t size_bytes = 0;
                if (::stat(entry.path().c_str(), &st) == 0) {
                    size_bytes = static_cast<size_t>(st.st_size);
                }

                results.push_back(GhostFileEntry{
                    .pid = pid,
                    .fd = fd_num,
                    .original_path = link_target,
                    .file_size = size_bytes
                });
            }
        }
        return results;
    }

    static std::expected<fs::path, std::error_code> 
    rescue_file(const GhostFileEntry& item, const fs::path& dest_dir) {
        std::error_code ec;
        fs::create_directories(dest_dir, ec);
        if (ec) return std::unexpected(ec);

        std::string clean_name = item.original_path;
        auto pos = clean_name.find(" (deleted)");
        if (pos != std::string::npos) {
            clean_name.erase(pos);
        }

        fs::path orig_p(clean_name);
        std::string fname = orig_p.filename().empty() ? "unnamed_ghost" : orig_p.filename().string();
        fs::path out_file = dest_dir / ("rescued_pid" + std::to_string(item.pid) + "_fd" + std::to_string(item.fd) + "_" + fname);

        fs::path magic_link = fs::path("/proc") / std::to_string(item.pid) / "fd" / std::to_string(item.fd);

        int in_fd = ::open(magic_link.c_str(), O_RDONLY | O_CLOEXEC);
        if (in_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        int out_fd = ::open(out_file.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0640);
        if (out_fd < 0) {
            int err = errno;
            ::close(in_fd);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        std::vector<char> buffer(65536);
        ssize_t bytes_read = 0;
        while ((bytes_read = ::read(in_fd, buffer.data(), buffer.size())) > 0) {
            char* ptr = buffer.data();
            ssize_t to_write = bytes_read;
            while (to_write > 0) {
                ssize_t written = ::write(out_fd, ptr, to_write);
                if (written < 0) {
                    if (errno == EINTR) continue;
                    int err = errno;
                    ::close(in_fd);
                    ::close(out_fd);
                    return std::unexpected(std::error_code(err, std::generic_category()));
                }
                ptr += written;
                to_write -= written;
            }
        }

        ::close(in_fd);
        ::close(out_fd);
        return out_file;
    }
};
```
:::

## 3. Практичний експеримент: створення, вилучення та порятунок

Щоб наочно переконатися у роботі механіки та перевірити розроблені утиліти, проведемо покроковий лабораторний експеримент у терміналі Linux.

### Крок 1: Запуск фонового процесу з відкритим файлом

Створимо простий однорядковий фоновий скрипт, який відкриває файл `/tmp/critical_service.data` на запис і щосекунди дописує туди поточний час із лічильником:

```bash
# Запускаємо безперервний запис у файл у фоні
python3 -c '
import time, os
with open("/tmp/critical_service.data", "w") as f:
    i = 0
    while True:
        f.write(f"Record {i}: {time.ctime()}\n")
        f.flush()
        time.sleep(1)
        i += 1
' &
PID=$!
echo "Запущено тестовий процес із PID: $PID"
```

### Крок 2: Видалення файлу та перевірка розбіжності

Тепер імітуємо випадкове видалення файлу адміністратором або ротаційним скриптом:

```bash
# Видаляємо ім'я з каталогу
rm /tmp/critical_service.data

# Перевіряємо, чи файл існує в каталозі
ls -l /tmp/critical_service.data
# ls: cannot access '/tmp/critical_service.data': No such file or directory
```

У каталозі файлу немає. Проте перевіримо стан процесу та файлової системи через `lsof`:

```bash
lsof -p $PID
```

У виводі ми чітко бачимо:

```
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF   NODE NAME
python3 14205 user    3w   REG    0,36      480 184512 /tmp/critical_service.data (deleted)
```

Дескриптор `3w` відкритий, розмір файлу продовжує зростати, а ядро додало мітку `(deleted)`.

### Крок 3: Порятунок даних через утиліту

Запускаємо нашу програму порятунку для знайденого PID:

```bash
# Створюємо теку для врятованих даних
mkdir -p /tmp/recovery_box

# Зчитуємо дані безпосередньо з дескриптора ядра
cat /proc/$PID/fd/3 > /tmp/recovery_box/recovered_critical.data

# Перевіряємо вміст врятованого файлу
head -n 5 /tmp/recovery_box/recovered_critical.data
```

Усі рядки журналу, записані до цього моменту, успішно відновлені в новому файлі без зупинки працюючого процесу. Після завершення процесу (`kill $PID`) ядро закриє дескриптор `3`, і старий інод остаточно звільнить пам'ять.

## 4. Пастки безпеки: гонитви в загальних каталогах (`/tmp`)

Під час створення тимчасових файлів для подальшого виклику `rename()` у каталогах зі спільним доступом (наприклад, `/tmp` або `/var/tmp`) виникає серйозний клас уразливостей, пов'язаний із так званими атаками за часом перевірки до часу використання (англ. *Time-of-Check to Time-of-Use*, TOCTOU).

### Атака через підміну символьного посилання

Якщо тимчасове ім'я формується передбачувано (наприклад, на основі фіксованого імені або лише номера PID, який легко перебрати), зловмисник може заздалегідь створити символьне посилання з таким ім'ям, що вказує на критичний системний файл:

```bash
# Зловмисник створює пастку в /tmp
ln -s /etc/shadow /tmp/.tmp_atomic_1042_120
```

Коли привілейована програма, що працює від імені `root`, викличе `open("/tmp/.tmp_atomic_1042_120", O_WRONLY | O_CREAT)`, системний виклик перейде за символьним посиланням і перезапише вміст системного файлу паролів `/etc/shadow`.

### Захист на рівні прапорців ядра

Для запобігання таким атакам використовують два обов'язкові рівні захисту:

1. **Прапорець `O_EXCL` разом із `O_CREAT`:** У системному виклику `open()` комбінація `O_CREAT | O_EXCL` змушує ядро перевірити, чи існує файл на момент створення. Якщо за цим шляхом уже існує файл або символьне посилання, виклик гарантовано зазнає невдачі з кодом `EEXIST`, не переходячи за посиланням.
2. **Системний захист ядра Linux (Sticky bit та sysctl):** За замовчуванням каталог `/tmp` має встановлений sticky-біт (`chmod 1777 /tmp`), який забороняє звичайним користувачам видаляти або перейменовувати файли інших користувачів. Крім того, сучасні ядра Linux за замовчуванням мають увімкнені захисні параметри `sysctl`:

```bash
sysctl fs.protected_symlinks=1
sysctl fs.protected_hardlinks=1
sysctl fs.protected_regular=2
sysctl fs.protected_fifos=2
```

Параметр `fs.protected_symlinks=1` забороняє перехід за символьними посиланнями у каталогах зі sticky-бітом (`/tmp`), якщо власник посилання не збігається з власником каталогу або користувачем, який ініціював відкриття.

Параметр `fs.protected_hardlinks=1` забороняє звичайним користувачам створювати жорсткі посилання на файли, якими вони не володіють і до яких не мають повних прав читання та запису. Це унеможливлює ситуацію, коли зловмисник створює жорстке посилання на конфіденційний системний файл (наприклад, базу даних або ключ), штучно збільшуючи `i_nlink` і запобігаючи фізичному видаленню блоків даних після того, як адміністратор викличе `rm` на оригінальному файлі.

## 5. Трасування системних викликів за допомогою `strace` та eBPF

Щоб переконатися у відсутності прихованих розгалужень та зафіксувати точну послідовність операцій ядра під час виконання розроблених утиліт, скористаємося інструментом `strace`.

Виконаємо трасування функції атомарного запису:

```bash
strace -e trace=openat,write,fsync,close,rename,unlink ./atomic_writer /etc/app/config.json "new_data"
```

У журналі трасування відображається бездоганний ланцюжок дій:

```
openat(AT_FDCWD, "/etc/app/.tmp_atomic_14022_8", O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC, 0644) = 3
write(3, "new_data", 8)                 = 8
fsync(3)                                = 0
close(3)                                = 0
rename("/etc/app/.tmp_atomic_14022_8", "/etc/app/config.json") = 0
openat(AT_FDCWD, "/etc/app", O_RDONLY|O_DIRECTORY|O_CLOEXEC) = 3
fsync(3)                                = 0
close(3)                                = 0
```

Зверніть увагу: жоден системний виклик не звертався до старого інода файлу `/etc/app/config.json` на запис. Перехід відбувся єдиним неподільним кроком `rename()`, після чого оновлений стан батьківського каталогу було синхронізовано на носій другим викликом `fsync()`.

Для глибшого спостереження за поведінкою драйвера файлової системи на рівні ядра можна використати інструмент `bpftrace`, підключившись до внутрішніх точок трасування VFS:

```bash
bpftrace -e '
tracepoint:syscalls:sys_enter_renameat2 {
    printf("RENAME: old=%s -> new=%s, flags=%d\n", 
           str(args->oldname), str(args->newname), args->flags);
}
tracepoint:ext4:ext4_unlink_enter {
    printf("EXT4_UNLINK: parent_dir_ino=%lu, name=%s\n", 
           args->dir, str(args->dentry));
}
'
```

Цей скрипт фіксує точний момент, коли виклик `rename()` входить у ядро, блокує м'ютекс каталогу `inode_lock()` і виконує операцію підміни без жодного проміжного стану, видимого іншим процесам операційної системи.
