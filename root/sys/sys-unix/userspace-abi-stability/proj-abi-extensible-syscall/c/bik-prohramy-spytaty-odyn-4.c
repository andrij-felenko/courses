int pacer_arm(int fd, const struct pacer_caps *caps,
              __u64 rate, __u32 burst, __u64 deadline_ns, int cgroup_fd)
{
        struct pacer_policy p = { 0 };   /* обнулити ВСЮ структуру — обов'язково */

        if (deadline_ns && !PACER_HAS(caps, deadline_ns))
                return -1;               /* дедлайну тут не буде — вирішує програма */
        if (cgroup_fd >= 0 && !(caps->flags & PACER_CGROUP))
                return -1;

        p.size  = sizeof(p);
        p.flags = PACER_STRICT;
        p.rate  = rate;
        p.burst = burst;
        p.deadline_ns = deadline_ns;
        if (cgroup_fd >= 0) {
                p.flags     |= PACER_CGROUP;
                p.cgroup_fd  = cgroup_fd;
        }

        /* сюди ми входимо, лише знаючи, що ядро це вміє; E2BIG чи EINVAL
           звідси — не «старе ядро», а помилка в нашому власному коді */
        return ioctl(fd, PACER_ARM, &p);
}
