CREATE TABLE tree_nodes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tree_closure (
    ancestor_id INT NOT NULL REFERENCES tree_nodes(id) ON DELETE CASCADE,
    descendant_id INT NOT NULL REFERENCES tree_nodes(id) ON DELETE CASCADE,
    depth INT NOT NULL,
    PRIMARY KEY (ancestor_id, descendant_id)
);

-- Індекс для миттєвого пошуку предків вузла за descendant_id
CREATE INDEX idx_closure_descendant ON tree_closure (descendant_id, depth);
