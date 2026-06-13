/* math/linear-algebra/manifest.js — per-module маніфест (генерується split-modules.js).
   Книга-довідник: розділ = самостійна тема. Складає scripts/bookbuild.js. */
(window.__MODREG__ = window.__MODREG__ || []).push(
{
  "n": 1,
  "title": "Лінійна алгебра",
  "slug": "linear-algebra",
  "chapters": [
    {
      "n": "1",
      "status": "pending",
      "title": "Системи лінійних рівнянь: що означає «розв'язати»"
    },
    {
      "n": "2",
      "slug": "gauss-elimination",
      "status": "done",
      "dir": "gauss-elimination/",
      "main": "gauss-elimination.md",
      "title": "Метод Гаусса: виключення крок за кроком"
    },
    {
      "n": "3",
      "slug": "matrices-as-operations",
      "status": "done",
      "dir": "matrices-as-operations/",
      "main": "matrices-as-operations.md",
      "title": "Матриці як дії над векторами"
    },
    {
      "n": "4",
      "status": "pending",
      "title": "Матриці повороту й звідки береться gimbal lock"
    },
    {
      "n": "5",
      "slug": "hamming-distance",
      "status": "done",
      "dir": "hamming-distance/",
      "main": "hamming-distance.md",
      "title": "Відстань Гемінга і коди з виправленням помилок"
    },
    {
      "n": "6",
      "slug": "crc-cyclic-redundancy",
      "status": "done",
      "dir": "crc-cyclic-redundancy/",
      "main": "crc-cyclic-redundancy.md",
      "title": "Циклічна надмірність: поліноми над GF(2)"
    }
  ]
}
);
