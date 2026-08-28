struct xfrm_policy {
    struct sibling_node     bydst;      /* Вузол хеш-таблиці за адресою призначення */
    struct hlist_node       byidx;      /* Пошуковий вузол за унікальним індексом */
    const struct net       *net;        /* Мережевий простір імен (netns) */
    u32                     index;      /* Індекс політики */
    u8                      type;       /* Тип політики (XFRM_POLICY_TYPE_MAIN) */
    u8                      action;     /* XFRM_POLICY_ALLOW / BLOCK */
    u16                     flags;      /* Прапорці конфігурації */
    u32                     priority;   /* Пріоритет (числове значення) */
    struct xfrm_selector    selector;   /* Селектор фільтрації трафіку */
    struct xfrm_lifetime_cfg lft;       /* Межі часу життя */
    struct xfrm_lifetime_cur curlft;    /* Поточна статистика */
    u16                     xfrm_nr;    /* Кількість шаблонів у ланцюжку */
    struct xfrm_tmpl        xfrm_vec[XFRM_MAX_DEPTH]; /* Шаблони необхідних SA */
};
