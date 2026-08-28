struct xfrm_userpolicy_info {
    struct xfrm_selector sel;        /* Селектор трафіку (IP, порти, протокол) */
    struct xfrm_lifetime_cfg lft;    /* Обмеження часу життя політики */
    struct xfrm_lifetime_cur curlft; /* Поточний стан використання політики */
    __u32                priority;   /* Пріоритет (менше значення = вища перевага) */
    __u32                index;      /* Унікальний системний індекс політики */
    __u8                 dir;        /* Напрямок: XFRM_POLICY_IN, OUT, FWD */
    __u8                 action;     /* Дія: XFRM_POLICY_ALLOW або XFRM_POLICY_BLOCK */
    __u8                 flags;      /* Додаткові прапорці політики */
    __u8                 share;      /* Рівень спільного використання (XFRM_SHARE_ANY) */
};
