CREATE TABLE categories_nested (
    id SERIAL PRIMARY KEY,
    lft INT NOT NULL,
    rgt INT NOT NULL,
    name VARCHAR(128) NOT NULL,
    CONSTRAINT chk_nested_valid CHECK (lft < rgt)
);

CREATE INDEX idx_nested_lft ON categories_nested (lft);
CREATE INDEX idx_nested_rgt ON categories_nested (rgt);
CREATE INDEX idx_nested_range ON categories_nested (lft, rgt);
