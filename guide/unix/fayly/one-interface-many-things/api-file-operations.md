# 📋 Таблиця операцій файлу: контракт struct file_operations

Структура ядра Linux `struct file_operations` є контрактом, через який віртуальна файлова система (VFS) спрямовує всі системні виклики роботи з дескрипторами до конкретних драйверів пристроїв, файлових систем, мережевих сокетів та каналів міжпроцесної взаємодії. Організація полів цієї таблиці, правила їхньої синхронізації та конвенції повернення кодів помилок визначають поліморфізм файлового інтерфейсу в ядрі.

Структура оголошена в заголовковому файлі ядра `<linux/fs.h>`. Кожен відкритий у системі файл представлений екземпляром `struct file`, поле `f_op` якого містить покажчик на статичний екземпляр `struct file_operations`.

## Повна структура інтерфейсу

Таблиця складається виключно з покажчиків на функції та покажчика на модуль-власник. Якщо підсистема або драйвер не підтримує певну операцію (наприклад, мережевий сокет не підтримує позиціювання `llseek`), відповідне поле залишається нульовим (`NULL`). Ядро перевіряє наявність покажчика перед викликом і повертає відповідний код помилки за замовчуванням (найчастіше `-EINVAL`, `-ENOTTY` або `-ESPIPE`).

```c
struct file_operations {
    struct module *owner;
    loff_t (*llseek) (struct file *, loff_t, int);
    ssize_t (*read) (struct file *, char __user *, size_t, loff_t *);
    ssize_t (*write) (struct file *, const char __user *, size_t, loff_t *);
    ssize_t (*read_iter) (struct kiocb *, struct iov_iter *);
    ssize_t (*write_iter) (struct kiocb *, struct iov_iter *);
    int (*iopoll)(struct kiocb *kiocb, struct io_comp_batch *, unsigned int flags);
    int (*iterate_shared) (struct file *, struct dir_context *);
    __poll_t (*poll) (struct file *, struct poll_table_struct *);
    long (*unlocked_ioctl) (struct file *, unsigned int, unsigned long);
    long (*compat_ioctl) (struct file *, unsigned int, unsigned long);
    int (*mmap) (struct file *, struct vm_area_struct *);
    int (*open) (struct inode *, struct file *);
    int (*flush) (struct file *, fl_owner_t id);
    int (*release) (struct inode *, struct file *);
    int (*fsync) (struct file *, loff_t, loff_t, int datasync);
    int (*fasync) (int, struct file *, int);
    int (*lock) (struct file *, int, struct file_lock *);
    unsigned long (*get_unmapped_area)(struct file *, unsigned long, unsigned long, unsigned long, unsigned long);
    int (*check_flags)(int);
    int (*flock) (struct file *, int, struct file_lock *);
    ssize_t (*splice_write)(struct pipe_inode_info *, struct file *, loff_t *, size_t, unsigned int);
    ssize_t (*splice_read)(struct file *, loff_t *, struct pipe_inode_info *, size_t, unsigned int);
    int (*setlease)(struct file *, int, struct file_lease **, void **);
    long (*fallocate)(struct file *file, int mode, loff_t offset, loff_t len);
    void (*show_fdinfo)(struct seq_file *m, struct file *f);
    ssize_t (*copy_file_range)(struct file *, loff_t, struct file *, loff_t, size_t, unsigned int);
    loff_t (*remap_file_range)(struct file *file_in, loff_t pos_in,
                               struct file *file_out, loff_t pos_out,
                               loff_t len, unsigned int remap_flags);
    int (*fadvise)(struct file *, loff_t, loff_t, int);
} __randomize_layout;
```

Атрибут `__randomize_layout` дозволяє компілятору випадково переставляти поля структури під час збирання ядра із увімкненим захистом GCC/Clang plugin `RANDSTRUCT`, що ускладнює експлуатацію вразливостей ядра через фіксовані зсуви покажчиків.

## Детальний опис методів та їхніх контрактів

### 1. `owner` (`struct module *`)

Покажчик на модуль ядра, що надав цю таблицю операцій (зазвичай ініціалізується макросом `THIS_MODULE`). VFS автоматично збільшує лічильник посилань модуля при відкритті файлу (`try_module_get()`) та зменшує при закритті (`module_put()`). Це запобігає вивантаженню модуля з пам'яті ядра (`rmmod`), поки його дескриптор використовується хоча б одним процесом. Для вбудованих підсистем ядра поле ініціалізується як `NULL`.

### 2. `llseek` (`loff_t (*)(struct file *file, loff_t offset, int whence)`)

Змінює поточну позицію читання/запису (`file->f_pos`). Викликається при зверненні до системного виклику `lseek(2)` або позиційованих операцій:

* `file`: дескриптор відкритого файлу;
* `offset`: величина зсуву у байтах (може бути від'ємною);
* `whence`: точка відліку (`SEEK_SET` — від початку файлу, `SEEK_CUR` — від поточної позиції, `SEEK_END` — від кінця файлу, `SEEK_DATA` — до наступного непорожнього блоку, `SEEK_HOLE` — до наступної дірки у розрідженому файлі).

Повертає нову абсолютну позицію у файлі або від'ємний код помилки (наприклад, `-ESPIPE` для непозиційовних об'єктів або `-EINVAL` при виході за межі допустимого діапазону). Для стандартних файлових систем ядро надає готові помічники `generic_file_llseek()` та `default_llseek()`. Якщо поле рівне `NULL`, ядро використовує `default_llseek()`, який змінює `f_pos` без консультації з драйвером. Якщо ж об'єкт у принципі не підтримує зсув (як-от сокети чи канали), драйвер явно встановлює `noop_llseek` або викликає `nonseekable_open()`, що гарантує повернення помилки `-ESPIPE`.

### 3. `read_iter` та `write_iter` (`ssize_t (*)(struct kiocb *iocb, struct iov_iter *to)`)

Сучасний векторний та асинхронний інтерфейс передачі даних. Усі виклики `read`, `write`, `pread`, `pwrite`, `readv`, `writev`, а також сучасні асинхронні інтерфейси вводу-виводу (`io_uring`, POSIX AIO `io_submit`) транслюються ядром у виклики цих двох методів:

* `iocb`: структура керування блоком операції (`struct kiocb`). Вона об'єднує покажчик на відкритий файл (`iocb->ki_filp`), позицію у файлі (`iocb->ki_pos`), прапорці виконання (`iocb->ki_flags`, зокрема `IOCB_NOWAIT`, `IOCB_DIRECT`, `IOCB_SYNC`), прапорець завершення для опитування `IOCB_HIPRI`, а також зворотний виклик завершення `iocb->ki_complete` для асинхронного сповіщення;
* `to` / `from`: ітератор векторного буфера (`struct iov_iter`), що абстрагує розташування та тип цільової пам'яті (пам'ять користувача `ITER_IOVEC`, сторінки фізичної пам'яті ядра `ITER_BVEC`, сторінки віртуальної пам'яті ядра `ITER_KVEC`, кільцеві буфери каналів `ITER_PIPE` або користувацькі буфери `ITER_UBUF`).

Повертає кількість успішно прочитаних або записаних байтів, від'ємний код помилки, або спеціальне значення `-EIOCBQUEUED` у випадку успішного асинхронного планування операції без негайного блокування. Традиційні скалярні методи `.read` та `.write` вважаються застарілими для високопродуктивних підсистем і підтримуються заради простоти дрібних символьних драйверів.

### 4. `iopoll` (`int (*)(struct kiocb *kiocb, struct io_comp_batch *, unsigned int flags)`)

Метод активного опитування завершення операцій асинхронного вводу-виводу без використання переривань (polling I/O для надшвидких NVMe накопичувачів та мережевих інтерфейсів). Викликається підсистемами на зразок `io_uring` у режимі `IORING_SETUP_IOPOLL`. Драйвер перевіряє черги апаратних дескрипторів контролера на наявність завершених запитів і сповіщає ядро, уникаючи затримок на обробку апаратних переривань та перемикання контексту.

### 5. `iterate_shared` (`int (*)(struct file *file, struct dir_context *ctx)`)

Читання списку записів каталогу (системні виклики `getdents(2)`, `getdents64(2)`). Працює під спільним блокуванням читача на рівні inode каталогу (`down_read(&inode->i_rwsem)`), що дозволяє кільком потокам одночасно читати вміст одного каталогу. Контекст `struct dir_context` містить поточну позицію ітератора `ctx->pos` та зворотний виклик `ctx->actor`, який файлова система викликає для кожного знайденого запису каталогу для заповнення буфера простору користувача.

### 6. `poll` (`__poll_t (*)(struct file *file, struct poll_table_struct *wait)`)

Забезпечує синхронне мультиплексування вводу-виводу для системних викликів `select(2)`, `poll(2)` та `epoll(7)`:

* `file`: відкритий файл;
* `wait`: таблиця очікування, в яку драйвер реєструє свої черги очікування подій (`wait_queue_head_t`) за допомогою функції `poll_wait()`.

Метод виконує дві фундаментальні дії:
1. Реєструє поточний процес у чергах очікування драйвера (якщо `wait != NULL`);
2. Обчислює та повертає бітову маску поточної готовності файлу (`EPOLLIN`, `EPOLLOUT`, `EPOLLERR`, `EPOLLHUP`, `EPOLLRDHUP`).

Якщо дані готові для негайного читання без блокування, драйвер повертає маску з піднятим бітом `EPOLLIN | EPOLLRDNORM`. Якщо вихідний буфер має вільне місце для запису — `EPOLLOUT | EPOLLWRNORM`. Якщо віддалена сторона закрила з'єднання — `EPOLLRDHUP | EPOLLHUP`.

### 7. `unlocked_ioctl` (`long (*)(struct file *file, unsigned int cmd, unsigned long arg)`)

Універсальний інтерфейс керування для команд, що виходять за межі потокової моделі читання/запису:

* `cmd`: 32-бітне число команди, сконструйоване за допомогою макросів `_IO()`, `_IOR()`, `_IOW()`, `_IOWR()`, які кодують тип магічного числа, порядковий номер операції, розмір структури аргументу та напрямок копіювання даних;
* `arg`: числовий аргумент або покажчик на структуру даних у просторі користувача.

Слово `unlocked` у назві історично підкреслює, що ядро викликає метод без захоплення застарілого глобального блокування ядра (Big Kernel Lock). Драйвер зобов'язаний сам забезпечити коректну гранулярну синхронізацію доступу до своїх внутрішніх структур. Повертає 0 або додатне число при успіху, або від'ємний код помилки (`-ENOTTY`, якщо команда не підтримується цим драйвером, `-EFAULT` при недійсному покажчику користувача, `-EINVAL` при некоректних параметрах).

### 8. `compat_ioctl` (`long (*)(struct file *file, unsigned int cmd, unsigned long arg)`)

Викликається тоді, коли 32-бітна прикладна програма виконує системний виклик `ioctl` на 64-бітному ядрі. Необхідний для трансляції структур даних, що містять покажчики або типи `long`, чий розмір та правила вирівнювання пам'яті різняться між 32-бітним та 64-бітним ABI. Якщо структури повністю бінарно сумісні, драйвер призначає сюди ту саму функцію, що й для `unlocked_ioctl`.

### 9. `mmap` (`int (*)(struct file *file, struct vm_area_struct *vma)`)

Створює відображення вмісту файлу або апаратної пам'яті пристрою у віртуальний адресний простір процесу:

* `vma`: дескриптор регіону віртуальної пам'яті процесу (`struct vm_area_struct`), сформований підсистемою керування пам'яттю ядра для діапазону адрес виклику `mmap(2)`.

Драйвер або файлова система зазвичай ініціалізує поле `vma->vm_ops` власною таблицею операцій віртуальної пам'яті (`struct vm_operations_struct`), зокрема обробником сторінкових збоїв `.fault`, або безпосередньо відображає діапазон фізичних адрес чи пам'яті вводу-виводу (MMIO) за допомогою `remap_pfn_range()` чи `io_remap_pfn_range()`. Повертає 0 при успішному налаштуванні відображення або від'ємний код помилки (`-ENODEV`, `-EINVAL`, `-EAGAIN`).

### 10. `open` (`int (*)(struct inode *inode, struct file *file)`)

Викликається VFS у момент відкриття файлу після успішної перевірки прав доступу на рівні inode:

* `inode`: вузол файлової системи, що представляє відкриваний об'єкт;
* `file`: щойно створений екземпляр опису відкритого файлу.

У цьому методі драйвер зазвичай:
1. Знаходить власну структуру даних пристрою через `inode->i_cdev` або аналіз номерів `iminor(inode)`, `imajor(inode)`;
2. Зберігає покажчик на структуру екземпляра у приватному полі `file->private_data`;
3. Ініціалізує апаратний стан пристрою (якщо це перше відкриття);
4. Налаштовує специфічні прапорці роботи.

Повертає 0 при успіху або від'ємний код помилки. Якщо метод повертає помилку, VFS негайно знищує `struct file` і повертає помилку у простір користувача.

### 11. `release` (`int (*)(struct inode *inode, struct file *file)`)

Викликається тоді, коли лічильник посилань на `struct file` (`file->f_count`) досягає нуля — тобто коли закрився останній дескриптор, що посилався на цей опис відкритого файлу (після всіх викликів `close()`, дублювання `dup()` та завершення процесів після `fork()`).

Тут драйвер звільняє ресурси, виділені у `.open`, очищає `file->private_data`, зупиняє передавання апаратних даних або скидає буфери. На відміну від системного виклику `close(2)` у просторі користувача, метод ядра `.release` викликається рівно один раз на весь життєвий цикл опису файлу і не може повернути помилку (його повертане значення ігнорується VFS).

### 12. `fsync` (`int (*)(struct file *file, loff_t start, loff_t end, int datasync)`)

Забезпечує примусове скидання брудних сторінок кешу та метаданих файлу на постійний фізичний носій (виклики `fsync(2)` та `fdatasync(2)`):

* `start`, `end`: діапазон байтів для скидання;
* `datasync`: прапорець, що дорівнює 1 для виклику `fdatasync` (скидати лише сторінки даних та критичні метадані, необхідні для читання, такі як розмір файлу `i_size`, ігноруючи другорядні метадані на зразок часу модифікації `mtime`).

### 13. `fasync` (`int (*)(int fd, struct file *file, int on)`)

Підтримка асинхронного сповіщення процесу через сигнал `SIGIO` / `SIGURG` при появі нових даних (асинхронний ввід-вивід за стандартом POSIX, що налаштовується прапорцем `O_ASYNC` через `fcntl(F_SETFL)`). Драйвер використовує стандартний помічник ядра `fasync_helper()` для керування чергою процесів-одержувачів сигналу.

### 14. `splice_read` та `splice_write`

Забезпечують високоефективне передавання даних без проміжного копіювання (zero-copy) між файлом та анонімним каналом (системні виклики `splice(2)`, `vmsplice(2)`, `tee(2)` та `sendfile(2)`). Замість перенесення байтів через буфери простору користувача ядро передає покажчики на сторінки фізичної пам'яті `struct page` безпосередньо у кільцевий буфер каналу `struct pipe_inode_info`.

### 15. `fallocate` (`long (*)(struct file *file, int mode, loff_t offset, loff_t len)`)

Безпосереднє попереднє виділення фізичних блоків на диску або звільнення простору (виклики `fallocate(2)` та `posix_fallocate(3)`). Режими керування включають:
* `FALLOC_FL_KEEP_SIZE`: виділити дискові блоки, не змінюючи видимий розмір файлу `i_size`;
* `FALLOC_FL_PUNCH_HOLE`: звільнити дискові блоки у вказаному діапазоні, перетворюючи його на розріджену «дірку» без видалення файлу;
* `FALLOC_FL_COLLAPSE_RANGE` / `FALLOC_FL_INSERT_RANGE`: видалення або вставка діапазону байтів зі зсувом фізичних екстентів без перезапису даних.

### 16. `copy_file_range` та `remap_file_range`

Апаратне та файлове копіювання блоків на рівні накопичувача (server-side copy, reflinks, copy-on-write клонування файлів у файлових системах Btrfs, XFS, NFSv4, SMB3). Дозволяє дублювати гігабайти даних за частки мілісекунди шляхом створення спільних посилань на фізичні екстенти замість їхнього вичитування та повторного запису.

### 17. `show_fdinfo` (`void (*)(struct seq_file *m, struct file *f)`)

Викликається ядром під час читання псевдофайлу `/proc/[pid]/fdinfo/[fd]`. Дозволяє драйверу або підсистемі експортувати специфічну діагностичну інформацію про стан дескриптора (наприклад, прапорці підписки `epoll`, маску зареєстрованих сигналів для `signalfd`, позицію лічильника `eventfd` або налаштування годинника `timerfd`).

## Реалізація таблиці різними підсистемами ядра

Різні типи системних об'єктів підключаються до VFS через спеціалізовані екземпляри `struct file_operations`. Таблиця нижче демонструє, як ключові підсистеми ядра реалізують ці операції:

| Операція | Регулярний файл (Ext4) | Мережевий сокет (Socket) | Анонімний канал (Pipe) | Символьний пристрій (UART) | Блоковий пристрій (/dev/sda) |
|---|---|---|---|---|---|
| `llseek` | `ext4_file_llseek` | `no_llseek` (`-ESPIPE`) | `no_llseek` (`-ESPIPE`) | `noop_llseek` / `NULL` | `block_llseek` |
| `read_iter` | `ext4_file_read_iter` | `sock_read_iter` | `pipe_read` | `tty_read` | `blkdev_read_iter` |
| `write_iter` | `ext4_file_write_iter` | `sock_write_iter` | `pipe_write` | `tty_write` | `blkdev_write_iter` |
| `poll` | `NULL` (завжди готовий) | `sock_poll` | `pipe_poll` | `tty_poll` | `NULL` (завжди готовий) |
| `unlocked_ioctl` | `ext4_ioctl` | `sock_ioctl` | `pipe_ioctl` | `tty_ioctl` | `blkdev_ioctl` |
| `mmap` | `ext4_file_mmap` | `sock_no_mmap` (`-ENODEV`) | `NULL` (`-ENODEV`) | `NULL` або власна пам'ять | `generic_file_mmap` |
| `open` | `ext4_file_open` | `sock_no_open` | `NULL` | `chrdev_open` → driver `.open` | `blkdev_open` |
| `release` | `ext4_release_file` | `sock_close` | `pipe_release` | driver `.release` | `blkdev_release` |
| `fsync` | `ext4_sync_file` | `no_fsync` (`-EINVAL`) | `NULL` (`-EINVAL`) | `NULL` | `blkdev_fsync` |
| `splice_read` | `filemap_splice_read` | `sock_splice_read` | `copy_splice_read` | `NULL` | `filemap_splice_read` |
| `fallocate` | `ext4_fallocate` | `NULL` (`-EOPNOTSUPP`) | `NULL` (`-ESPIPE`) | `NULL` (`-ENODEV`) | `blkdev_fallocate` |

## Конвенція кодів повернення та обробки помилок

Методи `struct file_operations` використовують строгу конвенцію ядра Linux:

1. **Успішне читання або запис**: повертається додатне число — кількість фактично оброблених байтів (`> 0`).
2. **Кінець потоку даних (EOF)**: методи читання повертають `0`.
3. **Помилка**: повертається від'ємне значення коду помилки (`-errno`), наприклад `-EFAULT`. Шар системних викликів VFS перехоплює це від'ємне число, записує його абсолютне значення у змінну `errno` потоку простору користувача і повертає `-1` у прикладну програму.

Основні коди помилок у методах VFS:

* `-EAGAIN` / `-EWOULDBLOCK`: операція не може бути виконана негайно у неблокуючому режимі (`O_NONBLOCK`).
* `-EINTR`: виконання виклику перервано надходженням сигналу до того, як вдалося передати бодай один байт даних.
* `-EFAULT`: покажчик на буфер простору користувача вказує на недійсну або недоступну для читання/запису пам'ять (помилка `copy_to_user()` / `copy_from_user()`).
* `-ESPIPE`: спроба виконати позиціювання (`lseek`) на об'єкті, що є непозиційовним потоком (канал, сокет, FIFO).
* `-ENODEV`: операція не підтримується цим типом об'єкта (наприклад, спроба виклику `mmap` на мережевому сокеті).
* `-ENOTTY`: виклик `ioctl` передав код команди, якого драйвер не знає (історична назва «Not a typewriter»).
* `-EPIPE`: спроба запису в канал або сокет, у якого закрито сторону читання (супроводжується надсиланням процесу сигналу `SIGPIPE`).
* `-EBUSY`: ресурс або апаратний пристрій зайнятий ексклюзивним використанням іншим потоком.
* `-EOPNOTSUPP` / `-ENOSYS`: операція не реалізована драйвером або файловою системою.

## Правила синхронізації та інваріанти

При реалізації обробників `struct file_operations` драйвер зобов'язаний дотримуватися фундаментальних інваріантів ядра:

1. **Паралельне виконання**: VFS може одночасно викликати `.read_iter`, `.write_iter` та `.unlocked_ioctl` для одного й того самого `struct file` з різних процесорних ядер (наприклад, якщо дескриптор розділено між кількома потоками або процесами після `fork()`). Усі спільні змінні драйвера мають бути захищені спінлоками (`spinlock_t`) або м'ютексами (`struct mutex`).
2. **Синхронізація позиції (`f_pos_lock`)**: VFS автоматично захоплює м'ютекс `file->f_pos_lock` під час викликів, що модифікують поточну позицію файлу (`read`, `write`, `lseek`), якщо об'єкт не має встановленого прапорця `FMODE_ATOMIC_POS` або якщо кілька потоків одночасно звертаються до одного опису файлу. Це гарантує атомарність послідовних зсувів.
3. **Безпечний доступ до пам'яті користувача**: драйвер ніколи не повинен розіменовувати покажчики простору користувача напряму. Доступ виконується виключно через ітератори `iov_iter` або функції `copy_to_user()`, `copy_from_user()`, `get_user()`, `put_user()`. Вони обробляють сторінкові збої ядра та захищають від некоректних або ворожих адрес.
4. **Контекст сну**: методи `.read_iter`, `.write_iter`, `.unlocked_ioctl`, `.open`, `.release` викликаються у контексті процесу (process context) і мають право блокуватися (засинати в очікуванні м'ютекса, сторінки кешу або завершення апаратного переривання). Натомість обробники апаратних переривань (hard IRQ) ніколи не звертаються до `struct file_operations` напряму.

## Приклад: повноцінний скелет символьного драйвера

Нижче наведено мінімальний робочий модуль ядра, що реєструє власну таблицю `file_operations` для взаємодії з простором користувача через символьний пристрій `/dev/mychardev`:

```c
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/cdev.h>
#include <linux/slab.h>
#include <linux/poll.h>

#define DEVICE_NAME "mychardev"
#define BUFFER_SIZE 1024

static dev_t dev_num;
static struct cdev my_cdev;
static char device_buffer[BUFFER_SIZE];
static size_t data_size = 0;
static DEFINE_MUTEX(dev_mutex);
static DECLARE_WAIT_QUEUE_HEAD(read_queue);

static int dev_open(struct inode *inodep, struct file *filep)
{
    pr_info("mychardev: пристрій відкрито pid=%d\n", current->pid);
    return 0;
}

static int dev_release(struct inode *inodep, struct file *filep)
{
    pr_info("mychardev: пристрій закрито\n");
    return 0;
}

static ssize_t dev_read(struct file *filep, char __user *buffer, size_t len, loff_t *offset)
{
    ssize_t bytes_to_read;

    if (mutex_lock_interruptible(&dev_mutex))
        return -ERESTARTSYS;

    while (data_size == 0) {
        mutex_unlock(&dev_mutex);
        if (filep->f_flags & O_NONBLOCK)
            return -EAGAIN;
        if (wait_event_interruptible(read_queue, data_size > 0))
            return -ERESTARTSYS;
        if (mutex_lock_interruptible(&dev_mutex))
            return -ERESTARTSYS;
    }

    if (*offset >= data_size) {
        mutex_unlock(&dev_mutex);
        return 0; /* EOF */
    }

    bytes_to_read = min(len, (size_t)(data_size - *offset));

    if (copy_to_user(buffer, device_buffer + *offset, bytes_to_read) != 0) {
        mutex_unlock(&dev_mutex);
        return -EFAULT;
    }

    *offset += bytes_to_read;
    mutex_unlock(&dev_mutex);

    return bytes_to_read;
}

static ssize_t dev_write(struct file *filep, const char __user *buffer, size_t len, loff_t *offset)
{
    ssize_t bytes_to_write;

    if (mutex_lock_interruptible(&dev_mutex))
        return -ERESTARTSYS;

    bytes_to_write = min(len, (size_t)(BUFFER_SIZE - *offset));
    if (bytes_to_write <= 0) {
        mutex_unlock(&dev_mutex);
        return -ENOSPC;
    }

    if (copy_from_user(device_buffer + *offset, buffer, bytes_to_write) != 0) {
        mutex_unlock(&dev_mutex);
        return -EFAULT;
    }

    *offset += bytes_to_write;
    if (*offset > data_size)
        data_size = *offset;

    wake_up_interruptible(&read_queue);
    mutex_unlock(&dev_mutex);
    return bytes_to_write;
}

static __poll_t dev_poll(struct file *filep, struct poll_table_struct *wait)
{
    __poll_t mask = 0;

    poll_wait(filep, &read_queue, wait);

    mutex_lock(&dev_mutex);
    if (data_size > 0)
        mask |= EPOLLIN | EPOLLRDNORM;
    if (data_size < BUFFER_SIZE)
        mask |= EPOLLOUT | EPOLLWRNORM;
    mutex_unlock(&dev_mutex);

    return mask;
}

static loff_t dev_llseek(struct file *filep, loff_t offset, int whence)
{
    loff_t new_pos;

    if (mutex_lock_interruptible(&dev_mutex))
        return -ERESTARTSYS;

    switch (whence) {
    case SEEK_SET:
        new_pos = offset;
        break;
    case SEEK_CUR:
        new_pos = filep->f_pos + offset;
        break;
    case SEEK_END:
        new_pos = data_size + offset;
        break;
    default:
        mutex_unlock(&dev_mutex);
        return -EINVAL;
    }

    if (new_pos < 0 || new_pos > BUFFER_SIZE) {
        mutex_unlock(&dev_mutex);
        return -EINVAL;
    }

    filep->f_pos = new_pos;
    mutex_unlock(&dev_mutex);
    return new_pos;
}

static const struct file_operations fops = {
    .owner          = THIS_MODULE,
    .open           = dev_open,
    .release        = dev_release,
    .read           = dev_read,
    .write          = dev_write,
    .poll           = dev_poll,
    .llseek         = dev_llseek,
};

static int __init mychardev_init(void)
{
    int ret;

    ret = alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);
    if (ret < 0)
        return ret;

    cdev_init(&my_cdev, &fops);
    my_cdev.owner = THIS_MODULE;

    ret = cdev_add(&my_cdev, dev_num, 1);
    if (ret < 0) {
        unregister_chrdev_region(dev_num, 1);
        return ret;
    }

    pr_info("mychardev: зареєстровано з major = %d, minor = %d\n",
            MAJOR(dev_num), MINOR(dev_num));
    return 0;
}

static void __exit mychardev_exit(void)
{
    cdev_del(&my_cdev);
    unregister_chrdev_region(dev_num, 1);
    pr_info("mychardev: модуль вивантажено\n");
}

module_init(mychardev_init);
module_exit(mychardev_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Unix Architecture Guide");
MODULE_DESCRIPTION("Приклад реалізації struct file_operations для символьного драйвера");
```

## Діагностика та трасування таблиці операцій

У робочій системі дізнатися, які саме функції з `struct file_operations` викликаються для конкретного дескриптора, можна кількома інструментами діагностики:

1. **Перевірка типу та стану дескриптора через `/proc/[pid]/fdinfo/[fd]`**:
   Псевдофайл показує позицію `pos`, прапорці `flags` у вісімковій системі числення, прапорці монтування та специфічні поля драйвера:
   ```sh
   cat /proc/$$/fdinfo/0
   # pos:    0
   # flags:  0100002
   # mnt_id: 28
   # ino:    14
   ```

2. **Трасування викликів через ftrace або bpftrace**:
   Можна динамічно відстежувати розіменування покажчика `file->f_op->read_iter` або час виконання конкретної реалізації:
   ```sh
   bpftrace -e 'kprobe:vfs_read { printf("PID %d читає через f_op %p\n", pid, ((struct file *)arg0)->f_op); }'
   ```

3. **Пошук адрес у таблиці символів ядра `/proc/kallsyms`**:
   Адресу таблиці `ext4_file_operations`, `socket_file_ops` чи драйвера пристрою можна зіставити з покажчиком у дампі пам'яті:
   ```sh
   grep "ext4_file_operations" /proc/kallsyms
   # ffffffff824b2140 r ext4_file_operations
   ```

Така організація таблиці операцій дозволяє VFS досягати максимальної швидкодії динамічного зв'язування з нульовими накладними витратами на синтаксичні перевірки типу в системних викликах ядра.
