/* Створення об'єкта UMEM */
int xsk_umem__create(struct xsk_umem **umem,
                     void *umem_area, uint64_t size,
                     struct xsk_ring_prod *fill,
                     struct xsk_ring_cons *comp,
                     const struct xsk_umem_config *config);

/* Створення та прив'язка сокета AF_XDP */
int xsk_socket__create(struct xsk_socket **xsk,
                       const char *ifname, uint32_t queue_id,
                       struct xsk_umem *umem,
                       struct xsk_ring_cons *rx,
                       struct xsk_ring_prod *tx,
                       const struct xsk_socket_config *config);
