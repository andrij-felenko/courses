-- Таблиця сутностей (не містить жодних зовнішніх ключів дерева)
CREATE TABLE categories_node (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL
);

-- Таблиця замикання: зберігає всі пари (предок, нащадок) та відстань між ними
CREATE TABLE category_closure (
    ancestor_id INT NOT NULL REFERENCES categories_node(id) ON DELETE CASCADE,
    descendant_id INT NOT NULL REFERENCES categories_node(id) ON DELETE CASCADE,
    depth INT NOT NULL,
    PRIMARY KEY (ancestor_id, descendant_id)
);

CREATE INDEX idx_closure_descendant ON category_closure (descendant_id, depth);
