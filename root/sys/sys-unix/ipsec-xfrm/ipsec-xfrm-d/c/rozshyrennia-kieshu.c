struct xfrm_dst {
    union {
        struct dst_entry    dst;
        struct xfrm_dst    *next;
    };
    struct dst_entry       *route;      /* Реальний вихідний маршрут фізичного пристрою */
    struct xfrm_policy     *policy;     /* Відповідна політика XFRM */
    struct xfrm_state      *xfrm_genid;
    u32                     xfrm_nr;    /* Кількість вкладених перетворень */
};
