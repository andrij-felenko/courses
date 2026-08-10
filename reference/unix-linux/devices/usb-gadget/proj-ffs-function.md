# ⚙️ Своя функція через FunctionFS: демон, який і є USB-пристроєм

Зберемо пристрій, якого в ядрі немає: власний клас, дві масові кінцеві точки, і вся поведінка — у звичайній програмі на C, яку можна перезапустити з-під налагоджувача. Ядру дістається транспорт, протокол лишається програмі; на тому самому стику стоїть adbd в Android, а поруч із ним — передача файлів по MTP, тільки протокол у них складніший.

## Примірник, монтування й права

Функція `f_fs` заводиться так само, як будь-яка інша, але після посилання в конфігурацію додається монтування:

```sh
mkdir functions/ffs.echo
ln -s functions/ffs.echo configs/c.1/

mkdir -p /dev/ffs-echo
mount -t functionfs echo /dev/ffs-echo -o uid=1000,gid=1000,rmode=0750,fmode=0660
```

Слово `echo` на місці «пристрою» в команді монтування — не довільна назва: ядро шукає примірник за дослівним збігом із тим, що стоїть після крапки в `ffs.echo`. Помилився літерою — монтування не вдасться, і причину доведеться шукати довго, бо повідомлення буде звичайне «немає такого пристрою».

Опції теж не косметика. Монтує root, а працювати демонові краще без прав root — саме для цього `f_fs` розбирає `uid`, `gid`, `mode`, `rmode`, `fmode` і `no_disconnect`: перші п'ять кажуть, кому належать файли всередині й з якими правами вони створяться, тож демон під власним обліковим записом дістає `ep0` і точки, не отримуючи разом із ними всієї машини.

У щойно змонтованій теці лежить рівно один файл — `ep0`. Більше нічого не з'явиться, поки програма не скаже, чим вона є.

## Дескриптори — двійковий блок, а не текст

Ядро не вигадає дескрипторів за програму: воно не знає ні скільки в неї точок, ні якого вони типу. Тому перше, що демон робить після відкриття `ep0`, — пише туди суцільний двійковий блок такої будови (усі числа — молодшим байтом уперед, незалежно від машини):

```
зсув  поле       тип    що кладемо
   0  magic      LE32   FUNCTIONFS_DESCRIPTORS_MAGIC_V2 = 3
   4  length     LE32   довжина всього блоку разом із заголовком
   8  flags      LE32   HAS_FS_DESC | HAS_HS_DESC
  12  fs_count   LE32   3 — скільки дескрипторів у повношвидкісному наборі
  16  hs_count   LE32   3 — стільки ж у високошвидкісному
  20  fs_descrs  …      інтерфейс, точка OUT, точка IN
   …  hs_descrs  …      те саме, інший wMaxPacketSize
```

Лічильники йдуть у жорсткому порядку — `eventfd`, `fs`, `hs`, `ss`, `os_desc` — і присутні лише ті, чий прапорець піднято. Саме тому `struct usb_functionfs_descs_head_v2` у заголовку ядра обривається на `flags`, а лічильники залишено дописати самому: далі вигляд блоку залежить від того, що саме ти оголосив.

```c
/* ffs-echo.c — власна USB-функція в просторі користувача.
 * cc -O2 -Wall -pthread -o ffs-echo ffs-echo.c                              */
#define _GNU_SOURCE
#include <endian.h>
#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdio.h>
#include <unistd.h>
#include <linux/usb/ch9.h>
#include <linux/usb/functionfs.h>

#define STR_INTERFACE "echo"

static const struct {
    struct usb_functionfs_descs_head_v2 header;
    __le32 fs_count, hs_count;              /* рівно під підняті прапорці */
    struct {
        struct usb_interface_descriptor intf;
        struct usb_endpoint_descriptor_no_audio out;   /* стане ep1 */
        struct usb_endpoint_descriptor_no_audio in;    /* стане ep2 */
    } __attribute__((packed)) fs, hs;
} __attribute__((packed)) descs = {
    .header = {
        .magic  = htole32(FUNCTIONFS_DESCRIPTORS_MAGIC_V2),
        .length = htole32(sizeof descs),
        .flags  = htole32(FUNCTIONFS_HAS_FS_DESC | FUNCTIONFS_HAS_HS_DESC),
    },
    .fs_count = htole32(3),
    .hs_count = htole32(3),
    .fs = {
        .intf = { .bLength          = sizeof descs.fs.intf,
                  .bDescriptorType  = USB_DT_INTERFACE,
                  .bInterfaceNumber = 0,       /* libcomposite перепише */
                  .bNumEndpoints    = 2,
                  .bInterfaceClass  = USB_CLASS_VENDOR_SPEC,
                  .iInterface       = 1 },     /* індекс у НАШОМУ блоці рядків */
        .out  = { .bLength          = sizeof descs.fs.out,
                  .bDescriptorType  = USB_DT_ENDPOINT,
                  .bEndpointAddress = 1 | USB_DIR_OUT,
                  .bmAttributes     = USB_ENDPOINT_XFER_BULK,
                  .wMaxPacketSize   = htole16(64) },
        .in   = { .bLength          = sizeof descs.fs.in,
                  .bDescriptorType  = USB_DT_ENDPOINT,
                  .bEndpointAddress = 2 | USB_DIR_IN,
                  .bmAttributes     = USB_ENDPOINT_XFER_BULK,
                  .wMaxPacketSize   = htole16(64) },
    },
    .hs = {
        .intf = { .bLength          = sizeof descs.hs.intf,
                  .bDescriptorType  = USB_DT_INTERFACE,
                  .bNumEndpoints    = 2,
                  .bInterfaceClass  = USB_CLASS_VENDOR_SPEC,
                  .iInterface       = 1 },
        .out  = { .bLength          = sizeof descs.hs.out,
                  .bDescriptorType  = USB_DT_ENDPOINT,
                  .bEndpointAddress = 1 | USB_DIR_OUT,
                  .bmAttributes     = USB_ENDPOINT_XFER_BULK,
                  .wMaxPacketSize   = htole16(512) },
        .in   = { .bLength          = sizeof descs.hs.in,
                  .bDescriptorType  = USB_DT_ENDPOINT,
                  .bEndpointAddress = 2 | USB_DIR_IN,
                  .bmAttributes     = USB_ENDPOINT_XFER_BULK,
                  .wMaxPacketSize   = htole16(512) },
    },
};

static const struct {
    struct usb_functionfs_strings_head header;
    struct {
        __le16 code;                      /* 0x0409 — англійська (США) */
        char   str1[sizeof STR_INTERFACE];
    } __attribute__((packed)) lang0;
} __attribute__((packed)) strs = {
    .header = {
        .magic      = htole32(FUNCTIONFS_STRINGS_MAGIC),
        .length     = htole32(sizeof strs),
        .str_count  = htole32(1),
        .lang_count = htole32(1),
    },
    .lang0 = { htole16(0x0409), STR_INTERFACE },
};
```

Три речі в цьому шматку варті окремої уваги.

**Тип дескриптора точки.** `struct usb_endpoint_descriptor` із `ch9.h` має дев'ять байтів: два останні, `bRefresh` і `bSynchAddress`, потрібні лише аудіо-класові. Блок — суцільний потік байтів, і ядро йде ним, відмірюючи кожен дескриптор його ж полем `bLength`. Візьмеш дев'ятибайтову структуру, а `bLength` залишиш сімкою — розбір поїде далі не з того місця, і запис обірветься помилкою; узгодиш із дев'яткою — блок пройде, зате хост дістане опис із двома зайвими байтами там, де їм не місце. Для всіх не-аудіо випадків є семибайтовий `usb_endpoint_descriptor_no_audio`, і саме його тут видно.

**Номери, які нічого не значать.** `bInterfaceNumber` дорівнює нулю, адреси точок — одиниця й двійка. Пишемо їх так, ніби наша функція в пристрої єдина; справжні номери проставить `libcomposite`, коли складе конфігурацію цілком. Так само `iInterface = 1` вказує не в загальний перелік рядків пристрою, а в наш власний блок, де нумерація починається з одиниці.

**Дві швидкості.** Набори `fs` і `hs` мусять описувати ті самі інтерфейси й ті самі точки — відрізняється тільки те, що від швидкості й залежить. Для масової точки на високій швидкості стандарт дозволяє єдиний розмір пакета — 512 байтів, тоді як на повній це 64 ([кінцеві точки USB](book:programming/usb-endpoints)).

## Порядок, у якому речі з'являються

Блоки пишуться двома викликами `write()` і саме в цьому порядку: спершу дескриптори, потім рядки. Кожен блок — один виклик: ядро розбирає рівно той буфер, що прийшов, і звіряє поле `length` із кількістю записаних байтів, тож розрізати блок на два записи не вийде, а переставити місцями — тим паче: магічне число не збіжиться зі станом, у якому ядро на цей момент перебуває, і `write` поверне `EINVAL`.

Файли кінцевих точок створюються не при монтуванні й не при прив'язці до контролера, а саме в обробнику **другого** запису — того, що приносить рядки. Тому послідовність у демоні природна: відкрити `ep0`, віддати два блоки, і аж потім відкривати `ep1` та `ep2`. Імена цих файлів послідовні, а їхній порядок повторює порядок точок у наборі дескрипторів: перша описана точка — `ep1`, друга — `ep2`. Яка апаратна точка стоїть за файлом, знати не треба й не можна: `ep1` може виявитися третьою точкою контролера, і від перезбирання гаджета це зміниться.

## Демон цілком

```c
static int ep0, ep_out, ep_in;

static void *echo_loop(void *unused)
{
    char buf[4096];             /* кратний максимальному пакетові обох швидкостей */
    (void)unused;

    for (;;) {
        ssize_t n = read(ep_out, buf, sizeof buf);
        if (n < 0) {
            if (errno == EINTR)                     /* сигнал урвав сон */
                continue;
            if (errno == ESHUTDOWN || errno == ECONNRESET)
                continue;       /* точку вимкнули: наступний read засне до ENABLE */
            perror("read ep1");
            return NULL;
        }
        for (ssize_t off = 0; off < n; ) {
            ssize_t w = write(ep_in, buf + off, n - off);
            if (w < 0) {
                if (errno == EINTR)
                    continue;
                break;          /* обмін обірвався — назад у читання */
            }
            off += w;
        }
    }
}

static void on_event(const struct usb_functionfs_event *e)
{
    switch (e->type) {
    case FUNCTIONFS_BIND:       /* гаджет прив'язано до контролера */
    case FUNCTIONFS_UNBIND:     /* … і відв'язано: точок більше немає */
    case FUNCTIONFS_ENABLE:     /* хост вибрав конфігурацію — обмін ожив */
    case FUNCTIONFS_DISABLE:    /* точки вимкнено, заявки скасовано */
    case FUNCTIONFS_SUSPEND:
    case FUNCTIONFS_RESUME:
        break;                  /* потік обміну сам упорається зі сном і прокиданням */
    case FUNCTIONFS_SETUP:
        /* Керуючий запит нам. Відповісти треба негайно, напрям — у bRequestType.
           Нічого не вміємо, тож закриваємо стадію порожньою передачею. */
        if (e->u.setup.bRequestType & USB_DIR_IN)
            write(ep0, NULL, 0);
        else
            read(ep0, NULL, 0);
        break;
    }
}

int main(int argc, char **argv)
{
    const char *dir = argc > 1 ? argv[1] : "/dev/ffs-echo";
    char path[256];
    pthread_t th;

    snprintf(path, sizeof path, "%s/ep0", dir);
    if ((ep0 = open(path, O_RDWR)) < 0) { perror(path); return 1; }

    if (write(ep0, &descs, sizeof descs) < 0) { perror("дескриптори"); return 1; }
    if (write(ep0, &strs,  sizeof strs)  < 0) { perror("рядки");      return 1; }

    snprintf(path, sizeof path, "%s/ep1", dir);          /* точка OUT */
    if ((ep_out = open(path, O_RDWR)) < 0) { perror(path); return 1; }
    snprintf(path, sizeof path, "%s/ep2", dir);          /* точка IN */
    if ((ep_in  = open(path, O_RDWR)) < 0) { perror(path); return 1; }

    pthread_create(&th, NULL, echo_loop, NULL);

    for (;;) {
        struct usb_functionfs_event ev[8];
        ssize_t n = read(ep0, ev, sizeof ev);
        if (n < 0) {
            if (errno == EINTR)
                continue;
            perror("read ep0");
            return 1;
        }
        for (size_t i = 0; i < (size_t)n / sizeof ev[0]; i++)
            on_event(&ev[i]);
    }
}
```

Читання `ep0` віддає стільки подій, скільки їх устигло накопичитись, тому буфер беруть із запасом і обробляють усі, що прийшли, а не першу.

## Дві точки, де все зупиняється

Тепер видно, чому запис імені контролера в файл `UDC` не оживляє пристрій одразу. Ядро реєструє гаджет лише тоді, коли всі змонтовані примірники FunctionFS уже дістали свої дескриптори, — інакше воно просто не має чого відповісти хостові на перше ж питання. Порядок команд від цього стає вільним: запустиш демона першим — пристрій з'явиться на записі в `UDC`; запишеш `UDC` першим — він з'явиться, коли демон віддасть блоки. Оживає на пізнішому з двох моментів.

Друге очікування — усередині самого обміну. Читання й запис на файлі точки, поки та не ввімкнена, не помиляються, а сплять: ядро тримає викликача на черзі очікування, доки хост не вибере конфігурацію. Відкрив точку з `O_NONBLOCK` — замість сну дістанеш `EAGAIN`, і це не помилка, а «точки ще нема».

![Демон і ядро по черзі чекають одне на одного.](/reference/unix-linux/devices/usb-gadget/img/ffs-handshake.svg)

*Дві червоні смуги — не збій, а звичайний робочий стан: спершу ядро чекає на дескриптори, потім демон — на ввімкнення конфігурації.*

## Чого це коштує

Стеля шини рахується коротко:

```
масова точка на високій швидкості:
  13 транзакцій × 512 Б у мікрокадрі 125 мкс
  6656 Б / 125 мкс ≈ 53.2 МБ/с
```

Демон із однією заявкою в польоті цієї стелі не побачить. Наш цикл спершу дочитує пакет до кінця, потім повертається з ядра в програму, і лише тоді кладе відповідь; між цими митями кінцева точка порожня, і на кожен токен від хоста контролер відповідає «поки нічого нема». Хост від цього не простоює — він опитує інших, — але наша частка смуги падає в рази, і винен у цьому не розмір буфера й не мова, а те, що покласти більш ніж одну заявку наперед синхронні `read`/`write` не вміють. Звідси й береться асинхронний ввід-вивід у справжніх демонах: кілька заявок, поданих заздалегідь, роблять так, що наступному пакетові з шини вже є куди лягти, а на зустрічний токен завжди є що віддати.

## Пастки

**Події `DISCONNECT` не існує.** Їх усього сім: `BIND`, `UNBIND`, `ENABLE`, `DISABLE`, `SETUP`, `SUSPEND`, `RESUME`. Висмикнутий кабель приходить як `DISABLE`, а `echo "" > UDC` — як `DISABLE` і слідом `UNBIND`.

**Після `DISABLE` файли точок не закривають.** Спокуса «перевідкрити все начисто» веде до перегонів із ядром, а потреби в ній немає: заявки в польоті вже скасовано, читання повернулося з `ESHUTDOWN`, і наступний виклик просто засне до нового `ENABLE`. Демон, який на кожне від'єднання завершується, дає гірше: закриття `ep0` для ядра означає, що функції більше немає, і пристрій зникає в хоста; пережити перезапуск демона дозволяє опція монтування `no_disconnect=1`.

**`poll()` на файлах точок бреше.** У наборі файлових операцій `f_fs` для них немає обробника опитування — тільки читання, запис і `ioctl`. Отже, `select`, `poll` і `epoll` завжди звітують «готовий», і побудувати на них однопотоковий цикл не вийде. Лишаються два чесні шляхи: [окремий потік](book:unix-linux/threads-as-tasks) на кожен напрям, як зроблено вище, або асинхронний ввід-вивід через [io_submit](book:unix-linux/linux-aio-io-submit) із [eventfd](book:unix-linux/eventfd-and-futex) як сповіщувачем — саме так влаштований adbd, бо йому потрібні кілька заявок у польоті водночас. Дрібниця з `EAGAIN` виявляється тут наріжною: неблокуючий режим без опитування нічого не дає, тільки перетворює сон на порожнє прокручування ([блокуючий і неблокуючий режим](book:unix-linux/blocking-and-nonblocking)).

**`EINTR` — це не кінець.** Будь-який сигнал уриває і сон на точці, і читання подій. Цикл, який вважає першу невдачу фатальною, помре від першого ж `SIGWINCH` у налагоджувальному запуску.

**Стадія даних краде події.** Поки керуючий запит не завершено, наступне читання `ep0` віддасть не подію, а дані цього запиту. Тому обробник `SETUP` мусить закрити стадію тут-таки, а не відкладати «на потім»: інакше подієвий цикл читатиме зовсім не те, чого чекає. За звичайних умов до демона доходять лише запити класу й виробника, адресовані його інтерфейсу; решту забирає `libcomposite`, а прапорець `FUNCTIONFS_ALL_CTRL_RECIP` у блоці дескрипторів каже віддавати демонові все, що не зачіпає роботу самого пристрою.
