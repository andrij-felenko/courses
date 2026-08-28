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
