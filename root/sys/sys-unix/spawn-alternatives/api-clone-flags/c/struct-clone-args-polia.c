struct clone_args {
    __aligned_u64 flags;
    __aligned_u64 pidfd;
    __aligned_u64 child_tid;      /* увага: спершу child, потім parent —    */
    __aligned_u64 parent_tid;     /* у сирому clone порядок саме зворотний  */
    __aligned_u64 exit_signal;
    __aligned_u64 stack;          /* найнижчий байт, а не верхівка          */
    __aligned_u64 stack_size;
    __aligned_u64 tls;
    __aligned_u64 set_tid;        /* з 5.5 */
    __aligned_u64 set_tid_size;   /* з 5.5 */
    __aligned_u64 cgroup;         /* з 5.7 */
};
