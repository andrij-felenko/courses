/* Збільшити лічильник посилань dentry (перехід у стан Active) */
struct dentry *dget(struct dentry *dentry);

/* Безпечно отримати посилання на батьківський каталог із захистом від паралельного переміщення */
struct dentry *dget_parent(struct dentry *dentry);

/* Зменшити лічильник посилань. Якщо d_count стає 0, запис переміщується до списку LRU */
void dput(struct dentry *dentry);

/* Зменшити лічильник і перенести dentry у вказаний тимчасовий список для пакетного вивільнення */
void dput_to_list(struct dentry *dentry, struct list_head *list);

/* Примусово вилучити dentry з глобальної хеш-таблиці (позначити як unhashed/застарілий) */
void d_drop(struct dentry *dentry);

/* Позначити dentry як видалений та ініціювати його вивільнення або перетворення на негативний */
void d_delete(struct dentry *dentry);

/* Зробити недійсним dentry та всі його дочірні записи, примусово очищаючи піддерево */
void d_invalidate(struct dentry *dentry);
