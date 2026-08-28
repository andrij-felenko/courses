struct key_vector {
    t_key          key;        /* Префікс адреси */
    unsigned char  pos;        /* Позиція аналізованого біта (0..31) */
    unsigned char  bits;       /* Кількість біт у рівні (stride k) */
    unsigned char  slen;       /* Максимальна довжина суфіксу */
    union {
        struct key_vector *tnode[0]; /* Масив дочірніх вузлів (якщо bits > 0) */
        struct hlist_head leaf;      /* Зв'язаний список fib_alias (якщо bits == 0) */
    };
};
