#ifndef CGROUP2_SUPER_MAGIC
#  define CGROUP2_SUPER_MAGIC 0x63677270   /* байти "cgrp" */
#endif

static int probe_cgroup2(void)
{
    struct statfs sf;
    if (statfs("/sys/fs/cgroup", &sf) != 0)
        return 0;                  /* точки монтування немає — відповіді немає */
    return sf.f_type == CGROUP2_SUPER_MAGIC;
}
