-- Створення таблиці просторових полігонів
CREATE TABLE municipal_parcels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    geom GEOMETRY(Polygon, 4326)
);

-- Побудова R-дерево індексу GiST
CREATE INDEX idx_parcels_spatial ON municipal_parcels USING GIST (geom);

-- Віконний запит із використанням індексу (оператор && перевіряє перетин MBR)
SELECT id, name 
FROM municipal_parcels 
WHERE geom && ST_MakeEnvelope(30.45, 50.40, 30.55, 50.50, 4326);
