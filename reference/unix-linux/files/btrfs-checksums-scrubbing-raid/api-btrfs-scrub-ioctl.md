# 🔌 Довідник ioctl підсистеми Btrfs Scrub

Цей довідник описує системні виклики `ioctl` для програмного керування та моніторингу фонового сканування цілісності дискового масиву (Scrubbing) у Btrfs.

Оголошення структур та констант містяться у заголовочному файлі `<linux/btrfs.h>`.

## Системні виклики ioctl

| Команда ioctl | Структура аргументу | Опис |
| :--- | :--- | :--- |
| `BTRFS_IOC_SCRUB` | `struct btrfs_ioctl_scrub_args` | Запускає фоновий процес перевірки та відновлення цілісності блоків. |
| `BTRFS_IOC_SCRUB_CANCEL` | `struct btrfs_ioctl_scrub_args` | Зупиняє активний процес scrub. |
| `BTRFS_IOC_SCRUB_PROGRESS` | `struct btrfs_ioctl_scrub_args` | Запитує поточний прогрес та лічильники помилок. |

## Структура аргументу btrfs_ioctl_scrub_args

```c
struct btrfs_ioctl_scrub_args {
    __u64 devid;                // ID фізичного пристрою для сканування
    __u64 start;                // Початкова логічна адреса
    __u64 end;                  // Кінцева логічна адреса
    __u64 flags;                // Прапорці виконання (READONLY тощо)
    struct btrfs_scrub_progress progress; // Структура підсумкової статистики
    __u64 unused[6 * 8 - 1];
};

struct btrfs_scrub_progress {
    __u64 data_extents_scrubbed;  // Проскановано екстентів даних
    __u64 tree_extents_scrubbed;  // Проскановано вузлів метаданих
    __u64 data_bytes_scrubbed;    // Проскановано байт даних
    __u64 tree_bytes_scrubbed;    // Проскановано байт метаданих
    __u64 read_errors;            // Кількість апаратних помилок читання
    __u64 csum_errors;            // Кількість виявлених незбігів CRC32c
    __u64 verify_errors;          // Помилки валідації заголовків
    __u64 uncorrectable_errors;   // Помилки, які НЕ вдалося відновити з RAID
    __u64 corrected_errors;       // Успішно відновлено з RAID копій!
    __u64 last_physical;
    __u64 unverified_errors;
};
```
