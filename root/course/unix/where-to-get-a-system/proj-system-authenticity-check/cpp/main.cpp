#include <iostream>
#include <string>
#include <string_view>
#include <array>
#include <vector>
#include <expected>
#include <system_error>
#include <span>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <sys/un.h>

#if defined(__x86_64__) || defined(__i386__)
#include <cpuid.h>
#endif

// RAII-обгортка для файлових дескрипторів
class FileDescriptor {
public:
    explicit FileDescriptor(int fd = -1) noexcept : fd_(fd) {}
    ~FileDescriptor() noexcept { reset(); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.release()) {}
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
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

private:
    int fd_{-1};
};

void probe_cpuid_hypervisor() noexcept {
#if defined(__x86_64__) || defined(__i386__)
    unsigned int eax = 0, ebx = 0, ecx = 0, edx = 0;
    
    if (__get_cpuid(1, &eax, &ebx, &ecx, &edx)) {
        bool is_hypervisor = (ecx & (1U << 31)) != 0;
        std::cout << "[CPUID] Біт гіпервізора (Leaf 1, ECX.31): "
                  << (is_hypervisor ? "1 (Виявлено віртуалізацію)" : "0 (Пряме залізо / Bare Metal)")
                  << '\n';
        
        if (is_hypervisor && __get_cpuid(0x40000000, &eax, &ebx, &ecx, &edx)) {
            std::array<char, 13> sig{};
            std::memcpy(sig.data() + 0, &ebx, 4);
            std::memcpy(sig.data() + 4, &ecx, 4);
            std::memcpy(sig.data() + 8, &edx, 4);
            std::cout << "[CPUID] Сигнатура гіпервізора: \"" << sig.data() << "\"\n";
        }
    }
#else
    std::cout << "[CPUID] Архітектура не x86_64 (зондування CPUID пропущено)\n";
#endif
}

void probe_proc_kernel_version() {
    FileDescriptor fd(::open("/proc/version", O_RDONLY));
    if (!fd.valid()) {
        std::cout << "[PROC] /proc/version: НЕ ЗНАЙДЕНО (можлива емуляція Windows / Cygwin)\n";
        return;
    }

    std::array<char, 512> buf{};
    ssize_t n = ::read(fd.get(), buf.data(), buf.size() - 1);
    if (n > 0) {
        std::string_view content(buf.data(), static_cast<size_t>(n));
        std::cout << "[PROC] /proc/version знайдено:\n       "
                  << content.substr(0, 120) << "...\n";

        if (content.find("microsoft-standard-WSL2") != std::string_view::npos) {
            std::cout << "[ІДЕНТИФІКАЦІЯ] Виявлено середовище: WSL2 (Windows Hyper-V Micro-VM)\n";
        } else if (content.find("Microsoft") != std::string_view::npos) {
            std::cout << "[ІДЕНТИФІКАЦІЯ] Виявлено середовище: WSL1 (Емуляція ядра NT lxcore.sys)\n";
        }
    }
}

void probe_dmi_product() {
    FileDescriptor fd(::open("/sys/class/dmi/id/product_name", O_RDONLY));
    if (fd.valid()) {
        std::array<char, 128> buf{};
        ssize_t n = ::read(fd.get(), buf.data(), buf.size() - 1);
        if (n > 0) {
            std::string_view name(buf.data(), static_cast<size_t>(n));
            if (!name.empty() && name.back() == '\n') {
                name.remove_suffix(1);
            }
            std::cout << "[SYSFS] DMI product_name: \"" << name << "\"\n";
        }
    } else {
        std::cout << "[SYSFS] DMI таблиці недоступні у /sys/class/dmi/id/\n";
    }
}

void probe_container_markers() {
    bool is_docker = (::access("/.dockerenv", F_OK) == 0);
    bool is_containerenv = (::access("/run/.containerenv", F_OK) == 0);

    std::cout << "[CONTAINER] Маркери контейнеризації:\n"
              << "            /.dockerenv: " << (is_docker ? "ТАК (Docker)" : "НІ") << '\n'
              << "            /run/.containerenv: " << (is_containerenv ? "ТАК (Podman)" : "НІ") << '\n';

    FileDescriptor fd(::open("/proc/1/environ", O_RDONLY));
    if (fd.valid()) {
        std::array<char, 1024> buf{};
        ssize_t n = ::read(fd.get(), buf.data(), buf.size() - 1);
        if (n > 0) {
            std::span<const char> bytes(buf.data(), static_cast<size_t>(n));
            size_t offset = 0;
            while (offset < bytes.size()) {
                std::string_view var(bytes.data() + offset);
                if (var.starts_with("container=")) {
                    std::cout << "            /proc/1/environ: " << var << '\n';
                    break;
                }
                offset += var.size() + 1;
            }
        }
    }
}

void probe_posix_unlink_semantics() {
    char tmppath[] = "/tmp/probe_unlink_XXXXXX";
    FileDescriptor fd(::mkstemp(tmppath));
    if (!fd.valid()) {
        std::cout << "[POSIX-ТЕСТ] Не вдалося створити тимчасовий файл\n";
        return;
    }

    constexpr std::string_view payload = "Справжнє ядро зберігає inode відкритого файлу!";
    ::write(fd.get(), payload.data(), payload.size());

    if (::unlink(tmppath) != 0) {
        std::cout << "[POSIX-ТЕСТ] unlink() відкритого файлу ПРОВАЛЕНО (семантика блокування)\n";
        return;
    }

    if (::access(tmppath, F_OK) == 0) {
        std::cout << "[POSIX-ТЕСТ] Файл лишився видимим після unlink (порушення POSIX)\n";
    } else {
        ::lseek(fd.get(), 0, SEEK_SET);
        std::array<char, 128> readbuf{};
        ssize_t rb = ::read(fd.get(), readbuf.data(), readbuf.size() - 1);
        if (rb > 0 && std::string_view(readbuf.data(), static_cast<size_t>(rb)) == payload) {
            std::cout << "[POSIX-ТЕСТ] unlink() семантика: ВІДПОВІДАЄ POSIX (inode активний до close)\n";
        } else {
            std::cout << "[POSIX-ТЕСТ] Не вдалося прочитати з безіменного дескриптора\n";
        }
    }
}

void probe_af_unix_fd_passing() {
    std::array<int, 2> sv{-1, -1};
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, sv.data()) < 0) {
        std::cout << "[AF_UNIX] socketpair() провалено: емуляція сокетів\n";
        return;
    }

    FileDescriptor sock0(sv[0]);
    FileDescriptor sock1(sv[1]);
    FileDescriptor test_fd(::open("/dev/null", O_RDONLY));

    if (!test_fd.valid()) {
        return;
    }

    struct msghdr msg{};
    char iov_buf[1] = {'X'};
    struct iovec io{.iov_base = iov_buf, .iov_len = sizeof(iov_buf)};
    msg.msg_iov = &io;
    msg.msg_iovlen = 1;

    alignas(struct cmsghdr) char cmsg_buf[CMSG_SPACE(sizeof(int))]{};
    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);

    struct cmsghdr* cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));
    int raw_test_fd = test_fd.get();
    std::memcpy(CMSG_DATA(cmsg), &raw_test_fd, sizeof(int));

    if (::sendmsg(sock0.get(), &msg, 0) < 0) {
        std::cout << "[AF_UNIX] sendmsg(SCM_RIGHTS) провалено: емуляція без підтримки передачі дескрипторів\n";
    } else {
        std::cout << "[AF_UNIX] SCM_RIGHTS передача дескриптора: УСПІШНО (справжнє ядро IPC)\n";
    }
}

int main() {
    std::cout << "=== ДІАГНОСТИЧНИЙ ЗОНД АВТЕНТИЧНОСТІ ЯДРА ===\n\n";
    probe_cpuid_hypervisor();
    std::cout << '\n';
    probe_proc_kernel_version();
    std::cout << '\n';
    probe_dmi_product();
    std::cout << '\n';
    probe_container_markers();
    std::cout << '\n';
    probe_posix_unlink_semantics();
    std::cout << '\n';
    probe_af_unix_fd_passing();
    std::cout << "\n============================================\n";
    return 0;
}
