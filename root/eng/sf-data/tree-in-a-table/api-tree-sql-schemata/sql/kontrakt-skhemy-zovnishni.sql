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
