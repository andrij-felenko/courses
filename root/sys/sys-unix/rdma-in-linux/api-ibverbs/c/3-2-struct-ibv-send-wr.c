// Формування та публікація RDMA Write у C
struct ibv_sge sge = {
    .addr = (uint64_t)local_buffer,
    .length = 1024,
    .lkey = mr->lkey
};

struct ibv_send_wr wr = {
    .wr_id = 1001,
    .next = NULL,
    .sg_list = &sge,
    .num_sge = 1,
    .opcode = IBV_WR_RDMA_WRITE,
    .send_flags = IBV_SEND_SIGNALED | IBV_SEND_INLINE,
    .wr.rdma = {
        .remote_addr = remote_target_addr,
        .rkey = remote_rkey
    }
};

struct ibv_send_wr *bad_wr = NULL;
int ret = ibv_post_send(qp, &wr, &bad_wr);
if (ret != 0) {
    fprintf(stderr, "Помилка ibv_post_send: %d\n", ret);
}
