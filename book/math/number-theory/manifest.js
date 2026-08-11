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
        { mrt: "1.1.1", title: "Формула Сильвестра", status: "done", scope: "Базове розуміння" },
        { kind: "hist", file: "hist-sylvester-1884.md", at: "top", status: "done", title: "Історія публікації Сильвестра 1884 року" }
      ]
    },
    {
      n: 2,
      title: "Алгоритм та рекодування Бута",
      dir: "booth-algorithm",
      main: "booth-algorithm-d.md",
      status: "done",
      scope: "Алгоритм множення та рекодування Бута",
      topics: [
        { mrt: "1.2.1", title: "Алгоритм та рекодування Бута", status: "done", scope: "Radix-4, 2's complement" },
        { kind: "hist", file: "hist-andrew-booth-arc.md", at: "top", status: "done", title: "Історія Ендрю Дональда Бута" },
        { kind: "math", file: "math-booth-algebraic-proof.md", at: "math", status: "done", title: "Математичне доведення" },
        { kind: "proj", file: "proj-booth-radix4-sim.md", at: "bottom", status: "done", title: "C++ симулятор" }
      ]
    },
    {
      n: 3,
      title: "Решітка дільників та частковий порядок",
      dir: "divisor-lattice",
      main: "divisor-lattice-d.md",
      status: "done",
      scope: "Решітка дільників D_n, діаграми Хассе",
      topics: [
        { mrt: "1.3.1", title: "Решітка дільників", status: "done", scope: "inf(a,b)=gcd, sup(a,b)=lcm" },
        { kind: "hist", file: "hist-hasse-lattice.md", at: "top", status: "done", title: "Історія діаграм Хассе" },
        { kind: "math", file: "math-boolean-sublattices.md", at: "math", status: "done", title: "Булеві підалгебри 2^k" },
        { kind: "proj", file: "proj-hasse-generator.md", at: "bottom", status: "done", title: "Генератор діаграм (C++)" }
      ]
    },
    {
      n: 4,
      title: "Сходи Монтгомері",
      dir: "montgomery-ladder",
      main: "montgomery-ladder-d.md",
      status: "done",
      scope: "Скалярне множення без витоків за часом",
      topics: [
        { mrt: "1.4.1", title: "Сходи Монтгомері", status: "done", scope: "Constant-time scalar multiplication" },
        { kind: "hist", file: "hist-peter-montgomery.md", at: "top", status: "done", title: "Історія Пітера Монтгомері" },
        { kind: "math", file: "math-ladder-invariant-proof.md", at: "math", status: "done", title: "Доведення інваріанту R1 - R0 = P" },
        { kind: "proj", file: "proj-montgomery-ladder-sim.md", at: "bottom", status: "done", title: "C++ симулятор сходів" }
      ]
    },
    {
      n: 5,
      title: "Тотожність Безу",
      dir: "bezout-identity",
      main: "bezout-identity-d.md",
      status: "done",
      scope: "Тотожність Безу",
      topics: [
        { mrt: "1.5.1", title: "Тотожність Безу", status: "done", scope: "Розширений алгоритм Евкліда" },
        { kind: "hist", file: "hist-etienne-bezout.md", at: "1.5.1", status: "done", title: "Етьєн Безу" },
        { kind: "math", file: "math-extended-gcd-proof.md", at: "1.5.1", status: "done", title: "Доведення інваріантів" },
        { kind: "proj", file: "proj-ext-gcd-solver.md", at: "1.5.1", status: "done", title: "Реалізація C++" }
      ]
    },
    {
      n: 6,
      title: "Метод хорди та Піфагорові трійки",
      dir: "chord-method-triples",
      main: "chord-method-triples-d.md",
      status: "done",
      scope: "Раціональна параметризація кола",
      topics: [
        { mrt: "1.6.1", title: "Геометричне виведення трійок", status: "done", scope: "Метод хорди" },
        { kind: "hist", file: "hist-diophantus-chord.md", at: "1.6.1", status: "done", title: "Історія Діофанта" },
        { kind: "math", file: "math-rational-param-proof.md", at: "1.6.1", status: "done", title: "Математичне доведення повноти" },
        { kind: "proj", file: "proj-pythagorean-generator.md", at: "1.6.1", status: "done", title: "Генератор трійок на C++" }
      ]
    },
    {
      n: 6,
      title: "Теорема Евкліда — Ейлера про досконалі числа",
      dir: "euclid-euler-theorem",
      main: "euclid-euler-theorem-d.md",
      status: "done",
      scope: "Теорема Евкліда — Ейлера про досконалі числа",
      topics: [
        { mrt: "1.6.1", title: "Теорема Евкліда — Ейлера", status: "done", scope: "Досконалі числа" },
        { kind: "hist", file: "hist-perfect-numbers.md", at: "1.6.1", status: "done", title: "Історія пошуку досконалих чисел" },
        { kind: "math", file: "math-sigma-multiplicative-proof.md", at: "1.6.1", status: "done", title: "Мультиплікативність функції σ(n)" },
        { kind: "proj", file: "proj-perfect-number-generator.md", at: "1.6.1", status: "done", title: "Генератор досконалих чисел (C++)" }
      ]
    },
    {
      n: 7,
      title: "Квадратичний закон взаємності",
      dir: "quadratic-reciprocity",
      main: "quadratic-reciprocity-d.md",
      status: "done",
      scope: "Квадратичний закон взаємності, символ Лежандра",
      topics: [
        { mrt: "1.7.1", title: "Квадратичний закон взаємності", status: "done", scope: "Золота теорема Гаусса, доведення Ейзенштейна" },
        { kind: "hist", file: "hist-gauss-theorema-aureum.md", at: "1.7.1", status: "done", title: "Теорема Aureum: Золота теорема Гаусса" },
        { kind: "math", file: "math-eisenstein-proof.md", at: "1.7.1", status: "done", title: "Геометричне доведення Ейзенштейна" },
        { kind: "proj", file: "proj-legendre-jacobi-calculator.md", at: "1.7.1", status: "done", title: "Калькулятор символів Лежандра та Якобі" }
      ]
    }
  ]
});
