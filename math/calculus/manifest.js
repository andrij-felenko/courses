/* math/calculus/manifest.js — per-module маніфест (генерується split-modules.js).
   Книга-довідник: розділ = самостійна тема. Складає scripts/bookbuild.js. */
(window.__MODREG__ = window.__MODREG__ || []).push(
{
  "n": 4,
  "title": "Похідні та інтеграли",
  "slug": "calculus",
  "chapters": [
    {
      "n": "1",
      "slug": "derivative",
      "status": "done",
      "dir": "derivative/",
      "main": "derivative.md",
      "title": "Похідна як миттєва швидкість зміни"
    },
    {
      "n": "2",
      "status": "pending",
      "title": "Інтеграл як неперервна сума"
    },
    {
      "n": "3",
      "status": "pending",
      "title": "Похідна й інтеграл для ПІД-регулятора"
    },
    {
      "n": "4",
      "status": "pending",
      "title": "Згортка: математика FIR-фільтра"
    },
    {
      "n": "5",
      "slug": "derivative-max",
      "status": "done",
      "dir": "derivative-max/",
      "main": "derivative-max.md",
      "title": "Похідна для пошуку максимуму: екстремуми функцій"
    },
    {
      "n": "6",
      "slug": "derivative-cap",
      "status": "done",
      "dir": "derivative-cap/",
      "main": "derivative-cap.md",
      "title": "Похідна струму конденсатора: i = C·dV/dt"
    },
    {
      "n": "7",
      "slug": "exponential-ode",
      "status": "done",
      "dir": "exponential-ode/",
      "main": "exponential-ode.md",
      "title": "Експоненційний ОДУ: заряд конденсатора"
    },
    {
      "n": "8",
      "slug": "rl-ode",
      "status": "done",
      "dir": "rl-ode/",
      "main": "rl-ode.md",
      "title": "ОДУ RL-кола: наростання струму в індукторі"
    },
    {
      "n": "9",
      "slug": "rms-derivation",
      "status": "done",
      "dir": "rms-derivation/",
      "main": "rms-derivation.md",
      "title": "Виведення RMS: середньоквадратичне значення синусоїди"
    },
    {
      "n": "10",
      "slug": "sine-derivative",
      "status": "done",
      "dir": "sine-derivative/",
      "main": "sine-derivative.md",
      "title": "Похідна синуса: чому d/dt sin(ωt) = ω·cos(ωt)"
    },
    {
      "n": "11",
      "slug": "work-integral",
      "status": "done",
      "dir": "work-integral/",
      "main": "work-integral.md",
      "title": "Інтеграл роботи: робота у полі як лінійний інтеграл"
    },
    {
      "n": "12",
      "slug": "half-power",
      "status": "done",
      "dir": "half-power/",
      "main": "half-power.md",
      "title": "Точка -3 дБ: частота напівпотужності"
    },
    {
      "n": "13",
      "slug": "logarithms",
      "status": "done",
      "dir": "logarithms/",
      "main": "logarithms.md",
      "title": "Логарифми й децибели: шкала для широкого діапазону"
    },
    {
      "n": "14",
      "slug": "transfer-function",
      "status": "done",
      "dir": "transfer-function/",
      "main": "transfer-function.md",
      "title": "Передавальна функція: від ОДУ до H(jω)"
    },
    {
      "n": "15",
      "slug": "cascading",
      "status": "done",
      "dir": "cascading/",
      "main": "cascading.md",
      "title": "Каскадування фільтрів: множення передавальних функцій"
    },
    {
      "n": "16",
      "slug": "thomson-formula",
      "status": "done",
      "dir": "thomson-formula/",
      "main": "thomson-formula.md",
      "title": "Формула Томсона: резонансна частота LC-контуру"
    }
  ]
}
);
