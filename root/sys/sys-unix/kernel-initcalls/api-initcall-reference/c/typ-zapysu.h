typedef int (*initcall_t)(void);

#ifdef CONFIG_HAVE_ARCH_PREL32_RELOCATIONS
typedef int initcall_entry_t;          /* 4 байти: знаковий зсув */
#else
typedef initcall_t initcall_entry_t;   /* повний покажчик */
#endif

static inline initcall_t initcall_from_entry(initcall_entry_t *entry);
extern int do_one_initcall(initcall_t fn);
