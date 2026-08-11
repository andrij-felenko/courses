window.__MODREG__ = window.__MODREG__ || [];
window.__MODREG__.push({
  n: 1,
  slug: "number-theory",
  title: "Теорія чисел",
  chapters: [
    {
      n: 1,
      title: "Діофантові рівняння та задача про монети",
      dir: "sylvester-frobenius-formula",
      main: "sylvester-frobenius-formula-d.md",
      status: "done",
      scope: "Формула Сильвестра для числа Фробеніуса",
      topics: [
        { mrt: "1.1.1", title: "Формула Сильвестра", status: "done", scope: "Базове розуміння" }
      ]
    },
    {
      n: 2,
      title: "Тотожність Ейлера та Дзета-функція",
      dir: "euler-product-formula",
      main: "euler-product-formula-d.md",
      status: "done",
      scope: "Тотожність Ейлера",
      topics: [
        { 
          mrt: "1.2.1", 
          title: "Тотожність Ейлера", 
          status: "done", 
          scope: "Зв'язок простих чисел та дзета-функції",
          hist: [{ file: "hist-euler-1737.md", status: "done" }],
          math: [{ file: "math-analytic-continuation-proof.md", status: "done" }],
          proj: [{ file: "proj-zeta-product-sim.md", status: "done" }]
        }
      ]
    },
    {
      n: 3,
      title: "Теорема Евкліда — Ейлера про досконалі числа",
      dir: "euclid-euler-theorem",
      main: "euclid-euler-theorem-d.md",
      status: "done",
      scope: "Досконалі числа",
      topics: [
        { 
          mrt: "1.3.1", 
          title: "Теорема Евкліда — Ейлера", 
          status: "done", 
          scope: "Теорема Евкліда — Ейлера про досконалі числа",
          hist: [{ file: "hist-perfect-numbers.md", status: "done", title: "Історія пошуку" }],
          math: [{ file: "math-sigma-multiplicative-proof.md", status: "done", title: "Мультиплікативність σ" }],
          proj: [{ file: "proj-perfect-number-generator.md", status: "done", title: "Генератор (C++)" }]
        }
      ]
    }
  ]
});
