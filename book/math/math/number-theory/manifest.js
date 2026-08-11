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
      title: "Метод хорди та Піфагорові трійки",
      dir: "chord-method-triples",
      main: "chord-method-triples-d.md",
      status: "done",
      scope: "Раціональна параметризація кола",
      topics: [
        { 
          mrt: "1.3.1", 
          title: "Геометричне виведення трійок", 
          status: "done", 
          scope: "Метод хорди",
          hist: [{ file: "hist-diophantus-chord.md", status: "done", title: "Історія Діофанта" }],
          math: [{ file: "math-rational-param-proof.md", status: "done", title: "Математичне доведення повноти" }],
          proj: [{ file: "proj-pythagorean-generator.md", status: "done", title: "Генератор трійок на C++" }]
        }
      ]
    }
  ]
});
