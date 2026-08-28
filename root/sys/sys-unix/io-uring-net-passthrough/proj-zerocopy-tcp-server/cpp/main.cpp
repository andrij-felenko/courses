/* cpp */
#include <iostream>
#include <vector>
#include <memory>
#include <span>
#include <stdexcept>
#include <system_error>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <liburing.h>

namespace net {

constexpr size_t QueueDepth = 256;
constexpr size_t BufferSize = 65536;
constexpr size_t NumBuffers = 64;

class IoUringRing {
    struct io_uring ring_{};
public:
    explicit IoUringRing(unsigned entries) {
        if (int ret = io_uring_queue_init(entries, &ring_, 0); ret < 0) {
            throw std::system_error(-ret, std::generic_category(), "io_uring_queue_init failed");
        }
    }

    ~IoUringRing() noexcept {
        io_uring_queue_exit(&ring_);
    }

    IoUringRing(const IoUringRing&) = delete;
    IoUringRing& operator=(const IoUringRing&) = delete;

    struct io_uring* get() noexcept { return &ring_; }

    void register_fixed_buffers(std::span<const iovec> iovs) {
        if (int ret = io_uring_register_buffers(&ring_, iovs.data(), iovs.size()); ret < 0) {
            throw std::system_error(-ret, std::generic_category(), "io_uring_register_buffers failed");
        }
    }
};

class SocketOwner {
    int fd_{-1};
public:
    explicit SocketOwner(int fd) noexcept : fd_(fd) {}
    ~SocketOwner() noexcept {
        if (fd_ >= 0) ::close(fd_);
    }
    SocketOwner(SocketOwner&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    SocketOwner& operator=(SocketOwner&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

struct BufferPool {
    alignas(4096) std::array<std::array<char, BufferSize>, NumBuffers> storage;
    std::vector<uint16_t> free_indices;

    BufferPool() {
        free_indices.reserve(NumBuffers);
        for (uint16_t i = 0; i < NumBuffers; ++i) {
            free_indices.push_back(i);
        }
    }

    int acquire() {
        if (free_indices.empty()) return -1;
        int idx = free_indices.back();
        free_indices.pop_back();
        return idx;
    }

    void release(uint16_t idx) {
        free_indices.push_back(idx);
    }
};

enum class State { Accept, Read, SendZCWaitNotif };

struct ClientContext {
    SocketOwner client_sock;
    uint16_t buffer_index{0};
    State state{State::Read};

    ClientContext(int fd, uint16_t buf_idx) 
        : client_sock(fd), buffer_index(buf_idx), state(State::Read) {}
};

} // namespace net

int main(int argc, char* argv[]) {
    uint16_t port = 8080;
    if (argc > 1) port = static_cast<uint16_t>(std::atoi(argv[1]));

    net::SocketOwner listen_sock(::socket(AF_INET, SOCK_STREAM, 0));
    if (listen_sock.get() < 0) {
        perror("socket");
        return 1;
    }

    int val = 1;
    ::setsockopt(listen_sock.get(), SOL_SOCKET, SO_REUSEADDR, &val, sizeof(val));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (::bind(listen_sock.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        perror("bind");
        return 1;
    }

    if (::listen(listen_sock.get(), 128) < 0) {
        perror("listen");
        return 1;
    }

    try {
        net::IoUringRing ring(net::QueueDepth);
        auto pool = std::make_unique<net::BufferPool>();

        std::vector<iovec> iovs(net::NumBuffers);
        for (size_t i = 0; i < net::NumBuffers; ++i) {
            iovs[i].iov_base = pool->storage[i].data();
            iovs[i].iov_len = net::BufferSize;
        }

        ring.register_fixed_buffers(iovs);
        std::cout << "C++20 SendZC Server running on port " << port << "...\n";

        // Початкова підготовка accept
        auto* sqe = io_uring_get_sqe(ring.get());
        io_uring_prep_accept(sqe, listen_sock.get(), nullptr, nullptr, 0);
        io_uring_sqe_set_data(sqe, nullptr); // null означає підключення слухаючого сокета
        io_uring_submit(ring.get());

        while (true) {
            io_uring_cqe* cqe{nullptr};
            if (io_uring_wait_cqe(ring.get(), &cqe) < 0) break;

            auto* ctx = static_cast<net::ClientContext*>(io_uring_cqe_get_data(cqe));
            int res = cqe->res;
            unsigned int flags = cqe->flags;

            if (ctx == nullptr) {
                // Подія від listen_sock
                if (res >= 0) {
                    int client_fd = res;
                    int buf_idx = pool->acquire();
                    if (buf_idx >= 0) {
                        auto client_ctx = std::make_unique<net::ClientContext>(client_fd, static_cast<uint16_t>(buf_idx));
                        auto* read_sqe = io_uring_get_sqe(ring.get());
                        io_uring_prep_read_fixed(read_sqe, client_fd, 
                                                 pool->storage[buf_idx].data(), 
                                                 net::BufferSize, 0, buf_idx);
                        io_uring_sqe_set_data(read_sqe, client_ctx.release());
                    } else {
                        ::close(client_fd);
                    }
                }
                // Перереєстрація accept
                sqe = io_uring_get_sqe(ring.get());
                io_uring_prep_accept(sqe, listen_sock.get(), nullptr, nullptr, 0);
                io_uring_sqe_set_data(sqe, nullptr);
                io_uring_submit(ring.get());
            } else {
                if (ctx->state == net::State::Read) {
                    if (res > 0) {
                        ctx->state = net::State::SendZCWaitNotif;
                        auto* send_sqe = io_uring_get_sqe(ring.get());
                        // Ініціалізація SendZC з зареєстрованим буфером
                        io_uring_prep_send_zc_fixed(send_sqe, ctx->client_sock.get(), 
                                                   pool->storage[ctx->buffer_index].data(), 
                                                   res, 0, 0, ctx->buffer_index);
                        io_uring_sqe_set_data(send_sqe, ctx);
                        io_uring_submit(ring.get());
                    } else {
                        pool->release(ctx->buffer_index);
                        delete ctx;
                    }
                } else if (ctx->state == net::State::SendZCWaitNotif) {
                    if (flags & IORING_CQE_F_NOTIF) {
                        // Отримано Notification CQE: DMA відправку повністю завершено
                        auto* read_sqe = io_uring_get_sqe(ring.get());
                        ctx->state = net::State::Read;
                        io_uring_prep_read_fixed(read_sqe, ctx->client_sock.get(), 
                                                 pool->storage[ctx->buffer_index].data(), 
                                                 net::BufferSize, 0, ctx->buffer_index);
                        io_uring_sqe_set_data(read_sqe, ctx);
                        io_uring_submit(ring.get());
                    } else if (res < 0) {
                        pool->release(ctx->buffer_index);
                        delete ctx;
                    }
                }
            }

            io_uring_cqe_seen(ring.get(), cqe);
        }
    } catch (const std::exception& e) {
        std::cerr << "Fatal Server Error: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
