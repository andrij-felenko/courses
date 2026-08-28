-- Та сама таблиця вимірів. Різниця — одне слово: який рушій під нею.
CREATE TABLE measurement (
    sensor_id  BIGINT,
    ts         DATETIME,
    value      DOUBLE,
    PRIMARY KEY (sensor_id, ts)
) ENGINE = InnoDB;     -- B-дерево: правити на місці

CREATE TABLE measurement (
    sensor_id  BIGINT,
    ts         DATETIME,
    value      DOUBLE,
    PRIMARY KEY (sensor_id, ts)
) ENGINE = ROCKSDB;    -- LSM (MyRocks): дописувати й зливати
