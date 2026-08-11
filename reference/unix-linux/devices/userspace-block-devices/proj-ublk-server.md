# ⚙️ Найпростіший сервер ublk власноруч

Двісті рядків C — і `/dev/ublkb0` стає вікном у звичайний файл: усе, що на цьому пристрої читають і пишуть, проходить через наш процес. Замінити `loop` тут не мета; мета — побачити каркас цілком, бо саме в нього потім вставляють справжню логіку: розшифрування, дедуплікацію, похід у мережеве сховище. Файл-підкладка — найдешевша заглушка, на якій видно, що каркас справді працює: `mkfs`, `mount` і все, що потім на цей пристрій навантажать, мають поводитися буденно.

## Задум: два кільця, одна черга, один потік

Кілець мусить бути два, і це не примха. Керуючі команди йдуть у `/dev/ublk-control`, і кожна несе `struct ublksrv_ctrl_cmd` — тридцять два байти. У звичайному 64-байтовому елементі подання io_uring під корисне навантаження команди відведено рівно шістнадцять байтів, тож керуюче кільце створюють із прапорцем `IORING_SETUP_SQE128`: елементи стають удвічі більші, і структура вміщається. Робоче кільце ходить у `/dev/ublkc0` і несе `struct ublksrv_io_cmd` на шістнадцять байтів — йому звичайного розміру досить.

Черга одна, потік один. Це не спрощення заради стислості: драйвер запам'ятовує, який саме потік озброїв теги черги, і команди від будь-якого іншого потоку відхиляє. Кілька черг означало б кілька потоків, кожен зі своїм кільцем — і жодного нового поняття, лише повторення того самого. [io_uring](book:unix-linux/io-uring) тут не прискорювач, а сам канал: у нього, крім читань і записів, можна класти операцію `IORING_OP_URING_CMD` — довільне доручення драйверові, з яким сервер уже й розмовляє.

Порядок кроків при запуску жорсткий, і кожен крок додає в системі рівно одну річ.

![Шість кроків запуску сервера ublk і те, що існує в системі після кожного з них](/reference/unix-linux/devices/userspace-block-devices/img/startup-order.svg)

*Символьний вузол з'являється після `ADD_DEV`, блоковий — аж після `START_DEV`; між ними мусять поміститися параметри, відображення описів і озброєння всіх тегів.*

Найважливіше тут — передостанній крок. `START_DEV` не повертає керування, доки кожен тег кожної черги не має озброєної команди: драйвер лічить готові теги й вважає чергу готовою лише тоді, коли їх рівно на глибину черги. Тому `FETCH_REQ` подають **до** `START_DEV`. Інакше блоковий вузол з'явився б раніше, ніж є кому відповідати.

Наш єдиний потік від цього не застрягає. `io_uring_submit` лише передає ядру озброєні команди й одразу повертається: команди лишаються в польоті — не завершені, а такі, що чекають на свій запит, — і лічильник готових тегів уже повний, коли черга доходить до керуючої команди. Разом зі `START_DEV` передають ідентифікатор процесу-демона: за ним ядро потім упізнає, чий саме відхід означає, що обслуговувати пристрій більше нема кому.

## Керуюча команда

```c
/* ublk-file.c — блоковий пристрій, за яким стоїть звичайний файл.
 *   cc -O2 -o ublk-file ublk-file.c -luring
 *   sudo modprobe ublk_drv && sudo ./ublk-file /srv/backing.img          */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <signal.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <linux/ublk_cmd.h>
#include <liburing.h>

#define QDEPTH     64                /* тегів у черзі — стільки запитів у польоті */
#define IO_BUF_SZ  (256u * 1024)     /* стеля одного запиту */
#define LOG_BS     4096u             /* логічний блок пристрою */

static struct io_uring ctrl_ring, io_ring;
static struct ublksrv_ctrl_dev_info info;
static const struct ublksrv_io_desc *desc;      /* спільна ділянка описів */
static char *buf[QDEPTH];                       /* по буферу на кожен тег */
static int ctrl_fd, cdev_fd, backing_fd;
static volatile sig_atomic_t stopping;

/* Одна керуюча команда: заповнити структуру, подати, дочекатися відповіді. */
static int ctrl_cmd(__u32 cmd_op, void *payload, __u16 len, __u64 data0)
{
        struct io_uring_sqe *sqe = io_uring_get_sqe(&ctrl_ring);
        struct ublksrv_ctrl_cmd *c;
        struct io_uring_cqe *cqe;
        int ret;

        memset(sqe, 0, 128);                    /* елемент тут 128-байтовий */
        sqe->opcode = IORING_OP_URING_CMD;
        sqe->fd     = ctrl_fd;
        sqe->cmd_op = cmd_op;

        c = (struct ublksrv_ctrl_cmd *)sqe->cmd;
        c->dev_id   = info.dev_id;
        c->queue_id = (__u16)-1;                /* команда не про окрему чергу */
        c->addr     = (__u64)(uintptr_t)payload;
        c->len      = len;
        c->data[0]  = data0;

        if (io_uring_submit(&ctrl_ring) < 0 ||
            io_uring_wait_cqe(&ctrl_ring, &cqe) < 0)
                return -EIO;
        ret = cqe->res;                         /* від'ємне — це −errno драйвера */
        io_uring_cqe_seen(&ctrl_ring, cqe);
        return ret;
}
```

Команди тут ходять у так званому ioctl-кодованому вигляді (`UBLK_U_CMD_*`, `UBLK_U_IO_*`): номер команди упакований разом із розміром і напрямком її структури, як у звичайному `ioctl`. Старіші ядра знали лише голі номери; чи вміє ядро нову форму, питають командою `UBLK_U_CMD_GET_FEATURES`.

## Створення пристрою й геометрія

```c
/* Пристрій існує як символьний вузол, геометрія оголошена. */
static int setup_device(__u64 bytes)
{
        struct ublk_params p;
        int ret;

        info.nr_hw_queues     = 1;
        info.queue_depth      = QDEPTH;
        info.max_io_buf_bytes = IO_BUF_SZ;
        info.dev_id           = (__u32)-1;      /* номер хай вибере ядро */

        ret = ctrl_cmd(UBLK_U_CMD_ADD_DEV, &info, sizeof(info), 0);
        if (ret < 0)
                return ret;                     /* тепер info.dev_id — справжній */

        memset(&p, 0, sizeof(p));
        p.len   = sizeof(p);
        p.types = UBLK_PARAM_TYPE_BASIC;
        p.basic.attrs             = UBLK_ATTR_VOLATILE_CACHE | UBLK_ATTR_FUA;
        p.basic.logical_bs_shift  = 12;         /* 4 КіБ — під вирівнювання O_DIRECT */
        p.basic.physical_bs_shift = 12;
        p.basic.io_min_shift      = 12;
        p.basic.io_opt_shift      = 12;
        p.basic.max_sectors       = IO_BUF_SZ / 512;
        p.basic.dev_sectors       = (bytes / LOG_BS) * (LOG_BS / 512);

        return ctrl_cmd(UBLK_U_CMD_SET_PARAMS, &p, sizeof(p), 0);
}
```

`ADD_DEV` — команда «туди й назад»: ядро вписує виданий номер у ту саму структуру, і всі подальші імена будуються з нього.

Два рішення тут потім не переграти. Перше: `UBLK_ATTR_VOLATILE_CACHE` оголошує, що в пристрою є непостійний кеш запису, — і лише після цього до нас узагалі почнуть приходити `FLUSH`, а `UBLK_ATTR_FUA` набуде сенсу. Не оголосив кеш — блоковий шар вважає кожен твій успішний запис уже довговічним і жодного [`fsync`](book:unix-linux/page-cache-durability) до сервера не донесе. Друге: логічний блок у 4 КіБ узято не заради швидкості, а щоб усі запити приходили вирівняними так, як вимагає `O_DIRECT` на підкладці. Ємність при цьому однаково рахується в 512-байтових секторах — це наскрізна домовленість блокового шару, і `start_sector` з `nr_sectors` в описі запиту теж у них.

## Канал

```c
/* Описи — у спільній пам'яті; буфери — наші й на весь час життя пристрою. */
static int open_channel(void)
{
        const long   page   = sysconf(_SC_PAGESIZE);
        /* крок між чергами — МАКСИМАЛЬНА глибина, а не наша: 4096 × 32 Б = 128 КіБ */
        const size_t stride = UBLK_MAX_QUEUE_DEPTH * sizeof(struct ublksrv_io_desc);
        size_t len = QDEPTH * sizeof(struct ublksrv_io_desc);
        char path[64];
        unsigned t;

        len = (len + page - 1) & ~(size_t)(page - 1);
        snprintf(path, sizeof(path), "/dev/ublkc%u", info.dev_id);
        if ((cdev_fd = open(path, O_RDWR)) < 0)
                return -errno;

        desc = mmap(NULL, len, PROT_READ, MAP_SHARED | MAP_POPULATE,
                    cdev_fd, UBLKSRV_CMD_BUF_OFFSET + 0 * stride);   /* черга 0 */
        if (desc == MAP_FAILED)
                return -errno;

        for (t = 0; t < QDEPTH; t++) {
                if (posix_memalign((void **)&buf[t], page, IO_BUF_SZ))
                        return -ENOMEM;
                mlock(buf[t], IO_BUF_SZ);
        }
        return io_uring_queue_init(QDEPTH, &io_ring, 0);
}
```

Рядок зі `stride` вартий години налагодження, якщо його не помітити. Драйвер вираховує номер черги зі зсуву в `mmap` діленням саме на максимальний розмір ділянки описів — а не на той, що відповідає вашій глибині. Порахуєте від своєї шістдесят четвірки — і черга 1 відобразиться туди, де черги немає. Ділянку беремо лише на читання: описи заповнює ядро, серверові там нічого міняти.

> 🔧 **Навіщо це.** `mlock` і `posix_memalign` наперед виглядають як передчасна оптимізація, але вони тут із іншої причини. Сервер стоїть у шляху запису на пристрій, і серед цих записів бувають ті, що їх ядро робить, вивільняючи пам'ять. Якщо на шляху обробки запиту сервер попросить пам'яті, а вільної немає, ядро піде вивільняти її записом — на цей самий пристрій. Коло замикається, і машина стає. Тому все, що знадобиться, виділяють і закріплюють до `START_DEV`, а в гарячому шляху не звертаються по пам'ять взагалі.

Ціна цієї домовленості рахується в один рядок:

```
буфери  64 теги × 256 КіБ = 16 МіБ закріпленої пам'яті
описи   64 теги ×  32 Б   = 2 КіБ — одна сторінка спільної ділянки
```

Подвоєння глибини черги подвоює й закріплену пам'ять, і платить її сервер увесь час, поки пристрій живий. Тому глибину беруть за справжнім паралелізмом сховища під сервером, а не «щоб було з запасом».

## Обслуговування

```c
/* Одна команда на тег: озброїти вперше або віддати вердикт і озброїти знову. */
static void arm(unsigned tag, __u32 cmd_op, int result)
{
        struct io_uring_sqe *sqe = io_uring_get_sqe(&io_ring);
        struct ublksrv_io_cmd *c;

        io_uring_prep_rw(IORING_OP_URING_CMD, sqe, cdev_fd, NULL, 0, 0);
        sqe->cmd_op = cmd_op;           /* лежить там само, де off, — тому ПІСЛЯ prep */

        c = (struct ublksrv_io_cmd *)sqe->cmd;
        c->q_id   = 0;
        c->tag    = (__u16)tag;
        c->result = result;
        c->addr   = (__u64)(uintptr_t)buf[tag];
        io_uring_sqe_set_data64(sqe, tag);
}

/* Тут і тільки тут живе «що це за сховище». Решта файлу — обв'язка. */
static int serve(const struct ublksrv_io_desc *iod, char *b)
{
        __u32  op  = iod->op_flags & 0xff;
        off_t  off = (off_t)iod->start_sector * 512;
        size_t len = (size_t)iod->nr_sectors * 512;
        ssize_t n;

        switch (op) {
        case UBLK_IO_OP_READ:
                n = pread(backing_fd, b, len, off);
                return n < 0 ? -errno : (int)n;

        case UBLK_IO_OP_WRITE:
                n = pwrite(backing_fd, b, len, off);
                if (n < 0)
                        return -errno;
                if (iod->op_flags & UBLK_IO_F_FUA)       /* «на носій — до відповіді» */
                        if (fdatasync(backing_fd) < 0)
                                return -errno;
                return (int)n;

        case UBLK_IO_OP_FLUSH:                           /* хтось нагорі покликав fsync */
                return fdatasync(backing_fd) < 0 ? -errno : 0;

        default:
                return -EOPNOTSUPP;
        }
}
```

## Головний цикл

```c
static void on_signal(int sig) { (void)sig; stopping = 1; }

int main(int argc, char **argv)
{
        struct io_uring_params cp = { .flags = IORING_SETUP_SQE128 };
        struct sigaction sa = { .sa_handler = on_signal };  /* без SA_RESTART: */
        struct stat st;                                     /* щоб очікування урвалося */
        unsigned t;
        int ret;

        if (argc != 2)
                return fprintf(stderr, "вжиток: %s <файл-підкладка>\n", argv[0]), 2;

        /* O_DIRECT: наші читання й записи не залежать від кешу сторінок */
        backing_fd = open(argv[1], O_RDWR | O_DIRECT);
        if (backing_fd < 0 || fstat(backing_fd, &st) < 0)
                return perror("підкладка"), 1;
        if ((ctrl_fd = open("/dev/ublk-control", O_RDWR)) < 0)
                return perror("/dev/ublk-control"), 1;
        io_uring_queue_init_params(32, &ctrl_ring, &cp);

        if ((ret = setup_device(st.st_size)) < 0)
                return fprintf(stderr, "створення: %s\n", strerror(-ret)), 1;
        if ((ret = open_channel()) < 0) {
                fprintf(stderr, "канал: %s\n", strerror(-ret));
                goto del;
        }

        for (t = 0; t < QDEPTH; t++)
                arm(t, UBLK_U_IO_FETCH_REQ, 0);
        io_uring_submit(&io_ring);              /* усі теги озброєні */

        sigaction(SIGINT, &sa, NULL);
        sigaction(SIGTERM, &sa, NULL);

        if ((ret = ctrl_cmd(UBLK_U_CMD_START_DEV, NULL, 0, (__u64)getpid())) < 0) {
                fprintf(stderr, "запуск: %s\n", strerror(-ret));
                goto del;
        }
        printf("/dev/ublkb%u живий; Ctrl-C — зупинити\n", info.dev_id);

        while (!stopping) {
                struct io_uring_cqe *cqe;
                unsigned tag;
                int res;

                if (io_uring_wait_cqe(&io_ring, &cqe) < 0)
                        break;                  /* сигнал урвав очікування */
                tag = (unsigned)io_uring_cqe_get_data64(cqe);
                res = cqe->res;
                io_uring_cqe_seen(&io_ring, cqe);

                if (res < 0)                    /* −ENODEV: пристрій зупиняють */
                        break;

                arm(tag, UBLK_U_IO_COMMIT_AND_FETCH_REQ, serve(&desc[tag], buf[tag]));
                io_uring_submit(&io_ring);
        }

        ctrl_cmd(UBLK_U_CMD_STOP_DEV, NULL, 0, 0);   /* блоковий вузол зникає */
del:
        ctrl_cmd(UBLK_U_CMD_DEL_DEV, NULL, 0, 0);    /* номер вивільняється */
        return 0;
}
```

Цикл читається як одне речення: прокинулися, взяли тег, глянули в комірку, зробили роботу, віддали вердикт і тим самим рухом стали в чергу знову. Ані `read`, ані `write` на каналі немає — усе перенесення робить пара «команда в кільці плюс спільна ділянка». Поле `c->addr` в `arm` при цьому стосується не того запиту, який щойно закінчили, а наступного: підтвердження й озброєння — одна операція, тож адресу буфера ми називаємо наперед.

## Один запит наскрізь

**Умова.** Файлова система над `/dev/ublkb0` скидає 32 КіБ за зсувом 1 МіБ; блоковий шар дав цьому запитові тег 7.

```
комірка desc[7] після пробудження:
  op_flags     = 1          UBLK_IO_OP_WRITE, жодного прапорця понад операцію
  start_sector = 2048       1 МіБ ÷ 512 Б
  nr_sectors   = 64         32 КіБ ÷ 512 Б
  addr         = buf[7]     адреса, яку ми самі назвали, озброюючи тег 7

арифметика в serve():
  off = 2048 · 512 = 1048576
  len =   64 · 512 =   32768
```

До того, як сервер прокинувся, ядро вже перенесло ці 32 КіБ зі сторінок запиту в `buf[7]` — дані лежать на місці, читати їх нема звідки. `pwrite(backing_fd, buf[7], 32768, 1048576)` повертає 32768; ознаки `FUA` немає, тож `fdatasync` не робимо; `arm(7, UBLK_U_IO_COMMIT_AND_FETCH_REQ, 32768)` віддає вердикт і знову ставить тег 7 у чергу очікування.

Порахуймо, чого це коштувало: один `pwrite` і один `io_uring_submit`. Опис запиту не пересилався жодного разу — його прочитали з пам'яті; повідомлення про запит теж не пересилалося — ним була завершена команда, що вже висіла в кільці. Саме тому подання можна робити рідше, ніж раз на запит: якщо в кільці завершень чекає одразу кілька тегів, `serve` викликають для кожного, а `io_uring_submit` — один раз на всю пачку.

## Перевірка

```sh
truncate -s 4G /srv/backing.img
sudo ./ublk-file /srv/backing.img &
cat /sys/block/ublkb0/queue/logical_block_size   # 4096 — те, що оголосили
sudo mkfs.ext4 /dev/ublkb0 && sudo mount /dev/ublkb0 /mnt
```

Пройшов `mkfs`, змонтувалося, файли пишуться — каркас цілий. Найпряміша перевірка на правильність не в швидкості, а в збіжності: записавши щось у `/mnt` і скинувши кеші, порівняйте пристрій із підкладкою в обхід себе — `sudo cmp /dev/ublkb0 /srv/backing.img` має промовчати. Розбіжність означає, що десь переплутано одиниці: сектори з байтами або логічний блок із фізичним.

## Пастки

**Вердикт — число зі знаком.** У полі `result` невід'ємне значення означає кількість оброблених байтів, від'ємне — `−errno`, який блоковий шар перекладе на свій код помилки. Тому в `serve` усюди `-errno`, а не `-1`: інакше пристрій відповість на всі збої однаково й нагорі побачать не «місця немає», а безлике «помилка вводу-виводу».

**Мовчання гірше за помилку.** Тег, на який сервер не відповів, лишається в польоті; блоковий шар має власний таймаут, але поки він не спрацював, файлова система над пристроєм стоїть, а разом із нею — усе, що в неї писало. Гілка `default: -EOPNOTSUPP` тут не формальність: невідома операція мусить дістати відповідь, а не тишу.

**Стеля запиту мусить збігатися з буфером.** `max_io_buf_bytes` в описі пристрою і `basic.max_sectors` у параметрах — це та сама межа, названа двічі: у байтах і в 512-байтових секторах. Тут обидві виведені з `IO_BUF_SZ`, і поки так, `serve` може довіряти `nr_sectors` без перевірки. Розійдуться — перший же великий запит перепише пам'ять за `buf[tag]`, і винним здаватиметься ядро.

**Скидання виконуйте чесно.** [`O_DIRECT`](book:unix-linux/buffered-and-direct-io) не робить запис довговічним: дані оминули кеш сторінок, але в носія під підкладкою є власний кеш, а у файла — метадані. Тому `FLUSH` і запис із ознакою `FUA` — це `fdatasync` **перед** відповіддю. Сервер, що відповідає раніше, перетворює чужий `fsync` на брехню, і журналювання файлової системи перестає захищати будь-що.

**Підкладка не може стояти на власному пристрої.** Ані прямо, ані через шар device mapper, ані через файлову систему, змонтовану з `/dev/ublkb0`. Кожен такий шлях — очікування на самого себе всередині обробки запиту.

**Discard не приходить без оголошення.** Ми виставили лише `UBLK_PARAM_TYPE_BASIC`, тож `UBLK_IO_OP_DISCARD` і `WRITE_ZEROES` до сервера не потраплять і `fstrim` нічого не звільнить. Для файлової підкладки їх природно виконує `fallocate` з `FALLOC_FL_PUNCH_HOLE`, але спершу треба додати `UBLK_PARAM_TYPE_DISCARD` із межами.

**Права потрібні лише на створення.** `/dev/ublk-control` відкриває тільки root, тож без нього пристрою не буде взагалі. Прапорець `UBLK_F_UNPRIVILEGED_DEV` у `info.flags` розводить ці ролі: пристрій заводить привілейований помічник, а обслуговує його звичайний користувач — той, кому [правила udev](book:unix-linux/udev-rules) віддали вузол `/dev/ublkc<N>`.

**Смерть демона.** Убийте цей процес — і пристрій зникне разом із ним, а змонтована зверху файлова система побачить, що носія більше немає. Щоб пережити перезапуск сервера, пристрій створюють із прапорцем `UBLK_F_USER_RECOVERY`: вузол лишається, запити, які ще не встигли піти в простір користувача, ставлять назад у чергу, а новий демон приєднується до того самого `/dev/ublkc0` і забирає їх далі.
