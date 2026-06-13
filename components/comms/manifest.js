/* components/comms/manifest.js — per-module маніфест (генерується split-modules.js).
   Книга-довідник: розділ = самостійна тема. Складає scripts/bookbuild.js. */
(window.__MODREG__ = window.__MODREG__ || []).push(
{
  "n": 3,
  "title": "Зв'язок",
  "slug": "comms",
  "chapters": [
    {
      "n": "1",
      "status": "pending",
      "title": "Радіомодуль (nRF24-клас)"
    },
    {
      "n": "2",
      "status": "pending",
      "title": "LoRa-модуль"
    },
    {
      "n": "3",
      "status": "pending",
      "title": "GNSS-модуль (NEO-клас) і вихід PPS"
    },
    {
      "n": "4",
      "status": "done",
      "slug": "nfc-rfid",
      "dir": "comms/nfc-rfid/",
      "main": "nfc-rfid.md",
      "title": "NFC/RFID-модуль"
    },
    {
      "n": "5",
      "status": "done",
      "slug": "utp-cable",
      "dir": "comms/utp-cable/",
      "main": "utp-cable.md",
      "title": "UTP-кабель (витата пара)"
    },
    {
      "n": "6",
      "status": "done",
      "slug": "shielded-cable",
      "dir": "comms/shielded-cable/",
      "main": "shielded-cable.md",
      "title": "Екранований кабель"
    },
    {
      "n": "7",
      "status": "done",
      "slug": "wroom-module",
      "dir": "comms/wroom-module/",
      "main": "wroom-module.md",
      "title": "ESP32-WROOM модуль"
    },
    {
      "n": "8",
      "status": "done",
      "slug": "esp32-antenna",
      "dir": "comms/esp32-antenna/",
      "main": "esp32-antenna.md",
      "title": "Антена ESP32"
    }
  ]
}
);
