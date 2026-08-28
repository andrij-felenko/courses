static void pacer_fill_info(struct pacer_info *ki)
{
        memset(ki, 0, sizeof(*ki));
        ki->size            = sizeof(*ki);
        ki->flags_supported = PACER_STRICT | PACER_NOTIFY | PACER_CGROUP;
        ki->attrs_supported = PACER_ATTRS_KNOWN;  /* мапа типів, які ми розбираємо */
        ki->policy_size     = sizeof(struct pacer_policy);
}

static int pacer_put_info(void __user *uarg)
{
        struct pacer_info ki;
        u32 usize;

        if (get_user(usize, (const u32 __user *)uarg))
                return -EFAULT;
        if (usize < PACER_INFO_SIZE_VER0)
                return -EINVAL;

        pacer_fill_info(&ki);

        /* віддаємо стільки, скільки програма здатна прийняти, але size — наш */
        if (copy_to_user(uarg, &ki, min_t(u32, usize, sizeof(ki))))
                return -EFAULT;
        if (usize > sizeof(ki) &&
            clear_user((char __user *)uarg + sizeof(ki), usize - sizeof(ki)))
                return -EFAULT;   /* хвіст, якого ми не заповнили, мусить бути чистим */

        return 0;
}
