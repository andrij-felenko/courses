/* manifest — «Плати» (тип "catalog"). Схема — AUTHORING.md §2 (v6). Заведено з hardware-інвентарю. */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "catalog", slug: "boards", title: "Плати",
  sections: [
    { slug: "compute", title: "Одноплатні компʼютери", scope: "Одноплатні компʼютери (SBC) та x86-міні-ПК для обчислень і хостингу.",
      topics: [
        { slug: "raspberry-pi-family", title: "Родина Raspberry Pi", basic: { status: "done" }, detailed: { status: "empty" }, hist: [{ file: "hist-birth-of-pi.md", status: "done" }] },
        { slug: "rpi5", title: "Raspberry Pi 5", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-gpio-api.md", status: "done" }] },
        { slug: "rpi4", title: "Raspberry Pi 4 Model B", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-gpio.md", status: "done" }] },
        { slug: "minipc-chuwi", title: "Міні-ПК Chuwi (x86)", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-headless-server.md", status: "done" }] },
      ] },
    { slug: "mcu", title: "Мікроконтролерні плати", scope: "Плати з мікроконтролером для прошивок: AVR, ESP32/ESP8266.",
      topics: [
        { slug: "esp32-family", title: "Родина ESP32/ESP8266 (Espressif)", basic: { status: "done" }, detailed: { status: "pending" }, hist: [{ file: "hist-generations.md", status: "done" }] },
        { slug: "arduino-family", title: "Родина Arduino", basic: { status: "done" }, detailed: { status: "empty" }, hist: [{ file: "hist-name-arduin.md", status: "done" }, { file: "hist-avr-atmel.md", status: "done" }, { file: "hist-open-hardware.md", status: "done" }], proj: [{ file: "proj-arduino-framework.md", status: "done" }] },
        { slug: "arduino-uno", title: "Arduino UNO R3 (CH340)", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-blink-io.md", status: "done" }] },
        { slug: "arduino-nano", title: "Arduino Nano (ATmega, USB-C)", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-arduino-nano.md", status: "done" }] },
        { slug: "esp32-c6-zero", title: "Waveshare ESP32-C6-Zero", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-quickstart.md", status: "done" }] },
        { slug: "esp32-s3-pico", title: "Waveshare ESP32-S3-Pico", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-quickstart.md", status: "done" }] },
        { slug: "esp32-s3-supermini", title: "ESP32-S3 SuperMini", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-esp32-s3-supermini-api.md", status: "done" }] },
        { slug: "esp32-cam", title: "ESP32-CAM (OV2640 + microSD)", basic: { status: "done" }, detailed: { status: "pending" }, hist: [{ file: "hist-ov2640-cheap-cam.md", status: "done" }], proj: [{ file: "proj-cam-sdcard.md", status: "done" }] },
        { slug: "esp-01s", title: "ESP-01S (Wi-Fi, ESP8266)", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-blink-wifi.md", status: "done" }] },
        { slug: "esp-01", title: "ESP-01 (Wi-Fi, ESP8266)", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-flash-blink.md", status: "done" }] },
      ] },
    { slug: "flight", title: "Польотні контролери", scope: "Автопілоти й супутні адаптери для дронів/роверів.",
      topics: [
        { slug: "pixhawk-6c", title: "Pixhawk 6C — польотний контролер", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-mavlink-control.md", status: "done" }] },
        { slug: "pixhawk-pwm-adapter", title: "PWM-адаптер для Pixhawk", basic: { status: "done" }, detailed: { status: "empty" }, proj: [{ file: "proj-pwm-config.md", status: "done" }] },
      ] },
    { slug: "expansion", title: "Модулі-розширення", scope: "Плати-розширення до обчислювальних плат: памʼять, накопичувачі, дисплеї, шилди.",
      topics: [
        { slug: "microsd-card", title: "microSD-модуль", basic: { status: "done" }, detailed: { status: "pending" } },
        { slug: "lcd-1602", title: "Символьний дисплей LCD 1602A", basic: { status: "done" }, detailed: { status: "pending" }, hist: [{ file: "hist-hd44780.md", status: "done" }], proj: [{ file: "proj-liquidcrystal.md", status: "done" }] },
        { slug: "i2c-lcd-adapter", title: "I2C-адаптер для LCD 1602 (PCF8574)", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-lcd-i2c-api.md", status: "done" }] },
        { slug: "seg-5641as", title: "Семисегментний індикатор 5641AS (4 розряди)", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-scan-driver.md", status: "done" }] },
        { slug: "seg-5161as", title: "Семисегментний індикатор 5161AS (1 розряд)", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-drive.md", status: "done" }] },
        { slug: "led-matrix-8x8", title: "Світлодіодна матриця 8×8 (1588BS)", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-driver.md", status: "done" }] },
        { slug: "multifunction-shield", title: "Multi-function Shield для Arduino UNO", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-multifunction-shield-api.md", status: "done" }] },
        { slug: "gpio-extension-board", title: "GPIO Extension Board для Raspberry Pi", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-libgpiod-breadboard.md", status: "done" }] },
      ] },
  ]
});
