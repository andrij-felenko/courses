# ⚙️ Автоматизоване керування життєвим циклом VF та прив'язка до VFIO-PCI

Цей практичний розбір деталізує процес створення віртуальних функцій SR-IOV через системний інтерфейс sysfs ядра Linux, вимкнення автоматичної прив'язки хостових мережевих драйверів та передачу створених VF під контроль підсистеми `vfio-pci` для подальшого прокидання у віртуальні машини KVM/QEMU.

Для розробників системного програмного забезпечення наведені готові реалізації мовами C та C++.

## 1. Конвеєр управління життєвим циклом віртуальних функцій

Автоматизоване виділення та передавання віртуальних функцій у середовищах віртуалізації (наприклад, OpenStack, Proxmox або Kubernetes KubeVirt) складається з п'яти послідовних етапів:

1. **Вимкнення автоматичного завантаження хостового драйвера (Autoprobe Disable):**
   За замовчуванням підсистема PCI ядра Linux після створення кожної нової VF негайно шукає відповідний мережевий драйвер хоста (наприклад, `iavf` для карт Intel або `mlx5_core` для карт NVIDIA/Mellanox) і створює мережевий інтерфейс хоста (наприклад, `eth1`, `eth2`). Для віртуалізації це створює гонку ресурсів (Race Condition). Запис значення `0` у `/sys/bus/pci/devices/<PF_BDF>/sriov_drivers_autoprobe` наказує ядру створювати пристрої PCI, але не прив'язувати до них жодних мережевих драйверів.

2. **Ініціалізація та нарізка VF:**
   Запис бажаної кількості віртуальних функцій у sysfs-атрибут `/sys/bus/pci/devices/<PF_BDF>/sriov_numvfs`. Драйвер Physical Function зчитує конфігураційний простір SR-IOV Extended Capability, ініціалізує апаратні черги в кремнії та реєструє нові пристрої на шині PCI.

3. **Динамічна прив'язка до драйвера `vfio-pci`:**
   Кожна створена VF має власну адресу BDF (Bus:Device.Function), а також Vendor ID та Device ID (наприклад, `8086:154c`). Щоб передати пристрій у QEMU, його ID реєструється в псевдодрайвері `vfio-pci` через запис у `/sys/bus/pci/drivers/vfio-pci/new_id`, після чого виконується запис BDF у `/sys/bus/pci/drivers/vfio-pci/bind`.

4. **Визначення IOMMU-групи:**
   Ядро Linux виділяє кожній VF окремий ідентифікатор IOMMU-групи. Програма зчитує символьне посилання `/sys/bus/pci/devices/<VF_BDF>/iommu_group`, яке вказує на відповідний символьний пристрій `/dev/vfio/<group_id>`.

5. **Передавання у віртуальну машину:**
   Отриманий номер IOMMU-групи та BDF передаються аргументом у команду запуску гіпервізора QEMU/KVM (`-device vfio-pci,host=<VF_BDF>`).

---

## 2. Обробка помилок системних викликів sysfs

При взаємодії з псевдофайловою системою sysfs ядра Linux системні виклики `open()`, `write()` та `readlink()` звертаються не до фізичних файлів на диску, а до точок входу в коді драйвера ядра. Тому звичайні виклики запису можуть повертати специфічні коди помилок (збережені у змінній `errno`), які вимагають аналізу:

- **`-EBUSY` (Device or resource busy):**
  Повертається при спробі записати нове значення у `sriov_numvfs`, коли віртуальні функції вже активні (`numvfs > 0`), або коли хоча б одна з VF прокинута у працюючу ВМ чи утримується драйвером `vfio-pci`. Щоб змінити кількість VF, спочатку необхідно записати `0`.
- **`-EINVAL` (Invalid argument):**
  Виникає у разі спроби записати значення `sriov_numvfs`, яке перевищує апаратне обмеження `sriov_totalvfs`, або коли драйвер пристрою не підтримує запитану кількість VF.
- **`-ENODEV` (No such device):**
  Свідчить про те, що вказана PCI-адреса BDF не існує в системі або відповідний Physical Function не має підтримки розширеної спроможності SR-IOV Extended Capability.
- **`-EPERM` / `-EACCES` (Permission denied):**
  Виникає, якщо запуск здійснюється від імені звичайного користувача. Модифікація атрибутів SR-IOV вимагає прав суперкористувача `root` або наявності системної мандатної спроможності `CAP_SYS_ADMIN`.

---

## 3. Реалізація менеджера SR-IOV мовами C та C++

Наведені нижче приклади реалізують повний цикл конфігурації sysfs, обробку помилок системних викликів, перевірку наявності файлів та сканування IOMMU-груп.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <dirent.h>
#include <sys/stat.h>

/* Запис текстового значення у файл sysfs із обробкою помилок */
static int write_sysfs_str(const char *path, const char *val) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "[-] Помилка відкриття %s: %s\n", path, strerror(errno));
        return -1;
    }
    ssize_t len = strlen(val);
    ssize_t ret = write(fd, val, len);
    close(fd);
    if (ret != len) {
        fprintf(stderr, "[-] Помилка запису '%s' у %s: %s\n", val, path, strerror(errno));
        return -1;
    }
    return 0;
}

/* Перевірка наявності шляху у sysfs */
static int sysfs_exists(const char *path) {
    return access(path, F_OK) == 0;
}

/* Прив'язка окремої VF до драйвера vfio-pci */
static int bind_vf_to_vfio(const char *vf_bdf, const char *vendor_id, const char *device_id) {
    char path[512];
    char id_str[64];

    /* 1. Відв'язуємо VF від поточного драйвера хоста (якщо він був прив'язаний) */
    snprintf(path, sizeof(path), "/sys/bus/pci/devices/%s/driver/unbind", vf_bdf);
    if (sysfs_exists(path)) {
        write_sysfs_str(path, vf_bdf);
    }

    /* 2. Реєструємо ідентифікатори Vendor/Device в vfio-pci */
    snprintf(id_str, sizeof(id_str), "%s %s", vendor_id, device_id);
    write_sysfs_str("/sys/bus/pci/drivers/vfio-pci/new_id", id_str);

    /* 3. Прив'язуємо BDF до vfio-pci */
    snprintf(path, sizeof(path), "/sys/bus/pci/drivers/vfio-pci/bind");
    if (write_sysfs_str(path, vf_bdf) < 0) {
        if (errno != EBUSY) {
            return -1;
        }
    }
    return 0;
}

/* Прогляд створених VF та визначення їхніх IOMMU груп */
static void inspect_iommu_groups(const char *pf_bdf) {
    char dir_path[512];
    snprintf(dir_path, sizeof(dir_path), "/sys/bus/pci/devices/%s", pf_bdf);

    DIR *dir = opendir(dir_path);
    if (!dir) return;

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strncmp(entry->d_name, "virtfn", 6) == 0) {
            char link_path[512];
            char target_path[512];
            snprintf(link_path, sizeof(link_path), "%s/%s", dir_path, entry->d_name);

            ssize_t len = readlink(link_path, target_path, sizeof(target_path) - 1);
            if (len > 0) {
                target_path[len] = '\0';
                char *vf_bdf = strrchr(target_path, '/');
                if (vf_bdf) vf_bdf++; else vf_bdf = target_path;

                char iommu_link[512];
                char iommu_target[512];
                snprintf(iommu_link, sizeof(iommu_link), "%s/%s/iommu_group", dir_path, entry->d_name);

                ssize_t i_len = readlink(iommu_link, iommu_target, sizeof(iommu_target) - 1);
                if (i_len > 0) {
                    iommu_target[i_len] = '\0';
                    char *grp_num = strrchr(iommu_target, '/');
                    if (grp_num) grp_num++; else grp_num = iommu_target;
                    printf("  └─ VF [%s]: %s → IOMMU Group: %s (/dev/vfio/%s)\n", 
                           entry->d_name, vf_bdf, grp_num, grp_num);
                }
            }
        }
    }
    closedir(dir);
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Використання: %s <PF_BDF> <NUM_VFS>\n", argv[0]);
        printf("Приклад:     %s 0000:03:00.0 4\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *pf_bdf = argv[1];
    const char *num_vfs_str = argv[2];
    char path[512];

    printf("[+] Ініціалізація управління SR-IOV для PF: %s\n", pf_bdf);

    /* 1. Вимикаємо авто-прив'язку хостових драйверів для нових VF */
    snprintf(path, sizeof(path), "/sys/bus/pci/devices/%s/sriov_drivers_autoprobe", pf_bdf);
    if (write_sysfs_str(path, "0") < 0) {
        fprintf(stderr, "[!] Попередження: Не вдалося встановити sriov_drivers_autoprobe\n");
    }

    /* 2. Скидаємо існуючі VF до 0 */
    snprintf(path, sizeof(path), "/sys/bus/pci/devices/%s/sriov_numvfs", pf_bdf);
    write_sysfs_str(path, "0");

    /* 3. Задаємо нову кількість VF */
    if (write_sysfs_str(path, num_vfs_str) < 0) {
        fprintf(stderr, "[-] Фатальна помилка виділення %s VF для пристрою %s\n", num_vfs_str, pf_bdf);
        return EXIT_FAILURE;
    }

    printf("[+] Успішно створено %s VF для пристрою %s\n", num_vfs_str, pf_bdf);
    
    /* 4. Інспектуємо виділені IOMMU групи */
    inspect_iommu_groups(pf_bdf);

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>
#include <system_error>
#include <format>

namespace fs = std::filesystem;

class SriovManager {
public:
    explicit SriovManager(std::string_view pf_bdf)
        : pf_path_(fs::path("/sys/bus/pci/devices") / pf_bdf) {
        if (!fs::exists(pf_path_)) {
            throw std::invalid_argument(
                std::format("PCI пристрій {} не знайдено у sysfs", pf_bdf)
            );
        }
    }

    // RAII-безпечний запис у файли sysfs
    void write_sysfs(const fs::path& rel_path, std::string_view value) const {
        fs::path full_path = pf_path_ / rel_path;
        std::ofstream ofs(full_path);
        if (!ofs.is_open()) {
            throw std::system_error(
                make_error_code(std::errc::no_such_file_or_directory),
                std::format("Не вдалося відкрити sysfs файл: {}", full_path.string())
            );
        }
        ofs << value;
        if (!ofs.good()) {
            throw std::system_error(
                make_error_code(std::errc::io_error),
                std::format("Помилка запису '{}' у {}", value, full_path.string())
            );
        }
    }

    void configure_vfs(size_t num_vfs) const {
        std::cout << std::format("[+] Конфігурація {} VF для PF: {}\n", num_vfs, pf_path_.filename().string());

        // 1. Вимикаємо autoprobe хоста, щоб нові VF не захоплювалися мережевим стеком
        try {
            write_sysfs("sriov_drivers_autoprobe", "0");
        } catch (const std::exception& e) {
            std::cerr << std::format("[!] Попередження: {}\n", e.what());
        }

        // 2. Скидаємо поточний стан VF
        write_sysfs("sriov_numvfs", "0");

        // 3. Записуємо бажану кількість віртуальних функцій
        write_sysfs("sriov_numvfs", std::to_string(num_vfs));

        std::cout << std::format("[+] Успішно згенеровано {} VF у системі.\n", num_vfs);
    }

    void inspect_vf_iommu_groups() const {
        for (const auto& entry : fs::directory_iterator(pf_path_)) {
            std::string filename = entry.path().filename().string();
            if (filename.starts_with("virtfn")) {
                fs::path vf_target = fs::read_symlink(entry.path());
                fs::path vf_bdf = vf_target.filename();
                fs::path iommu_group_path = pf_path_ / entry.path() / "iommu_group";

                if (fs::exists(iommu_group_path)) {
                    fs::path group_target = fs::read_symlink(iommu_group_path);
                    std::cout << std::format("  └─ VF [{}] ({}) → IOMMU Group: {} (/dev/vfio/{})\n", 
                                             filename, vf_bdf.string(), 
                                             group_target.filename().string(),
                                             group_target.filename().string());
                }
            }
        }
    }

private:
    fs::path pf_path_;
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << std::format("Використання: {} <PF_BDF> <NUM_VFS>\n", argv[0]);
        return EXIT_FAILURE;
    }

    try {
        std::string_view pf_bdf = argv[1];
        size_t num_vfs = std::stoul(argv[2]);

        SriovManager manager(pf_bdf);
        manager.configure_vfs(num_vfs);
        manager.inspect_vf_iommu_groups();

    } catch (const std::exception& ex) {
        std::cerr << std::format("[-] Фатальна помилка: {}\n", ex.what());
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 4. Детальний аналіз роботи програми та розбір консольного виводу

Після виконання компіляції та запуску програми з правами суперкористувача `root`, утиліта створює віртуальні функції та проводить діагностику IOMMU-структури системи:

```text
[+] Конфігурація 4 VF для PF: 0000:03:00.0
[+] Успішно згенеровано 4 VF у системі.
  └─ VF [virtfn0] (0000:03:02.0) → IOMMU Group: 24 (/dev/vfio/24)
  └─ VF [virtfn1] (0000:03:02.1) → IOMMU Group: 25 (/dev/vfio/25)
  └─ VF [virtfn2] (0000:03:02.2) → IOMMU Group: 26 (/dev/vfio/26)
  └─ VF [virtfn3] (0000:03:02.3) → IOMMU Group: 27 (/dev/vfio/27)
```

### Особливості реалізації мовою C:
- Функція `write_sysfs_str()` використовує низькорівневий системний виклик `open()` з прапором `O_WRONLY`. Використання виклику `write()` гарантує атомарну передачу текстового рядка безпосередньо у буфер драйвера ядра.
- Для обходу символьних посилань `virtfn0`..`virtfnN` використовується системний виклик `readlink()`, який зчитує відносний шлях цільового PCI-пристрою у sysfs без копіювання файлових даних.

### Особливості реалізації мовою C++:
- Клас `SriovManager` використовує стандартну бібліотеку `std::filesystem` (C++17) для маніпуляції шляхами sysfs.
- Методи обробки файлових потоків `std::ofstream` загорнуті в механізм винятків `std::system_error` з відстеженням системних кодів `std::errc`.
- Форматування текстових рядків та шляхів здійснюється за допомогою `std::format` (C++20), що усуває можливість буферних переповнень, характерних для `snprintf`.

### Важливі діагностичні висновки:

1. **Кожна VF в окремій IOMMU-групі:**
   У виводі вище пристрої `0000:03:02.0`, `0000:03:02.1`, `0000:03:02.2` та `0000:03:02.3` отримали унікальні номери груп `24`, `25`, `26` та `27`. Це означає, що материнська плата хоста та чипсет підтримують специфікацію PCIe Access Control Services (ACS), і кожна VF може бути ізольовано прокинута в окремі віртуальні машини без ризику витоку даних.

2. **Захист від конфліктів з NetworkManager:**
   Завдяки вимкненню `sriov_drivers_autoprobe` мережевий стек хоста не створює мережеві інтерфейси (типу `eth1`), і системні служби автоматичної конфігурації мережі (NetworkManager або `systemd-networkd`) не втручаються в роботу віртуальних функцій.

3. **Запуск віртуальної машини QEMU:**
   Отриманий символьний файл пристрою `/dev/vfio/24` передається гіпервізору:

   ```bash
   qemu-system-x86_64 -enable-kvm -m 4G \
       -drive file=disk.qcow2,if=virtio \
       -device vfio-pci,host=03:02.0,id=net0
   ```
