#include <linux/sched.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <system_error>

pid_t invoke_clone3_user_ns() {
    struct clone_args cl_args{};
    cl_args.flags = CLONE_NEWUSER | CLONE_NEWNS | CLONE_NEWNET;
    cl_args.exit_signal = SIGCHLD;
    
    long pid = ::syscall(SYS_clone3, &cl_args, sizeof(cl_args));
    if (pid == -1) {
        throw std::system_error(errno, std::generic_category(), "clone3 failed");
    }
    return static_cast<pid_t>(pid);
}
