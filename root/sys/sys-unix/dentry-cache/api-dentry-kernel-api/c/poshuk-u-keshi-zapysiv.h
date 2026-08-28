/* Знайти дочірній dentry за іменем name у каталозі parent через dentry_hashtable */
struct dentry *d_lookup(const struct dentry *parent, const struct qstr *name);

/* Обчислити хеш рядка та виконати швидкий пошук dentry в каталозі parent */
struct dentry *d_hash_and_lookup(struct dentry *parent, struct qstr *name);

/* Знайти або створити dentry для рядка заданої довжини (вимагає захоплення блокування каталогу) */
struct dentry *lookup_one_len(const char *name, struct dentry *base, int len);

/* Знайти або створити dentry для рядка заданої довжини без блокування батьківського каталогу */
struct dentry *lookup_one_len_unlocked(const char *name, struct dentry *base, int len);
