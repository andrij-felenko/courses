# 📋 Параметри, CLI-інтерфейс та керування зашифрованими датасетами ZFS

Матеріал надає повний системний довідник із команд утиліт `zfs` та `zpool`, властивостей датасетів, індикаторів стану, параметрів ядра Linux та інтерфейсів kstat для створення зашифрованих томів ZFS, керування майстер-ключами, моніторингу таблиці дедуплікації DDT та виконання безпечного сирого реплікування.

## 1. Властивості шифрування та керування ключами

Вбудоване шифрування ZFS налаштовується за допомогою набору специфічних властивостей датасету. Деякі з них можна задати лише під час створення датасету (незмінні властивості — Immutable Properties), інші можна змінювати динамічно під час експлуатації.

### Основні властивості датасету

| Властивість | Можливі значення | Можливість зміни | Опис |
| :--- | :--- | :--- | :--- |
| `encryption` | `off`, `on`, `aes-128-gcm`, `aes-192-gcm`, `aes-256-gcm`, `aes-128-ccm`, `aes-192-ccm`, `aes-256-ccm` | Лише при створенні | Визначає криптографічний алгоритм шифрування блоків. Значення `on` є замовчувальним псевдонімом для `aes-256-gcm`. |
| `keyformat` | `none`, `raw`, `hex`, `passphrase` | Лише при створенні | Формат подання Wrapping Key. Режим `passphrase` вимагає від 8 до 512 символів; `raw` — 32 бінарні байти; `hex` — 64 шістнадцяткові символи. |
| `keylocation` | `prompt`, `file://<path>`, `https://<url>` | Динамічна | Джерело отримання Wrapping Key при виклику `zfs load-key`. `prompt` запитує ключ з `stdin`/терміналу, `file://` зчитує з локального шляху. |
| `keystatus` | `none`, `unavailable`, `available` | Лише для читання | Поточний стан Майстер-ключа в пам'яті ядра. Значення `available` означає, що ключ завантажено і датасет можна монтувати. |
| `encryptionroot` | `<dataset_name>` | Лише для читання | Назва датасету, який є коренем шифрування (Encryption Root) для даного об'єкта та його дочірніх снапшотів. |
| `pbkdf2iters` | ціле число, не менше `100000` | Задається при створенні або при `zfs change-key` | Кількість ітерацій алгоритму PBKDF2 HMAC-SHA256 при перетворенні пароля на Wrapping Key (за замовчуванням 350 000). |

## 2. Команди адміністрування шифрування

### Створення зашифрованих томів та розрив коренів шифрування

Створення зашифрованого датасету з введенням парольної фрази через інтерактивний термінал:

```bash
# zfs create -o encryption=on -o keyformat=passphrase pool/securedataset
Enter passphrase:
Re-enter passphrase:
```

Створення кореня шифрування з автоматичним зчитуванням сирого бінарного 256-бітного ключа з файлу захищеного носія:

```bash
# dd if=/dev/urandom of=/etc/zfs/keys/pool_secret.key bs=32 count=1
# chmod 600 /etc/zfs/keys/pool_secret.key
# zfs create -o encryption=aes-256-gcm -o keyformat=raw \
    -o keylocation=file:///etc/zfs/keys/pool_secret.key pool/secret
```

Створення дочірнього датасету з власним незалежним Майстер-ключем (розірвання успадкування від батьківського кореня):

```bash
# zfs create -o encryption=on -o keyformat=passphrase pool/securedataset/isolated
```

### Завантаження та вивантаження ключів у пам'ять ядра

Перевірка поточного стану ключів усіх зашифрованих датасетів у системі:

```bash
# zfs get -r encryption,keystatus,keylocation,encryptionroot pool
NAME                      PROPERTY        VALUE                           SOURCE
pool                      encryption      off                             default
pool/securedataset        encryption      on                              local
pool/securedataset        keystatus       available                       -
pool/securedataset        keylocation     prompt                          local
pool/securedataset        encryptionroot  pool/securedataset              -
pool/securedataset/home   encryption      on                              inherited from pool/securedataset
pool/securedataset/home   keystatus       available                       -
pool/securedataset/home   keylocation     prompt                          local
pool/securedataset/home   encryptionroot  pool/securedataset              -
```

Вивантаження Майстер-ключа з оперативної пам'яті ядра (з попереднім розмонтуванням тома):

```bash
# zfs unmount pool/securedataset
# zfs unload-key pool/securedataset
Key unloaded for 'pool/securedataset'.
```

Завантаження ключа в пам'ять ядра для подальшого монтування:

```bash
# zfs load-key pool/securedataset
Enter passphrase for 'pool/securedataset':
# zfs mount pool/securedataset
```

Автоматичне завантаження ключів для всіх зашифрованих датасетів системи під час старту операційної системи:

```bash
# zfs load-key -a
```

### Зміна пароля та форсоване ротування майстер-ключа

Зміна парольної фрази або файлу ключа без перешифрування блоків даних на диску (перегортається лише Wrapping Key):

```bash
# zfs change-key -o keyformat=passphrase -o keylocation=prompt pool/securedataset
Enter new passphrase:
Re-enter new passphrase:
```

Зміна джерела зчитування ключа з терміналу на локальний файл:

```bash
# zfs change-key -o keylocation=file:///etc/zfs/keys/new.key pool/securedataset
```

Перевід дочірнього датасету під успадкування ключа батьківського кореня шифрування:

```bash
# zfs change-key -i pool/securedataset/isolated
```

Повного ротування Майстер-ключа ZFS не має: перешифрувати вже записані блоки на місці неможливо, `zfs change-key` міняє лише Wrapping Key. Єдиний спосіб отримати новий Майстер-ключ для тих самих даних — створити новий корінь шифрування і перелити дані звичайним (не сирим) потоком, який на приймачі шифрується заново:

```bash
# zfs create -o encryption=on -o keyformat=passphrase pool/rekeyed
# zfs snapshot pool/securedataset@migrate
# zfs send pool/securedataset@migrate | zfs receive pool/rekeyed/data
```

## 3. Команди реплікування зашифрованих потоків (Raw Send)

Передача зашифрованого снапшота на віддалений сервер резервного копіювання без розкриття Майстер-ключа (на приймаючому сервері ключі відсутні):

```bash
# zfs snapshot pool/securedataset@backup_v1
# zfs send -w pool/securedataset@backup_v1 | ssh user@backup-server zfs receive backup_pool/archivedataset
```

Перевірка стану зашифрованого датасету на приймаючому резервному сервері:

```bash
# ssh user@backup-server zfs get encryption,keystatus,encryptionroot backup_pool/archivedataset
NAME                        PROPERTY        VALUE                SOURCE
backup_pool/archivedataset  encryption      on                   received
backup_pool/archivedataset  keystatus       unavailable          -
backup_pool/archivedataset  encryptionroot  backup_pool/archivedataset local
```

Як видно з виводу, на бекап-сервері `keystatus` залишається у стані `unavailable` — датасет зберігається в зашифрованому вигляді й не може бути змонтованим без введення пароля, але всі снапшоти збережені в повному обсязі.

## 4. Керування та діагностика дедуплікації (DDT)

### Увімкнення та налаштування дедуплікації

Увімкнення дедуплікації з обчисленням хешу SHA-256:

```bash
# zfs set dedup=on pool/data
```

Увімкнення дедуплікації із застосуванням побайтової перевірки вмісту (`verify`): при збігу SHA-256 ядро додатково зчитує оригінальний блок з диска і порівнює його побайтово для гарантії захисту від колізій:

```bash
# zfs set dedup=verify pool/data
```

### Моніторинг DDT та інтерфейси kstat

Перевірка стану таблиці дедуплікації у пулі та її впливу на пам'ять:

```bash
# zpool status -D pool
  pool: pool
 state: ONLINE
  scan: scrub repaired 0B in 00:05:12 with 0 errors on Wed Aug 12 10:00:00 2026

DDT entries 524288, alloc 160M, metadata 32M, blocks 1048576

deduplicated blocks = 1048576, allocated count = 524288, ratio = 2.00x

DDT histogram (allocated blocks):

bucket              allocated             referenced          
------+------------------+------------------
refcnt              blocks   LSIZE   PSIZE      blocks   LSIZE   PSIZE
------              ------   -----   -----      ------   -----   -----
     2               524288   64G     32G       1048576  128G     64G
 Total               524288   64G     32G       1048576  128G     64G
```

Інтерпретація ключових лічильників:
- `DDT entries`: загальна кількість унікальних хеш-записів у таблиці DDT.
- `alloc`: обсяг пам'яті RAM/ARC, виділений під індекс дедуплікації.
- `ratio = 2.00x`: коефіцієнт дедуплікації — відношення кількості посилань на блоки (`referenced`) до кількості реально збережених блоків (`allocated`); виграш від стискання сюди не входить, він рахується окремо.

## 5. Параметри модуля ядра ZFS та інспекція крайових випадків

Налаштування поведінки шифрування та DDT в реальному часі здійснюється через псевдофайли `/sys/module/zfs/parameters/`:

- `/sys/module/zfs/parameters/zfs_ddt_data_is_special`: при значенні `1` перераховує блоки DDT як спеціальні метадані, дозволяючи зберігати їх на високошвидкісних VDEV накопичувачах типу `special` чи `dedup` (NVMe SSD).
- `/sys/module/zfs/parameters/zfs_key_max_salt_uses`: скільки блоків дозволено зашифрувати на одній солі, доки ZFS не виведе з Майстер-ключа новий ключ шифрування (за замовчуванням 400 000 000).
- `/sys/module/zfs/parameters/zfs_dedup_prefetch`: при значенні `1` дозволяє попереднє підвантаження таблиці DDT у ARC перед записом (за замовчуванням вимкнено: на великих DDT саме префетч і вимиває кеш).

Системний лог та повідомлення налагодження шифрування ZFS доступні для трасування через файл `/proc/spl/kstat/zfs/dbgmsg` командою `cat /proc/spl/kstat/zfs/dbgmsg`.

### Специфіка клонування та відновлення зашифрованих датасетів

При виконанні операції клонування зашифрованого снапшота (`zfs clone pool/data@snap pool/clone`) новостворений датасет `pool/clone` автоматично ділить той самий Encryption Root і Майстер-ключ, що й оригінальний снапшот. Клон ділить з походженням самі блоки, тож нового Майстер-ключа він дістати не може: `zfs change-key` зробить його окремим коренем шифрування лише в тому сенсі, що клон дістане власну парольну фразу й власний Wrapping Key, а Майстер-ключ під ними залишиться той самий:

```bash
# zfs clone pool/data@snap pool/clone
# zfs change-key -o keyformat=passphrase pool/clone
```

Операція створює для клону власний об'єкт `dsl_crypto_key_phys_t` із новою обгорткою, тож пароль батьківського датасету більше не відмикає клон — але дані обох і далі лежать під одним Майстер-ключем.

### Автоматичне завантаження ключів через systemd

Для автоматичного завантаження ключів під час завантаження системи Linux використовується системна служба `zfs-load-key`. Служба може запускатися перед монтуванням файлових систем:

```ini
[Unit]
Description=Load ZFS Encryption Keys
DefaultDependencies=no
After=zfs-import.target
Before=zfs-mount.service local-fs.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/sbin/zfs load-key -a

[Install]
WantedBy=zfs-mount.service
```

Використання цієї служби гарантує, що всі зашифровані датасети з налаштованим `keylocation=file://...` будуть автоматично розблоковані до моменту монтування точок у системному дереві.
