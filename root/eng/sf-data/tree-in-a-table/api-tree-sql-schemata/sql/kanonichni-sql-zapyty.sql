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
