/* Виділити новий dentry в slab-кеші dentry_cache як нащадка parent із заданим іменем name */
struct dentry *d_alloc(struct dentry *parent, const struct qstr *name);

/* Виділити анонімний dentry, не прив'язаний до батьківського каталогу (для кореня або сокетів) */
struct dentry *d_alloc_anon(struct super_block *sb);

/* Зв'язати новий dentry з існуючим inode (створити позитивний запис) */
void d_instantiate(struct dentry *dentry, struct inode *inode);

/* Додати новий dentry в хеш-таблицю dentry_hashtable та прив'язати до inode (або NULL) */
void d_add(struct dentry *dentry, struct inode *inode);

/* Спеціалізоване додавання для файлових систем без урахування регістру (case-insensitive) */
struct dentry *d_add_ci(struct dentry *dentry, struct inode *inode, struct qstr *name);

/* Прив'язати або підмінити аліас каталогу (критично для NFS та переміщень каталогів) */
struct dentry *d_splice_alias(struct inode *inode, struct dentry *dentry);
