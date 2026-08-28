static int pacer_fetch_policy(struct pacer_policy *dst, const void __user *uarg)
{
        u32 usize;
        int err;

        /* довжина лежить першою — читаємо її, ще нічого не знаючи про решту */
        if (get_user(usize, (const u32 __user *)uarg))
                return -EFAULT;

        if (usize < PACER_POLICY_SIZE_VER0)
                return -EINVAL;   /* коротше за найпершу версію — це не наша структура */
        if (usize > PAGE_SIZE)
                return -E2BIG;    /* стеля проти безглуздих чисел */

        /* три випадки одним викликом: збіг, добивання нулями, перевірка хвоста */
        err = copy_struct_from_user(dst, sizeof(*dst), uarg, usize);
        if (err)
                return err;       /* -E2BIG, якщо в хвості не самі нулі */

        if (dst->flags & ~(PACER_STRICT | PACER_NOTIFY | PACER_CGROUP))
                return -EINVAL;   /* біт, якого ми не знаємо */
        if (dst->__reserved0 | dst->__reserved1 | dst->__reserved2 | dst->__reserved3)
                return -EINVAL;   /* заповнювач мусить бути чистим */
        if (!(dst->flags & PACER_CGROUP) && dst->cgroup_fd)
                return -EINVAL;   /* поле без свого біта — теж прохання, якого ми не розуміємо */

        return 0;
}
