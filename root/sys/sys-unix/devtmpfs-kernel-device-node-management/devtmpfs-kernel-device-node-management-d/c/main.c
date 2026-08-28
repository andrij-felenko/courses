static struct req {
    struct req *next;
    struct completion done;
    int err;
    const char *name;
    umode_t mode;   /* 0 => delete */
    kuid_t uid;
    kgid_t gid;
    struct device *dev;
} *requests;
