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
