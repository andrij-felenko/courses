// Опублікування RDMA Write у C++20 з безпечною перевіркою типом
#include <infiniband/verbs.h>
#include <expected>
#include <cstdint>

std::expected<void, int> post_rdma_write_cpp(ibv_qp* qp, uint64_t wr_id,
                                             uint64_t local_addr, uint32_t len, uint32_t lkey,
                                             uint64_t remote_addr, uint32_t rkey) {
    ibv_sge sge{
        .addr = local_addr,
        .length = len,
        .lkey = lkey
    };

    ibv_send_wr wr{};
    wr.wr_id = wr_id;
    wr.next = nullptr;
    wr.sg_list = &sge;
    wr.num_sge = 1;
    wr.opcode = IBV_WR_RDMA_WRITE;
    wr.send_flags = IBV_SEND_SIGNALED;
    wr.wr.rdma.remote_addr = remote_addr;
    wr.wr.rdma.rkey = rkey;

    ibv_send_wr* bad_wr{nullptr};
    int err = ibv_post_send(qp, &wr, &bad_wr);
    if (err != 0) {
        return std::unexpected(err);
    }
    return {};
}
