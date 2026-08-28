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
