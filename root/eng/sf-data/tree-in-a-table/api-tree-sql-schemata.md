# 📋 Схеми DDL та контракт SQL-запитів для чотирьох моделей дерев

Реляційне збереження ієрархій вимагає точного узгодження між декларативною схемою таблиць (DDL), типами індексів для прискорення діапазонного пошуку чи з'єднань, обмеженнями цілісності та структурою SQL-запитів. Помилка у виборі операторного класу індексу (наприклад, звичайний B-Tree замість `text_pattern_ops` для префіксного пошуку) або відсутність каскадного зовнішнього ключа призводить до деградації продуктивності або появи неконсистентних «висячих» вузлів.

Нижче наведено повну довідкову специфікацію контрактів, DDL-схем, індексів, тригерних процедур та канонічних запитів для чотирьох основних моделей деревних структур: списку суміжності (Adjacency List), матеріалізованого шляху (Materialized Path), вкладених множин (Nested Sets) та таблиці замикання (Closure Table).

---

## 1. Список суміжності (Adjacency List)

### Контракт схеми, зовнішні ключі та оптимізація індексів

Модель списку суміжності зберігає сутності та їхні прямі батьківські зв'язки в одній реляційній таблиці. Поле `parent_id` обов'язково оголошується зовнішнім ключем, що посилається на первинний ключ цієї ж таблиці. Для кореневих вузлів дерева (вершин нульового рівня) поле `parent_id` містить значення `NULL`.

Вибір правила видалення зовнішнього ключа визначає поведінку всієї гілки:
- `ON DELETE CASCADE`: видалення батьківського вузла автоматично рекурсивно видаляє всі вкладені піддерева на рівні СУБД.
- `ON DELETE RESTRICT`: забороняє видалення вузла, якщо він має хоча б один дочірній елемент, запобігаючи випадковому осиротінню записів.

Для забезпечення високої швидкості рекурсивних запитів та вибірки прямих дітей створюється стандартний B-Tree індекс на стовпчик `parent_id`. Без цього індексу кожна ітерація рекурсивного CTE виконуватиме повне послідовне сканування таблиці (`Sequential Scan`). Крім того, для миттєвого пошуку всіх кореневих вузлів системи створюється частковий індекс (Partial Index) `WHERE parent_id IS NULL`.

```sql
CREATE TABLE tree_adjacency (
    id SERIAL PRIMARY KEY,
    parent_id INT NULL REFERENCES tree_adjacency(id) ON DELETE CASCADE,
    name VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- B-Tree індекс для прискорення з'єднання в рекурсивному CTE та пошуку дітей
CREATE INDEX idx_tree_adj_parent ON tree_adjacency(parent_id);

-- Частковий індекс для миттєвого пошуку коренів дерева
CREATE INDEX idx_tree_adj_roots ON tree_adjacency(id) WHERE parent_id IS NULL;
```

### Канонічні SQL-запити та керування рекурсією

Контракт вибірки піддерева базується на стандарті SQL:1999 `WITH RECURSIVE`. Запит ітерує від якірного вузла до листків, накопичуючи глибину та історію шляху для запобігання зацикленню.

Для запобігання нескінченним циклам при пошкодженні даних у запит обов'язково включається масив відвіданих ідентифікаторів `ARRAY[id]`, а у рекурсивному члені перевіряється умова `WHERE NOT (c.id = ANY(s.path_track))`.

```sql
-- 1. Вибірка всього піддерева на довільну глибину
WITH RECURSIVE subtree AS (
    -- Якірний член: вибираємо цільовий корінь піддерева
    SELECT id, parent_id, name, 0 AS depth, ARRAY[id] AS path_track
    FROM tree_adjacency
    WHERE id = :target_id

    UNION ALL

    -- Рекурсивний член: приєднуємо дітей, перевіряючи відсутність циклів
    SELECT c.id, c.parent_id, c.name, s.depth + 1, s.path_track || c.id
    FROM tree_adjacency c
    JOIN subtree s ON c.parent_id = s.id
    WHERE NOT (c.id = ANY(s.path_track))
)
SELECT id, parent_id, name, depth
FROM subtree
ORDER BY depth, id;

-- 2. Вибірка всіх предків до кореня (навігаційні хлібні крихти)
WITH RECURSIVE breadcrumbs AS (
    -- Якірний член: стартуємо з поточного вузла
    SELECT id, parent_id, name, 0 AS level
    FROM tree_adjacency
    WHERE id = :target_id

    UNION ALL

    -- Рекурсивний член: піднімаємося вгору до parent_id IS NULL
    SELECT p.id, p.parent_id, p.name, b.level + 1
    FROM tree_adjacency p
    JOIN breadcrumbs b ON b.parent_id = p.id
)
SELECT id, parent_id, name, level
FROM breadcrumbs
ORDER BY level DESC;

-- 3. Вставка нового вузла (сталий час O(1))
INSERT INTO tree_adjacency (parent_id, name)
VALUES (:parent_id, :node_name)
RETURNING id;

-- 4. Переміщення піддерева під нового батька (O(1))
UPDATE tree_adjacency
SET parent_id = :new_parent_id
WHERE id = :moving_id;

-- 5. Видалення піддерева (автоматичний каскад)
DELETE FROM tree_adjacency WHERE id = :target_id;
```

---

## 2. Матеріалізований шлях (Materialized Path)

### Контракт схеми: Generic VARCHAR та PostgreSQL `ltree`

Модель матеріалізованого шляху кодує повну генеалогію вузла в одному атрибуті у вигляді текстового рядка або бінарного шляху. Існують дві основні реалізації:

1. **Generic VARCHAR:** переносимий текстовий рядок із роздільниками (наприклад, `'/1/4/12/'`). Специфікація вимагає обов'язкової наявності роздільників на початку та наприкінці рядка. Це унеможливлює помилкові збіги підрядків (наприклад, щоб пошук за шляхом `'/1/2/'` випадково не вибрав вузол `'/1/20/'`). Обов'язково створюється B-Tree індекс зі спеціальним операторним класом `varchar_pattern_ops` (у PostgreSQL), який вимикає локалезалежні правила сортування для швидкого префіксного пошуку за оператором `LIKE 'prefix%'`.
2. **PostgreSQL розширення `ltree`:** бінарно оптимізований тип даних для ієрархічних міток із крапками (`'Top.Science.Physics'`). Використовує GiST-індекси (Generalized Search Tree) на основі сигнатурних бітових масок для прискорення топологічних предикатів.

```sql
-- Варіант А: Переносимий текстовий шлях (VARCHAR)
CREATE TABLE tree_path_varchar (
    id SERIAL PRIMARY KEY,
    path VARCHAR(1024) NOT NULL, -- Формат: '/1/4/12/' (з обов'язковими слешами на кінцях)
    name VARCHAR(128) NOT NULL
);

-- Спеціалізований індекс для оптимізації префіксного сканування
CREATE INDEX idx_tree_path_prefix ON tree_path_varchar (path varchar_pattern_ops);

-- Варіант Б: PostgreSQL розширення ltree
CREATE EXTENSION IF NOT EXISTS ltree;

CREATE TABLE tree_path_ltree (
    id SERIAL PRIMARY KEY,
    path LTREE NOT NULL, -- Формат: 'Top.Electronics.Phones'
    name VARCHAR(128) NOT NULL
);

-- GiST індекс для операцій предка/нащадка та квантифікаторів рівнів
CREATE INDEX idx_tree_ltree_gist ON tree_path_ltree USING GIST (path);
```

### Канонічні SQL-запити для VARCHAR

Для вибірки піддерева використовується префіксний оператор `LIKE :parent_path || '%'`. Для вибірки предків рядок шляху розбивається на масив цілих чисел за допомогою функції `string_to_array()`.

Переміщення піддерева вимагає масового оновлення рядків шляху для всіх нащадків. Операція виконується за допомогою функції `SUBSTRING()`, яка замінює старий префікс шляху на новий.

```sql
-- 1. Вибірка всього піддерева (префіксне діапазонне сканування)
SELECT * FROM tree_path_varchar
WHERE path LIKE :parent_path || '%'
ORDER BY path;

-- 2. Вибірка предків (хлібні крихти для вузла зі шляхом '/1/2/5/')
SELECT * FROM tree_path_varchar
WHERE id = ANY(string_to_array(trim(both '/' from :node_path), '/')::int[])
ORDER BY LENGTH(path);

-- 3. Вставка нового вузла
-- Спершу генерується ID або використовується функція/тригер для конкатенації
INSERT INTO tree_path_varchar (path, name)
VALUES (:parent_path || :new_id || '/', :node_name);

-- 4. Переміщення піддерева (каскадна заміна префікса для всіх k нащадків)
UPDATE tree_path_varchar
SET path = :new_prefix || SUBSTRING(path FROM LENGTH(:old_prefix) + 1)
WHERE path LIKE :old_prefix || '%';

-- 5. Видалення гілки
DELETE FROM tree_path_varchar
WHERE path LIKE :target_path || '%';
```

### Канонічні операції для PostgreSQL `ltree`

Модуль `ltree` надає багатий набір спеціалізованих операторів:
- `<@` — перевірка на те, чи є лівий шлях нащадком правого;
- `@>` — перевірка на те, чи є лівий шлях предком правого;
- `~` — зіставлення за шаблонами рівнів (LQuery), де зірочка позначає рівні дерева;
- `nlevel(path)` — миттєве повернення поточної глибини вузла.

```sql
-- 1. Вибірка піддерева за допомогою оператора <@ (нащадок)
SELECT * FROM tree_path_ltree
WHERE path <@ 'Top.Electronics'
ORDER BY path;

-- 2. Вибірка всіх предків за допомогою оператора @> (предок)
SELECT * FROM tree_path_ltree
WHERE path @> 'Top.Electronics.Phones'
ORDER BY nlevel(path);

-- 3. Пошук вузлів на точній глибині 3 від кореня
SELECT * FROM tree_path_ltree
WHERE path ~ 'Top.*{2}';
```

---

## 3. Вкладені множини (Nested Sets)

### Контракт схеми, обмеження та блокування

У моделі Джо Селко кожен вузол містить числовий інтервал `[lft, rgt]`. Схема повинна містити перевірочне обмеження цілісності `CHECK (lft < rgt)`, а також унікальні індекси на лівий і правий ключі для гарантування неповторюваності числових меж.

Складений індекс `(lft, rgt)` забезпечує виконання запитів на вибірку піддерева за мінімальну кількість операцій дискового вводу-виводу (Index Only Scan).

```sql
CREATE TABLE tree_nested_sets (
    id SERIAL PRIMARY KEY,
    lft INT NOT NULL,
    rgt INT NOT NULL,
    name VARCHAR(128) NOT NULL,
    CONSTRAINT chk_nested_order CHECK (lft < rgt),
    CONSTRAINT uq_nested_lft UNIQUE (lft),
    CONSTRAINT uq_nested_rgt UNIQUE (rgt)
);

CREATE INDEX idx_nested_range ON tree_nested_sets (lft, rgt);
```

### Канонічні SQL-запити та транзакційні процедури

Вибірка піддерева здійснюється за один реляційний крок за допомогою діапазонного предикату `BETWEEN`.

Операції вставки та видалення обов'язково виконуються всередині ізольованої транзакції (`BEGIN ... COMMIT`), оскільки вони вимагають попереднього зсуву числових ключів у всіх рядках таблиці, розташованих праворуч від точки модифікації.

```sql
-- 1. Вибірка всього піддерева без рекурсії (найшвидший B-Tree range scan)
SELECT node.*
FROM tree_nested_sets AS parent
JOIN tree_nested_sets AS node
  ON node.lft BETWEEN parent.lft AND parent.rgt
WHERE parent.id = :target_id
ORDER BY node.lft;

-- 2. Вибірка всіх предків до кореня
SELECT parent.*
FROM tree_nested_sets AS node
JOIN tree_nested_sets AS parent
  ON node.lft BETWEEN parent.lft AND parent.rgt
WHERE node.id = :target_id
ORDER BY parent.lft;

-- 3. Обчислення кількості нащадків та перевірка на листок
SELECT id, name,
       (rgt - lft - 1) / 2 AS total_descendants,
       CASE WHEN rgt - lft = 1 THEN TRUE ELSE FALSE END AS is_leaf
FROM tree_nested_sets
WHERE id = :target_id;

-- 4. Вставка нового вузла праворуч від батьківського інтервалу (Транзакція)
BEGIN;
-- Блокуємо та зсуваємо числовий простір праворуч від точки вставки
UPDATE tree_nested_sets SET rgt = rgt + 2 WHERE rgt >= :parent_rgt;
UPDATE tree_nested_sets SET lft = lft + 2 WHERE lft > :parent_rgt;

-- Вставляємо новий вузол у звільнений інтервал
INSERT INTO tree_nested_sets (lft, rgt, name)
VALUES (:parent_rgt, :parent_rgt + 1, :node_name);
COMMIT;

-- 5. Видалення піддерева зі згортанням числового простору
BEGIN;
SELECT lft, rgt, (rgt - lft + 1) AS width INTO :del_lft, :del_rgt, :del_width
FROM tree_nested_sets WHERE id = :target_id;

DELETE FROM tree_nested_sets WHERE lft BETWEEN :del_lft AND :del_rgt;

UPDATE tree_nested_sets SET rgt = rgt - :del_width WHERE rgt > :del_rgt;
UPDATE tree_nested_sets SET lft = lft - :del_width WHERE lft > :del_rgt;
COMMIT;
```

---

## 4. Таблиця замикання (Closure Table)

### Контракт схеми, матриця зв'язків та посиланняльна цілісність

Таблиця замикання відокремлює атрибути вузла від зв'язків графа. Створюються дві нормалізовані таблиці:
1. `tree_nodes` — містить виключно бізнес-атрибути сутності (назву, опис, час створення);
2. `tree_closure` — містить матрицю транзитивного замикання графа.

Таблиця зв'язків містить складений первинний ключ `PRIMARY KEY (ancestor_id, descendant_id)` та числовий атрибут `depth`, який показує точну кількість ребер між предком і нащадком. Обидва стовпчики зв'язку захищені каскадними зовнішніми ключами `ON DELETE CASCADE`.

Для прискорення зворотного пошуку (отримання предків або хлібних крихт за відомим `descendant_id`) обов'язково створюється вторинний індекс `(descendant_id, depth)`.

```sql
CREATE TABLE tree_nodes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tree_closure (
    ancestor_id INT NOT NULL REFERENCES tree_nodes(id) ON DELETE CASCADE,
    descendant_id INT NOT NULL REFERENCES tree_nodes(id) ON DELETE CASCADE,
    depth INT NOT NULL,
    PRIMARY KEY (ancestor_id, descendant_id)
);

-- Індекс для миттєвого пошуку предків вузла за descendant_id
CREATE INDEX idx_closure_descendant ON tree_closure (descendant_id, depth);
```

### Канонічні SQL-запити

Вибірка піддерева або предків виконується за допомогою стандартного з'єднання `JOIN` за первинним або вторинним індексом.

Переміщення піддерева розбивається на дві операції: видалення старих зв'язків між предками попереднього батька та нащадками гілки, а потім створення нових зв'язків через Декартів добуток (`CROSS JOIN`) між множиною предків нового батька та множиною нащадків переміщуваного вузла.

```sql
-- 1. Вибірка всього піддерева (простий індексований JOIN)
SELECT n.id, n.name, c.depth
FROM tree_nodes n
JOIN tree_closure c ON n.id = c.descendant_id
WHERE c.ancestor_id = :target_id
ORDER BY c.depth, n.id;

-- 2. Вибірка тільки безпосередніх дітей
SELECT n.id, n.name
FROM tree_nodes n
JOIN tree_closure c ON n.id = c.descendant_id
WHERE c.ancestor_id = :target_id AND c.depth = 1
ORDER BY n.name;

-- 3. Вибірка всіх предків (хлібні крихти)
SELECT n.id, n.name, c.depth
FROM tree_nodes n
JOIN tree_closure c ON n.id = c.ancestor_id
WHERE c.descendant_id = :target_id
ORDER BY c.depth DESC;

-- 4. Вставка нового вузла під батька :parent_id
BEGIN;
INSERT INTO tree_nodes (name) VALUES (:node_name) RETURNING id INTO :new_id;

-- Копіюємо всі зв'язки батьківського вузла з depth + 1 та додаємо рефлексивний запис (depth = 0)
INSERT INTO tree_closure (ancestor_id, descendant_id, depth)
SELECT ancestor_id, :new_id, depth + 1
FROM tree_closure
WHERE descendant_id = :parent_id
UNION ALL
SELECT :new_id, :new_id, 0;
COMMIT;

-- 5. Переміщення піддерева :moving_id під нового батька :new_parent_id
BEGIN;
-- Розриваємо зв'язки між предками старого батька та всіма нащадками переміщуваної гілки
DELETE FROM tree_closure
WHERE descendant_id IN (
    SELECT descendant_id FROM tree_closure WHERE ancestor_id = :moving_id
)
AND ancestor_id IN (
    SELECT ancestor_id FROM tree_closure
    WHERE descendant_id = :moving_id AND ancestor_id != :moving_id
);

-- Встановлюємо нові транзитивні зв'язки через Декартів добуток (CROSS JOIN)
INSERT INTO tree_closure (ancestor_id, descendant_id, depth)
SELECT supertree.ancestor_id, subtree.descendant_id, supertree.depth + subtree.depth + 1
FROM tree_closure AS supertree
CROSS JOIN tree_closure AS subtree
WHERE supertree.descendant_id = :new_parent_id
  AND subtree.ancestor_id = :moving_id;
COMMIT;

-- 6. Видалення піддерева
DELETE FROM tree_nodes
WHERE id IN (
    SELECT descendant_id FROM tree_closure WHERE ancestor_id = :target_id
);
```

Специфікація цих контрактів гарантує передбачуваність часу виконання запитів (query plan latency), збереження реляційної цілісності та відсутність блокувальних колізій при паралельному доступі.
