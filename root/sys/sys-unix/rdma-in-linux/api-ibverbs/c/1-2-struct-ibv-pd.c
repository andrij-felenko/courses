// Створення та звільнення PD у C
struct ibv_device **dev_list = ibv_get_device_list(NULL);
struct ibv_context *ctx = ibv_open_device(dev_list[0]);
ibv_free_device_list(dev_list);

struct ibv_pd *pd = ibv_alloc_pd(ctx);
if (!pd) {
    perror("ibv_alloc_pd failed");
    return -1;
}

// ... використання ...
ibv_dealloc_pd(pd);
ibv_close_device(ctx);
