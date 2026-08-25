# ⚙️ Низькорівневе клонування вузла VFS: повне збереження метаданих на C та C++

Утиліти копіювання файлових дерев спираються на послідовне виконання низькорівневих системних викликів ядра. Щоб зрозуміти, чому просте читання та запис байтів призводить до втрати контексту файлової системи, необхідно розглянути точний алгоритм реплікації одного вузла VFS.

## Архітектурний життєвий цикл копіювання інода

Процес точного клонування вимагає суворого дотримання послідовності викликів ядра, оскільки порушення порядку призводить до незворотного скидання встановлених метаданих:

```
[1. statx(AT_SYMLINK_NOFOLLOW)] ──► Зчитування типу, прав, UID/GID, timestamps, size
             │
             ▼
[2. openat / mkdirat / symlinkat / mknodat] ──► Створення вузла-приймача
             │
             ▼
[3. copy_file_range / lseek(SEEK_DATA)] ──► Клонування даних або розріджених дірок
             │
             ▼
[4. llistxattr / lgetxattr / lsetxattr] ──► Реплікація розширених атрибутів і ACL
             │
             ▼
[5. fchownat(AT_SYMLINK_NOFOLLOW)] ──► Встановлення власника (скидає SUID/SGID!)
             │
             ▼
[6. fchmodat] ──► Фіксація повного mode (SUID/SGID/Sticky відновлюються)
             │
             ▼
[7. utimensat(AT_SYMLINK_NOFOLLOW)] ──► Фіксація atime/mtime (завжди останній крок)
```

### Чому порядок операцій є критичним

1. **Зчитування джерела через `statx` з `AT_SYMLINK_NOFOLLOW`:**
   Прапорець `AT_SYMLINK_NOFOLLOW` гарантує, що якщо джерелом є символьне посилання, системний виклик поверне метадані самого посилання (його права, власника, розмір, що дорівнює довжині рядка шляху), а не об'єкта, на який воно вказує. Без цього прапорця копіювання symlink перетвориться на дублювання цільового файлу.

2. **Створення вузла відповідного типу та безпека початкових прав:**
   - Для звичайного файлу використовується `open` із прапорцем `O_CREAT | O_WRONLY | O_TRUNC` та навмисно обмеженими початковими правами `0600`. Це запобігає стану гонитви (race condition), коли сторонній непривілейований процес міг би прочитати недописані конфіденційні дані до того, як на файл буде накладено вихідні списки доступу ACL чи обмеження mode;
   - Для каталогів викликається `mkdirat` із тимчасовими правами `0700`, що забезпечує можливість безперешкодного створення вкладених файлів навіть тоді, коли кінцевий каталог повинен мати права `0555` (тільки читання);
   - Для символьних посилань вичитується рядок цілі через `readlinkat` і створюється новий вузол через `symlinkat`;
   - Для спеціальних файлів (FIFO, символьних чи блокових пристроїв) обчислюється комбінований номер пристрою `makedev(major, minor)` і викликається `mknodat`. При цьому сокети домену Unix (`S_IFSOCK`) не копіюються як файли даних, оскільки вони є тимчасовими точками зв'язку запущених процесів.

3. **Перенесення розріджених даних та екстентів:**
   Звичайний цикл `read/write` призвів би до фізичного виділення дисків під нульові блоки. Функція `copy_sparse_data` використовує системні виклики `lseek(src_fd, offset, SEEK_DATA)` для пошуку початків блоків із реальними даними та `lseek(src_fd, data_start, SEEK_HOLE)` для визначення їхньої довжини. Тільки діапазони між `data_start` та `hole_start` читаються з диска й записуються у файл призначення; дірки пропускаються за допомогою `lseek` на приймачі, а підсумковий розмір файлу фіксується викликом `ftruncate`. Перед цим робиться спроба виклику `copy_file_range`, що дозволяє файловій системі виконати миттєве Copy-on-Write клонування екстентів без навантаження на диск.

4. **Двоетапне копіювання розширених атрибутів (xattr):**
   Функція `copy_xattrs` спочатку викликає `llistxattr` із нульовим розміром буфера, щоб дізнатися точну кількість байтів, необхідну для збереження списку імен атрибутів. Після виділення пам'яті список вичитується повторно, і для кожного імені (включно з `system.posix_acl_access` та `security.selinux`) зчитується бінарне значення та записується на цільовий інод через `lsetxattr`. Якщо цільова файлова система не підтримує розширені атрибути (наприклад, VFAT або стара конфігурація NFS), помилка `ENOTSUP` або `EOPNOTSUPP` перехоплюється як допустиме обмеження носія.

5. **Встановлення власника та відновлення прав:**
   Виклик `fchownat` змінює числові ідентифікатори `stx_uid` та `stx_gid`. Оскільки ядро Linux з міркувань безпеки автоматично очищує біти `S_ISUID` та `S_ISGID` під час зміни власника (механізм `ATTR_KILL_SUID` / `ATTR_KILL_SGID`), виклик `fchmodat` обов'язково виконується наступним, повертаючи початкову маску прав. Якщо процес працює без привілею `CAP_CHOWN`, виклик `fchownat` поверне `EPERM`, тому утиліти зазвичай ігнорують цю помилку для звичайних користувачів, зберігаючи власність поточного запущеного процесу.

6. **Фіксація часових позначок:**
   Будь-яка операція запису даних чи зміни атрибутів інода оновлює мітки часу модифікації `mtime` та зміни стану `ctime`. Тому виклик `utimensat` із передачею збережених наносекундних структур `timespec` завершує процедуру клонування.

## Обробка жорстких посилань під час обходу дерева

Під час рекурсивного копіювання ієрархії каталогів програма повинна підтримувати глобальну хеш-таблицю відповідності пар `(dev_t, ino_t) -> std::string` (шлях до вже створеного цільового файлу).

```
Коли stx.stx_nlink > 1:
1. Перевірити таблицю: чи бачили ми вже пару (stx_dev_major:stx_dev_minor, stx_ino)?
   • ТАК: викликати linkat(AT_FDCWD, existing_dst_path, AT_FDCWD, new_dst_path, 0)
          та завершити обробку поточного вузла.
   • НІ:  виконати повне клонування вузла та зберегти (dev, ino) -> new_dst_path у таблицю.
```

Це запобігає дублюванню фізичних даних на диску та повністю зберігає початкову топологію іменованих зв'язків. Оскільки жорсткі посилання не можуть перетинати межі різних файлових систем (системний виклик `linkat` повертає `EXDEV`), перевірка пристрою `stx_dev` є обов'язковим первинним ключем таблиці.

## Обробка переривань та крайових випадків уводу-виводу

Низькорівневе копіювання великих файлів стикається з типовими ситуаціями POSIX I/O:
- **Переривання сигналами (`EINTR`):** Системні виклики `read`, `write`, `copy_file_range` можуть бути перервані надходженням сигналу до передачі повного блоку. Код зобов'язаний повторювати виклик у циклі `while`.
- **Неповний запис (Short Writes):** Виклик `write()` не гарантує запис усього буфера за один крок (наприклад, при наближенні до межі дискової квоти або через переповнення внутрішніх черг ядра). Цикл запису повинен зміщувати покажчик буфера на кількість фактично записаних байтів `written += n_write`.
- **Зняття блокувань та витік дескрипторів:** У C++ застосування патерну RAII через клас `ScopedFd` гарантує закриття дескрипторів навіть у разі генерації винятків `std::system_error` під час помилок запису або нестачі дискового простору `ENOSPC`.

## Реалізація мовами C та C++

Нижче наведено повний вихідний код програми клонування окремого файлового вузла зі збереженням усього спектра метаданих двома мовами програмування: на чистому C та ідіоматичному C++20 із застосуванням RAII-обгорток для файлових дескрипторів та обробки винятків.

:::tabs
@tab c
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/sysmacros.h>
#include <sys/xattr.h>
#include <linux/fs.h>

#define COPY_BUF_SIZE 65536

static int copy_sparse_data(int src_fd, int dst_fd, off_t total_size) {
    off_t offset = 0;
    char buffer[COPY_BUF_SIZE];

    while (offset < total_size) {
        off_t data_start = lseek(src_fd, offset, SEEK_DATA);
        if (data_start == -1) {
            if (errno == ENXIO) {
                /* Більше даних немає, решта файлу є діркою */
                break;
            }
            return -1;
        }

        off_t hole_start = lseek(src_fd, data_start, SEEK_HOLE);
        if (hole_start == -1) {
            hole_start = total_size;
        }

        if (lseek(dst_fd, data_start, SEEK_SET) == -1) {
            return -1;
        }

        off_t remaining = hole_start - data_start;
        lseek(src_fd, data_start, SEEK_SET);

        while (remaining > 0) {
            size_t to_read = (remaining < COPY_BUF_SIZE) ? (size_t)remaining : COPY_BUF_SIZE;
            ssize_t n_read = read(src_fd, buffer, to_read);
            if (n_read <= 0) {
                if (n_read < 0 && errno == EINTR) continue;
                return -1;
            }

            ssize_t written = 0;
            while (written < n_read) {
                ssize_t n_write = write(dst_fd, buffer + written, n_read - written);
                if (n_write <= 0) {
                    if (n_write < 0 && errno == EINTR) continue;
                    return -1;
                }
                written += n_write;
            }
            remaining -= n_read;
        }
        offset = hole_start;
    }

    if (ftruncate(dst_fd, total_size) == -1) {
        return -1;
    }
    return 0;
}

static int copy_xattrs(const char *src_path, const char *dst_path) {
    ssize_t list_len = llistxattr(src_path, NULL, 0);
    if (list_len <= 0) {
        return (list_len == 0 || errno == ENOTSUP || errno == ENODATA) ? 0 : -1;
    }

    char *list = malloc(list_len);
    if (!list) return -1;

    list_len = llistxattr(src_path, list, list_len);
    if (list_len < 0) {
        free(list);
        return -1;
    }

    const char *attr_name = list;
    while (attr_name < list + list_len) {
        ssize_t val_len = lgetxattr(src_path, attr_name, NULL, 0);
        if (val_len > 0) {
            void *val = malloc(val_len);
            if (val) {
                if (lgetxattr(src_path, attr_name, val, val_len) == val_len) {
                    lsetxattr(dst_path, attr_name, val, val_len, 0);
                }
                free(val);
            }
        } else if (val_len == 0) {
            lsetxattr(dst_path, attr_name, "", 0, 0);
        }
        attr_name += strlen(attr_name) + 1;
    }

    free(list);
    return 0;
}

int clone_vfs_node(const char *src_path, const char *dst_path) {
    struct statx stx;
    unsigned int mask = STATX_TYPE | STATX_MODE | STATX_UID | STATX_GID |
                        STATX_ATIME | STATX_MTIME | STATX_SIZE;

    if (statx(AT_FDCWD, src_path, AT_SYMLINK_NOFOLLOW, mask, &stx) != 0) {
        perror("statx");
        return -1;
    }

    mode_t type = stx.stx_mode & S_IFMT;

    if (S_ISREG(type)) {
        int src_fd = open(src_path, O_RDONLY | O_NOFOLLOW);
        if (src_fd < 0) return -1;

        int dst_fd = open(dst_path, O_WRONLY | O_CREAT | O_TRUNC, 0600);
        if (dst_fd < 0) {
            close(src_fd);
            return -1;
        }

        /* Спроба скопіювати через CoW copy_file_range */
        loff_t in_off = 0, out_off = 0;
        ssize_t reflink_res = copy_file_range(src_fd, &in_off, dst_fd, &out_off, stx.stx_size, 0);
        if (reflink_res < 0 || (size_t)reflink_res < stx.stx_size) {
            /* Повернення на початок та звичайне розріджене копіювання */
            lseek(src_fd, 0, SEEK_SET);
            lseek(dst_fd, 0, SEEK_SET);
            if (copy_sparse_data(src_fd, dst_fd, stx.stx_size) != 0) {
                close(src_fd);
                close(dst_fd);
                return -1;
            }
        }

        close(src_fd);
        close(dst_fd);
    } else if (S_ISDIR(type)) {
        if (mkdir(dst_path, 0700) != 0 && errno != EEXIST) {
            return -1;
        }
    } else if (S_ISLNK(type)) {
        char link_target[PATH_MAX];
        ssize_t len = readlink(src_path, link_target, sizeof(link_target) - 1);
        if (len < 0) return -1;
        link_target[len] = '\0';

        if (symlink(link_target, dst_path) != 0) return -1;
    } else if (S_ISFIFO(type)) {
        if (mkfifo(dst_path, 0600) != 0) return -1;
    } else if (S_ISCHR(type) || S_ISBLK(type)) {
        dev_t dev = makedev(stx.stx_rdev_major, stx.stx_rdev_minor);
        if (mknod(dst_path, type | 0600, dev) != 0) return -1;
    }

    /* Відновлення розширених атрибутів (xattr, ACL, SELinux) */
    copy_xattrs(src_path, dst_path);

    /* Відновлення власника та групи (потрібні права root / CAP_CHOWN) */
    fchownat(AT_FDCWD, dst_path, stx.stx_uid, stx.stx_gid, AT_SYMLINK_NOFOLLOW);

    /* Відновлення прав доступу mode (після fchownat, щоб не скинулись SUID/SGID) */
    if (!S_ISLNK(type)) {
        fchmodat(AT_FDCWD, dst_path, stx.stx_mode & 07777, 0);
    }

    /* Відновлення міток часу (atime та mtime) */
    struct timespec times[2];
    times[0].tv_sec = stx.stx_atime.tv_sec;
    times[0].tv_nsec = stx.stx_atime.tv_nsec;
    times[1].tv_sec = stx.stx_mtime.tv_sec;
    times[1].tv_nsec = stx.stx_mtime.tv_nsec;

    utimensat(AT_FDCWD, dst_path, times, AT_SYMLINK_NOFOLLOW);

    return 0;
}
```
@tab cpp
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <system_error>
#include <filesystem>
#include <span>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/sysmacros.h>
#include <sys/xattr.h>
#include <linux/fs.h>

namespace fs = std::filesystem;

class ScopedFd {
public:
    explicit ScopedFd(int fd = -1) noexcept : m_fd(fd) {}
    ~ScopedFd() { reset(); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            reset(other.m_fd);
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
        m_fd = new_fd;
    }

private:
    int m_fd;
};

class VfsCloner {
public:
    static constexpr size_t BufferSize = 65536;

    static void copySparseData(int src_fd, int dst_fd, off_t total_size) {
        off_t offset = 0;
        std::vector<char> buffer(BufferSize);

        while (offset < total_size) {
            off_t data_start = ::lseek(src_fd, offset, SEEK_DATA);
            if (data_start == -1) {
                if (errno == ENXIO) break; // Більше немає даних
                throw std::system_error(errno, std::generic_category(), "lseek SEEK_DATA failed");
            }

            off_t hole_start = ::lseek(src_fd, data_start, SEEK_HOLE);
            if (hole_start == -1) {
                hole_start = total_size;
            }

            if (::lseek(dst_fd, data_start, SEEK_SET) == -1) {
                throw std::system_error(errno, std::generic_category(), "lseek dst SEEK_SET failed");
            }

            off_t remaining = hole_start - data_start;
            ::lseek(src_fd, data_start, SEEK_SET);

            while (remaining > 0) {
                size_t to_read = std::min(static_cast<size_t>(remaining), BufferSize);
                ssize_t n_read = ::read(src_fd, buffer.data(), to_read);
                if (n_read <= 0) {
                    if (n_read < 0 && errno == EINTR) continue;
                    throw std::system_error(errno, std::generic_category(), "read failed");
                }

                ssize_t written = 0;
                while (written < n_read) {
                    ssize_t n_write = ::write(dst_fd, buffer.data() + written, n_read - written);
                    if (n_write <= 0) {
                        if (n_write < 0 && errno == EINTR) continue;
                        throw std::system_error(errno, std::generic_category(), "write failed");
                    }
                    written += n_write;
                }
                remaining -= n_read;
            }
            offset = hole_start;
        }

        if (::ftruncate(dst_fd, total_size) == -1) {
            throw std::system_error(errno, std::generic_category(), "ftruncate failed");
        }
    }

    static void copyXattrs(const std::string& src_path, const std::string& dst_path) {
        ssize_t list_len = ::llistxattr(src_path.c_str(), nullptr, 0);
        if (list_len <= 0) {
            if (list_len == 0 || errno == ENOTSUP || errno == ENODATA) return;
            throw std::system_error(errno, std::generic_category(), "llistxattr failed");
        }

        std::vector<char> list_buf(list_len);
        list_len = ::llistxattr(src_path.c_str(), list_buf.data(), list_buf.size());
        if (list_len < 0) {
            throw std::system_error(errno, std::generic_category(), "llistxattr read failed");
        }

        const char* current_attr = list_buf.data();
        while (current_attr < list_buf.data() + list_len) {
            ssize_t val_len = ::lgetxattr(src_path.c_str(), current_attr, nullptr, 0);
            if (val_len > 0) {
                std::vector<char> val_buf(val_len);
                if (::lgetxattr(src_path.c_str(), current_attr, val_buf.data(), val_buf.size()) == val_len) {
                    ::lsetxattr(dst_path.c_str(), current_attr, val_buf.data(), val_buf.size(), 0);
                }
            } else if (val_len == 0) {
                ::lsetxattr(dst_path.c_str(), current_attr, "", 0, 0);
            }
            current_attr += std::strlen(current_attr) + 1;
        }
    }

    static void cloneNode(const std::string& src_path, const std::string& dst_path) {
        struct statx stx{};
        unsigned int mask = STATX_TYPE | STATX_MODE | STATX_UID | STATX_GID |
                            STATX_ATIME | STATX_MTIME | STATX_SIZE;

        if (::statx(AT_FDCWD, src_path.c_str(), AT_SYMLINK_NOFOLLOW, mask, &stx) != 0) {
            throw std::system_error(errno, std::generic_category(), "statx failed for " + src_path);
        }

        mode_t type = stx.stx_mode & S_IFMT;

        if (S_ISREG(type)) {
            ScopedFd src_fd(::open(src_path.c_str(), O_RDONLY | O_NOFOLLOW));
            if (!src_fd.valid()) {
                throw std::system_error(errno, std::generic_category(), "open src failed: " + src_path);
            }

            ScopedFd dst_fd(::open(dst_path.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0600));
            if (!dst_fd.valid()) {
                throw std::system_error(errno, std::generic_category(), "open dst failed: " + dst_path);
            }

            loff_t in_off = 0, out_off = 0;
            ssize_t reflink_res = ::copy_file_range(src_fd.get(), &in_off, dst_fd.get(), &out_off, stx.stx_size, 0);
            if (reflink_res < 0 || static_cast<size_t>(reflink_res) < stx.stx_size) {
                ::lseek(src_fd.get(), 0, SEEK_SET);
                ::lseek(dst_fd.get(), 0, SEEK_SET);
                copySparseData(src_fd.get(), dst_fd.get(), stx.stx_size);
            }
        } else if (S_ISDIR(type)) {
            if (::mkdir(dst_path.c_str(), 0700) != 0 && errno != EEXIST) {
                throw std::system_error(errno, std::generic_category(), "mkdir failed: " + dst_path);
            }
        } else if (S_ISLNK(type)) {
            std::vector<char> link_target(PATH_MAX);
            ssize_t len = ::readlink(src_path.c_str(), link_target.data(), link_target.size() - 1);
            if (len < 0) {
                throw std::system_error(errno, std::generic_category(), "readlink failed: " + src_path);
            }
            link_target[len] = '\0';

            if (::symlink(link_target.data(), dst_path.c_str()) != 0) {
                throw std::system_error(errno, std::generic_category(), "symlink failed: " + dst_path);
            }
        } else if (S_ISFIFO(type)) {
            if (::mkfifo(dst_path.c_str(), 0600) != 0) {
                throw std::system_error(errno, std::generic_category(), "mkfifo failed: " + dst_path);
            }
        } else if (S_ISCHR(type) || S_ISBLK(type)) {
            dev_t dev = makedev(stx.stx_rdev_major, stx.stx_rdev_minor);
            if (::mknod(dst_path.c_str(), type | 0600, dev) != 0) {
                throw std::system_error(errno, std::generic_category(), "mknod failed: " + dst_path);
            }
        }

        // Копіювання xattr, ACL та контекстів безпеки
        copyXattrs(src_path, dst_path);

        // Відновлення власника
        ::fchownat(AT_FDCWD, dst_path.c_str(), stx.stx_uid, stx.stx_gid, AT_SYMLINK_NOFOLLOW);

        // Відновлення прав
        if (!S_ISLNK(type)) {
            ::fchmodat(AT_FDCWD, dst_path.c_str(), stx.stx_mode & 07777, 0);
        }

        // Відновлення міток часу
        struct timespec times[2]{};
        times[0].tv_sec = stx.stx_atime.tv_sec;
        times[0].tv_nsec = stx.stx_atime.tv_nsec;
        times[1].tv_sec = stx.stx_mtime.tv_sec;
        times[1].tv_nsec = stx.stx_mtime.tv_nsec;

        ::utimensat(AT_FDCWD, dst_path.c_str(), times, AT_SYMLINK_NOFOLLOW);
    }
};
```
:::

## Діагностика та трасування системних викликів через `strace`

Перевірити коректність виконання послідовності викликів на практиці можна за допомогою утиліти `strace`:

```sh
strace -e trace=statx,openat,copy_file_range,lseek,llistxattr,lgetxattr,lsetxattr,fchownat,fchmodat,utimensat ./cloner src.txt dst.txt
```

У виводі `strace` чітко видно кожну фазу операції:
1. `statx(AT_FDCWD, "src.txt", AT_SYMLINK_NOFOLLOW, ...)` повертає повну структуру інода;
2. `openat(AT_FDCWD, "dst.txt", O_WRONLY|O_CREAT|O_TRUNC, 0600)` створює файл із безпечними правами;
3. `copy_file_range(...) = 1048576` миттєво шарить CoW-блоки або повертає помилку `EXDEV`;
4. `lsetxattr("dst.txt", "security.selinux", ...)` записує контексти безпеки;
5. `fchownat(AT_FDCWD, "dst.txt", 1000, 1000, AT_SYMLINK_NOFOLLOW)` змінює власника;
6. `fchmodat(AT_FDCWD, "dst.txt", 0644)` відновлює режим доступу;
7. `utimensat(AT_FDCWD, "dst.txt", [{...}, {...}], AT_SYMLINK_NOFOLLOW)` фіксує точний час.

Такий аналіз дозволяє переконатися, що жодна інша операція ядра не спотворює кінцевий стан створеного об'єкта VFS.
