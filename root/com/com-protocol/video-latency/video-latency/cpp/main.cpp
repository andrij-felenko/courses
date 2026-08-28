// бюджет затримки відео, мс — кожна ланка додається до суми
const float t_sensor =  18.0f;  // експозиція + зчитування рядків сенсора
const float t_encode =  22.0f;  // кодек: стиснути кадр перед передачею
const float t_link   =   8.0f;  // канал: радіо/кабель донести біти
const float t_buffer =  25.0f;  // приймальний буфер проти ривків
const float t_decode =  12.0f;  // декодер: розтиснути кадр
const float t_screen =  12.0f;  // екран: оновлення + відгук пікселя

float glass_to_glass =
    t_sensor + t_encode + t_link + t_buffer + t_decode + t_screen;
// = 18 + 22 + 8 + 25 + 12 + 12 = 97 мс
