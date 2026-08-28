void setup() {
    Serial.begin(115200);

    if (!camera_start())  return;   // камера не піднялася — далі немає сенсу
    if (!sdcard_start())  return;   // картка не змонтувалася — так само

    // Ім'я файлу зі зростаючим лічильником, щоб не затирати попередні.
    static int n = 0;
    char path[32];
    snprintf(path, sizeof(path), "/photo_%04d.jpg", n++);

    save_photo(path);
}

void loop() {
    // порожньо: один знімок зробили в setup(); тут можна спати або чекати кнопки
}
