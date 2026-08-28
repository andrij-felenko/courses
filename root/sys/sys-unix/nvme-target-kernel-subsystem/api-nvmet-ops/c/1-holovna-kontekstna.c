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
