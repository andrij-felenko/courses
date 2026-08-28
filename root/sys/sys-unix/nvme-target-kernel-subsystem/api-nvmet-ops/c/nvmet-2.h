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
