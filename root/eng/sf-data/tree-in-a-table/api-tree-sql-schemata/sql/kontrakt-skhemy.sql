CREATE TABLE tree_nested_sets (
    id SERIAL PRIMARY KEY,
    lft INT NOT NULL,
    rgt INT NOT NULL,
    name VARCHAR(128) NOT NULL,
    CONSTRAINT chk_nested_order CHECK (lft < rgt),
    CONSTRAINT uq_nested_lft UNIQUE (lft),
    CONSTRAINT uq_nested_rgt UNIQUE (rgt)
);

CREATE INDEX idx_nested_range ON tree_nested_sets (lft, rgt);
