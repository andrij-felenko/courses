WITH RECURSIVE category_tree AS (
    -- Якірний член: починаємо з обраного кореня (наприклад, id = 1)
    SELECT id, parent_id, name, 0 AS depth, ARRAY[id] AS path
    FROM categories
    WHERE id = 1

    UNION ALL

    -- Рекурсивний член: приєднуємо дітей до знайдених батьків
    SELECT c.id, c.parent_id, c.name, ct.depth + 1, ct.path || c.id
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT id, parent_id, name, depth, path
FROM category_tree
ORDER BY depth, id;
