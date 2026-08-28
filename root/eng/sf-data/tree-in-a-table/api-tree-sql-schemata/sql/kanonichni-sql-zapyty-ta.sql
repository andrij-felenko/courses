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
