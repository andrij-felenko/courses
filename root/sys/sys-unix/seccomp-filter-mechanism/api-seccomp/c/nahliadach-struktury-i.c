struct seccomp_notif_sizes { __u16 seccomp_notif, seccomp_notif_resp, seccomp_data; };

struct seccomp_notif      { __u64 id; __u32 pid; __u32 flags; struct seccomp_data data; };
struct seccomp_notif_resp { __u64 id; __s64 val; __s32 error; __u32 flags; };
struct seccomp_notif_addfd{ __u64 id; __u32 flags; __u32 srcfd, newfd, newfd_flags; };

#define SECCOMP_USER_NOTIF_FLAG_CONTINUE   (1UL << 0)  /* у resp.flags, з 5.5 */
#define SECCOMP_ADDFD_FLAG_SETFD           (1UL << 0)  /* вжити задане newfd */
#define SECCOMP_ADDFD_FLAG_SEND            (1UL << 1)  /* addfd + send атомарно, з 5.14 */
#define SECCOMP_USER_NOTIF_FD_SYNC_WAKE_UP (1UL << 0)  /* у SET_FLAGS, з 6.6 */
