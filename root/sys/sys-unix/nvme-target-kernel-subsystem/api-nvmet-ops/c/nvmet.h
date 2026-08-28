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
