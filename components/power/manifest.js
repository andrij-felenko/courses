/* components/power/manifest.js — per-module маніфест (генерується split-modules.js).
   Книга-довідник: розділ = самостійна тема. Складає scripts/bookbuild.js. */
(window.__MODREG__ = window.__MODREG__ || []).push(
{
  "n": 2,
  "title": "Живлення",
  "slug": "power",
  "chapters": [
    {
      "n": "1",
      "status": "pending",
      "title": "Лінійний стабілізатор (LDO)"
    },
    {
      "n": "2",
      "status": "pending",
      "title": "Понижувальний перетворювач (buck)"
    },
    {
      "n": "3",
      "status": "pending",
      "title": "Підвищувальний перетворювач (boost)"
    },
    {
      "n": "4",
      "status": "pending",
      "title": "Зарядка Li-ion (TP4056-клас)"
    },
    {
      "n": "5",
      "status": "done",
      "slug": "tp4056-charger",
      "dir": "power/tp4056-charger/",
      "main": "tp4056-charger.md",
      "title": "TP4056: зарядний контролер Li-ion"
    },
    {
      "n": "6",
      "status": "done",
      "slug": "fuel-gauge",
      "dir": "power/fuel-gauge/",
      "main": "fuel-gauge.md",
      "title": "Fuel gauge: лічильник заряду"
    },
    {
      "n": "7",
      "status": "done",
      "slug": "usb-cc-resistors",
      "dir": "power/usb-cc-resistors/",
      "main": "usb-cc-resistors.md",
      "title": "USB CC-резистори"
    },
    {
      "n": "8",
      "status": "done",
      "slug": "usb-pd-sink",
      "dir": "power/usb-pd-sink/",
      "main": "usb-pd-sink.md",
      "title": "USB PD sink-контролер"
    },
    {
      "n": "9",
      "status": "done",
      "slug": "power-path",
      "dir": "power/power-path/",
      "main": "power-path.md",
      "title": "Power-path менеджер"
    },
    {
      "n": "10",
      "status": "done",
      "slug": "sync-rectifier",
      "dir": "power/sync-rectifier/",
      "main": "sync-rectifier.md",
      "title": "Синхронний випрямляч"
    },
    {
      "n": "11",
      "status": "done",
      "slug": "charge-pump",
      "dir": "power/charge-pump/",
      "main": "charge-pump.md",
      "title": "Charge pump (індуктивний без)"
    },
    {
      "n": "12",
      "status": "done",
      "slug": "wall-adapter",
      "dir": "power/wall-adapter/",
      "main": "wall-adapter.md",
      "title": "Мережевий адаптер (wall adapter)"
    },
    {
      "n": "13",
      "status": "done",
      "slug": "dc-dc-module",
      "dir": "power/dc-dc-module/",
      "main": "dc-dc-module.md",
      "title": "DC-DC модуль живлення"
    },
    {
      "n": "14",
      "status": "done",
      "slug": "electronic-load",
      "dir": "power/electronic-load/",
      "main": "electronic-load.md",
      "title": "Електронне навантаження"
    }
  ]
}
);
