# 📋 Ядерний інтерфейс nvmet: структури nvmet_req, nvmet_fabrics_ops та бекенд-операції

Підсистема `nvmet` у ядрі Linux побудована на чіткому розділенні функціональних обов'язків між мережевими транспортами, центральним диспетчером команд та бекендами зберігання. Для цього ядро визначає набір внутрішніх C-структур та таблиць зворотних викликів (callback tables) у заголовних файлах вихідного коду ядра `drivers/nvme/target/nvmet.h`.

Оскільки `nvmet` є внутрішньоядерним модулем (Kernel Subsystem), цей інтерфейс виконується виключно в просторі ядра (Kernel Space). Розуміння цих структур необхідне для розробки нових мережевих транспортів (наприклад, для експериментальних мережевих протоколів або апаратних акселераторів DPU/SmartNIC) та створення власного бекенду зберігання даних (наприклад, для розподілених файлових систем чи об'єктних сховищ).

## 1. Головна контекстна структура: struct nvmet_req

Об'єкт `struct nvmet_req` представляє одну I/O або Admin команду NVMe, що перебуває в процесі виконання цільовою системою. Ця структура не виділяється на льоту: транспорт заздалегідь резервує масив команд на кожну чергу (у `nvmet-tcp` це `struct nvmet_tcp_cmd`, усередині якої `nvmet_req` лежить полем), тож на гарячому шляху лишається взяти вільний елемент. `nvmet_req` супроводжує команду від моменту вилучення з мережевого сокета до відправки підтвердження (CQE).

```c
/* Спрощений витяг із drivers/nvme/target/nvmet.h: поля згруповано за
   призначенням, частину (метадані, p2pdma, резервування) опущено.
   Імена й типи лишених полів — точно як у ядрі. */
struct nvmet_req {
    struct nvme_command    *cmd;          /* Вказівник на сиру 64-байтову NVMe-команду з капсули */
    struct nvme_completion *cqe;          /* Елемент черги завершення (CQE), що повертається */
    struct nvmet_sq        *sq;           /* Submission Queue, з якої прийшла команда */
    struct nvmet_cq        *cq;           /* Completion Queue для відправки відповіді */
    struct nvmet_ns        *ns;           /* NVMe Namespace, до якого адресована команда */
    struct nvmet_port      *port;         /* Фізичний або логічний порт прийому */

    struct scatterlist     *sg;           /* SGL-список сторінок пам'яті для даних */
    int                    sg_cnt;        /* Кількість елементів у SGL-списку */
    size_t                 transfer_len;  /* Довжина даних, узята з SGL-дескриптора */
    size_t                 metadata_len;  /* Розмір метаданих (якщо підтримуються) */

    void (*execute)(struct nvmet_req *req);  /* Функція виконання команди бекендом */
    const struct nvmet_fabrics_ops *ops;     /* Таблиця транспорту, який прийняв команду */

    /* Вбудований вектор + вбудований bio: fast-path без kmalloc.
       У ядрі inline_bio лежить в анонімному об'єднанні, окремим
       полем для кожного бекенду — .b.inline_bio, .p.inline_bio,
       .z.inline_bio; файловий бекенд натомість тримає там kiocb. */
    struct bio_vec         inline_bvec[NVMET_MAX_INLINE_BIOVEC];
    struct bio             inline_bio;

    u16                    error_loc;     /* Зсув поля команди, що спричинило помилку */
    u64                    error_slba;    /* LBA, на якому впала операція */
};
```

### Детальний аналіз полів та життєвого циклу

- **`cmd` та `cqe`:** Поле `cmd` вказує на 64-байтовий блок команди NVMe (наприклад, `struct nvme_rw_command` або `struct nvme_identify_command`), розпакований з мережевої капсули. Поле `cqe` вказує на 16-байтову структуру відповіді, де підсистема `nvmet` формує статус виконання (`status`), результат виконання та ідентифікатор команди (`command_id`).
- **`sq` та `cq`:** Посилання на об'єкти черг надсилання та завершення. Кожна черга `nvmet_sq` прив'язана до конкретного контексту контролера `struct nvmet_ctrl`, що забезпечує беззамкову ідентифікацію сесії.
- **`sg` та `sg_cnt`:** Описують фізичні сторінки оперативної пам'яті цілі (Scatter-Gather List). При операціях читання бекенд заповнює ці сторінки даними з носія, після чого транспорт надсилає їх у мережу. При операціях запису транспорт спочатку отримує дані з мережі у ці сторінки, після чого викликає колбек `execute`.
- **`inline_bvec` та `inline_bio`:** Оптимізація підсистеми `blk-mq` для малого I/O. Якщо запит уміщається у вбудований вектор `inline_bvec` (`NVMET_MAX_INLINE_BIOVEC` = 8 елементів, тобто до 8 сторінок = 32 КіБ), ядро використовує об'єкт `inline_bio`, розміщений безпосередньо в `struct nvmet_req`. Це повністю усуває динамічні виклики `kmalloc()` або `bio_alloc()` на гарячому шляху виконання (Fast-Path). Для більших запитів окремого поля немає: `nvmet_bdev_execute_rw()` довиділяє наступні `struct bio` через `bio_alloc()` і зшиває їх у ланцюжок `bio_chain()` — вказівники живуть у локальних змінних, а не в самій `nvmet_req`.
- **`execute`:** Вказівник на конкретну функцію обробки бекенду (`nvmet_bdev_execute_rw`, `nvmet_file_execute_rw` або `nvmet_passthru_execute_cmd`), який ставить розбирач команди; саме він і починає фактичну роботу з носієм.

## 2. Інтерфейс мережевих транспортів: struct nvmet_fabrics_ops

Кожен мережевий транспорт (`nvmet-tcp`, `nvmet-rdma`, `nvmet-fc`, `nvmet-loop`) реєструється у центральному ядрі за допомогою структури `struct nvmet_fabrics_ops`. Ця структура визначає спосіб взаємодії ядра NVMe Target з конкретним мережевим стеком.

```c
/* Витяг із вихідного коду ядра Linux: drivers/nvme/target/nvmet.h */
struct nvmet_fabrics_ops {
    struct module   *owner;
    unsigned int    type;    /* Тип транспорту: NVMF_TRTYPE_TCP, NVMF_TRTYPE_RDMA тощо */
    unsigned int    msdbd;   /* Maximum SGL Data Block Descriptors у капсулі */
    unsigned int    flags;   /* NVMF_KEYED_SGLS | NVMF_METADATA_SUPPORTED */

    void (*queue_response)(struct nvmet_req *req);
    int  (*add_port)(struct nvmet_port *port);
    void (*remove_port)(struct nvmet_port *port);
    void (*delete_ctrl)(struct nvmet_ctrl *ctrl);
    void (*disc_traddr)(struct nvmet_req *req,
                        struct nvmet_port *port, char *traddr);
    u16  (*install_queue)(struct nvmet_sq *nvme_sq);
    void (*discovery_chg)(struct nvmet_port *port);
    u8   (*get_mdts)(const struct nvmet_ctrl *ctrl);
    u16  (*get_max_queue_size)(const struct nvmet_ctrl *ctrl);
};
```

### Семантика зворотних викликів транспортного рівня

1. **`add_port(port)` / `remove_port(port)`:** Викликаються підсистемою `configfs` при прив'язці або відв'язці мережевого порту. Наприклад, для `nvmet-tcp` функція `add_port` створює сокет ядра (`struct socket`), прив'язує його до вказаного IP та TCP-порту (за замовчуванням 4420) і реєструє обробник подій прийому даних `sk_data_ready`.
2. **`queue_response(req)`:** Головна асинхронна функція завершення I/O. Коли бекенд завершив виконання читання чи запису, ядро викликає `queue_response`. Транспортний модуль формує відповідний кадр (Response PDU для TCP або RDMA Send Work Request) і надсилає його мережевому ініціатору.
3. **`delete_ctrl(ctrl)`:** Очищає мережеві ресурси та закриває з'єднання при припиненні сесії ініціатором або виникненні таймауту Keep-Alive.
4. **`disc_traddr(req, port, traddr)`:** Підставляє транспортну адресу цього порту в запис сторінки виявлення (Discovery Log Page). Транспорт має шанс віддати адресу того інтерфейсу, яким прийшов сам запит, — саме так ініціатор під час `nvme discover` отримує придатну для підключення адресу, а не «0.0.0.0» з конфігурації. Про зміну складу порту ядро повідомляє транспорт через `discovery_chg()`.
5. **`install_queue(nvme_sq)`:** Викликається після команди Connect для щойно створеної черги — транспорт тут звіряє глибину черги з власними межами та прив'язує її до свого контексту.

## 3. Інтерфейс бекендів зберігання

Тут будова навмисно інша, ніж у транспортів: таблиці зворотних викликів для бекендів немає взагалі. Бекенд не реєструється — він обирається один раз, коли простір імен вмикають, і далі про нього говорить лише поле `req->execute`, яке ставить розбирач команд. Ціна такого рішення — закритий набір бекендів (`bdev`, `file`, `passthru`, `zbd`): свій додати не можна, не правлячи розбирач. Виграш — жодного зайвого непрямого виклику на гарячому шляху.

```c
/* Витяг із вихідного коду ядра Linux: drivers/nvme/target/nvmet.h */

/* Увімкнення/вимкнення простору імен: який бекенд обслуговує цей ns */
int  nvmet_bdev_ns_enable(struct nvmet_ns *ns);
void nvmet_bdev_ns_disable(struct nvmet_ns *ns);
int  nvmet_file_ns_enable(struct nvmet_ns *ns);
void nvmet_file_ns_disable(struct nvmet_ns *ns);
bool nvmet_bdev_zns_enable(struct nvmet_ns *ns);

/* Розбір I/O-команди: ставить req->execute відповідного бекенду */
u16 nvmet_bdev_parse_io_cmd(struct nvmet_req *req);
u16 nvmet_file_parse_io_cmd(struct nvmet_req *req);
u16 nvmet_bdev_zns_parse_io_cmd(struct nvmet_req *req);
u16 nvmet_parse_passthru_io_cmd(struct nvmet_req *req);
u16 nvmet_parse_passthru_admin_cmd(struct nvmet_req *req);

/* Синхронізація носія */
u16 nvmet_bdev_flush(struct nvmet_req *req);
u16 nvmet_file_flush(struct nvmet_req *req);
```

### Як це працює

- **Вибір бекенду при `enable`:** `nvmet_ns_enable()` спершу пробує `nvmet_bdev_ns_enable()` — той відкриває шлях `device_path` через `bdev_file_open_by_path()`. Якщо шлях виявився не блоковим пристроєм (або в атрибуті `buffered_io` стоїть `1`), повертається `-ENOTBLK`, і простір імен підхоплює `nvmet_file_ns_enable()` з `filp_open()`. Звідси ж беруться `ns->size` і `ns->blksize_shift`.
- **Розбір команди:** `nvmet_req_init()` викликає `nvmet_parse_io_cmd()`, а той — `nvmet_bdev_parse_io_cmd()`, `nvmet_file_parse_io_cmd()` або `nvmet_bdev_zns_parse_io_cmd()`. Розбирач звіряє Opcode і записує у `req->execute` конкретну функцію (`nvmet_bdev_execute_rw`, `nvmet_file_execute_rw`, `nvmet_passthru_execute_cmd`). Ненульове значення, що повернув розбирач, — це вже готовий код помилки NVMe.
- **Читання й запис:** для бекенду `bdev` сформований `struct bio` іде у `blk-mq` через `submit_bio()`; для `file` — через ітераторні методи `f_op->read_iter()` / `f_op->write_iter()` з підготованим `struct kiocb`.
- **`flush`:** блоковий бекенд подає порожній bio з `REQ_OP_WRITE | REQ_PREFLUSH` (а якщо в пристрою немає кешу запису — одразу відповідає `NVME_SC_SUCCESS`); файловий викликає `vfs_fsync()`.
- **Identify Namespace:** відповідь на цю Admin-команду — 4096-байтова структура `struct nvme_id_ns`, куди ядро підставляє розмір простору імен, формат LBA та підтримувані функції; для блокових пристроїв межі (максимальний розмір передачі, гранули discard) заповнює `nvmet_bdev_set_limits()`.

## 4. Коди статусів NVMe (NVMe Status Codes)

Окремого поля `status` у `struct nvmet_req` немає: код статусу — це 16-бітне значення, яке розбирач чи бекенд повертає з себе, а `nvmet_req_complete()` кладе у `req->cqe->status`. Старші біти цього значення визначають тип статусу (Status Code Type: Generic Command Status, Command Specific Status, Media and Data Integrity Errors), а молодші вісім — конкретну причину в межах типу.

| Константа ядра Linux | Значення (HEX) | Опис та сценарій виникнення |
| :--- | :--- | :--- |
| `NVME_SC_SUCCESS` | `0x0000` | Успішне виконання команди бекендом без помилок |
| `NVME_SC_INVALID_OPCODE` | `0x0001` | Непідтримуваний Opcode (наприклад, спроба виконання Admin-команди на I/O черзі) |
| `NVME_SC_INVALID_FIELD` | `0x0002` | Некоректне значення поля у команді або невалідний список SGL-дескрипторів |
| `NVME_SC_DATA_XFER_ERROR` | `0x0004` | Помилка мережевого перенесення даних (таймаут TCP-сокета або розрив RDMA-сесії) |
| `NVME_SC_INTERNAL` | `0x0006` | Внутрішня помилка ядра (відмова виділення пам'яті або збій бекенду диска) |
| `NVME_SC_INVALID_NS` | `0x000B` | Вказаний Namespace ID не існує, вимкнений або не прив'язаний до підсистеми |
| `NVME_SC_CONNECT_INVALID_PARAM` | `0x0182` | Хибний параметр у команді Connect (наприклад, недозволена глибина черги) |
| `NVME_SC_CONNECT_INVALID_HOST` | `0x0184` | Host NQN ініціатора відсутній у `allowed_hosts` підсистеми при `attr_allow_any_host = 0` |

## 5. Процедура ініціалізації та асинхронного завершення

Коли мережевий транспортний модуль отримує кадр з NVMe-капсулою, ядро виконує таку послідовність викликів внутрішньоядерних функцій:

```c
/* Витяг із вихідного коду ядра Linux: drivers/nvme/target/nvmet.h */

/* 1. Ініціалізація структури запиту з перевіркою валідності */
bool nvmet_req_init(struct nvmet_req *req, struct nvmet_cq *cq,
                    struct nvmet_sq *sq, const struct nvmet_fabrics_ops *ops);

/* 2. Диспетчеризація команд встановлення сесії та авторизації.
      Обидва виконавці Connect — статичні у drivers/nvme/target/fabrics-cmd.c,
      назовні видно лише розбирач. */
u16 nvmet_parse_connect_cmd(struct nvmet_req *req);

/* 3. Асинхронне завершення запиту після виконання I/O */
void nvmet_req_complete(struct nvmet_req *req, u16 status);
```

Послідовність роботи ядра:
1. `nvmet_req_init()` розбирає заголовок прибулої капсули, звіряє ID простору імен `nsid` і призначає відповідні процедури обробки.
2. Якщо команда є мережевою фабричною командою (Fabrics Command), викликається `nvmet_parse_connect_cmd()`, яка перевіряє права доступу ініціатора та валідує NQN.
3. Після завершення читання/запису дисковим бекендом викликається `nvmet_req_complete()`. Вона записує підсумковий статус у 16-байтову структуру CQE і передає запит у метод транспорту `ops->queue_response(req)`. Якщо операція завершилася з помилкою, у `req->error_loc` уже стоїть байтовий зсув того поля команди ініціатора, яке спричинило відмову (його виставляє розбирач або обробник бекенду), і цей зсув потрапляє у журнал помилок контролера.
