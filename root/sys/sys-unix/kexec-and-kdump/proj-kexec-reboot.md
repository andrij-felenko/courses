# ⚙️ Завантажувач kexec мовами C та C++: використання sys_kexec_file_load

Цей практичний проєкт демонструє створення повноцінної системної утиліти мовами C та C++, яка використовує сучасний системний виклик `kexec_file_load()` для підготовки та завантаження нового ядра Linux безпосередньо з файлів на диску, із обробкою файлових дескрипторів, налаштуванням командного рядка та забезпеченням безпечного закриття ресурсів (RAII). Додатково розглядається розгортання аварійного сервісу `kdump`, фільтрація дампу утилітою `makedumpfile`, відлагодження утилітою `crash`, тестування у QEMU, трасування `strace`, архтектурні особливості ARM64, інваріанти безпеки та обробка крайових випадків.

---

## 1. Архітектура системної утиліти kexec-loader

Для реалізації власної утиліти гарячого завантаження ядра Linux через системний виклик `kexec_file_load()` необхідно правильно підготувати ресурсне оточення програми у просторі користувача. Основна відмінність `kexec_file_load` від класичного виклику `kexec_load` полягає в тому, що програма більше не повинна зчитувати та розпаковувати файл ядра чи створювати асоційовані ассемблерні заглушки релокації (purgatory). За замість цього утиліта працює як координатор файлових дескрипторів.

Послідовність системних дій утиліти складається з таких кроків:

1. **Перевірка привілеїв доступу**: Запуск утиліти вимагає наявності привілеїв суперкористувача (root) або наявності системного мандата `CAP_SYS_BOOT`. Без цього мандата ядро негайно відхиляє системний виклик із помилкою `EPERM` (Permission denied).
2. **Відкриття образу ядра (`vmlinuz`)**: Програма відкриває підписаний файл ядра за допомогою системного виклику `open()` у режимі `O_RDONLY`. Прапорець `O_CLOEXEC` гарантує, що дескриптор не протече у дочірні процеси у разі виконання системного виклику `execve`.
3. **Відкриття початкового образу `initramfs`**: Якщо для запуску системи необхідний тимчасовий корінь пам'яті, програма відкриває файл `initrd.img`. Якщо система завантажується без initramfs, у системний виклик передається значення `-1`.
4. **Формування рядка командного рядка**: Програма готує буфер із параметрами завантаження ядра (наприклад, `"root=UUID=... console=ttyS0 quiet"`) та розраховує його довжину з урахуванням термінуючого нуля `\0`.
5. **Виконання системного виклику `kexec_file_load()`**: Виклик здійснюється через загальну обгортку `syscall()`, оскільки стандартна бібліотека `glibc` на багатьох дистрибутивах не надає прямої C-обгортки для `kexec_file_load`.
6. **Запуск перезавантаження**: Після успішного повернення з виклику ядро сигналізує про готовність образу. Програма може виконати виклик `reboot(LINUX_REBOOT_CMD_KEXEC)` для миттєвого перезапуску або завершити роботу, залишивши завантаження на системний менеджер `systemd`.

---

## 2. Внутрішня обробка системного виклику в ядрі

Коли програма викликає `kexec_file_load()`, підсистема ядра виконує наступну послідовність дій:

1. **`kimage_file_alloc_init()`**: Ядро створює внутрішню структуру `struct kimage` для збереження сегментів майбутнього завантаження.
2. **Перевірка виконуваного формату**: Драйвери завантажувачів ядерних форматів (наприклад, `kexec_bzImage64_probe`) оглядають перші байти відкритого файла `kernel_fd` і підтверджують відповідність специфікації `bzImage` або PE/COFF.
3. **Валідація підпису Secure Boot**: Ядро перевіряє цифровий підпис у сертифікатній таблиці PKCS7 за допомогою вбудованого системного рингу ключів. Якщо підпис недійсний або пошкоджений, виклик повертає помилку `EKEYREJECTED`.
4. **Формування сегментів пам'яті**: Ядро самостійно розпаковує заголовки, розраховує точки входу, створює сегменти пам'яті та вшиває ассемблерний стаб purgatory у безпечну контрольну сторінку.

---

## 3. Налаштування аварійного ядра kdump у Linux

Підсистема `kdump` використовує механізм `kexec` для завантаження другого (аварійного) ядра в разі критичного збою основного ядра (Kernel Panic). Це аварійне ядро працює в спеціально зарезервованій області RAM і експортує пам'ять померлої системи через файл `/proc/vmcore`.

### 3.1. Резервування пам'яті через параметр завантаження `crashkernel`

Щоб підсистема kdump мала куди завантажити аварійне ядро, первинне ядро має зарезервувати суцільну ділянку фізичної пам'яті під час старту ОС. Це робиться за допомогою параметра командного рядка GRUB у `/etc/default/grub`:

```text
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash crashkernel=512M"
```

Для систем із великим обсягом RAM застосовується синтаксис з діапазонами або високим відображенням:
- `crashkernel=256M@16M`: Виділяє 256 МБ пам'яті, починаючи суворо з фізичної адреси 16 МБ.
- `crashkernel=512M,high`: Виділяє 512 МБ у високій зоні пам'яті (вище 4 ГБ). Разом із цим ядро автоматично додає невеличку ділянку `crashkernel=128M,low` у низькій зоні для 32-бітних DMA-буферів старих контролерів.
- `crashkernel=auto`: Автоматичне розрахування обсягу пам'яті за правилами дистрибутива (зазвичай 128M до 512M залежно від обсягу RAM).

Після внесення змін необхідно оновити конфігурацію завантажувача (`update-grub` або `grub2-mkconfig -o /boot/grub2/grub.cfg`) та перезавантажити сервер.

---

### 3.2. Конфігурування сервісу kdump (`/etc/kdump.conf`)

Конфігураційний файл `/etc/kdump.conf` контролює поведінку initramfs аварійного ядра під час запису дампу:

```text
# Запис дампу на локальний розділ файлової системи
path /var/crash

# Або запис безпосередньо на блоковий пристрій за UUID
# ext4 UUID=a1b2c3d4-e5f6-7890-abcd-1234567890ab

# Або відправка дампу по мережі через NFS
# nfs storage.example.com:/srv/crash

# Утиліта стиснення та рівень фільтрації
core_collector makedumpfile -l --message-level 7 -d 31

# Поведінка після успішного збереження дампу
default reboot
```

---

### 3.3. Управління службам kdump через systemd

Після редагування конфігурації служба kdump керується через стандартні утиліти системного менеджера `systemd`:

```bash
# Включення та запуск служби kdump
sudo systemctl enable --now kdump.service

# Перевірка стану завантаження аварійного ядра
sudo kdumpctl status
# Очікуваний вивід: Kexec-loaded Kernel is loaded

# Перезавантаження конфігурації та оновлення аварійного ядра у пам'яті
sudo kdumpctl reload
```

У разі виникнення помилок при ініціалізації слід перевірити журнал `/var/log/kdump.log`, який містить деталі генерації initramfs та викликів `kexec_file_load`.

---

### 3.4. Вибір цільового сховища (Disk, NFS, SSH)

- **Локальна файлова система**: Найпростіший спосіб. Збереження виконується на змонтований ext4/xfs розділ `/var/crash`.
- **Мережевий NFS-сервер**: Використовується в безапаратних бездискових кластерах. Аварійне ядро підключає мережеву карту, ініціалізує спрощений мережевий стек та монтує каталог NFS.
- **SSH/SFTP**: Аварійне ядро запускає `makedumpfile`, який передає зашифрований потік через `ssh` на віддалений хост збірника дампів.

---

## 4. Обробка та фільтрація дампу пам'яті через `makedumpfile`

Стандартний вміст `/proc/vmcore` може досягати сотень гігабайтів (дорівнює повному обсягу RAM). Спроба записати такий дамп на диск займає забагато часу і потребує величезного місця. Утиліта `makedumpfile` оптимізує цей процес шляхом фільтрації та стиснення.

### 4.1. Маска рівнів фільтрації (`dump_level`)

Прапорець `-d <dump_level>` утиліти `makedumpfile` визначає, які типи сторінок пам'яті слід виключити із підсумкового дамп-файлу. Маска створюється шляхом побітового додавання прапорців:

| Біт | Значення | Категорія сторінок пам'яті для виключення |
| :---: | :---: | :--- |
| `1` | `1` | **Zero pages**: Сторінки пам'яті, заповнені виключно нулями. |
| `2` | `2` | **Cache pages**: Сторінки файлового кешу (page cache ядра). |
| `4` | `4` | **Cache private pages**: Приватні кешовані сторінки процесів. |
| `8` | `8` | **User process data pages**: Сторінки анонімної пам'яті користувацьких процесів. |
| `16` | `16` | **Free pages**: Вільні сторінки у розпоряднику пам'яті ядра (Buddy Allocator). |

На практиці найпопулярнішим рівнем є **`-d 31`** (`1 + 2 + 4 + 8 + 16 = 31`). Цей рівень залишає у дампі лише власний код та структури даних ядра Linux, виключаючи всю пам'ять процесів користувача та вільні сторінки. Це зменшує розмір дампу з 512 ГБ RAM до 1–3 ГБ.

---

### 4.2. Прапорці оптимізації продуктивності `makedumpfile`

- **`--cyclic`**: Використовує циклічний буфер для аналізу пам'яті частинами. Це дозволяє фільтрувати багатотерабайтові дампи навіть у середовищі аварійного ядра з мінімально зарезервованою пам'яттю (наприклад, 256 МБ `crashkernel`).
- **`--split`**: Розбиває вихідний дамп на кілька файлів заданого розміру (наприклад, для запису на декілька носіїв або завантаження по частинах).
- **`-c` (zlib)** / **`-l` (lzo)** / **`-z` (zstd)**: Алгоритми стиснення даних. LZO забезпечує найвищу швидкість, а zstd — краще стиснення при низькому навантаженні на CPU.

Команда запуску:
```bash
makedumpfile --cyclic -l -d 31 /proc/vmcore /var/crash/127.0.0.1-2026-08-14/vmcore
```

---

### 4.3. Відлагодження дампу пам'яті за допомогою утиліти `crash`

Після того, як `makedumpfile` зберіг стиснений файл `/var/crash/.../vmcore`, інженер виконує його аналіз за допомогою інтерактивного відлагоджувача `crash`. Для аналізу потрібен сам дамп та збігається образ `vmlinux` із символами відлагодження (debuginfo):

```bash
# Запуск утиліти crash
sudo crash /usr/lib/debug/lib/modules/$(uname -r)/vmlinux /var/crash/127.0.0.1-2026-08-14/vmcore
```

#### Ключові команди утиліти `crash`:
- **`bt` (backtrace)**: Виводить стек викликів функцій ядра для процесу, що спричинив Kernel Panic.
- **`ps`**: Відображає стан усіх процесів у момент аварії (R, S, D, Z).
- **`log`**: Витягує кільцевий буфер повідомлень ядра (`dmesg`), дозволяючи побачити первинне повідомлення про помилку `kernel BUG at...` або `Null pointer dereference`.
- **`dis <function>`**: Виконує дизасемблювання конкретної ядерної функції з вказівкою зсуву панічного інструкту.

---

## 5. Простеження системних викликів утилітою strace

Для перевірки дій програми `kexec-loader` на рівні операційної системи використовується інструмент `strace`:

```bash
sudo strace -e trace=openat,syscall,reboot ./kexec_runner /boot/vmlinuz-$(uname -r) /boot/initrd.img-$(uname -r) "root=LABEL=rootfs console=ttyS0"
```

### Типовий журнал системних викликів `strace`:

```text
openat(AT_FDCWD, "/boot/vmlinuz-6.8.0-generic", O_RDONLY|O_CLOEXEC) = 3
openat(AT_FDCWD, "/boot/initrd.img-6.8.0-generic", O_RDONLY|O_CLOEXEC) = 4
syscall_0x140(0x3, 0x4, 0x21, "root=LABEL=rootfs console=ttyS0\0", 0) = 0
close(4)                                = 0
close(3)                                = 0
write(1, "Ядро успішно підготовлено до з"..., 45) = 45
```

Рядок `syscall_0x140` відповідає системному виклику номер 320 (`0x140` у шістнадцятковій системі для x86_64), що є `SYS_kexec_file_load`. Передані файлові дескриптори `3` та `4` успішно оброблені ядром і закриті через RAII-контейнер `UniqueFd` у C++ або блок `goto cleanup` у C.

---

## 6. Симуляція та тестування kdump у середовищі QEMU / KVM

Для перевірки коректності конфігурації kdump без ризику для реального сервера розгортається віртуальна машина QEMU.

### 6.1. Параметри запуску віртуальної машини QEMU

```bash
qemu-system-x86_64 \
  -m 4G \
  -smp 2 \
  -enable-kvm \
  -kernel /boot/vmlinuz-$(uname -r) \
  -initrd /boot/initrd.img-$(uname -r) \
  -append "root=/dev/sda1 console=ttyS0 crashkernel=512M" \
  -drive file=ubuntu-guest.qcow2,format=qcow2 \
  -nographic
```

---

### 6.2. Штучне викликування паніки ядра (SysRq Panic)

Після завантаження віртуальної системи та активації служби `kdump` випробовується панічний перехід через механізм `sysrq-trigger`:

```bash
# Дозволити виконання всіх системних команд SysRq
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward /proc/sys/kernel/sysrq

# Примусово викликати Kernel Panic (Null Pointer Dereference у ядрі)
echo c | sudo tee /proc/sysrq-trigger
```

#### Спостереження за процесом завантаження:
1. Поточне ядро реєструє паніку і припиняє виконання стандартних процесів.
2. Процесор миттєво переходить на точку входу purgatory у зарезервованій зоні `crashkernel`.
3. Консоль віртуальної машини виводить рядок завантаження аварійного ядра: `Loading crashkernel...`.
4. Скрипти аварійного initramfs запускають `makedumpfile`, записують файл `/var/crash/127.0.0.1-2026-08-14-*/vmcore` та виконують апаратний `reboot`.

---

## 7. Архітектурні особливості ARM64 (AArch64)

На архітектурі ARM64 підготовка аварійного ядра має свої особливості порівняно з x86_64:

- **Передача Device Tree Blob (DTB)**: Замість сегмента `zero_page` у регістрі `x0` передається фізична адреса структури Device Tree.
- **Вузол `/reserved-memory`**: Аварійне ядро маркує зарезервований регіон `crashkernel` як `no-map` у файлі Device Tree первинного ядра, що забороняє основній системі створювати специфічні мапінги сторінок.
- **Подвійний рівень трансляції (Stage 2 Page Tables)**: Якщо система працює під управлінням гіпервізора (KVM або Xen), пам'ять `crashkernel` має бути зарезервована та зафіксована у гіпервізорі для запобігання перехопленню сторінок іншими віртуальними машинами.

---

## 8. Автоматизація оновлення ядер у CI/CD за допомогою kexec

У сучасних дата-центрах `kexec` використовується для безперервного розгортання та тестування нових ядер у хмарних вузлах:

```bash
#!/usr/bin/env bash
set -euo pipefail

NEW_KERNEL="/boot/vmlinuz-6.10.0-rc1"
NEW_INITRD="/boot/initrd.img-6.10.0-rc1"
CMDLINE="root=UUID=f47a-4281-b661 console=ttyS0,115200 quiet"

echo "Завантаження нового ядра $NEW_KERNEL у пам'ять..."
./kexec_runner "$NEW_KERNEL" "$NEW_INITRD" "$CMDLINE"

echo "Ядро підготовлено. Запуск гарячого перезавантаження без POST..."
sudo systemctl kexec
```

Виклики `systemctl kexec` зв'язуються із системним менеджер `systemd`, який ізольовано закриває користувацькі служби, відмонтовує файлові системи та виконує виклик `reboot(LINUX_REBOOT_CMD_KEXEC)` без повторної ініціалізації апаратури BIOS.

### 8.1. Збереження логів журналювання між завантаженнями `systemd-journald`

Оскільки при гарячому перезавантаженні через `kexec` оперативна пам'ять очищується, за замовчуванням `systemd-journald` у режимі `Storage=volatile` втрачає останні байти журналів. Для збереження логів до моменту виклику `kexec` у конфігурації `/etc/systemd/journald.conf` встановлюється:

```text
[Journal]
Storage=persistent
SyncIntervalSec=1s
```

Це гарантує, що всі події підготовки ядра та закриття системних служб зберігаються на дисковому носії `/var/log/journal/` перш ніж `systemd` викличе `reboot(LINUX_REBOOT_CMD_KEXEC)`.

---

## 9. Крайові випадки (Edge Cases) та інваріанти підсистеми kexec/kdump

Робота з гарячим завантаженням та обробкою аварій вимагає суворого дотримання інваріантів та врахування апаратних обмежень.

### 9.1. Інваріанти безпеки панічного переходу

1. **Ізоляція пам'яті аварійного ядра**: Аварійне ядро kdump функціонує суворо в межах зарезервованого регіону `crashkernel`. Спроба аварійного ядра виділити сторінку за межами цього регіону вважається критичною помилкою.
2. **Однопоточна ініціалізація**: Аварійне ядро запускається з параметром `nr_cpus=1`. Всі інші процесорні ядра зупиняються викликом NMI-переривання (`crash_kexec_stop_cpus`).
3. **Заборона модифікації померлої пам'яті**: Пам'ять первинного ядра вважається доступною виключно у режимі читання (`read-only`).

---

### 9.2. Проблема повторної паніки (Double Panic)

Якщо паніка виникає всередині самого аварійного ядра (наприклад, через відсутність драйвера диска в initramfs kdump), виникає стан **Double Panic**.
Для запобігання вічному зацикленню в командний рядок аварійного ядра обов'язково додається параметр `panic=10`. Це вказує ядру виконати апаратне перезавантаження через BIOS/UEFI після 10 секунд очікування при виникненні повторної паніки.

---

### 9.3. Скидання периферійних пристроїв та апаратний DMA-захист (IOMMU)

Під час Kernel Panic периферійні контролери (NVMe, SAS HBA, Ethernet) можуть залишатися в стані активного виконання шинних транзакцій DMA. Якщо контролер продовжить писати в оперативну пам'ять за старими фізичними адресами, він пошкодить пам'ять аварійного ядра.

Для запобігання цьому застосовуються такі заходи:
- Параметр **`reset_devices`** у командному рядку аварійного ядра: вимагає від кожного драйвера примусово скинути контроллер (`pci_reset_function`) при завантаженні.
- Апаратне блокування **IOMMU** (`intel_iommu=on` або `amd_iommu=on`): IOMMU миттєво відключає всі таблиці трансляції DMA для пристроїв при вході в purgatory.

---

### 9.4. Брак пам'яті аварійного ядра та помилки ініціалізації

Якщо розмір зарезервованої зони `crashkernel` занадто малий (наприклад, 128 МБ при великій кількості PCIe пристроїв), аварійне ядро завершиться помилкою **Out Of Memory (OOM)** під час завантаження initramfs. Симптомом цього є раптовий перезапуск сервера без створення файлу `vmcore`. Вирішенням є збільшення розміру до `crashkernel=512M` або `crashkernel=1G`.

---

## 10. Практична реалізація системної утиліти мовами C та C++

Нижче наведено повний вихідний код утиліти `kexec-loader` для завантаження ядра Linux через `kexec_file_load`, перевірки стану та виконання гарячого перезавантаження.

:::tabs
@tab C
```c
/* kexec_runner.c — Реалізація мовою C з обробкою помилок goto cleanup */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/syscall.h>
#include <sys/reboot.h>
#include <linux/kexec.h>

#ifndef SYS_kexec_file_load
#if defined(__x86_64__)
#define SYS_kexec_file_load 320
#elif defined(__aarch64__)
#define SYS_kexec_file_load 294
#endif
#endif

int is_kexec_already_loaded(void) {
    int fd = open("/sys/kernel/kexec_loaded", O_RDONLY | O_CLOEXEC);
    if (fd < 0) return 0;
    
    char buf[4] = {0};
    ssize_t ret = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    
    return (ret > 0 && buf[0] == '1');
}

int load_new_kernel(const char *kernel_path, const char *initrd_path, const char *cmdline, unsigned long flags) {
    int kernel_fd = -1;
    int initrd_fd = -1;
    int result = -1;

    kernel_fd = open(kernel_path, O_RDONLY | O_CLOEXEC);
    if (kernel_fd < 0) {
        fprintf(stderr, "Помилка відкриття ядра '%s': %s\n", kernel_path, strerror(errno));
        goto cleanup;
    }

    if (initrd_path != NULL && strlen(initrd_path) > 0) {
        initrd_fd = open(initrd_path, O_RDONLY | O_CLOEXEC);
        if (initrd_fd < 0) {
            fprintf(stderr, "Помилка відкриття initramfs '%s': %s\n", initrd_path, strerror(errno));
            goto cleanup;
        }
    }

    size_t cmdline_len = cmdline ? strlen(cmdline) + 1 : 0;

    long ret = syscall(SYS_kexec_file_load, kernel_fd, initrd_fd, cmdline_len, cmdline, flags);
    if (ret != 0) {
        fprintf(stderr, "Системний виклик kexec_file_load завершився з помилкою %ld: %s\n", ret, strerror(errno));
        goto cleanup;
    }

    printf("Ядро успішно підготовлено до запуску через kexec!\n");
    result = 0;

cleanup:
    if (initrd_fd >= 0) close(initrd_fd);
    if (kernel_fd >= 0) close(kernel_fd);
    return result;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Використання: %s <path_to_vmlinuz> [path_to_initrd] [cmdline]\n", argv[0]);
        return 1;
    }

    if (is_kexec_already_loaded()) {
        printf("Увага: У пам'яті вже підготовлено ядро для kexec.\n");
    }

    const char *kernel_path = argv[1];
    const char *initrd_path = (argc > 2 && strlen(argv[2]) > 0) ? argv[2] : NULL;
    const char *cmdline = (argc > 3) ? argv[3] : "console=tty0 quiet";

    if (load_new_kernel(kernel_path, initrd_path, cmdline, 0) == 0) {
        printf("Для виклику гарячого перезавантаження виконайте: reboot -f\n");
    }

    return 0;
}
```

@tab C++
```cpp
// kexec_runner.cpp — Ідіоматична реалізація мовою C++20 (RAII, std::expected, std::string_view)
#include <iostream>
#include <fstream>
#include <string_view>
#include <system_error>
#include <expected>
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/reboot.h>
#include <linux/kexec.h>

#ifndef SYS_kexec_file_load
#if defined(__x86_64__)
#define SYS_kexec_file_load 320
#elif defined(__aarch64__)
#define SYS_kexec_file_load 294
#endif
#endif

namespace sys {

// RAII обгортка для автоматичного управління файловими дескрипторами
class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_{-1};
};

} // namespace sys

class KexecLoader {
public:
    static bool is_kexec_loaded() noexcept {
        std::ifstream status_file("/sys/kernel/kexec_loaded");
        int value = 0;
        return (status_file >> value) && (value == 1);
    }

    static std::expected<void, std::error_code> load_kernel(
        std::string_view kernel_path,
        std::string_view initrd_path,
        std::string_view cmdline,
        unsigned long flags = 0) noexcept
    {
        sys::UniqueFd kernel_fd(::open(kernel_path.data(), O_RDONLY | O_CLOEXEC));
        if (!kernel_fd.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        sys::UniqueFd initrd_fd;
        if (!initrd_path.empty()) {
            initrd_fd.reset(::open(initrd_path.data(), O_RDONLY | O_CLOEXEC));
            if (!initrd_fd.valid()) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
        }

        const int raw_initrd_fd = initrd_fd.valid() ? initrd_fd.get() : -1;
        const size_t cmdline_len = cmdline.empty() ? 0 : cmdline.size() + 1;
        const char* cmdline_ptr = cmdline.empty() ? nullptr : cmdline.data();

        long ret = ::syscall(SYS_kexec_file_load, kernel_fd.get(), raw_initrd_fd, cmdline_len, cmdline_ptr, flags);
        if (ret != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return {};
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "Використання: " << argv[0] << " <path_to_vmlinuz> [path_to_initrd] [cmdline]\n";
        return 1;
    }

    if (KexecLoader::is_kexec_loaded()) {
        std::cout << "Увага: У системі вже завантажено ядро через kexec.\n";
    }

    const std::string_view kernel_path = argv[1];
    const std::string_view initrd_path = (argc > 2) ? argv[2] : "";
    const std::string_view cmdline = (argc > 3) ? argv[3] : "console=tty0 quiet";

    auto result = KexecLoader::load_kernel(kernel_path, initrd_path, cmdline);
    if (!result) {
        std::cerr << "Помилка завантаження ядра через kexec: " << result.error().message() << '\n';
        return 1;
    }

    std::cout << "Ядро успішно завантажено в пам'ять! Ресурси закриті автоматично RAII.\n";
    std::cout << "Для активації нового ядра виконайте системний виклик reboot.\n";
    return 0;
}
```
:::

---

## 11. Докладний порівняльний аналіз реалізацій (C vs C++20)

1. **Гарантія звільнення файлових дескрипторів**:
   - У C-версії для запобігання витоку відкритих дескрипторів при виникненні помилок застосовано класичну конструкцію з міткою `goto cleanup`. Якщо системний виклик звертається з помилкою на етапі відкриття `initrd`, функція зобов'язана явно перевірити `kernel_fd` і викликати `close()`.
   - У C++ реалізації клас `sys::UniqueFd` реалізує концепцію **RAII** (Resource Acquisition Is Initialization). Усі відкриті дескриптори гарантовано закриваються під час руйнування стекового об'єкта в момент виходу з функції `load_kernel()`. Це робить код стійким до передчасних повернень (`return`) та унеможливлює витоки системних ресурсів.

2. **Безбезпечна обробка системних помилок**:
   - Версія мовою C повертає стандартне цілочисельне значення `-1` та покладається на глобальну змінну `errno`.
   - C++ версія застосовує стандартний тип C++20 `std::expected<void, std::error_code>`. Можливість помилки виражається у самому типі поверненого значення. Це змушує клієнтський код у функції `main` явно перевірити стан об'єкта `result` перед зверненням до результату, запобігаючи неперехопленим виняткам завдяки специфікатору `noexcept`.

3. **Робота з рядками та пам'яттю**:
   - У C++ реалізації застосування `std::string_view` дає змогу передавати параметри завантаження без копіювання рядків у динамічній пам'яті (`heap`), уникаючи сирих вказівників `char*` та гарантуючи відсутність витоків пам'яті при форматуванні командного рядка ядра.

4. **Обробка крайових кодувань помилок**:
   - `EKEYREJECTED`: Цифровий підпис ядра не збігається з ключами у системному рингу Secure Boot.
   - `EBADF`: Передано недійсний або закритий файловий дескриптор.
   - `ENOEXEC`: Файл за вказаним дескриптором не є коректним виконаним образом ядра (`bzImage`).
   - `ENOMEM`: Недостатньо оперативної пам'яті у зарезервованій зоні `crashkernel` для завантаження образу.
   - `EACCES`: Активовано режим `kernel lockdown`, що блокує непідписані виклики kexec.

5. **Архітектурне масштабування та збірка під різноманітні платформи**:
   - Обгортка `KexecLoader` є платформонезалежною завдяки абстрагуванню номером системного виклику у препроцесорному блоці `#ifndef SYS_kexec_file_load` для архітектур x86_64 (`320`), ARM64 (`294`), RISC-V (`294`) та PowerPC64 (`382`). Це робить C++ код портованим для крос-компіляції у вбудовані Linux-системи.
