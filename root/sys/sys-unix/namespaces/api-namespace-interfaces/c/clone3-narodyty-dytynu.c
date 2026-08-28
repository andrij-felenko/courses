/* визначення з <linux/sched.h> */
struct clone_args {
    __aligned_u64 flags;        /* CLONE_NEW* через «або» */
    __aligned_u64 pidfd;        /* куди покласти дескриптор дитини */
    __aligned_u64 child_tid;
    __aligned_u64 parent_tid;
    __aligned_u64 exit_signal;  /* окреме поле — тому CSIGNAL тут не заважає */
    __aligned_u64 stack;
    __aligned_u64 stack_size;
    __aligned_u64 tls;
    __aligned_u64 set_tid;      /* замовити конкретні номери по рівнях */
    __aligned_u64 set_tid_size;
    __aligned_u64 cgroup;
};

/* обгортки в glibc немає — виклик роблять напряму */
long res = syscall(SYS_clone3, &args, sizeof args);
