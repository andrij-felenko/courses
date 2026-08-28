-- 1. Довідник категорій товарів
CREATE TABLE product_categories (
    category_id   INT GENERATED ALWAYS AS IDENTITY,
    category_code VARCHAR(32) NOT NULL,
    title         VARCHAR(128) NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_product_categories PRIMARY KEY (category_id),
    CONSTRAINT uq_categories_code UNIQUE (category_code)
);

-- 2. Каталог товарів
CREATE TABLE products (
    product_id    INT GENERATED ALWAYS AS IDENTITY,
    category_id   INT NOT NULL,
    sku           VARCHAR(64) NOT NULL,
    name          VARCHAR(255) NOT NULL,
    unit_price    NUMERIC(12, 2) NOT NULL,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT pk_products PRIMARY KEY (product_id),
    CONSTRAINT uq_products_sku UNIQUE (sku),
    CONSTRAINT fk_products_category FOREIGN KEY (category_id)
        REFERENCES product_categories (category_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT chk_products_price CHECK (unit_price >= 0.00)
);

-- Індекс на зовнішній ключ для швидких операцій видалення та з'єднання
CREATE INDEX idx_products_category_id ON products (category_id);

-- 3. Клієнти
CREATE TABLE customers (
    customer_id   INT GENERATED ALWAYS AS IDENTITY,
    email         VARCHAR(255) NOT NULL,
    first_name    VARCHAR(64) NOT NULL,
    last_name     VARCHAR(64) NOT NULL,
    city          VARCHAR(128) NOT NULL,
    phone         VARCHAR(32),

    CONSTRAINT pk_customers PRIMARY KEY (customer_id),
    CONSTRAINT uq_customers_email UNIQUE (email),
    CONSTRAINT chk_customers_email_format CHECK (email LIKE '%_@__%.__%')
);

-- 4. Замовлення (Заголовок замовлення)
CREATE TABLE orders (
    order_id      BIGINT GENERATED ALWAYS AS IDENTITY,
    customer_id   INT NOT NULL,
    order_status  VARCHAR(24) NOT NULL DEFAULT 'PENDING',
    ordered_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_orders PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id)
        REFERENCES customers (customer_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT chk_orders_status CHECK (
        order_status IN ('PENDING', 'PAID', 'SHIPPED', 'CANCELLED')
    )
);

CREATE INDEX idx_orders_customer_id ON orders (customer_id);

-- 5. Позиції замовлення (Деталі замовлення)
CREATE TABLE order_items (
    order_id      BIGINT NOT NULL,
    product_id    INT NOT NULL,
    quantity      INT NOT NULL DEFAULT 1,
    actual_price  NUMERIC(12, 2) NOT NULL,

    CONSTRAINT pk_order_items PRIMARY KEY (order_id, product_id),
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id)
        REFERENCES orders (order_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id)
        REFERENCES products (product_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT chk_order_items_qty CHECK (quantity > 0),
    CONSTRAINT chk_order_items_price CHECK (actual_price >= 0.00)
);

CREATE INDEX idx_order_items_product_id ON order_items (product_id);
