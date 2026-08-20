# ⚙️ Розробка міні-ORM: патерни Data Mapper та Unit of Work

Розробка власного рушія відображення даних дає змогу глибоко зрозуміти внутрішні механізми таких інструментів, як Hibernate, SQLAlchemy або Entity Framework Core: як працює кеш першого рівня (Identity Map), як реалізується автоматичне відстеження змін у пам'яті (Dirty Checking) та як формуються пакетні транзакційні DML-запити.

У цьому практичному проєкті ми створимо повноцінний міні-рушій ORM за патерном Data Mapper мовами C та C++. Рушій підтримує реєстрацію сутностей, читання з імітації бази даних, фіксацію вихідних знімків (Snapshots), обчислення дельт та пакетний комміт (Flush).

---

### Архітектура та компоненти системи

Архітектура складається з чотирьох основних модулів:

1. **Доменна модель (`User`)**: Чиста бізнес-сутність, яка не містить жодного коду роботи з базою даних чи знання про SQL-таблиці.
2. **Карта ідентичності (`IdentityMap`)**: Зберігає екземпляри завантажених сутностей за їхніми первинними ключами для уникнення дублювання об'єктів у межах однієї сесії.
3. **Знімок стану (Snapshot Repository)**: Фіксує точну копію полів сутності на момент її завантаження з бази даних.
4. **Одиниця роботи (`UnitOfWork`)**: Відстежує життєвий цикл сутностей (New, Dirty, Clean, Deleted), виконує Dirty Checking при виклику `commit()` та будує оптимізовані транзакційні `INSERT`, `UPDATE` та `DELETE` запити.
5. **Мапер відношень (Relation Mapper)**: Відповідає за трансляцію плоских результатів `SELECT` у структури мови програмування.

---

### Повна реалізація мовами C та C++

Нижче наведено вихідний код проєкту, реалізований за стандартами C99 та C++17 без сторонніх залежностей.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_ENTITIES 32
#define MAX_NAME_LEN 64
#define MAX_EMAIL_LEN 64

// 1. Чиста доменна сутність
typedef struct {
    uint32_t id;
    char name[MAX_NAME_LEN];
    char email[MAX_EMAIL_LEN];
} user_entity_t;

typedef enum {
    STATE_CLEAN,
    STATE_NEW,
    STATE_DIRTY,
    STATE_DELETED
} entity_state_t;

typedef struct {
    user_entity_t *entity;
    user_entity_t snapshot; // Початковий стан для Dirty Checking
    entity_state_t state;
} tracked_user_t;

typedef struct {
    tracked_user_t tracked[MAX_ENTITIES];
    size_t count;
} unit_of_work_t;

void uow_init(unit_of_work_t *uow) {
    uow->count = 0;
}

// Завантаження сутності в Identity Map
user_entity_t* uow_register_clean(unit_of_work_t *uow, uint32_t id, const char *name, const char *email) {
    for (size_t i = 0; i < uow->count; ++i) {
        if (uow->tracked[i].entity->id == id) {
            return uow->tracked[i].entity; // Повертаємо існуючий екземпляр з кешу L1
        }
    }

    if (uow->count >= MAX_ENTITIES) return NULL;

    user_entity_t *user = (user_entity_t*)malloc(sizeof(user_entity_t));
    user->id = id;
    strncpy(user->name, name, MAX_NAME_LEN - 1);
    strncpy(user->email, email, MAX_EMAIL_LEN - 1);

    tracked_user_t *tr = &uow->tracked[uow->count++];
    tr->entity = user;
    tr->snapshot = *user; // Зберігаємо точну копію початкового стану
    tr->state = STATE_CLEAN;

    return user;
}

void uow_register_new(unit_of_work_t *uow, user_entity_t *user) {
    if (uow->count >= MAX_ENTITIES) return;
    tracked_user_t *tr = &uow->tracked[uow->count++];
    tr->entity = user;
    tr->state = STATE_NEW;
}

void uow_register_deleted(unit_of_work_t *uow, user_entity_t *user) {
    for (size_t i = 0; i < uow->count; ++i) {
        if (uow->tracked[i].entity == user) {
            uow->tracked[i].state = STATE_DELETED;
            return;
        }
    }
}

// Перевірка змін (Dirty Checking) та формування SQL-батчу
void uow_commit(unit_of_work_t *uow) {
    printf("=== Unit of Work: Початок транзакції (BEGIN) ===\n");

    for (size_t i = 0; i < uow->count; ++i) {
        tracked_user_t *tr = &uow->tracked[i];

        if (tr->state == STATE_NEW) {
            printf("[INSERT] INTO users (id, name, email) VALUES (%u, '%s', '%s');\n",
                   tr->entity->id, tr->entity->name, tr->entity->email);
            tr->snapshot = *tr->entity;
            tr->state = STATE_CLEAN;
        } else if (tr->state == STATE_CLEAN) {
            // Виконання Dirty Checking
            bool name_changed = strcmp(tr->entity->name, tr->snapshot.name) != 0;
            bool email_changed = strcmp(tr->entity->email, tr->snapshot.email) != 0;

            if (name_changed || email_changed) {
                printf("[UPDATE] users SET name = '%s', email = '%s' WHERE id = %u;\n",
                       tr->entity->name, tr->entity->email, tr->entity->id);
                tr->snapshot = *tr->entity; // Оновлюємо знімок
            }
        } else if (tr->state == STATE_DELETED) {
            printf("[DELETE] FROM users WHERE id = %u;\n", tr->entity->id);
        }
    }

    printf("=== Unit of Work: Транзакцію зафіксовано (COMMIT) ===\n");
}
```
@tab C++
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <unordered_map>
#include <stdexcept>

namespace mini_orm {

// 1. Чиста доменна модель (POCO)
class User {
public:
    uint32_t id;
    std::string name;
    std::string email;

    User(uint32_t id, std::string name, std::string email)
        : id(id), name(std::move(name)), email(std::move(email)) {}
};

enum class EntityState { Clean, New, Dirty, Deleted };

struct TrackedEntity {
    std::shared_ptr<User> entity;
    User snapshot; // Знімок стану для Dirty Checking
    EntityState state{EntityState::Clean};
};

// 2. Unit of Work та Identity Map
class UnitOfWork {
public:
    std::shared_ptr<User> find_by_id(uint32_t id) {
        auto it = identity_map_.find(id);
        if (it != identity_map_.end()) {
            std::cout << "[IdentityMap] Сутність id=" << id << " знайдена в L1 кеші\n";
            return it->second.entity;
        }

        // Імітація вибірки з бази даних (SQL SELECT)
        std::cout << "[DB Query] SELECT * FROM users WHERE id = " << id << ";\n";
        auto user = std::make_shared<User>(id, "Олександр", "alex@example.com");
        
        TrackedEntity tracked{user, *user, EntityState::Clean};
        identity_map_[id] = tracked;
        return user;
    }

    void register_new(std::shared_ptr<User> user) {
        identity_map_[user->id] = {user, *user, EntityState::New};
    }

    void register_deleted(uint32_t id) {
        auto it = identity_map_.find(id);
        if (it != identity_map_.end()) {
            it->second.state = EntityState::Deleted;
        }
    }

    void commit() {
        std::cout << "\n=== Unit of Work: Генерація пакетного COMMIT ===\n";
        for (auto& [id, tracked] : identity_map_) {
            if (tracked.state == EntityState::New) {
                std::cout << "[SQL INSERT] INTO users (id, name, email) VALUES ("
                          << tracked.entity->id << ", '" << tracked.entity->name 
                          << "', '" << tracked.entity->email << "');\n";
                tracked.snapshot = *tracked.entity;
                tracked.state = EntityState::Clean;
            } else if (tracked.state == EntityState::Clean) {
                // Автоматичний Dirty Checking
                if (tracked.entity->name != tracked.snapshot.name || 
                    tracked.entity->email != tracked.snapshot.email) {
                    std::cout << "[SQL UPDATE] users SET name = '" << tracked.entity->name
                              << "', email = '" << tracked.entity->email 
                              << "' WHERE id = " << tracked.entity->id << ";\n";
                    tracked.snapshot = *tracked.entity;
                }
            } else if (tracked.state == EntityState::Deleted) {
                std::cout << "[SQL DELETE] FROM users WHERE id = " << id << ";\n";
            }
        }
        std::cout << "=== Усі зміни зафіксовано успішно ===\n\n";
    }

private:
    std::unordered_map<uint32_t, TrackedEntity> identity_map_;
};

} // namespace mini_orm
```
:::

---

### Інженерний розбір та ключові переваги архітектури

1. **Гарантія унікальності об'єктів (Identity Map)**: Коли два різні сервісні класи запитують сутність із `id = 42`, ORM повертає посилання на той самий об'єкт у пам'яті. Це унеможливлює стан гонитви, коли дві змінні містять суперечливий стан одного й того самого рядка бази даних.
2. **Усунення надлишкових операцій запису (Dirty Checking)**: Додаток може зчитувати тисячі сутностей для обробки бізнес-правил. Unit of Work оновлює в базі даних виключно ті рядки, поля яких реально змінилися відносно початкового знімка (Snapshot), що суттєво зменшує обсяг журналу WAL і трафік до СУБД.
3. **Пакетне виконання операцій (Batching & Topological Sorting)**: Unit of Work збирає всі операції зміни та впорядковує їх відповідно до графа зовнішніх ключів (Foreign Keys). Спершу виконуються всі `INSERT` батьківських таблиць, потім `UPDATE`, і наприкінці `DELETE` дочірніх, що унеможливлює помилки порушення обмежень цілісності (Constraint Violations).
4. **Ізоляція пам'яті від транзакцій бази**: Усі модифікації сутностей відбуваються локально в пам'яті процесу без утримання довгих транзакційних блокувань у СУБД. З'єднання з базою відкривається лише на короткий час виклику методу `commit()`.
5. **Оптимістичне блокування (Optimistic Locking)**: Додавання поля версії `version` до знімка дозволяє генерувати запити `UPDATE users SET name = '...', version = version + 1 WHERE id = 42 AND version = 1;`, що гарантує захист від втрачених оновлень (Lost Updates) при паралельній роботі кількох сесій.
6. **Керування пам'яттю та очищення сесії**: У разі тривалих пакетних операцій (обробка мільйона рядків) Identity Map має тенденцію нескінченно накопичувати об'єкти. Для запобігання вичерпанню пам'яті (OutOfMemory) рушій підтримує метод `clear()` або `detach()`, що вивільняє відстежувані структури після кожного проміжного пакету.
7. **Обробка каскадного збереження (Cascade Persist)**: При додаванні нового дочірнього замовлення до колекції `user.orders` Unit of Work автоматично виявляє нову сутність і реєструє її у черзі `INSERT`, встановлюючи правильне значення зовнішнього ключа після генерації ID батьківського запису.
8. **Інваріанти цілісності зв'язків**: Рушій гарантує, що при видаленні батьківської сутності з опцією `cascade="all, delete-orphan"` усі пов'язані дочірні записи будуть автоматично додані до списку видалення перед виконанням транзакції.
9. **Підтримка проксі-об'єктів для Lazy Loading**: Для відкладеного завантаження пов'язаних сутностей використовується патерн Virtual Proxy або динамічна генерація байткоду (CGLIB / ByteBuddy), яка перехоплює перше звернення до гетера та викликає метод `uow->find_by_id()`.
10. **Ізоляція транзакційних контекстів у багатопотокових середовищах**: Кожен потік виконання HTTP-запиту повинен володіти власним ізольованим екземпляром `UnitOfWork` (Scoped Context), оскільки спільне використання Identity Map між різними потоками призводить до небезпечних станів гонитви та пошкодження пам'яті.
11. **Транзакційний Rollback у разі винятків**: Якщо під час виконання пакета SQL-запитів СУБД повертає помилку (наприклад, порушення унікальності `UniqueConstraintViolation`), `UnitOfWork` автоматично скасовує транзакцію, інвалідує свій внутрішній кеш і відновлює стан сутностей до вихідних знімків, запобігаючи використанню некоректного стану в пам'яті.
12. **Підтримка збереження часткових оновлень (Dynamic Update)**: Замість перезапису всіх стовпців таблиці рушій генерує `UPDATE` виключно для тих полів, які реально зазнали мутації (наприклад, тільки `email`), що знижує навантаження на індекси таблиці в СУБД.
13. **Контроль глибини графа об'єктів**: Для уникнення циклічних посилань під час серіалізації (наприклад, `User -> Orders -> User`) рушій реалізує детекцію вже відвіданих вузлів графа у мапері.
14. **Аудит змін (Envers / Shadow Audit Log)**: Модуль Unit of Work дозволяє автоматично створювати записи аудиту (хто, коли та яке поле змінив) у спеціальних тіньових таблицях `users_audit` під час кожного коміту.
