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
