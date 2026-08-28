#include <iostream>
#include <string>
#include <vector>
#include <array>
#include <system_error>
#include <unistd.h>
#include <sys/wait.h>
#include <fcntl.h>

struct ShellContext {
    int execution_counter = 0;
    std::string current_working_dir = "/var/log";
};

class FileDescriptor {
    int fd_ = -1;
public:
    explicit FileDescriptor(int fd) : fd_(fd) {}
    ~FileDescriptor() { if (fd_ >= 0) ::close(fd_); }
    int get() const noexcept { return fd_; }
    
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    FileDescriptor(FileDescriptor&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    FileDescriptor& operator=(FileDescriptor&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
};

void demonstrate_cpp_subshell_isolation() {
    ShellContext ctx;
    
    int raw_fd = ::open("/tmp/subshell_test_cpp.log", O_CREAT | O_RDWR | O_TRUNC, 0644);
    if (raw_fd == -1) {
        throw std::system_error(errno, std::generic_category(), "open failed");
    }
    FileDescriptor shared_fd(raw_fd);

    std::cout << "[Parent Before Fork] Counter: " << ctx.execution_counter 
              << ", CWD: " << ctx.current_working_dir << "\n";

    pid_t pid = ::fork();
    if (pid < 0) {
        throw std::system_error(errno, std::generic_category(), "fork failed");
    }

    if (pid == 0) {
        // Дочірній процес (Subshell)
        std::cout << "  [Subshell PID " << ::getpid() << "] Modifying context...\n";
        ctx.execution_counter = 999;
        ctx.current_working_dir = "/tmp";

        std::string subshell_msg = "Line from modern C++ subshell\n";
        ::write(shared_fd.get(), subshell_msg.data(), subshell_msg.size());

        std::cout << "  [Subshell PID " << ::getpid() << "] Counter: " 
                  << ctx.execution_counter << ", CWD: " << ctx.current_working_dir << "\n";
        std::exit(0);
    }

    int status = 0;
    ::waitpid(pid, &status, 0);

    std::string parent_msg = "Line from modern C++ parent\n";
    ::write(shared_fd.get(), parent_msg.data(), parent_msg.size());

    std::cout << "[Parent After Wait] Counter: " << ctx.execution_counter 
              << " (Unchanged), CWD: " << ctx.current_working_dir << "\n";

    ::lseek(shared_fd.get(), 0, SEEK_SET);
    std::array<char, 256> buf{};
    ssize_t n = ::read(shared_fd.get(), buf.data(), buf.size() - 1);
    if (n > 0) {
        buf[n] = '\0';
        std::cout << "[File Content Analysis]:\n" << buf.data();
    }

    ::unlink("/tmp/subshell_test_cpp.log");
}

int main() {
    try {
        demonstrate_cpp_subshell_isolation();
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
