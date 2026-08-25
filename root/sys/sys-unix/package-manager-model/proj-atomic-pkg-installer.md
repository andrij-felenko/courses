# ⚙️ Реалізація транзакційного інсталятора пакунків

Цей практичний приклад демонструє алгоритм атомарного встановлення бінарного файла пакунка із застосуванням журналювання, тимчасових файлів, виклику `fsync()` та атомарного виклику `rename()`.

## 1. Концепція та етапи безпечного запису

Головна вимога до будь-якого пакетного менеджера при інсталяції бінарних файлів на файлову систему — це **забезпечення суворої атомарності транзакції**. Якщо під час розпакування корисного навантаження пакунка розміром у кілька сотень мегабайт станеться раптовий збій живлення, аварійна зупинка ядра (Kernel Panic) або вичерпання дискового простору, на диску ні в якому разі не повинен залишитися наполовину записаний або пошкоджений бінарний файл.

Якщо розробник пакетного менеджера використав би прямий перезапис існуючого файла через системний виклик `open(O_WRONLY | O_TRUNC)`, це створило б дві фундаментальні загрози цілісності системи:

Перша загроза полягає у виникненні часового вікна незахищеності. У момент виклику `open()` із прапорцем `O_TRUNC` ядро Linux негайно обнуляє довжину існуючого інода. Якщо процес буде вбито до завершення повного циклу викликів `write()`, файл на диску залишиться з нульовим або частковим розміром. Усі інші програми в системі, які спробують виконати цей бінарний файл у цей момент, зазнають аварійного завершення із помилкою сегментації (`Segmentation fault`) або викликом `Exec format error`.

Друга загроза пов'язана з виконанням файлів у пам'яті. Якщо програма, бінарник якої оновлюється, у цей момент вже запущена й виконується іншим процесом в операційній системі, ядро заблокує прямий запис у її інод і поверне системну помилку `ETXTBSY` (Text file busy).

Щоб повністю усунути ці загрози, сучасні пакетні менеджери реалізують п'ятикрокову транзакційну схему інсталяції:

1. **Захоплення системного блокування:** Процес створює спеціальний lock-файл та захоплює ексклюзивне блокування за допомогою системного виклику `flock(LOCK_EX)`, щоб унеможливити паралельний запуск другого екземпляра пакетного менеджера.
2. **Запис у тимчасовий файл в тому ж каталозі:** Новий виконуваний файл створюється під суфіксом `.dpkg-new` в тому самому каталозі файлової системи, де має перебувати цільовий файл.
3. **Примусовий скид сторінкового кешу на диск (`fsync`):** Після завершення викликів `write()` процес викликає `fsync()`, змушуючи ядро виштовхнути брудні сторінки з буферного кешу RAM безпосередньо на фізичний накопичувач.
4. **Атомарна заміна через `rename(2)`:** Виклик `rename()` здійснює неподільну зміну запису в каталозі VFS. Існуючий файл миттєво замінюється новим інодом.
5. **Очищення та журналювання:** Фіксація нового стану пакунка у базі даних і вилучення тимчасових інсталяційних файлів.

---

## 2. Код реалізації (C та C++)

Нижче наведено робочий приклад атомарного інсталятора пакунків.

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
#include <sys/file.h>

#define TEMP_SUFFIX ".dpkg-new"
#define LOCK_FILE "/tmp/pkg_installer.lock"
#define BUFFER_SIZE 4096

typedef struct {
    const char *target_path;
    const char *payload_data;
    size_t payload_len;
    mode_t permissions;
} package_file_t;

/* Захоплення глобального блокування інсталятора */
static int acquire_system_lock(void) {
    int lock_fd = open(LOCK_FILE, O_RDWR | O_CREAT, 0600);
    if (lock_fd < 0) {
        perror("[ERROR] Не вдалося відкрити lock-файл");
        return -1;
    }
    if (flock(lock_fd, LOCK_EX | LOCK_NB) < 0) {
        fprintf(stderr, "[ERROR] Інший процес пакетного менеджера вже виконується.\n");
        close(lock_fd);
        return -1;
    }
    return lock_fd;
}

/* Звільнення блокування */
static void release_system_lock(int lock_fd) {
    if (lock_fd >= 0) {
        flock(lock_fd, LOCK_UN);
        close(lock_fd);
        unlink(LOCK_FILE);
    }
}

/* Виконує атомарну інсталяцію одного файла пакунка */
int install_package_file_atomic(const package_file_t *file) {
    char temp_path[4096];
    int fd = -1;
    ssize_t bytes_written;
    int res = -1;

    /* Створення шляху до тимчасового файла у тому ж каталозі */
    snprintf(temp_path, sizeof(temp_path), "%s%s", file->target_path, TEMP_SUFFIX);

    /* 1. Відкриваємо тимчасовий файл для запису (O_CREAT | O_WRONLY | O_TRUNC | O_NOFOLLOW) */
    fd = open(temp_path, O_WRONLY | O_CREAT | O_TRUNC | O_NOFOLLOW, file->permissions);
    if (fd < 0) {
        fprintf(stderr, "[ERROR] Не вдалося створити тимчасовий файл %s: %s\n",
                temp_path, strerror(errno));
        return -1;
    }

    /* 2. Записуємо корисне навантаження (payload) */
    bytes_written = write(fd, file->payload_data, file->payload_len);
    if (bytes_written < 0 || (size_t)bytes_written != file->payload_len) {
        fprintf(stderr, "[ERROR] Збій запису payload у файл %s: %s\n",
                temp_path, strerror(errno));
        goto err_cleanup;
    }

    /* 3. Примусово скидаємо сторінковий кеш на фізичний диск */
    if (fsync(fd) < 0) {
        fprintf(stderr, "[ERROR] Збій fsync для файла %s: %s\n",
                temp_path, strerror(errno));
        goto err_cleanup;
    }

    /* Закриваємо файловий дескриптор перед rename */
    close(fd);
    fd = -1;

    /* 4. Атомарна заміна існуючого файла новим через rename(2) */
    if (rename(temp_path, file->target_path) < 0) {
        fprintf(stderr, "[ERROR] Не вдалося перейменувати %s у %s: %s\n",
                temp_path, file->target_path, strerror(errno));
        unlink(temp_path);
        return -1;
    }

    printf("[SUCCESS] Файл %s успішно інстальовано атомарно.\n", file->target_path);
    return 0;

err_cleanup:
    if (fd >= 0) {
        close(fd);
    }
    unlink(temp_path);
    return res;
}

int main(void) {
    int lock_fd = acquire_system_lock();
    if (lock_fd < 0) {
        return EXIT_FAILURE;
    }

    package_file_t pkg_bin = {
        .target_path = "/tmp/my_app_binary",
        .payload_data = "#!/bin/sh\necho 'Hello from atomic package!'\n",
        .payload_len = 46,
        .permissions = 0755
    };

    int status = install_package_file_atomic(&pkg_bin);

    release_system_lock(lock_fd);
    return status == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <system_error>
#include <cerrno>
#include <unistd.h>
#include <fcntl.h>
#include <sys/file.h>

namespace fs = std::filesystem;

class SystemLock {
    int lock_fd_{-1};
    fs::path lock_path_;
public:
    explicit SystemLock(fs::path lock_path) : lock_path_(std::move(lock_path)) {
        lock_fd_ = ::open(lock_path_.c_str(), O_RDWR | O_CREAT, 0600);
        if (lock_fd_ < 0 || ::flock(lock_fd_, LOCK_EX | LOCK_NB) < 0) {
            throw std::runtime_error("Не вдалося захопити системне блокування");
        }
    }

    ~SystemLock() {
        if (lock_fd_ >= 0) {
            ::flock(lock_fd_, LOCK_UN);
            ::close(lock_fd_);
            fs::remove(lock_path_);
        }
    }

    SystemLock(const SystemLock&) = delete;
    SystemLock& operator=(const SystemLock&) = delete;
};

class AtomicPackageInstaller {
public:
    static bool install_file(const fs::path& target_path, std::string_view payload, mode_t mode = 0755) {
        fs::path temp_path = target_path;
        temp_path += ".dpkg-new";

        // RAII відкриття та закриття файлового дескриптора
        int fd = ::open(temp_path.c_str(), O_WRONLY | O_CREAT | O_TRUNC | O_NOFOLLOW, mode);
        if (fd < 0) {
            std::cerr << "[ERROR] Помилка відкриття " << temp_path << ": "
                      << std::strerror(errno) << '\n';
            return false;
        }

        struct FdGuard {
            int handle;
            ~FdGuard() { if (handle >= 0) ::close(handle); }
        } fd_guard{fd};

        // Запис даних у файл
        ssize_t written = ::write(fd, payload.data(), payload.size());
        if (written < 0 || static_cast<size_t>(written) != payload.size()) {
            std::cerr << "[ERROR] Збій запису даних у " << temp_path << '\n';
            fs::remove(temp_path);
            return false;
        }

        // Примусовий скид дискових буферів (fsync)
        if (::fsync(fd) < 0) {
            std::cerr << "[ERROR] Помилка fsync для " << temp_path << '\n';
            fs::remove(temp_path);
            return false;
        }

        ::close(fd_guard.handle);
        fd_guard.handle = -1;

        // Атомарна заміна через std::filesystem::rename
        std::error_code ec;
        fs::rename(temp_path, target_path, ec);
        if (ec) {
            std::cerr << "[ERROR] Не вдалося замінити " << target_path 
                      << ": " << ec.message() << '\n';
            fs::remove(temp_path, ec);
            return false;
        }

        std::cout << "[SUCCESS] Успішно інстальовано " << target_path << '\n';
        return true;
    }
};

int main() {
    try {
        SystemLock lock("/tmp/pkg_installer_cpp.lock");

        fs::path target = "/tmp/my_app_binary_cpp";
        std::string_view payload = "#!/bin/sh\necho 'Hello from C++ Atomic Package!'\n";

        return AtomicPackageInstaller::install_file(target, payload) ? 0 : 1;
    } catch (const std::exception& e) {
        std::cerr << "[FATAL] " << e.what() << '\n';
        return 1;
    }
}
```
:::

---

## 3. Глибинний аналіз системних викликів та крайових випадків

### Чому системний виклик rename() є атомарним на рівні ядра Linux
Коли процес викликає `rename(oldpath, newpath)`, ядро Linux переходить у простір ядра і бере блокування VFS інода каталогу (`inode->i_rwsem`). Алгоритм операції в файлових системах `ext4` або `xfs` виконується у три послідовні кроки в межах однієї журнальної транзакції (JBD2):

1. У каталозі додається новий запис, який вказує на інод тимчасового файла `oldpath`.
2. Якщо за адресою `newpath` вже існував старий інод, лічильник посилань цього старого інода (`i_nlink`) зменшується на одиницю. Якщо лічильник посилань стає рівним нулю і жоден процес не утримує відкритий файловий дескриптор, блоковий простір старого інода позначається як вільний.
3. Старий запис `oldpath` вилучається з каталогу, і журнальна транзакція фіксується (commit).

Завдяки цьому для будь-якого стороннього процесу в системі не існує моменту часу, коли файл `newpath` був би відсутній або пошкоджений.

### Пастка помилки перетину точки монтування (EXDEV Cross-device link)
Системний виклик `rename(2)` вимагає, щоб вихідний тимчасовий файл і цільовий файл перебували в межах однієї файлової системи (одної точки монтування VFS). Якщо розробник спробує створити тимчасовий файл у каталозі `/tmp` (який у багатьох дистрибутивах змонтовано як оперативну пам'ять `tmpfs`), а цільовий файл розташований у `/usr/bin/` (змонтованому на `ext4`), виклик `rename()` поверне помилку `EXDEV` (Cross-device link).

Саме тому пакетний менеджер зобов'язаний формувати шлях тимчасового файла строго у тому самому каталозі, де розташований цільовий файл (`/usr/bin/binary.dpkg-new`).

### Захист від атак через символьні посилання (Symlink Attacks)
Якщо зловмисник завчасно створить у системному каталозі символьне посилання під ім'ям `binary.dpkg-new`, яке вказує на критичний файл (наприклад, `/etc/shadow`), відкриття файла без прапорця `O_NOFOLLOW` призведе до того, що пакетний менеджер з правами `root` перезапише вміст системного файлу паролів. Прапорець `O_NOFOLLOW` гарантує, що якщо за тимчасовим шляхом виявлено символьне посилання, виклик `open()` негайно поверне помилку `ELOOP` і скасує інсталяцію.

### Відновлення безпекових контекстів SELinux та AppArmor
При створенні тимчасового файла йому присвоюється маска прав Umask поточного процесу. Перед здійсненням атомарної заміни пакетний менеджер повинен відновити розширені атрибути (xattr) та безпековий контекст SELinux за допомогою системних функцій `setfscreatecon()` або `matchpathcon()`, щоб після перейменування новий виконуваний файл не був заблокований підсистемою мандатного контролю доступу (MAC).
