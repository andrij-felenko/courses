/* components/memory/manifest.js — per-module маніфест (генерується split-modules.js).
   Книга-довідник: розділ = самостійна тема. Складає scripts/bookbuild.js. */
(window.__MODREG__ = window.__MODREG__ || []).push(
{
  "n": 5,
  "title": "Пам'ять",
  "slug": "memory",
  "chapters": [
    {
      "n": "1",
      "status": "pending",
      "title": "SPI-флеш"
    },
    {
      "n": "2",
      "status": "pending",
      "title": "EEPROM по I²C"
    },
    {
      "n": "3",
      "status": "pending",
      "title": "microSD-картка"
    },
    {
      "n": "4",
      "status": "done",
      "slug": "psram",
      "dir": "memory/psram/",
      "main": "psram.md",
      "title": "PSRAM (псевдостатична RAM)"
    }
  ]
}
);
