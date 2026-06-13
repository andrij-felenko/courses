/* components/interfaces/manifest.js — per-module маніфест (генерується split-modules.js).
   Книга-довідник: розділ = самостійна тема. Складає scripts/bookbuild.js. */
(window.__MODREG__ = window.__MODREG__ || []).push(
{
  "n": 6,
  "title": "Інтерфейси",
  "slug": "interfaces",
  "chapters": [
    {
      "n": "1",
      "status": "pending",
      "title": "Розширювач портів I²C (PCF8574-клас)"
    },
    {
      "n": "2",
      "status": "pending",
      "title": "Зсувний регістр (74HC595)"
    },
    {
      "n": "3",
      "status": "pending",
      "title": "Перетворювач рівнів логіки"
    },
    {
      "n": "4",
      "status": "done",
      "slug": "usb-c-connector",
      "dir": "interfaces/usb-c-connector/",
      "main": "usb-c-connector.md",
      "title": "USB-C конектор"
    },
    {
      "n": "5",
      "status": "done",
      "slug": "solenoid-relay",
      "dir": "interfaces/solenoid-relay/",
      "main": "solenoid-relay.md",
      "title": "Соленоїд і реле"
    },
    {
      "n": "6",
      "status": "done",
      "slug": "74hc165-piso",
      "dir": "interfaces/74hc165-piso/",
      "main": "74hc165-piso.md",
      "title": "74HC165: паралельний вхід / послідовний вихід"
    },
    {
      "n": "7",
      "status": "done",
      "slug": "74hc595-sipo",
      "dir": "interfaces/74hc595-sipo/",
      "main": "74hc595-sipo.md",
      "title": "74HC595: послідовний вхід / паралельний вихід"
    },
    {
      "n": "8",
      "status": "done",
      "slug": "74hc138-decoder",
      "dir": "interfaces/74hc138-decoder/",
      "main": "74hc138-decoder.md",
      "title": "74HC138: дешифратор / chip-select"
    },
    {
      "n": "9",
      "status": "done",
      "slug": "gpio-expander",
      "dir": "interfaces/gpio-expander/",
      "main": "gpio-expander.md",
      "title": "GPIO-розширювач"
    }
  ]
}
);
