#include <iostream>
#include <vector>
#include <string_view>
#include <span>
#include <memory>
#include <expected>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/mman.h>
#include <sys/eventfd.h>
#include <sys/wait.h>
#include <linux/fcntl.h>

constexpr size_t BUFFER_SIZE = 1024 * 1024; // 1 МБ спільного буфера

// RAII обгортка для безпечного керування дескрипторами ядра
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        reset(other.release());
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

// RAII обгортка для мапінгу віртуальної пам'яті
class MmapRegion {
    void* addr_{MAP_FAILED};
    size_t length_{0};
public:
    MmapRegion(void* addr, size_t len) noexcept : addr_(addr), length_(len) {}
    ~MmapRegion() noexcept {
        if (addr_ != MAP_FAILED) {
            ::munmap(addr_, length_);
        }
    }

    MmapRegion(const MmapRegion&) = delete;
    MmapRegion& operator=(const MmapRegion&) = delete;

    MmapRegion(MmapRegion&& other) noexcept 
        : addr_(other.addr_), length_(other.length_) {
        other.addr_ = MAP_FAILED;
    }

    [[nodiscard]] void* data() const noexcept { return addr_; }
    [[nodiscard]] bool valid() const noexcept { return addr_ != MAP_FAILED; }
    [[nodiscard]] size_t size() const noexcept { return length_; }
};

struct ControlHeader {
    uint32_t command_id;
    uint32_t payload_size;
};

// Відправка дескрипторів через SCM_RIGHTS із типізованою обробкою помилок
std::expected<void, std::string_view> send_fds(int sock_fd, const ControlHeader& hdr, int mem_fd, int evt_fd) {
    struct msghdr mh{};
    struct iovec iov[1]{};
    char cmsg_buf[CMSG_SPACE(sizeof(int) * 2)]{};

    iov[0].iov_base = const_cast<void*>(static_cast<const void*>(&hdr));
    iov[0].iov_len = sizeof(ControlHeader);
    mh.msg_iov = iov;
    mh.msg_iovlen = 1;

    mh.msg_control = cmsg_buf;
    mh.msg_controllen = sizeof(cmsg_buf);

    struct cmsghdr* cmsg = CMSG_FIRSTHDR(&mh);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int) * 2);

    int* fds = reinterpret_cast<int*>(CMSG_DATA(cmsg));
    fds[0] = mem_fd;
    fds[1] = evt_fd;

    if (::sendmsg(sock_fd, &mh, 0) < 0) {
        return std::unexpected("sendmsg failed");
    }
    return {};
}

// Прийом дескрипторів із сокета
std::expected<std::pair<UniqueFd, UniqueFd>, std::string_view> recv_fds(int sock_fd, ControlHeader& hdr) {
    struct msghdr mh{};
    struct iovec iov[1]{};
    char cmsg_buf[CMSG_SPACE(sizeof(int) * 2)]{};

    iov[0].iov_base = &hdr;
    iov[0].iov_len = sizeof(ControlHeader);
    mh.msg_iov = iov;
    mh.msg_iovlen = 1;

    mh.msg_control = cmsg_buf;
    mh.msg_controllen = sizeof(cmsg_buf);

    ssize_t recvd = ::recvmsg(sock_fd, &mh, 0);
    if (recvd <= 0) {
        return std::unexpected("recvmsg failed or peer disconnected");
    }

    for (struct cmsghdr* cmsg = CMSG_FIRSTHDR(&mh); cmsg != nullptr; cmsg = CMSG_NXTHDR(&mh, cmsg)) {
        if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_RIGHTS) {
            int* fds = reinterpret_cast<int*>(CMSG_DATA(cmsg));
            return std::make_pair(UniqueFd(fds[0]), UniqueFd(fds[1]));
        }
    }

    return std::unexpected("no SCM_RIGHTS control message received");
}

void run_client(UniqueFd sock) {
    std::cout << "[Клієнт C++ PID " << ::getpid() << "] Очікування дескрипторів від сервера..." << std::endl;
    ControlHeader hdr{};
    auto fds_res = recv_fds(sock.get(), hdr);
    if (!fds_res) {
        std::cerr << "[Клієнт C++] Помилка: " << fds_res.error() << std::endl;
        return;
    }

    auto [mem_fd, evt_fd] = std::move(*fds_res);
    std::cout << "[Клієнт C++] Отримано дескриптори: memfd=" << mem_fd.get() 
              << ", eventfd=" << evt_fd.get() << " (команда=" << hdr.command_id << ")" << std::endl;

    void* ptr = ::mmap(nullptr, BUFFER_SIZE, PROT_READ, MAP_SHARED, mem_fd.get(), 0);
    MmapRegion region(ptr, BUFFER_SIZE);
    if (!region.valid()) {
        std::cerr << "[Клієнт C++] mmap failed" << std::endl;
        return;
    }

    uint64_t evt_val = 0;
    if (::read(evt_fd.get(), &evt_val, sizeof(evt_val)) == sizeof(evt_val)) {
        std::string_view content(static_cast<const char*>(region.data()));
        std::cout << "[Клієнт C++] Отримано сигнал! Прочитано дані: \"" << content << "\"" << std::endl;
    }
}

int main() {
    int sv[2];
    if (::socketpair(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0, sv) == -1) {
        std::cerr << "socketpair failed" << std::endl;
        return 1;
    }

    UniqueFd server_sock(sv[0]);
    UniqueFd client_sock(sv[1]);

    pid_t pid = ::fork();
    if (pid < 0) {
        std::cerr << "fork failed" << std::endl;
        return 1;
    }

    if (pid == 0) {
        server_sock.reset();
        run_client(std::move(client_sock));
        return 0;
    }

    client_sock.reset();

    // 1. Створення анонімного файлу memfd
    UniqueFd mem_fd(::memfd_create("cpp_ipc_channel", MFD_CLOEXEC | MFD_ALLOW_SEALING));
    if (!mem_fd.valid() || ::ftruncate(mem_fd.get(), BUFFER_SIZE) == -1) {
        std::cerr << "memfd setup failed" << std::endl;
        return 1;
    }

    // Запис вихідних даних
    void* ptr = ::mmap(nullptr, BUFFER_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, mem_fd.get(), 0);
    {
        MmapRegion region(ptr, BUFFER_SIZE);
        const std::string message = "Високошвидкісний кадр C++23 [PID=" + std::to_string(::getpid()) + "]";
        std::memcpy(region.data(), message.data(), message.size() + 1);
    }

    // Запечатування пам'яті
    ::fcntl(mem_fd.get(), F_ADD_SEALS, F_SEAL_SHRINK | F_SEAL_GROW);

    // 2. Створення eventfd
    UniqueFd evt_fd(::eventfd(0, EFD_CLOEXEC | EFD_NONBLOCK));

    // 3. Відправка дескрипторів клієнту
    ControlHeader hdr{.command_id = 42, .payload_size = BUFFER_SIZE};
    if (auto res = send_fds(server_sock.get(), hdr, mem_fd.get(), evt_fd.get()); !res) {
        std::cerr << "send_fds error: " << res.error() << std::endl;
        return 1;
    }

    // 4. Сигналізація готовності
    usleep(5000);
    uint64_t notify = 1;
    ::write(evt_fd.get(), &notify, sizeof(notify));

    ::wait(nullptr);
    std::cout << "[Сервер C++] Успішне завершення." << std::endl;
    return 0;
}
