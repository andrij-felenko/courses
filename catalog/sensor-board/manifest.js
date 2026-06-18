/* catalog/sensor-board/manifest.js — книга-каталог «Сенсори-плати» (тип "catalog").
   Схема — AUTHORING.md §2. Статуси: done | empty | update | deeper | recheck. */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "catalog", slug: "sensor-board", title: "Сенсори-плати",
  sections: [
    { slug: "sensing", title: "Сенсорика", scope: "Модулі вимірювання фізичних величин: маса, рух, світло, відстань, струм.",
      topics: [
        { slug: "loadcell-hx711", title: "Тензодавач HX711", status: "empty" },
        { slug: "imu-board", title: "IMU-модуль", status: "empty" },
        { slug: "light-sensors", title: "Давачі світла", status: "empty" },
        { slug: "laser-tof", title: "Лазерний ToF-далекомір", status: "empty" },
        { slug: "shunt-current-monitor", title: "Монітор струму (шунт)", status: "empty" },
      ] },
    { slug: "positioning-comms", title: "Позиціювання і зв'язок", scope: "Модулі навігації та радіозв'язку.",
      topics: [
        { slug: "gnss-module", title: "GNSS-модуль", status: "empty" },
        { slug: "lora-module", title: "LoRa-модуль", status: "empty" },
        { slug: "nrf24-radio", title: "Радіомодуль nRF24", status: "empty" },
      ] },
    { slug: "storage", title: "Зберігання", scope: "Модулі зовнішньої пам'яті.",
      topics: [
        { slug: "microsd-card", title: "microSD-модуль", status: "empty" },
      ] },
  ]
});
