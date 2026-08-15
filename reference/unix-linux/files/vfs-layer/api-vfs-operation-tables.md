# 📋 Таблиці операцій VFS: поля, підписи й що означає порожній вказівник

Це довідка про контракт, який файлова система підписує з ядром Linux: шість структур із вказівниками на функції, кожен з яких вона або заповнює, або лишає порожнім. Підписи тут другорядні — вони міняються з випуску в випуск; головне те, що ядро робить із **порожнім** місцем, бо саме звідти беруться `EPERM` на `ln` поверх FAT, `ENOTTY` на `ioctl` до звичайного файлу і `EINVAL` на `open(O_DIRECT)`.

## Як читати цю довідку

Усі підписи наведено за поточним деревом mainline (стан на серпень 2026). Це **внутрішній** інтерфейс ядра, і сталим він не є: на відміну від [замороженої межі до простору користувача](book:unix-linux/kernel-abi-stability), таблиці VFS перебудовують, коли того вимагає задача, і одним махом правлять усі файлові системи в дереві. Тільки за останні роки: `->get_sb` і `->mount` зникли зовсім, `->readdir` замінено на `->iterate_shared`, `->readpage` перейменовано на `->read_folio`, `->writepage` прибрано з таблиці сторінок, `->mkdir` тепер повертає `dentry` замість числа, `->d_revalidate` дістав два додаткові аргументи, а функцію-заглушку `no_llseek` видалено. Тому підпис завжди звіряють із деревом того ядра, під яке пишуть; що тримається довше — це семантика порожнього поля.

Порожній вказівник у таблиці VFS означає одну з чотирьох різних речей, і плутати їх дорого:

| вид | що робить спільний шар |
|---|---|
| **підстановка** | бере власну типову реалізацію; ззовні різниці не видно |
| **тиша** | дію просто не виконує; програма помилки не бачить |
| **відмова кодом** | до програми доходить конкретний `errno` |
| **обов'язковий** | перевірки немає взагалі — ядро йде за вказівником; порожнє поле тут є хибою драйвера |

![Чотири види порожнього вказівника в таблицях VFS у вигляді чотирьох рядків. Перший рядок — підстановка: спільний шар бере власну типову реалізацію, приклади getattr до generic_fillattr, permission до generic_permission, setattr до simple_setattr. Другий рядок — тиша: дію не виконано й помилки немає, приклади write_inode, put_super, writepages. Третій рядок — відмова кодом: до програми доходить конкретний код помилки, приклади link дає EPERM, fsync дає EINVAL, statfs дає ENOSYS. Четвертий рядок — обов'язковий: перевірки немає, ядро йде за вказівником, приклади lookup у каталозі, dirty_folio у власній таблиці сторінок, kill_sb у типі файлової системи](/reference/unix-linux/files/vfs-layer/img/null-pointer-kinds.svg)

*Одне й те саме порожнє місце в різних полях значить протилежні речі: у двох випадках із чотирьох програма нічого не помічає, у третьому дістає код помилки, у четвертому — падає ядро.*

## Реєстрація: `struct file_system_type`

Це вхід у контракт: опис типу файлової системи, який модуль віддає ядру, щоб ім'я з'явилося серед доступних для монтування.

```c
struct file_system_type {
    const char *name;            /* ім'я для mount -t і /proc/filesystems */
    int fs_flags;                /* ознаки FS_*, перелік нижче */
    int (*init_fs_context)(struct fs_context *);
    const struct fs_parameter_spec *parameters;
    void (*kill_sb)(struct super_block *);
    struct module *owner;        /* THIS_MODULE */
    struct hlist_node list;      /* внутрішнє: місце в списку зареєстрованих */
    struct hlist_head fs_supers; /* внутрішнє: живі суперблоки цього типу */
    /* далі — ключі класів блокувань для lockdep */
};
```

| поле | стан | що робить |
|---|---|---|
| `name` | обов'язкове | те, що пишуть після `mount -t`; крапки в імені заборонено, ядро на цьому спиняється (`BUG_ON`) |
| `owner` | обов'язкове для модуля | `THIS_MODULE`; без нього [модуль](book:unix-linux/kernel-modules) можна вивантажити з-під змонтованої файлової системи |
| `init_fs_context` | обов'язкове | створює контекст [монтування](book:unix-linux/mount-model): розбирає параметри й зрештою віддає суперблок |
| `parameters` | необов'язкове | машинний опис допустимих параметрів; його перевіряють під час реєстрації |
| `kill_sb` | обов'язкове | звільняє суперблок; готові варіанти — `kill_block_super` для файлової системи на пристрої, `kill_anon_super` для тієї, що без носія |
| `fs_flags` | — | набір ознак, за якими ядро вирішує, як із цим типом поводитися |

Поля `->mount` тут більше немає: стару пару `->get_sb`/`->mount` прибрано, коли останню файлову систему в дереві перевели на контекст монтування. Це той самий перехід, через який `mount()` розпався на `fsopen()`, `fsconfig()`, `fsmount()` і `move_mount()`.

Найуживаніші ознаки в `fs_flags`:

| ознака | значення |
|---|---|
| `FS_REQUIRES_DEV` | без блокового пристрою монтуватися не вміє |
| `FS_BINARY_MOUNTDATA` | параметри монтування — двійкова структура, а не текст (як у NFS) |
| `FS_HAS_SUBTYPE` | ім'я типу має підтип після крапки: `fuse.sshfs` |
| `FS_USERNS_MOUNT` | тип можна монтувати з простору імен користувачів |
| `FS_ALLOW_IDMAP` | драйвер уміє монтування з перевідображенням власників |
| `FS_RENAME_DOES_D_MOVE` | перейменування драйвер завершує сам, VFS у кеш імен не втручається |

Сама реєстрація:

```c
int register_filesystem(struct file_system_type *fs);
int unregister_filesystem(struct file_system_type *fs);
```

`register_filesystem()` повертає `-EINVAL`, якщо опис `parameters` неузгоджений, і `-EBUSY`, якщо цю саму структуру вже зареєстровано або ім'я зайняте. `unregister_filesystem()` повертає `-EINVAL` для незареєстрованого типу, а перед поверненням чекає на кінець періоду відстрочки — доки не завершиться останній паралельний обхід списку. Реєстрація ще нічого не монтує: вона лише додає рядок у `/proc/filesystems`.

## `super_operations`: рівень примірника

Таблиця дій над змонтованим примірником і над його inode як цілим.

```c
struct super_operations {
    struct inode *(*alloc_inode)(struct super_block *sb);
    void (*destroy_inode)(struct inode *);
    void (*free_inode)(struct inode *);
    void (*dirty_inode)(struct inode *, int flags);
    int  (*write_inode)(struct inode *, struct writeback_control *wbc);
    int  (*drop_inode)(struct inode *);
    void (*evict_inode)(struct inode *);
    void (*put_super)(struct super_block *);
    int  (*sync_fs)(struct super_block *sb, int wait);
    int  (*freeze_fs)(struct super_block *);
    int  (*unfreeze_fs)(struct super_block *);
    int  (*statfs)(struct dentry *, struct kstatfs *);
    void (*umount_begin)(struct super_block *);
    int  (*show_options)(struct seq_file *, struct dentry *);
    long (*nr_cached_objects)(struct super_block *, struct shrink_control *);
    long (*free_cached_objects)(struct super_block *, struct shrink_control *);
};
```

| поле | порожній вказівник означає |
|---|---|
| `alloc_inode` | **підстановка**: VFS бере голий `struct inode` зі спільного кеша об'єктів. Годиться лише тим, кому нічого свого до inode долучати не треба |
| `destroy_inode`, `free_inode` | **підстановка**: пам'ять повертають у спільний кеш після [періоду відстрочки](book:programming/read-copy-update), щоб паралельні читачі не спіткнулися об звільнений об'єкт |
| `dirty_inode` | **тиша**: позначення inode брудним нікуди не доходить |
| `write_inode` | **тиша**: метадані inode ніколи не пишуть назад. Саме те, що треба tmpfs; для файлової системи на носії це втрата даних |
| `drop_inode` | **підстановка**: `inode_generic_drop` — викидати, коли зникло останнє ім'я або inode уже не в таблиці |
| `evict_inode` | **підстановка**: VFS сам скидає сторінки файлу й чистить inode. Своя реалізація потрібна тим, хто мусить звільнити місце на носії |
| `put_super` | **тиша**: під час відмонтування драйвер нічого не прибирає |
| `sync_fs` | **тиша**: `sync(2)` для цього примірника зводиться до скидання сторінок, власних журналів і карт ніхто не допише |
| `freeze_fs`, `unfreeze_fs` | **тиша**: `fsfreeze` вдається, але для драйвера це порожня операція |
| `statfs` | **відмова**: `statfs(2)` і `df` дістають `ENOSYS` |
| `umount_begin` | **тиша**: `umount -f` не має чим обірвати зависле мережеве очікування |
| `show_options` | **тиша**: у `/proc/mounts` не буде власних параметрів примірника |
| `nr_cached_objects`, `free_cached_objects` | **тиша**: під тиском на пам'ять ядро не проситиме драйвер звільнити свої кеші |

## `inode_operations`: об'єкт і імена всередині нього

Найважливіша таблиця, бо саме тут порожнє поле найчастіше перетворюється на код помилки в програмі.

```c
struct inode_operations {
    struct dentry *(*lookup)(struct inode *, struct dentry *, unsigned int);
    int  (*create)(struct mnt_idmap *, struct inode *, struct dentry *, umode_t, bool);
    int  (*link)(struct dentry *, struct inode *, struct dentry *);
    int  (*unlink)(struct inode *, struct dentry *);
    int  (*symlink)(struct mnt_idmap *, struct inode *, struct dentry *, const char *);
    struct dentry *(*mkdir)(struct mnt_idmap *, struct inode *, struct dentry *, umode_t);
    int  (*rmdir)(struct inode *, struct dentry *);
    int  (*mknod)(struct mnt_idmap *, struct inode *, struct dentry *, umode_t, dev_t);
    int  (*rename)(struct mnt_idmap *, struct inode *, struct dentry *,
                   struct inode *, struct dentry *, unsigned int);
    const char *(*get_link)(struct dentry *, struct inode *, struct delayed_call *);
    int  (*readlink)(struct dentry *, char __user *, int);
    int  (*permission)(struct mnt_idmap *, struct inode *, int);
    int  (*getattr)(struct mnt_idmap *, const struct path *, struct kstat *,
                    u32 request_mask, unsigned int query_flags);
    int  (*setattr)(struct mnt_idmap *, struct dentry *, struct iattr *);
    ssize_t (*listxattr)(struct dentry *, char *, size_t);
    struct posix_acl *(*get_inode_acl)(struct inode *, int, bool);
    int  (*set_acl)(struct mnt_idmap *, struct dentry *, struct posix_acl *, int);
    int  (*fiemap)(struct inode *, struct fiemap_extent_info *, u64 start, u64 len);
    void (*update_time)(struct inode *, enum fs_update_time type, int flags);
    int  (*atomic_open)(struct inode *, struct dentry *, struct file *,
                        unsigned open_flag, umode_t create_mode);
    int  (*tmpfile)(struct mnt_idmap *, struct inode *, struct file *, umode_t);
    int  (*fileattr_get)(struct dentry *, struct file_kattr *);
    int  (*fileattr_set)(struct mnt_idmap *, struct dentry *, struct file_kattr *);
};
```

Перший аргумент `struct mnt_idmap *` у більшості методів — не примха: через нього передають перевідображення власників того монтування, крізь яке прийшов запит, тому драйвер ніколи не порівнює ідентифікатори напряму.

| поле | порожній вказівник означає |
|---|---|
| `lookup` | **обов'язковий для каталогу**: розв'язати ім'я більше нема чим. Файловим системам, чиє дерево цілком живе в кеші імен, вистачає готової `simple_lookup` |
| `create` | **відмова**: `open(O_CREAT)` і `creat(2)` дають `EACCES` — єдиний виняток у цій групі, і в самому ядрі поруч стоїть коментар «а чи не мало б це бути `ENOSYS`?» |
| `link` | **відмова** `EPERM`. Ось звідки «Operation not permitted» на `ln` поверх FAT: [жорсткого посилання](book:unix-linux/hard-and-symbolic-links) там немає чим виразити |
| `unlink`, `symlink`, `mkdir`, `rmdir`, `mknod`, `rename` | **відмова** `EPERM` — той самий код на всі шість. У новому підписі `mkdir` помилку повертають як `ERR_PTR(-EPERM)`, бо метод віддає `dentry` |
| `get_link` | **обов'язковий для символьного посилання**, якщо драйвер не поклав готовий рядок у поле `i_link` самого inode; без обох об'єкт як посилання не працює |
| `readlink` | **підстановка**: VFS сам віддає програмі рядок, здобутий через `get_link`. Своя реалізація потрібна лише тим, у кого ціль не є простим рядком (procfs) |
| `permission` | **підстановка**: `generic_permission` — звичайні біти прав, потім [ACL](book:unix-linux/acl-and-xattr), потім можливості процесу |
| `getattr` | **підстановка**: `generic_fillattr` переписує в `kstat` те, що вже лежить в inode. Своя потрібна, щоб віддати поля [`statx`](book:unix-linux/statx-extended-stat), яких в inode немає, — час створення, ознаки шифрування, вирівнювання для прямого вводу-виводу (`STATX_DIOALIGN`) |
| `setattr` | **підстановка**: `simple_setattr` міняє поля в пам'яті й нічого не пише на носій — правильно для tmpfs, хибно для всіх інших |
| `listxattr` | **тиша з поверненням**: `listxattr(2)` віддасть тільки те, що додасть модуль безпеки; власних розширених атрибутів у переліку не буде |
| `get_inode_acl`, `set_acl` | **відмова**: `getfacl` бачить лише біти прав, `setfacl` не спрацьовує |
| `fiemap` | **відмова**: `FS_IOC_FIEMAP` не працює, і карту розміщення файлу нема як дістати |
| `update_time` | **підстановка**: VFS сам ставить часи в inode й позначає його брудним |
| `atomic_open` | **підстановка**: відкриття з можливим створенням VFS робить двома кроками — пошук, потім `create`. Мережеві файлові системи заповнюють це поле, щоб з'їздити на сервер один раз, а не двічі |
| `tmpfile` | **відмова**: `open(O_TMPFILE)` не працює |
| `fileattr_get`, `fileattr_set` | **відмова**: `lsattr` і `chattr` не мають чого показати й що поставити |

Один поширений код помилки в цю таблицю **не** входить. `EXDEV` під час `rename()` — не наслідок порожнього поля, а окрема перевірка в самому системному виклику: якщо старий і новий шляхи розв'язалися в різні монтування, ядро відмовляє, не дійшовши до жодного методу. Метод `rename` за задумом працює тільки в межах одного примірника файлової системи, тому `mv` між розділами перетворюється на копіювання з видаленням.

## `dentry_operations`: коли ім'я не просто байти

Найкоротша з таблиць і єдина, яку більшість файлових систем лишає порожньою цілком.

```c
struct dentry_operations {
    int  (*d_revalidate)(struct inode *, const struct qstr *, struct dentry *, unsigned int);
    int  (*d_weak_revalidate)(struct dentry *, unsigned int);
    int  (*d_hash)(const struct dentry *, struct qstr *);
    int  (*d_compare)(const struct dentry *, unsigned int, const char *, const struct qstr *);
    int  (*d_delete)(const struct dentry *);
    void (*d_release)(struct dentry *);
    void (*d_iput)(struct dentry *, struct inode *);
    char *(*d_dname)(struct dentry *, char *, int);
    struct vfsmount *(*d_automount)(struct path *);
    int  (*d_manage)(const struct path *, bool);
};
```

| поле | порожній вказівник означає |
|---|---|
| `d_revalidate` | кешоване ім'я вважається чинним, доки його не витіснить тиск на пам'ять. Для локальної файлової системи це правда за побудовою; мережева мусить заповнити, бо файл могли перейменувати на сервері |
| `d_weak_revalidate` | те саме для шляхів, що починаються не з кореня, а зі стрибка в середину дерева — від поточного каталогу або від дескриптора |
| `d_hash`, `d_compare` | імена порівнюють побайтово, хеш рахують стандартний. Заповнюють ті, у кого порівняння інше: нечутливість до регістру у vfat, згортання Юнікоду в ext4 і F2FS |
| `d_delete` | «завжди кешувати»: запис лишається в кеші й після зникнення останнього посилання. Повернути `1` означає «викидай негайно» — так роблять псевдофайлові системи, щоб не тримати сміття |
| `d_release`, `d_iput` | VFS сам відпускає inode звичайним `iput()` |
| `d_dname` | ім'я збирають обходом дерева вгору. Заповнюють ті, у кого імені в дереві немає: звідси `pipe:[12345]` і `socket:[67890]` у `/proc/PID/fd` |
| `d_automount`, `d_manage` | запис не є точкою автомонтування — ніякого монтування на дотик (autofs, переадресація NFS) |

## `file_operations`: уже відкритий файл

Ту саму структуру заповнюють і файлові системи, і драйвери символьних пристроїв — це найширше вживана таблиця в ядрі.

```c
struct file_operations {
    struct module *owner;
    fop_flags_t fop_flags;
    loff_t  (*llseek)(struct file *, loff_t, int);
    ssize_t (*read)(struct file *, char __user *, size_t, loff_t *);
    ssize_t (*write)(struct file *, const char __user *, size_t, loff_t *);
    ssize_t (*read_iter)(struct kiocb *, struct iov_iter *);
    ssize_t (*write_iter)(struct kiocb *, struct iov_iter *);
    int     (*iterate_shared)(struct file *, struct dir_context *);
    __poll_t (*poll)(struct file *, struct poll_table_struct *);
    long    (*unlocked_ioctl)(struct file *, unsigned int, unsigned long);
    long    (*compat_ioctl)(struct file *, unsigned int, unsigned long);
    int     (*mmap)(struct file *, struct vm_area_struct *);
    int     (*open)(struct inode *, struct file *);
    int     (*flush)(struct file *, fl_owner_t id);
    int     (*release)(struct inode *, struct file *);
    int     (*fsync)(struct file *, loff_t start, loff_t end, int datasync);
    int     (*fasync)(int, struct file *, int);
    int     (*lock)(struct file *, int, struct file_lock *);
    int     (*flock)(struct file *, int, struct file_lock *);
    ssize_t (*splice_read)(struct file *, loff_t *, struct pipe_inode_info *,
                           size_t, unsigned int);
    ssize_t (*splice_write)(struct pipe_inode_info *, struct file *, loff_t *,
                            size_t, unsigned int);
    long    (*fallocate)(struct file *, int mode, loff_t offset, loff_t len);
    ssize_t (*copy_file_range)(struct file *, loff_t, struct file *, loff_t,
                               size_t, unsigned int);
    loff_t  (*remap_file_range)(struct file *file_in, loff_t pos_in,
                                struct file *file_out, loff_t pos_out,
                                loff_t len, unsigned int remap_flags);
    int     (*fadvise)(struct file *, loff_t, loff_t, int);
    void    (*show_fdinfo)(struct seq_file *, struct file *);
};
```

`fop_flags` — не вказівник, а набір бітів (`FOP_*`), який раніше жив серед `FMODE_*`: чи можна виконувати метод без блокування, чи витримує драйвер паралельні прямі записи, чи вміє великі сторінки.

| поле | порожній вказівник означає |
|---|---|
| `llseek` | **відмова** `ESPIPE`. Це змінилося: колись порожнє поле означало типову реалізацію, а для відмови була окрема заглушка `no_llseek`. Її прибрали, і тепер порожнє поле **і є** відмовою — типову треба вказати явно (`generic_file_llseek`, `default_llseek` або `noop_llseek`, якщо позиція значення не має, але виклик має вдаватися) |
| `read` і `read_iter` | **відмова** `EINVAL`, коли порожні обидва. VFS нічого не підставляє: `generic_file_read_iter` треба вписати рукою. `read` має перевагу; `read_iter` обслуговує ще й вектори, `preadv2` та подання з кільця |
| `write` і `write_iter` | те саме — `EINVAL` на `write(2)` |
| `iterate_shared` | **відмова** `ENOTDIR` із `getdents64(2)`, навіть якщо inode справді каталог |
| `poll` | **підстановка** найгіршого можливого ґатунку: `select` і `poll` одразу кажуть «готовий і на читання, і на запис». Але покласти такий дескриптор в [epoll](book:unix-linux/select-poll-epoll) не вдасться — `epoll_ctl` відмовляє з `EPERM`. Ось чому звичайний файл у `epoll` не приймають: у нього немає `->poll` |
| `unlocked_ioctl` | **відмова** `ENOTTY` — те саме «Inappropriate ioctl for device». Код `ENOIOCTLCMD`, повернутий самим драйвером, ядро теж перетворює на `ENOTTY`, щоб назовні він не витік. Про сам канал — [ioctl](book:unix-linux/ioctl-interface) |
| `compat_ioctl` | 32-бітна програма на 64-бітному ядрі дістає `ENOTTY` на все, крім тих команд, що їх спільний код обробляє сам |
| `mmap` | **відмова** `ENODEV` із `mmap(2)`. Поле поступово заступає новіше `mmap_prepare`, яке працює з описом майбутнього відображення, а не з готовою областю. Про саме [відображення файлу в пам'ять](book:unix-linux/mmap-model) |
| `open` | **тиша**: відкриття вдається, драйвер про нього не дізнається |
| `flush` | **тиша**: `close(2)` повертає нуль. Це остання нагода віддати програмі помилку відкладеного запису, і мережеві файлові системи нею користуються |
| `release` | **тиша**: закриття останнього посилання минає без повідомлення драйверові |
| `fsync` | **відмова** `EINVAL` із `fsync(2)` і `fdatasync(2)`. Коли писати справді нічого, ставлять явну `noop_fsync` — «нічого не робимо, і це успіх». Про те, чому це важить, — [довговічність запису](book:unix-linux/page-cache-durability) |
| `fasync` | **тиша**: `O_ASYNC` вмикається, але `SIGIO` не надходить ніколи |
| `lock`, `flock` | **підстановка**: [замки](book:unix-linux/file-locking) VFS веде сам, у пам'яті цієї машини. Мережеві заповнюють, щоб замок дійшов до сервера, — інакше два клієнти «замикають» файл незалежно й обидва вважають, що виграли |
| `splice_read`, `splice_write` | **відмова** `EINVAL` (з рядком у журнал налагодження). Для звичайних файлів ставлять `filemap_splice_read` та `iter_file_splice_write`; без них не працює [передача без копіювання](book:unix-linux/zero-copy) |
| `fallocate` | **відмова** `EOPNOTSUPP` |
| `copy_file_range` | **підстановка**: VFS копіює сам, через канал у ядрі. Але якщо метод є в обох файлів і він **різний** — виклик відмовляє з `EXDEV`, бо швидкої дороги між різними драйверами немає |
| `remap_file_range` | **відмова** `EOPNOTSUPP` для `FICLONE` і `FIDEDUPERANGE` — [копій із поділом блоків](book:unix-linux/reflink-copies) не буде |
| `fadvise` | **підстановка**: `generic_fadvise` працює просто з кешем сторінок, і `POSIX_FADV_DONTNEED` справді викидає сторінки |
| `show_fdinfo` | **тиша**: у `/proc/PID/fdinfo/N` не з'явиться власних рядків драйвера |

## `address_space_operations`: сторінки файлу

Таблиця, якою файлова система під'єднується до кеша сторінок. Одиниця тут — не сторінка, а **folio**, група суміжних сторінок, яку кеш веде як ціле.

```c
struct address_space_operations {
    int  (*read_folio)(struct file *, struct folio *);
    void (*readahead)(struct readahead_control *);
    int  (*writepages)(struct address_space *, struct writeback_control *);
    bool (*dirty_folio)(struct address_space *, struct folio *);
    int  (*write_begin)(const struct kiocb *, struct address_space *,
                        loff_t pos, unsigned len, struct folio **, void **fsdata);
    int  (*write_end)(const struct kiocb *, struct address_space *,
                      loff_t pos, unsigned len, unsigned copied,
                      struct folio *, void *fsdata);
    sector_t (*bmap)(struct address_space *, sector_t);
    void (*invalidate_folio)(struct folio *, size_t start, size_t len);
    bool (*release_folio)(struct folio *, gfp_t);
    void (*free_folio)(struct folio *);
    ssize_t (*direct_IO)(struct kiocb *, struct iov_iter *);
    int  (*migrate_folio)(struct address_space *, struct folio *dst,
                          struct folio *src, enum migrate_mode);
    int  (*launder_folio)(struct folio *);
    bool (*is_partially_uptodate)(struct folio *, size_t from, size_t count);
    int  (*error_remove_folio)(struct address_space *, struct folio *);
};
```

| поле | порожній вказівник означає |
|---|---|
| `read_folio` | **обов'язковий** для всіх, хто взагалі користується кешем сторінок: типовим шляхам читання нема звідки взяти дані. Готова реалізація `mmap` це навіть перевіряє й відмовляє з несподіваним `ENOEXEC` |
| `readahead` | **підстановка**: [випереджувальне читання](book:unix-linux/readahead) зводиться до почергових викликів `read_folio` по одній групі. Працює, але дрібними запитами замість одного великого |
| `writepages` | **тиша**: брудні сторінки цього відображення не пише **ніхто**. Це не недогляд — саме так живуть tmpfs і символьні пристрої. Раніше тут була підстановка через `->writepage`, але це поле з таблиці прибрано, тож підстановки більше немає |
| `dirty_folio` | **обов'язковий, щойно ти поставив власну таблицю**: позначення сторінки брудною йде за вказівником без перевірки. Беруть одну з готових — `filemap_dirty_folio` для тих, хто без буферів, `block_dirty_folio` для тих, хто з ними, `noop_dirty_folio` для тих, кому нікуди писати |
| `write_begin`, `write_end` | пара для типового буферизованого запису: підготувати групу сторінок під зміну й прийняти скопійоване. Без них загальний шлях запису не працює |
| `bmap` | `FIBMAP` не працює і файл не можна віддати під підкачку |
| `invalidate_folio`, `release_folio`, `free_folio` | **тиша**: нічого свого до сторінок не прив'язано, звільняти нема чого |
| `direct_IO` | **відмова**, і рано: ядро не виставляє ознаку придатності до прямого вводу-виводу, тож `open(O_DIRECT)` завершується `EINVAL` ще до першого читання. Сучасні драйвери часто роблять [прямий ввід-вивід](book:unix-linux/buffered-and-direct-io) у власних `read_iter`/`write_iter` і виставляють ту ознаку самі в `->open` — тоді порожнє поле нічому не заважає |
| `migrate_folio` | **підстановка з пасткою**: запасна реалізація попереджає в журнал і **відмовляє з `EBUSY` на брудній сторінці**. Наслідок практичний — ущільнення пам'яті й видача суміжних областей спотикаються об ваші незаписані сторінки. Готові: `filemap_migrate_folio`, `buffer_migrate_folio` |
| `is_partially_uptodate` | часткове читання не оптимізують: читають групу цілком |
| `error_remove_folio` | апаратна помилка пам'яті в сторінці файлу не має тихого виходу — ядро не може просто викинути сторінку й перечитати її з носія |

## Готові реалізації замість власного коду

Більшість полів заповнюють не своїми функціями, а тим, що спільний шар уже написав. Ось відповідність, з якої варто починати:

| поле | готова функція |
|---|---|
| `llseek` для файлу в кеші сторінок | `generic_file_llseek` |
| `llseek`, коли позиція неістотна | `noop_llseek` |
| `read_iter`, `write_iter` | `generic_file_read_iter`, `generic_file_write_iter` |
| `splice_read`, `splice_write` | `filemap_splice_read`, `iter_file_splice_write` |
| `fsync`, коли писати нічого | `noop_fsync` |
| `permission` | `generic_permission` |
| `getattr` | `generic_fillattr` |
| `setattr` для файлової системи в пам'яті | `simple_setattr` |
| `statfs` | `simple_statfs` |
| `lookup`, коли дерево живе в кеші імен | `simple_lookup` |
| `drop_inode`, щоб не тримати inode без імен | `inode_just_drop` (колишня `generic_delete_inode`) |
| `kill_sb` для файлової системи без носія | `kill_anon_super` |
| `kill_sb` для файлової системи на пристрої | `kill_block_super` |
| `dirty_folio` | `filemap_dirty_folio`, `block_dirty_folio`, `noop_dirty_folio` |
| `migrate_folio` | `filemap_migrate_folio`, `buffer_migrate_folio` |

Для найпростішого випадку готові навіть цілі таблиці. Каталог, чий вміст цілком описано записами кеша імен, обходиться двома рядками:

```c
const struct inode_operations simple_dir_inode_operations = {
    .lookup = simple_lookup,
};

const struct file_operations simple_dir_operations = {
    .open           = dcache_dir_open,
    .release        = dcache_dir_close,
    .llseek         = dcache_dir_lseek,
    .read           = generic_read_dir,
    .iterate_shared = dcache_readdir,
    .fsync          = noop_fsync,
};
```

А файл, що живе просто в пам'яті, — чотирма:

```c
const struct address_space_operations ram_aops = {
    .read_folio  = simple_read_folio,
    .write_begin = simple_write_begin,
    .write_end   = simple_write_end,
    .dirty_folio = noop_dirty_folio,
};
```

Тож повний перелік того, що мусить бути своїм у найменшій файловій системі, яку взагалі можна змонтувати, короткий: `name`, `owner`, `init_fs_context` і `kill_sb` у типі; `lookup` і `iterate_shared` у таблицях кореневого каталогу — і ті двома готовими функціями; своя функція, що створює inode потрібного виду й підв'язує йому одну з наведених вище таблиць. `statfs` формально не обов'язковий, але без нього `df` дістає `ENOSYS`, тож його ставлять теж — майже завжди `simple_statfs`. Решту — а їх у цих шести таблицях під сотню — можна лишити порожніми, за умови, що ви точно знаєте, котре з них означає тишу, а котре `EPERM`.
