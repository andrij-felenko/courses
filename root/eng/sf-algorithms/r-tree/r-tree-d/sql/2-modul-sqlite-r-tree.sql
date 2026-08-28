-- Створення віртуальної просторової таблиці для 2D-рамок
CREATE VIRTUAL TABLE spatial_index USING rtree(
   id,              -- Унікальний числовий ідентифікатор
   minX, maxX,      -- Межі за віссю X
   minY, maxY       -- Межі за віссю Y
);

-- Вставка MBR
INSERT INTO spatial_index VALUES (1, 10.0, 20.0, 15.0, 25.0);

-- Віконний пошук
SELECT id FROM spatial_index 
WHERE minX <= 30.0 AND maxX >= 5.0 
  AND minY <= 30.0 AND maxY >= 5.0;
