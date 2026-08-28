struct pacer_caps {
        __u32 policy_size;
        __u64 flags;
        __u64 attrs;
};

/* чи є в ядрі поле з такою назвою — питання про довжину, а не про версію */
#define PACER_HAS(caps, field)                                          \
        ((caps)->policy_size >= offsetof(struct pacer_policy, field) +  \
                                sizeof(((struct pacer_policy *)0)->field))

static int pacer_caps_get(int fd, struct pacer_caps *out)
{
        struct pacer_info info = { .size = sizeof(info) };

        if (ioctl(fd, PACER_INFO, &info) == 0) {
                out->policy_size = info.policy_size;
                out->flags       = info.flags_supported;
                out->attrs       = info.attrs_supported;
                return 0;
        }

        /* драйвер не знає навіть самої команди-запиту — отже, він
           давніший за неї, а такою була рівно одна версія */
        if (errno == ENOTTY) {
                out->policy_size = PACER_POLICY_SIZE_VER0;
                out->flags       = PACER_STRICT;
                out->attrs       = 0;
                return 0;
        }
        return -1;
}
