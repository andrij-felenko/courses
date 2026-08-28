BEGIN;
-- Крок 1: Видалення старих предків для переміщуваного піддерева
DELETE FROM category_closure
WHERE descendant_id IN (
    SELECT descendant_id FROM category_closure WHERE ancestor_id = :moving_id
)
AND ancestor_id IN (
    SELECT ancestor_id FROM category_closure
    WHERE descendant_id = :moving_id AND ancestor_id != :moving_id
);

-- Крок 2: Встановлення нових зв'язків
INSERT INTO category_closure (ancestor_id, descendant_id, depth)
SELECT supertree.ancestor_id, subtree.descendant_id, supertree.depth + subtree.depth + 1
FROM category_closure AS supertree
CROSS JOIN category_closure AS subtree
WHERE supertree.descendant_id = :new_parent_id
  AND subtree.ancestor_id = :moving_id;
COMMIT;
