#include <iostream>
#include <string>
#include <vector>
#include <array>
#include <memory>
#include <system_error>
#include <filesystem>
#include <fstream>
#include <cstddef>
#include <unistd.h>
#include <fcntl.h>
#include <sched.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/mount.h>
#include <sys/syscall.h>
#include <sys/prctl.h>
#include <sys/sysmacros.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>

namespace fs = std::filesystem;

class Pipe {
public:
    Pipe() {
        if (pipe(fds_.data()) < 0) {
            throw std::system_error(errno, std::generic_category(), "pipe failed");
        }
    }
    ~Pipe() {
        close_read();
        close_write();
    }
    Pipe(const Pipe&) = delete;
    Pipe& operator=(const Pipe&) = delete;

    int read_fd() const noexcept { return fds_[0]; }
    int write_fd() const noexcept { return fds_[1]; }

    void close_read() noexcept {
        if (fds_[0] >= 0) {
            close(fds_[0]);
            fds_[0] = -1;
        }
    }
    void close_write() noexcept {
        if (fds_[1] >= 0) {
            close(fds_[1]);
            fds_[1] = -1;
        }
    }

private:
    std::array<int, 2> fds_{-1, -1};
};

class CgroupScope {
public:
    explicit CgroupScope(const fs::path& path) : path_(path) {
        fs::create_directories(path_);
    }
    ~CgroupScope() {
        std::error_code ec;
        fs::remove(path_, ec);
    }
    CgroupScope(const CgroupScope&) = delete;
    CgroupScope& operator=(const CgroupScope&) = delete;

    void configure(pid_t pid, std::string_view memory_bytes,
                   std::string_view cpu_quota, std::string_view pids_max) {
        write_entry("cgroup.procs", std::to_string(pid) + "\n");
        write_entry("memory.max", std::string(memory_bytes) + "\n");
        write_entry("cpu.max", std::string(cpu_quota) + "\n");
        write_entry("pids.max", std::string(pids_max) + "\n");
    }

private:
    void write_entry(const std::string& filename, const std::string& data) {
        std::ofstream ofs(path_ / filename);
        if (!ofs) {
            throw std::runtime_error("Failed to open cgroup control file: " + filename);
        }
        ofs << data;
        if (!ofs) {
            throw std::runtime_error("Failed to write to cgroup control file: " + filename);
        }
    }
    fs::path path_;
};

struct ContainerConfig {
    std::string rootfs;
    std::vector<std::string> args;
    int read_pipe_fd;
};

class MiniContainer {
public:
    static void install_seccomp() {
        struct sock_filter filter[] = {
            BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

            BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_reboot, 5, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_kexec_load, 4, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_init_module, 3, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_finit_module, 2, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_swapon, 1, 0),

            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & 0xffff))
        };

        struct sock_fprog prog = {
            .len = static_cast<unsigned short>(sizeof(filter) / sizeof(filter[0])),
            .filter = filter,
        };

        if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "prctl(PR_SET_NO_NEW_PRIVS) failed");
        }

        if (syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) < 0) {
            throw std::system_error(errno, std::generic_category(), "seccomp filter failed");
        }
    }

    static void setup_rootfs(const std::string& rootfs) {
        if (mount(nullptr, "/", nullptr, MS_REC | MS_PRIVATE, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "mount MS_PRIVATE failed");
        }

        if (mount(rootfs.c_str(), rootfs.c_str(), nullptr, MS_BIND | MS_REC, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "mount bind rootfs failed");
        }

        fs::path old_root_path = fs::path(rootfs) / ".old_root";
        fs::create_directories(old_root_path);

        if (syscall(SYS_pivot_root, rootfs.c_str(), old_root_path.c_str()) < 0) {
            throw std::system_error(errno, std::generic_category(), "pivot_root failed");
        }

        if (chdir("/") < 0) {
            throw std::system_error(errno, std::generic_category(), "chdir / failed");
        }

        if (umount2("/.old_root", MNT_DETACH) < 0) {
            throw std::system_error(errno, std::generic_category(), "umount2 .old_root failed");
        }
        fs::remove("/.old_root");

        fs::create_directories("/proc");
        if (mount("proc", "/proc", "proc", MS_NOSUID | MS_NODEV | MS_NOEXEC, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "mount /proc failed");
        }

        fs::create_directories("/sys");
        if (mount("sysfs", "/sys", "sysfs", MS_RDONLY | MS_NOSUID | MS_NODEV | MS_NOEXEC, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "mount /sys failed");
        }

        fs::create_directories("/dev");
        mount("tmpfs", "/dev", "tmpfs", MS_NOSUID | MS_STRICTATIME, "mode=755");

        mknod("/dev/null", S_IFCHR | 0666, makedev(1, 3));
        mknod("/dev/zero", S_IFCHR | 0666, makedev(1, 5));
        mknod("/dev/urandom", S_IFCHR | 0666, makedev(1, 9));
    }

    static int child_exec(void* arg) {
        auto* config = static_cast<ContainerConfig*>(arg);

        char byte_buf;
        while (read(config->read_pipe_fd, &byte_buf, 1) > 0) {}
        close(config->read_pipe_fd);

        sethostname("minibox", 7);

        try {
            setup_rootfs(config->rootfs);
            install_seccomp();
        } catch (const std::exception& ex) {
            std::cerr << "Container init error: " << ex.what() << "\n";
            return 1;
        }

        std::vector<char*> raw_args;
        raw_args.reserve(config->args.size() + 1);
        for (auto& s : config->args) {
            raw_args.push_back(s.data());
        }
        raw_args.push_back(nullptr);

        execvp(raw_args[0], raw_args.data());
        perror("execvp");
        return 1;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <rootfs_path> <cmd> [args...]\n";
        return 1;
    }

    if (getuid() != 0) {
        std::cerr << "Помилка: програма вимагає прав суперкористувача (root)\n";
        return 1;
    }

    try {
        Pipe sync_pipe;
        CgroupScope cgroup("/sys/fs/cgroup/minibox");

        ContainerConfig config;
        config.rootfs = argv[1];
        for (int i = 2; i < argc; ++i) {
            config.args.emplace_back(argv[i]);
        }
        config.read_pipe_fd = sync_pipe.read_fd();

        constexpr size_t stack_size = 1024 * 1024;
        auto stack = std::make_unique<char[]>(stack_size);
        char* stack_top = stack.get() + stack_size;

        int flags = CLONE_NEWNS | CLONE_NEWPID | CLONE_NEWUTS |
                    CLONE_NEWIPC | CLONE_NEWNET | CLONE_NEWCGROUP | SIGCHLD;

        pid_t child_pid = clone(MiniContainer::child_exec, stack_top, flags, &config);
        if (child_pid < 0) {
            throw std::system_error(errno, std::generic_category(), "clone failed");
        }

        sync_pipe.close_read();
        cgroup.configure(child_pid, "67108864", "20000 100000", "32");
        sync_pipe.close_write();

        int status = 0;
        waitpid(child_pid, &status, 0);

        if (WIFEXITED(status)) {
            return WEXITSTATUS(status);
        }
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
