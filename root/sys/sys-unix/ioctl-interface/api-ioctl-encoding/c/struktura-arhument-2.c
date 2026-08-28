struct good_cfg c;

if (copy_from_user(&c, (void __user *)arg, sizeof(c)))
        return -EFAULT;
if (c.__pad || (c.flags & ~CFG_KNOWN_FLAGS))
        return -EINVAL;                 /* незнайомого не пропускаємо */
if (c.len == 0 || c.len > CFG_MAX_LEN)
        return -EINVAL;
if (copy_from_user(kbuf, u64_to_user_ptr(c.buf), c.len))
        return -EFAULT;
