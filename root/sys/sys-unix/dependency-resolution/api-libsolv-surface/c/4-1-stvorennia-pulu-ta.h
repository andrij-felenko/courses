// Створення нового центрального пулу пам'яті
Pool *pool_create(void);

// Звільнення пам'яті пулу та всіх пов'язаних репозиторіїв і пакунків
void pool_free(Pool *pool);

// Перетворення сирого рядка у 32-бітний Id (create = 1 створює новий Id, якщо його не було)
Id pool_str2id(Pool *pool, const char *str, int create);

// Отримання сирого текстового рядка за його Id
const char *pool_id2str(const Pool *pool, Id id);

// Створення об'єкта репозиторію у пулі
Repo *repo_create(Pool *pool, const char *name);

// Призначення репозиторію як системного (містить вже встановлені пакунки)
void pool_set_installed(Pool *pool, Repo *repo);

// Побудова внутрішньої хеш-таблиці зворотної відповідності залежностей
void pool_createwhatprovides(Pool *pool);
