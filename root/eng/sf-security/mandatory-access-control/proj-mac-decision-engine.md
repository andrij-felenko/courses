# ⚙️ Реалізація рушія Type Enforcement та Access Vector Cache (AVC)

Рушій обов'язкового контролю доступу (MAC) у ядрі операційної системи розв'язує фундаментальну інженерну задачу: за заданим безпековим контекстом суб'єкта S, контекстом об'єкта O та класом операції C визначити бітову маску дозволених дій (Access Vector).

Оскільки прямий пошук у бінарному графі компільованої політики безпеки вимагає обходу сотень тисяч правил і є занадто повільним для критичного шляху системних викликів, архітектура FLASK (використана в SELinux) розділяє систему на дві взаємодіючі компоненти:
1. **Точка застосування політики (Policy Enforcement Point, PEP):** хуки LSM у ядрі, які перехоплюють системні виклики VFS, IPC та сокетів.
2. **Точка ухвалення рішень (Policy Decision Point, PDP) та Access Vector Cache (AVC):** високошвидкісна хеш-таблиця в оперативній пам'яті, що кешує результат перевірки для трійки `(source_type, target_type, target_class)`.

Нижче наведено детальний архітектурний розбір внутрішніх структур даних, механізмів синхронізації та повну програмну реалізацію рушія рішень Type Enforcement та кешу AVC мовами C та C++.

---

### 1. Анатомія вектора доступу та правила Type Enforcement

У моделі Type Enforcement усі дозволи для кожного класу об'єктів кодуються у вигляді 32-бітної бітової маски — **вектора доступу** (англ. *Access Vector*). Кожен біт у цьому векторі відповідає атомарній операції над об'єктом. Наприклад, для класу `file` вектор кодує такі права:
- Біт 0 (`1U << 0`): `read` — дозвіл на зчитування вмісту файлу;
- Біт 1 (`1U << 1`): `write` — дозвіл на прямий запис та модифікацію існуючих байтів;
- Біт 2 (`1U << 2`): `execute` — дозвіл на завантаження та виконання коду у пам'ять процесу;
- Біт 3 (`1U << 3`): `append` — дозвіл на дописування даних виключно в кінець файлу (режим логування);
- Біт 4 (`1U << 4`): `getattr` — читання метаданих іноди (`stat`, `lstat`);
- Біт 5 (`1U << 5`): `setattr` — зміна часових міток, прав власності або розміру файлу;
- Біт 6 (`1U << 6`): `unlink` — видалення посилання на файл із каталогу.

Правила політики безпеки є строго **адитивними**: якщо для певної пари доменів визначено декілька правил `allow`, рушій безпеки обчислює побітове логічне АБО (`OR`) між векторами всіх відповідних правил. Якщо для запитаної операції немає жодного правила `allow`, діє системне правило заборони за замовчуванням (Deny-by-Default).

Спеціальні директиви `neverallow` у вихідному коді політики не обчислюються під час роботи ядра: вони перевіряються компілятором `checkpolicy` на етапі збірки образу політики. Якщо розробник випадково додасть правило, що дозволяє вебсерверу читати системні паролі (`allow httpd_t shadow_t : file read;`), компілятор негайно перерве збірку з помилкою порушення фундаментального інваріанта безпеки.

---

### 2. Архітектура та життєвий цикл запиту в AVC

У реальному ядрі Linux кожен системний виклик (наприклад, читання файлу, підключення до сокета або надсилання сигналу) генерує запит до монітора безпеки. Оскільки операції з пам'яттю та VFS виконуються мільйони разів на секунду, звернення до повільної бази правил безпеки створило б неприпустимі накладні витрати.

Для усунення цих затримок використовується кеш векторів доступу (AVC). Робота рушія розбивається на чотири послідовні фази:

```
[ Системний виклик у ядрі ]
            │
            ▼
    [ avc_has_perm() ]
            │
            ├─── 1. Фільтр MLS (Bell-LaPadula / Biba)
            │      • Читання: L(S) dom L(O)   (No Read Up)
            │      • Запис:   L(O) dom L(S)   (No Write Down)
            │      └─> Порушення? ──> [ Відмова EACCES ]
            │
            ├─── 2. Пошук у хеш-таблиці AVC
            │      • Обчислення хешу від (src_type, target_type, target_class)
            │      • Обхід ланцюжка колізій
            │      └─> Знайдено? ──> [ Cache Hit: Миттєве повернення результату ]
            │
            ├─── 3. Обробка промаху (Cache Miss) у Security Server
            │      • Сканування скомпільованої таблиці правил Type Enforcement
            │      • Обчислення результуючої бітової маски (allowed_vector)
            │      • Створення нового вузла в хеш-таблиці AVC
            │      └─> Збереження запису для наступних викликів
            │
            └─── 4. Зіставлення маски дозволів
                   • (allowed_vector & requested_perm) == requested_perm ?
                   ├── ТАК ──> [ 0: Дозволено ]
                   └── НІ  ──> [ Запис в audit.log + Повернення -EACCES ]
```

### 3. Алгоритм хешування, колізії та синхронізація RCU

Для рівномірного розподілу записів по кошиках кешу використовується мультиплікативна хеш-функція над 16-бітними числовими ідентифікаторами безпеки (`SID`). Хеш комбінує біти типу джерела, типу цілі та класу операції через операції порозрядного зсуву та множення на константу золотого перетину.

У промисловому ядрі Linux хеш-таблиця AVC захищається механізмом RCU (Read-Copy Update). Під час перевірки прав потік ядра захоплює легковагове блокування читання `rcu_read_lock()`, що дозволяє тисячам ядер процесора одночасно виконувати паралельний пошук у кеші без жодної міжядерної конкуренції за шину пам'яті.

У разі зміни політики (наприклад, завантаження нового модуля через `semodule -i` або перемикання булевого прапорця `setsebool`) рушій безпеки викликає функцію очищення кешу `avc_flush()`, яка безпечно звільняє всі кешовані вузли після завершення пільгового періоду RCU (grace period), змушуючи систему заново обчислити дозволи за оновленими правилами.

### 4. Оптимізація обчислення багаторівневої безпеки (MLS/MCS)

Оцінка домінування категорій у моделях Bell-LaPadula та MCS зводиться до перевірки включення підмножин: множина категорій суб'єкта `S_cats` повинна повністю покривати категорії цільового об'єкта `O_cats`. 

У представленій програмній моделі множина категорій зберігається у вигляді 64-бітної маски `uint64_t`. Завдяки цьому математична операція `(S_cats ⊇ O_cats)` транслюється у надшвидку побітову інструкцію процесора:

```
(s->mls_categories & o->mls_categories) == o->mls_categories
```

Якщо всі одиничні біти об'єкта присутні у бітовій масці суб'єкта, побітове «І» повертає вихідну маску об'єкта за один машинний такт без використання динамічної пам'яті чи циклічних обходів.

У промислових системах (де кількість категорій сягає 1024) ядро використовує оптимізовані бітові масиви `DECLARE_BITMAP(categories, 1024)` разом із векторними інструкціями AVX2 / SSE для миттєвого порівняння.

---

### 5. Програмна реалізація мовами C та C++

Нижче наведено повні реалізації рушія рішень та кешу AVC. Обидва варіанти містять повноцінний набір тестів у точці входу `main()`, що перевіряють роботу при першому зверненні (Cache Miss), швидке повторне зчитування з кешу (Cache Hit), відхилення неавторизованого доступу та виведення статистики.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define AVC_CACHE_SLOTS 256
#define MAX_RULES 128

/* Бітові маски дозволів */
#define PERM_READ    (1U << 0)
#define PERM_WRITE   (1U << 1)
#define PERM_EXECUTE (1U << 2)
#define PERM_APPEND  (1U << 3)

/* Ідентифікатори типів безпеки та класів */
typedef uint16_t security_id_t;
typedef uint32_t access_vector_t;

#define SECCLASS_FILE   1
#define SECCLASS_SOCKET 2
#define SECCLASS_DIR    3

/* Контекст безпеки: тип та рівень MLS (чутливість + бітова маска категорій) */
typedef struct {
    security_id_t type_id;
    uint8_t mls_sensitivity;
    uint64_t mls_categories;
} security_context_t;

/* Запис у таблиці правил Type Enforcement */
typedef struct {
    security_id_t src_type;
    security_id_t target_type;
    uint16_t target_class;
    access_vector_t allowed_permissions;
} te_rule_t;

/* Вузол кешу AVC */
typedef struct avc_node {
    security_id_t src_type;
    security_id_t target_type;
    uint16_t target_class;
    access_vector_t allowed;
    access_vector_t audit_allow;
    access_vector_t audit_deny;
    struct avc_node *next;
} avc_node_t;

/* Головна структура рушія безпеки */
typedef struct {
    te_rule_t rules[MAX_RULES];
    size_t rule_count;
    avc_node_t *cache[AVC_CACHE_SLOTS];
    uint64_t cache_hits;
    uint64_t cache_misses;
} security_engine_t;

/* Перевірка домінування MLS: (S_sens >= O_sens) && (S_cats ⊇ O_cats) */
static inline bool mls_dominate(const security_context_t *s, const security_context_t *o) {
    if (s->mls_sensitivity < o->mls_sensitivity) {
        return false;
    }
    return (s->mls_categories & o->mls_categories) == o->mls_categories;
}

/* Хеш-функція для трійки (src, target, class) */
static inline uint8_t avc_hash(security_id_t s, security_id_t t, uint16_t c) {
    uint32_t val = ((uint32_t)s << 16) ^ ((uint32_t)t << 8) ^ (uint32_t)c;
    val = ((val >> 16) ^ val) * 0x45d9f3b;
    val = ((val >> 16) ^ val) * 0x45d9f3b;
    val = (val >> 16) ^ val;
    return (uint8_t)(val % AVC_CACHE_SLOTS);
}

void security_engine_init(security_engine_t *eng) {
    eng->rule_count = 0;
    eng->cache_hits = 0;
    eng->cache_misses = 0;
    memset(eng->cache, 0, sizeof(eng->cache));
}

bool security_engine_add_rule(security_engine_t *eng, security_id_t src,
                              security_id_t target, uint16_t cl, access_vector_t perms) {
    if (eng->rule_count >= MAX_RULES) return false;
    eng->rules[eng->rule_count++] = (te_rule_t){src, target, cl, perms};
    return true;
}

/* Обчислення дозволів у Security Server (повільний шлях при Cache Miss) */
static access_vector_t security_compute_av(const security_engine_t *eng,
                                          security_id_t src, security_id_t target,
                                          uint16_t cl) {
    access_vector_t av = 0;
    for (size_t i = 0; i < eng->rule_count; ++i) {
        if (eng->rules[i].src_type == src &&
            eng->rules[i].target_type == target &&
            eng->rules[i].target_class == cl) {
            av |= eng->rules[i].allowed_permissions;
        }
    }
    return av;
}

/* Перевірка прав через AVC з автоматичним поповненням кешу */
bool avc_has_perm(security_engine_t *eng,
                  const security_context_t *subj,
                  const security_context_t *obj,
                  uint16_t target_class,
                  access_vector_t requested_perm) {
    /* 1. Перевірка MLS для операцій читання (No Read Up) */
    if ((requested_perm & (PERM_READ | PERM_EXECUTE)) && !mls_dominate(subj, obj)) {
        return false;
    }
    /* Перевірка MLS для операцій запису (No Write Down) */
    if ((requested_perm & (PERM_WRITE | PERM_APPEND)) && !mls_dominate(obj, subj)) {
        return false;
    }

    /* 2. Пошук у кеші AVC */
    uint8_t h = avc_hash(subj->type_id, obj->type_id, target_class);
    avc_node_t *curr = eng->cache[h];
    while (curr) {
        if (curr->src_type == subj->type_id &&
            curr->target_type == obj->type_id &&
            curr->target_class == target_class) {
            eng->cache_hits++;
            return (curr->allowed & requested_perm) == requested_perm;
        }
        curr = curr->next;
    }

    /* 3. Cache Miss: звернення до Security Server */
    eng->cache_misses++;
    access_vector_t allowed = security_compute_av(eng, subj->type_id, obj->type_id, target_class);

    /* 4. Додавання результату в кеш AVC */
    avc_node_t *new_node = (avc_node_t *)malloc(sizeof(avc_node_t));
    if (new_node) {
        new_node->src_type = subj->type_id;
        new_node->target_type = obj->type_id;
        new_node->target_class = target_class;
        new_node->allowed = allowed;
        new_node->audit_allow = 0;
        new_node->audit_deny = requested_perm;
        new_node->next = eng->cache[h];
        eng->cache[h] = new_node;
    }

    return (allowed & requested_perm) == requested_perm;
}

void security_engine_destroy(security_engine_t *eng) {
    for (size_t i = 0; i < AVC_CACHE_SLOTS; ++i) {
        avc_node_t *curr = eng->cache[i];
        while (curr) {
            avc_node_t *tmp = curr;
            curr = curr->next;
            free(tmp);
        }
        eng->cache[i] = NULL;
    }
}

int main(void) {
    security_engine_t engine;
    security_engine_init(&engine);

    /* Реєстрація типів системи */
    const security_id_t TYPE_HTTPD_T         = 10;
    const security_id_t TYPE_HTTPD_CONTENT_T = 20;
    const security_id_t TYPE_SHADOW_T        = 30;

    /* Правило політики: вебсервер httpd_t може читати контент httpd_sys_content_t */
    security_engine_add_rule(&engine, TYPE_HTTPD_T, TYPE_HTTPD_CONTENT_T,
                             SECCLASS_FILE, PERM_READ);

    /* Контексти безпеки процесів та файлів */
    security_context_t proc_ctx = { .type_id = TYPE_HTTPD_T, .mls_sensitivity = 0, .mls_categories = 0 };
    security_context_t html_ctx = { .type_id = TYPE_HTTPD_CONTENT_T, .mls_sensitivity = 0, .mls_categories = 0 };
    security_context_t shadow_ctx = { .type_id = TYPE_SHADOW_T, .mls_sensitivity = 0, .mls_categories = 0 };

    /* 1. Перша перевірка: промах кешу (Cache Miss) -> Дозволено */
    bool ok1 = avc_has_perm(&engine, &proc_ctx, &html_ctx, SECCLASS_FILE, PERM_READ);
    printf("1. httpd_t -> httpd_sys_content_t (читання): %s\n", ok1 ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО");

    /* 2. Повторна перевірка: потрапляння в кеш (Cache Hit) -> Дозволено */
    bool ok2 = avc_has_perm(&engine, &proc_ctx, &html_ctx, SECCLASS_FILE, PERM_READ);
    printf("2. httpd_t -> httpd_sys_content_t (повторне читання): %s\n", ok2 ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО");

    /* 3. Спроба доступу до системних паролів: Заборонено політикою */
    bool ok3 = avc_has_perm(&engine, &proc_ctx, &shadow_ctx, SECCLASS_FILE, PERM_READ);
    printf("3. httpd_t -> shadow_t (читання паролів): %s\n", ok3 ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО");

    printf("Статистика роботи AVC: Влучань (Hits) = %llu, Промахів (Misses) = %llu\n",
           (unsigned long long)engine.cache_hits, (unsigned long long)engine.cache_misses);

    security_engine_destroy(&engine);
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <vector>
#include <unordered_map>
#include <cstdint>
#include <string_view>
#include <format>

enum class Permission : uint32_t {
    None    = 0,
    Read    = 1U << 0,
    Write   = 1U << 1,
    Execute = 1U << 2,
    Append  = 1U << 3,
};

constexpr Permission operator|(Permission a, Permission b) noexcept {
    return static_cast<Permission>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

constexpr Permission operator&(Permission a, Permission b) noexcept {
    return static_cast<Permission>(static_cast<uint32_t>(a) & static_cast<uint32_t>(b));
}

enum class SecurityClass : uint16_t {
    File   = 1,
    Socket = 2,
    Dir    = 3,
};

struct SecurityContext {
    uint16_t type_id{0};
    uint8_t mls_sensitivity{0};
    uint64_t mls_categories{0};

    [[nodiscard]] constexpr bool dominates(const SecurityContext& other) const noexcept {
        if (mls_sensitivity < other.mls_sensitivity) return false;
        return (mls_categories & other.mls_categories) == other.mls_categories;
    }
};

struct CacheKey {
    uint16_t src_type;
    uint16_t target_type;
    SecurityClass target_class;

    bool operator==(const CacheKey& o) const noexcept {
        return src_type == o.src_type && target_type == o.target_type && target_class == o.target_class;
    }
};

struct CacheKeyHash {
    std::size_t operator()(const CacheKey& k) const noexcept {
        const std::size_t h1 = std::hash<uint16_t>{}(k.src_type);
        const std::size_t h2 = std::hash<uint16_t>{}(k.target_type);
        const std::size_t h3 = std::hash<uint16_t>{}(static_cast<uint16_t>(k.target_class));
        return h1 ^ (h2 << 8) ^ (h3 << 16);
    }
};

struct PolicyRule {
    uint16_t src_type;
    uint16_t target_type;
    SecurityClass target_class;
    Permission allowed_permissions;
};

class SecurityEngine {
public:
    void add_rule(uint16_t src, uint16_t target, SecurityClass cl, Permission perms) {
        rules_.push_back({src, target, cl, perms});
        avc_cache_.clear(); // скидання кешу при зміні політики
    }

    [[nodiscard]] bool check_permission(const SecurityContext& subj,
                                        const SecurityContext& obj,
                                        SecurityClass target_class,
                                        Permission requested) {
        // 1. MLS-фільтрація
        const bool is_read = static_cast<bool>(requested & (Permission::Read | Permission::Execute));
        const bool is_write = static_cast<bool>(requested & (Permission::Write | Permission::Append));

        if (is_read && !subj.dominates(obj)) return false;
        if (is_write && !obj.dominates(subj)) return false;

        // 2. Швидкий пошук у хеш-таблиці AVC
        const CacheKey key{subj.type_id, obj.type_id, target_class};
        if (auto it = avc_cache_.find(key); it != avc_cache_.end()) {
            ++cache_hits_;
            return (it->second & requested) == requested;
        }

        // 3. Cache Miss: обчислення повного вектора дозволів у Security Server
        ++cache_misses_;
        const Permission allowed = compute_access_vector(subj.type_id, obj.type_id, target_class);
        avc_cache_[key] = allowed;

        return (allowed & requested) == requested;
    }

    [[nodiscard]] std::size_t hits() const noexcept { return cache_hits_; }
    [[nodiscard]] std::size_t misses() const noexcept { return cache_misses_; }

private:
    [[nodiscard]] Permission compute_access_vector(uint16_t src, uint16_t target, SecurityClass cl) const noexcept {
        auto result = Permission::None;
        for (const auto& rule : rules_) {
            if (rule.src_type == src && rule.target_type == target && rule.target_class == cl) {
                result = result | rule.allowed_permissions;
            }
        }
        return result;
    }

    std::vector<PolicyRule> rules_;
    std::unordered_map<CacheKey, Permission, CacheKeyHash> avc_cache_;
    std::size_t cache_hits_{0};
    std::size_t cache_misses_{0};
};

int main() {
    SecurityEngine engine;

    constexpr uint16_t TYPE_HTTPD_T         = 10;
    constexpr uint16_t TYPE_HTTPD_CONTENT_T = 20;
    constexpr uint16_t TYPE_SHADOW_T        = 30;

    engine.add_rule(TYPE_HTTPD_T, TYPE_HTTPD_CONTENT_T, SecurityClass::File, Permission::Read);

    const SecurityContext proc_ctx{.type_id = TYPE_HTTPD_T, .mls_sensitivity = 0, .mls_categories = 0};
    const SecurityContext html_ctx{.type_id = TYPE_HTTPD_CONTENT_T, .mls_sensitivity = 0, .mls_categories = 0};
    const SecurityContext shadow_ctx{.type_id = TYPE_SHADOW_T, .mls_sensitivity = 0, .mls_categories = 0};

    // 1. Cache Miss -> Дозволено
    const bool ok1 = engine.check_permission(proc_ctx, html_ctx, SecurityClass::File, Permission::Read);
    std::cout << "1. httpd_t -> httpd_sys_content_t (читання): " << (ok1 ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО") << "\n";

    // 2. Cache Hit -> Дозволено
    const bool ok2 = engine.check_permission(proc_ctx, html_ctx, SecurityClass::File, Permission::Read);
    std::cout << "2. httpd_t -> httpd_sys_content_t (повторне читання): " << (ok2 ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО") << "\n";

    // 3. Cache Miss -> Заборонено
    const bool ok3 = engine.check_permission(proc_ctx, shadow_ctx, SecurityClass::File, Permission::Read);
    std::cout << "3. httpd_t -> shadow_t (читання паролів): " << (ok3 ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО") << "\n";

    std::cout << "Статистика AVC: Влучань = " << engine.hits() << ", Промахів = " << engine.misses() << "\n";

    return 0;
}
```
:::
