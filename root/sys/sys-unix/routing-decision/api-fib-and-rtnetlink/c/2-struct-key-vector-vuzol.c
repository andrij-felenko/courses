struct key_vector {
    t_key          key;        /* 32-бітне значення префіксу адреси */
    unsigned char  pos;        /* Позиція аналізованого біта (0..31 від старшого біта) */
    unsigned char  bits;       /* Кількість біт у даному рівні (stride size, k = 1..8) */
    unsigned char  slen;       /* Максимальна довжина суфіксу в піддереві */
    union {
        struct key_vector *tnode[0]; /* Масив з 2^bits вказівників на дочірні вузли (Branch) */
        struct hlist_head leaf;      /* Зв'язаний список об'єктів fib_alias (Leaf) */
    };
};
