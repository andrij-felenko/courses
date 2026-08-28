/* Чи є dentry негативним (d_inode == NULL, файл гарантовано відсутній) */
static inline bool d_is_negative(const struct dentry *dentry);

/* Чи є dentry позитивним (d_inode != NULL, файл існує) */
static inline bool d_is_positive(const struct dentry *dentry);

/* Чи представляє dentry каталог (перевіряє прапорець DCACHE_DIRECTORY_TYPE) */
static inline bool d_is_dir(const struct dentry *dentry);

/* Чи представляє dentry символьне посилання (DCACHE_SYMLINK_TYPE) */
static inline bool d_is_symlink(const struct dentry *dentry);

/* Чи вилучено dentry з глобальної хеш-таблиці dentry_hashtable */
static inline int d_unhashed(const struct dentry *dentry);
