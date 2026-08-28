/*
 * rdma_pingpong.cpp — Ідіоматичний C++20 варіант із RAII-управлінням ресурсами
 * Збірка: g++ -std=c++20 -O2 rdma_pingpong.cpp -o rdma_pingpong -lrdmacm -libverbs
 */
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <stdexcept>
#include <netdb.h>
#include <rdma/rdma_cma.h>

// RAII Кастомні делітери для C++20 smart pointers
struct RdmaDeleters {
    void operator()(rdma_event_channel* ec) const noexcept { if (ec) rdma_destroy_event_channel(ec); }
    void operator()(rdma_cm_id* id) const noexcept { if (id) rdma_destroy_id(id); }
    void operator()(ibv_pd* pd) const noexcept { if (pd) ibv_dealloc_pd(pd); }
    void operator()(ibv_cq* cq) const noexcept { if (cq) ibv_destroy_cq(cq); }
    void operator()(ibv_mr* mr) const noexcept { if (mr) ibv_dereg_mr(mr); }
};

using UniqueEventChannel = std::unique_ptr<rdma_event_channel, RdmaDeleters>;
using UniqueCmId         = std::unique_ptr<rdma_cm_id, RdmaDeleters>;
using UniquePd           = std::unique_ptr<ibv_pd, RdmaDeleters>;
using UniqueCq           = std::unique_ptr<ibv_cq, RdmaDeleters>;
using UniqueMr           = std::unique_ptr<ibv_mr, RdmaDeleters>;

struct RemoteKeys {
    uint64_t remote_addr{0};
    uint32_t rkey{0};
};

class RdmaEndpoint {
public:
    explicit RdmaEndpoint(rdma_cm_id* id) : id_(id) {
        pd_.reset(ibv_alloc_pd(id_->verbs));
        if (!pd_) throw std::runtime_error("Не вдалося виділити Protection Domain");

        cq_.reset(ibv_create_cq(id_->verbs, 16, nullptr, nullptr, 0));
        if (!cq_) throw std::runtime_error("Не вдалося створити Completion Queue");

        ibv_qp_init_attr qp_attr{};
        qp_attr.send_cq = cq_.get();
        qp_attr.recv_cq = cq_.get();
        qp_attr.qp_type = IBV_QPT_RC;
        qp_attr.cap.max_send_wr = 16;
        qp_attr.cap.max_recv_wr = 16;
        qp_attr.cap.max_send_sge = 1;
        qp_attr.cap.max_recv_sge = 1;

        if (rdma_create_qp(id_, pd_.get(), &qp_attr) != 0) {
            throw std::runtime_error("Не вдалося створити Queue Pair");
        }
    }

    ~RdmaEndpoint() noexcept {
        if (id_ && id_->qp) {
            rdma_destroy_qp(id_);
        }
    }

    [[nodiscard]] ibv_pd* pd() const noexcept { return pd_.get(); }
    [[nodiscard]] ibv_cq* cq() const noexcept { return cq_.get(); }

    void poll_completion_blocking(uint64_t expected_wr_id) {
        ibv_wc wc{};
        while (true) {
            int ret = ibv_poll_cq(cq_.get(), 1, &wc);
            if (ret > 0) {
                if (wc.status != IBV_WC_SUCCESS) {
                    throw std::runtime_error("Помилка CQ status: " + std::to_string(wc.status));
                }
                if (wc.wr_id == expected_wr_id) return;
            } else if (ret < 0) {
                throw std::runtime_error("Помилка опитування ibv_poll_cq");
            }
        }
    }

private:
    rdma_cm_id* id_{nullptr};
    UniquePd pd_{nullptr};
    UniqueCq cq_{nullptr};
};

void run_cpp_server(std::string_view port) {
    UniqueEventChannel ec(rdma_create_event_channel());
    if (!ec) throw std::runtime_error("Помилка створення event channel");

    rdma_cm_id* raw_listen_id{nullptr};
    if (rdma_create_id(ec.get(), &raw_listen_id, nullptr, RDMA_PS_TCP) != 0) {
        throw std::runtime_error("Помилка rdma_create_id");
    }
    UniqueCmId listen_id(raw_listen_id);

    addrinfo hints{.ai_family = AF_INET, .ai_socktype = SOCK_STREAM, .ai_flags = AI_PASSIVE};
    addrinfo* res{nullptr};
    getaddrinfo(nullptr, port.data(), &hints, &res);
    rdma_bind_addr(listen_id.get(), res->ai_addr);
    freeaddrinfo(res);

    rdma_listen(listen_id.get(), 1);
    std::cout << "[C++ Server] Очікування на порту " << port << "...\n";

    rdma_cm_event* event{nullptr};
    rdma_get_cm_event(ec.get(), &event);
    UniqueCmId client_id(event->id);
    rdma_ack_cm_event(event);

    RdmaEndpoint ep(client_id.get());

    std::vector<char> target_buffer(1024, 0);
    UniqueMr target_mr(ibv_reg_mr(ep.pd(), target_buffer.data(), target_buffer.size(),
                                  IBV_ACCESS_LOCAL_WRITE | IBV_ACCESS_REMOTE_WRITE));

    RemoteKeys keys{.remote_addr = reinterpret_cast<uint64_t>(target_buffer.data()), .rkey = target_mr->rkey};
    UniqueMr keys_mr(ibv_reg_mr(ep.pd(), &keys, sizeof(keys), IBV_ACCESS_LOCAL_WRITE));

    ibv_sge sge{.addr = reinterpret_cast<uint64_t>(&keys), .length = sizeof(keys), .lkey = keys_mr->lkey};
    ibv_send_wr wr{.wr_id = 100, .sg_list = &sge, .num_sge = 1, .opcode = IBV_WR_SEND, .send_flags = IBV_SEND_SIGNALED};
    ibv_send_wr* bad_wr{nullptr};

    rdma_conn_param conn_param{};
    rdma_accept(client_id.get(), &conn_param);
    rdma_get_cm_event(ec.get(), &event);
    rdma_ack_cm_event(event);

    ibv_post_send(client_id->qp, &wr, &bad_wr);
    ep.poll_completion_blocking(100);

    std::cout << "[C++ Server] Метадані передано. Очікування RDMA Write...\n";
    sleep(2);

    std::cout << "[C++ Server] Результат буфера: '" << target_buffer.data() << "'\n";
}
