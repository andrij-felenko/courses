        const struct pacer_attr *tab[PACER_ATTR_MAX + 1];
        void *tail = NULL;

        if (pol.attrs_len) {
                if (pol.attrs_len > PACER_ATTRS_MAX_LEN)
                        return -E2BIG;
                tail = memdup_user(u64_to_user_ptr(pol.attrs), pol.attrs_len);
                if (IS_ERR(tail))
                        return PTR_ERR(tail);
                err = pacer_parse(tail, pol.attrs_len, tab, PACER_ATTR_MAX);
        }
