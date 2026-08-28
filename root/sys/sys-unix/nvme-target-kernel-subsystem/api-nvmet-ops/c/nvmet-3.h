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
