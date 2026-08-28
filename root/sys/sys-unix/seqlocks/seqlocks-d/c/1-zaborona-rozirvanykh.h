/* НЕБЕЗПЕЧНО! Заборонено використовувати seqlock з вказівниками! */
struct network_config {
    struct route_table *routes;
};

/* Читач у драйвері */
do {
    seq = read_seqbegin(&cfg_lock);
    ptr = global_cfg.routes;
    /* ЯКЩО ПИСЬМЕННИК В ЦЕЙ МОМЕНТ ЗВІЛЬНИТЬ ПАМ'ЯТЬ (kfree(ptr)): */
    val = ptr->default_gateway; /* звернення до звільненої пам'яті: Oops / Kernel Panic! */
} while (read_seqretry(&cfg_lock, seq));
