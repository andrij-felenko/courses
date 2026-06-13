/* math/vector-analysis/manifest.js — per-module маніфест (генерується split-modules.js).
   Книга-довідник: розділ = самостійна тема. Складає scripts/bookbuild.js. */
(window.__MODREG__ = window.__MODREG__ || []).push(
{
  "n": 2,
  "title": "Вектор-аналіз і потік",
  "slug": "vector-analysis",
  "chapters": [
    {
      "n": "1",
      "slug": "vector-components",
      "status": "done",
      "dir": "vector-components/",
      "main": "vector-components.md",
      "title": "Вектор: чому величина розкладається на незалежні складові"
    },
    {
      "n": "2",
      "status": "pending",
      "title": "Додавання векторів: правило паралелограма й |R|=√(Rx²+Ry²)"
    },
    {
      "n": "3",
      "slug": "gradient",
      "status": "done",
      "dir": "gradient/",
      "main": "gradient.md",
      "title": "Скалярний добуток як проєкція та «схожість»"
    },
    {
      "n": "4",
      "slug": "cross-product",
      "status": "done",
      "dir": "cross-product/",
      "main": "cross-product.md",
      "title": "Векторний добуток: момент сили і магнітна сила"
    },
    {
      "n": "5",
      "status": "pending",
      "title": "Потік і дивергенція: скільки витікає з точки"
    },
    {
      "n": "6",
      "status": "pending",
      "title": "Теорема Гаусса про потік: чому потік = заряд усередині"
    }
  ]
}
);
