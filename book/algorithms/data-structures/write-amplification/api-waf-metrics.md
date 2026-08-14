# 📋 Інтерфейси та метрики інспекції Write Amplification у Linux та СУБД

Оцінка та моніторинг підсилення запису (Write Amplification Factor, WAF) у реальних продуктивних системах є необхідною умовою для підтримки стійкості інфраструктури. WAF неможливо виміряти однією універсальною командою, оскільки підсилення виникає на кількох незалежних рівнях: апаратному (контролер SSD NAND Flash), системному (ядро Linux, VFS, блоковий шар) та прикладному (СУБД RocksDB, InnoDB, PostgreSQL). При аналізі систем необхідно враховувати, що кожен шар має власну поверхню моніторингу та власні одиниці вимірювання.

Нижче наведено повний довідник програмних інтерфейсів, команд системного аналізу, eBPF-скриптів та викликів API для простеження WAF на всіх рівнях стека.

---

## 1. Рівень апаратного носія: NVMe SMART та Vendor-Specific атрибути

На найнижчому апаратному рівні контролер SSD зберігає енергонезалежні лічильники обсягу даних, оброблених хостом, та фізичних записів, виконаних на кристали NAND Flash. Сучасні твердотільні накопичувачі мають складну внутрішню архітектуру, що включає швидкий SLC-кеш для первинного прийому даних та основний масив TLC або QLC пам'яті. Коли SLC-кеш переповнюється, контролер запускає фоновий процес скидання (folding), що створює додаткове підсилення запису безпосередньо усередині накопичувача.

### Інтерфейс CLI `nvme-cli`

Для зчитування стандартних метрик SMART блокового пристрою NVMe використовується утиліта `nvme`. Ця команда отримує дані з лог-сторінки SMART через спецзапит специфікації NVM Express:

```bash
sudo nvme smart-log /dev/nvme0n1
```

Приклад виводу ключових полів SMART:

```
Smart Log for NVMe device:nvme0n1 namespace-id:ffffffff
critical_warning                    : 0
temperature                         : 31 C
available_spare                     : 100%
available_spare_threshold           : 10%
percentage_used                     : 2%
data_units_read                     : 14523904 (7.44 TB)
data_units_written                  : 28910400 (14.80 TB)
host_read_commands                  : 120491022
host_write_commands                 : 245901239
controller_busy_time                : 1420
power_cycles                        : 12
power_on_hours                      : 3410
unsafe_shutdowns                    : 3
```

### Інтерпретація одиниць виміру NVMe

Поле `data_units_written` повертає кількість записаних одиниць. Важливо враховувати, що стандарт NVMe визначає одну одиницю як **512 000 байтів** (що відповідає 1000 секторів по 512 байтів), а не 512 кілобайтів (524 288 байтів). Нехтування цією різницею призводить до похибки вимірювання у 2.4%.

Формула переведення одиниць у байти:

```
Host_Write_Bytes = data_units_written × 512,000
```

Для отримання обсягу фізичного запису на NAND Flash використовується розширений лог вендора (Vendor Specific Log Page 0xCA або SMART Attribute 0xF1 / 0xF5). Ці вендорські атрибути показують реальну кількість фізичних програмувань осередків плаваючого затвора:

```bash
sudo nvme intel smart-log-add /dev/nvme0n1
```

Вивід вендорських атрибутів для Intel/Micron/Samsung:

```
Device nvme0n1 - Intel Vendor Specific Log:
NAND Bytes Written (Lower 32-bits) : 48920102
NAND Bytes Written (Upper 32-bits) : 0
Host Bytes Written                 : 14800000000000
Physical NAND Writes               : 44400000000000
```

### Математична формула обчислення апаратного WAF

```
WAF_hardware = Physical_NAND_Writes / (data_units_written × 512,000)
```

У наведеному прикладі підсилення обчислюється так:

```
WAF_hardware = 44,400,000,000,000 / 14,800,000,000,000 = 3.0
```

Це означає, що на кожен кілобайт даних, переданих драйвером ОС, контролер SSD був змушений фізично записати 3 кілобайти у NAND Flash через процеси збирання сміття та вирівнювання зносу.

---

## 2. Системний шар Linux Kernel: `/sys/block` та `/proc/diskstats`

Операційна система Linux збирає точну статистику операцій введення-виведення на рівні блокового пристрою. Шар блокового введення-виведення ядра (Block Layer) реєструє кожну операцію читання та запису, що проходить через дисковий шедулер (BFQ, Kyber або none/mq-deadline).

### Структура інтерфейсу `/sys/block/{device}/stat`

Кожен блоковий пристрій надає файл `stat`, який містить 17 числових колонок, відокремлених пробілами. Цей інтерфейс надає сирі лічильники ядра без накладних витрат на форматування:

```bash
cat /sys/block/nvme0n1/stat
```

Приклад виводу:

```
   124901     4501  4290120    12040   240102    12904  18902400    89040        0    34090   101080
```

### Детальна розшифровка полів `/sys/block/sda/stat`

| Номер колонки | Поле ядра Linux | Опис та розмірність |
| :--- | :--- | :--- |
| **Колонка 1** | `read_ios` | Кількість успішно завершених читань |
| **Колонка 3** | `read_sectors` | Кількість зчитаних секторів (по 512 байтів) |
| **Колонка 5** | `write_ios` | Кількість успішно завершених записів |
| **Колонка 7** | `write_sectors` | Кількість записаних секторів (по 512 байтів) |
| **Колонка 11** | `time_in_queue` | Врахований час перебування операцій у черзі (ms) |

Обчислення логічного обсягу записів операційної системи на пристрій:

```
OS_Write_Bytes = write_sectors (Колонка 7) × 512
```

### Моніторинг у реальном часі через `iostat`

Для спостереження за навантаженням та підсиленням запису в часі використовується утиліта `iostat` з пакета `sysstat`. Прапор `-x` вмикає розширену статистику, а прапор `-z` відсікає неактивні пристрої:

```bash
iostat -xz 1 10
```

Ключові показники виводу:
- `w/s`: кількість операцій запису за секунду (Write IOPS).
- `wkB/s`: пропускна здатність запису в кілобайтах за секунду.
- `w_await`: середня затримка виконання операцій запису (ms). Високі значення w_await при відносно невеликій швидкості wkB/s вказують на блокування черги через Garbage Collection у накопичувачі.
- `aqu-sz`: середня довжина черги запитів до носія.

---

## 3. Інспекція I/O на рівні ядра через eBPF (bpftrace)

Для вимірювання затримок запису та виявлення випадків, коли Garbage Collection FTL або Compaction СУБД блокують потоки застосунку, використовується сучасний інструментарій eBPF. За допомогою eBPF можна перехоплювати точні точки входу та виходу з ядерних точок трасування (tracepoints).

### Скрипт `bpftrace` для побудови гістограми затримок запису

Скрипт відстежує точний час від моменту відправки I/O запиту в драйвер блокового пристрою до його фізичного завершення перериванням апаратного контролера:

```systemd
#!/usr/bin/env bpftrace

kprobe:blk_account_io_start
{
    @start[arg0] = nsecs;
}

kprobe:blk_account_io_done
/@start[arg0]/
{
    $dur = (nsecs - @start[arg0]) / 1000; // затримка в мікросекундах
    @io_latency_us = hist($dur);
    delete(@start[arg0]);
}
```

Запуск даного скрипта дозволяє виявити характерний побутовий розподіл затримок: перша вершина (100–300 µs) відповідає звичайним записам у DRAM/SLC буфер, а друга вершина (2000–10000 µs) показує катастрофічні затримки, індуковані стиранням блоків NAND Flash при високому WAF.

---

## 4. Рівень СУБД RocksDB: Програмістський інтерфейс C та C++

СУБД RocksDB надає детальний C++ та C API для отримання внутрішньої статистики процесів Compaction та обчислення WAF на рівні бази даних. У RocksDB підсилення запису є ключовим індикатором здоров'я ущільнення.

### Отримання загальної статистики через `GetProperty`

Для збору статистичних полів у C++ застосунках використовується метод `GetProperty`. Цей метод дозволяє як зчитувати повний текстовий звіт про стан ущільнення, так і витягувати окремі числові лічильники операцій:

:::tabs
```cpp
#include <iostream>
#include <string>
#include <memory>
#include <rocksdb/db.h>
#include <rocksdb/options.h>

void inspect_rocksdb_amplification(rocksdb::DB* db) {
    std::string stats_out;
    
    // Отримання текстового звіту про стан рівнів та Compaction WAF
    if (db->GetProperty("rocksdb.stats", &stats_out)) {
        std::cout << "=== RocksDB Compaction Stats ===" << std::endl;
        std::cout << stats_out << std::endl;
    }

    // Отримання точних числових показників через GetIntProperty
    uint64_t bytes_written_user = 0;
    uint64_t bytes_written_flush = 0;
    uint64_t bytes_written_compaction = 0;

    db->GetIntProperty("rocksdb.stats.bytes-written", &bytes_written_user);
    db->GetIntProperty("rocksdb.base-level-write-bytes", &bytes_written_flush);
    db->GetIntProperty("rocksdb.compact-write-bytes", &bytes_written_compaction);

    if (bytes_written_user > 0) {
        uint64_t total_db_writes = bytes_written_flush + bytes_written_compaction;
        double db_waf = static_cast<double>(total_db_writes) / static_cast<double>(bytes_written_user);

        std::cout << "Логічний запис користувача: " << bytes_written_user / (1024 * 1024) << " MB\n";
        std::cout << "Запис при Flush (MemTable): " << bytes_written_flush / (1024 * 1024) << " MB\n";
        std::cout << "Запис при Compaction:       " << bytes_written_compaction / (1024 * 1024) << " MB\n";
        std::cout << "Підсумковий Database WAF:   " << db_waf << std::endl;
    }
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <rocksdb/c.h>

void inspect_rocksdb_amplification_c(rocksdb_t* db) {
    char* stats = rocksdb_property_value(db, "rocksdb.stats");
    if (stats) {
        printf("=== RocksDB Stats (C API) ===\n%s\n", stats);
        free(stats);
    }
    
    char* user_bytes_str = rocksdb_property_value(db, "rocksdb.stats.bytes-written");
    char* compact_bytes_str = rocksdb_property_value(db, "rocksdb.compact-write-bytes");
    
    if (user_bytes_str && compact_bytes_str) {
        unsigned long long user_bytes = strtoull(user_bytes_str, NULL, 10);
        unsigned long long compact_bytes = strtoull(compact_bytes_str, NULL, 10);
        
        if (user_bytes > 0) {
            double waf = (double)(user_bytes + compact_bytes) / (double)user_bytes;
            printf("User Bytes: %llu, Compact Bytes: %llu, WAF: %.2f\n", 
                   user_bytes, compact_bytes, waf);
        }
    }
    
    if (user_bytes_str) free(user_bytes_str);
    if (compact_bytes_str) free(compact_bytes_str);
}
```
:::

### Структура виводу `rocksdb.stats`

Текстова властивість `rocksdb.stats` повертає детальну таблицю по кожному рівню LSM-дерева:

```
Compaction Stats [Leveled]
Priority      Files   Size(MB)   Score     Read(MB)  Write(MB)  WAF
-------------------------------------------------------------------
L0              3        45.2     0.9           0.0       45.2   1.0
L1             10       102.1     1.0         145.0      145.0   3.2
L2             98       998.4     1.0        2100.2     2100.2   9.8
L3            950      9820.0     0.9       19800.5    19800.5   9.5
-------------------------------------------------------------------
Sum          1061     10965.7     0.0       22045.7    22090.9  23.5
```

Розшифровка полів виводу:
- `Score`: відношення поточного обсягу рівня до його нормативного ліміту. Якщо Score > 1.0, це означає, що рівень вимагає негайного ущільнення. Якщо Score на рівні L0 перевищує 1.5, RocksDB починає уповільнювати нові записи користувача (Write Stall).
- `Write(MB)`: загальний обсяг даних, записаних на цей рівень під час ущільнення з попереднього рівня.
- `WAF`: локальний коефіцієнт підсилення для конкретного рівня (Write(MB) / Input(MB)).

---

## 5. Інспекція WAF у MySQL InnoDB та PostgreSQL

Традиційні реляційні СУБД надають SQL-інтерфейси для моніторингу обсягів журналювання та скидання сторінок.

### MySQL InnoDB (SQL CLI)

Для обчислення підсилення у двигуні InnoDB використовуються глобальні лічильники статусу, що збирають статистику скидання буферного пулу (Buffer Pool Flush) та журналювання передзапису (Redo Log):

```sql
SHOW GLOBAL STATUS LIKE 'Innodb_data_written';
SHOW GLOBAL STATUS LIKE 'Innodb_pages_written';
SHOW GLOBAL STATUS LIKE 'Innodb_dblwr_pages_written';
SHOW GLOBAL STATUS LIKE 'Innodb_os_log_written';
```

Обчислення InnoDB WAF:

```
InnoDB_WAF = Innodb_data_written / (Logical_Row_Updates × Average_Row_Length)
```

Де `Innodb_data_written` складається із суми трьох компонентів:

```
Innodb_data_written = Doublewrite_Bytes + Redo_Log_Bytes + Data_Page_Bytes
```

Якщо у конфігурації MySQL ввімкнено параметр `innodb_doublewrite`, то кожна модифікована сторінка розміром 16 KB пишеться на диск двічі (спочатку в doublewrite buffer, а потім у файл табличного простору `.ibd`). Це створює базове підсилення WAF = 2.0 навіть без урахування запису в Redo Log.

### PostgreSQL (`pg_stat_bgwriter` та WAL statistics)

У PostgreSQL підсилення запису виникає через запис у WAL лог, роботу процесів Checkpointer та Background Writer, а також дію фонового очищення (AutoVacuum):

```sql
SELECT 
    buffers_clean,
    maxwritten_clean,
    buffers_checkpoint,
    buffers_backend,
    alloc
FROM pg_stat_bgwriter;
```

Для вимірювання обсягу WAL записів у сучасних версіях PostgreSQL (v14+):

```sql
SELECT 
    wal_records,
    wal_fpi,
    wal_bytes
FROM pg_stat_wal;
```

Поле `wal_fpi` (Full Page Images) показує кількість випадків, коли PostgreSQL після чекпоінту записує цілу 8 KB сторінку у WAL лог при її першій зміні (для захисту від розриву сторінок). При виникненні затяжних чекпоінтів високе значення `wal_fpi` є головною причиною раптового зростання WAF у PostgreSQL у десятки разів.
