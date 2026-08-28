// Заголовок кожного вузла або листка Btrfs (101 байт)
struct btrfs_header {
    u8 csum[32];               // Контрольна сума вмісту вузла (CRC32c, xxHash64, SHA256 або BLAKE2b)
    u8 fsid[16];               // UUID файлової системи
    __le64 bytenr;             // Логічна адреса цього вузла на диску
    __le64 flags;              // Прапорці вузла (WRITTEN, RELOC)
    u8 chunk_tree_uuid[16];    // UUID дерева чанків
    __le64 generation;         // Номер транзакції (Transaction ID), коли написано вузол
    __le64 owner;              // ID дерева-власника (наприклад, ROOT_TREE_OBJECTID)
    __le32 nritems;            // Кількість елементів у вузлі/листку
    u8 level;                  // Рівень у дереві (0 = leaf, 1..7 = internal node)
} __attribute__ ((packed));

// Фундаментальний ключ пошуку Btrfs (17 байтів)
struct btrfs_key {
    __le64 objectid;           // ID об'єкта (номер іноди, ID субтому, адреса екстента)
    u8 type;                   // Тип запису (INODE_ITEM, EXTENT_DATA, DIR_ITEM)
    __le64 offset;             // Зсув усередині об'єкта (байтовий зсув, хеш тощо)
} __attribute__ ((packed));

// Заголовок елемента всередині листка (рівень level == 0) — 25 байтів
struct btrfs_item {
    struct btrfs_key key;      // Повний ключ елемента
    __le32 offset;             // Зсув до тіла даних від початку області даних (за заголовком)
    __le32 size;               // Розмір тіла даних у байтах
} __attribute__ ((packed));

// Запис у внутрішньому вузлі (рівень level > 0) — 33 байти
struct btrfs_key_ptr {
    struct btrfs_key key;      // Найменший ключ у дочірньому вузлі
    __le64 blockptr;           // Логічна адреса дочірнього вузла на диску
    __le64 generation;         // Generation дочірнього вузла (для CoW перевірки)
} __attribute__ ((packed));

// Опис метаданих іноди файлу в листку (INODE_ITEM, 160 байтів)
struct btrfs_inode_item {
    __le64 generation;         // Транзакція створення або останньої модифікації
    __le64 transid;            // ID транзакції модифікації
    __le64 size;               // Розмір файлу в байтах
    __le64 nbytes;             // Фактично зайнятий обсяг дискового простору
    __le64 block_group;        // Резервне поле
    __le32 nlink;              // Кількість жорстких посилань
    __le32 uid;                // ID власника (User ID)
    __le32 gid;                // ID групи (Group ID)
    __le32 mode;               // Права доступу та тип файлу POSIX
    __le64 rdev;               // Номер пристрою (якщо файл пристрою)
    __le64 flags;              // Прапорці іноди (NODATACOW, NODATASUM, IMMUTABLE)
    __le64 sequence;           // Лічильник модифікацій для NFS
    __le64 reserved[4];
    struct btrfs_timespec atime; // Час останнього доступу
    struct btrfs_timespec mtime; // Час останньої модифікації вмісту
    struct btrfs_timespec ctime; // Час останньої зміни метаданих
    struct btrfs_timespec otime; // Час створення файлу (btime)
} __attribute__ ((packed));

// Опис дискового екстента вмісту файлу (EXTENT_DATA)
struct btrfs_file_extent_item {
    __le64 generation;         // Транзакція запису екстента
    __le64 ram_bytes;          // Розмір екстента після розпакування у RAM
    u8 compression;            // Алгоритм стиснення (0=NONE, 1=ZLIB, 2=LZO, 3=ZSTD)
    u8 encryption;             // Шифрування (0=NONE)
    __le16 other_encoding;     // Зарезервовано під інші кодування
    u8 type;                   // Тип екстента (0=INLINE, 1=REGULAR, 2=PREALLOC)
    __le64 disk_bytenr;        // Фізична логічна адреса екстента на диску
    __le64 disk_num_bytes;     // Розмір стисненого екстента на диску
    __le64 offset;             // Зсув усередині дискового екстента
    __le64 num_bytes;          // Довжина ділянки файлу, що покривається цим екстентом
} __attribute__ ((packed));
