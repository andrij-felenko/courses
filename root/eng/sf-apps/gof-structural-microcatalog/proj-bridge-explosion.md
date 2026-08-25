# ⚙️ Той самий редактор двічі: вибух підкласів і міст, що його гасить

<preknowlist>
- [Інтерфейс проти реалізації](topic:sf-apps/interface-vs-implementation) — різниця між тим, ЩО тип обіцяє назовні, і тим, ЯК він це робить усередині; тут на цій межі стоїть усе.
- [Композиція над спадкуванням](topic:sf-apps/composition-inheritance) — «має» проти «є»: чому поведінку частіше кладуть об'єктом у поле, ніж успадковують.
- [Поліморфізм і динамічне зв'язування](topic:sf-lang/polymorphism) — як виклик через спільний інтерфейс потрапляє в потрібну реалізацію під час роботи; без цього заміна на льоту неможлива.
</preknowlist>

Порахувати класи на дошці легко — і так само легко відмахнутися: ну дев'ять, ну дванадцять, невелика біда. Біда стає видною тоді, коли ці класи пишеш руками, а через місяць знаходиш помилку в геометрії зірки й ідеш виправляти її в трьох місцях, з яких два забудеш.

Тож зберімо один і той самий маленький редактор фігур **двічі**. Спершу так, як просить перша спокуса, — підклас на кожну пару «фігура × рушій». Потім мостом. Рахуватимемо класи на кожному кроці, замінимо рушій просто під час роботи й наприкінці виведемо умову, за якої міст дійсно дешевший — бо, як побачимо, дуже часто він не дешевший.

## Задача: чотири фігури, три рушії, один малюнок

Потрібен інструмент, що складає схему з фігур і виводить її. Вимоги приходять не разом — вони накопичуються, і саме в цьому вся сіль:

- **Тиждень 1.** Прямокутник і коло, вивід у SVG — щоб зберегти файл.
- **Тиждень 2.** Треба ще текстове прев'ю просто в терміналі: дивитися картинку в логах збірки, не відкриваючи редактора.
- **Тиждень 3.** Додається трикутник.
- **Тиждень 4.** Потрібен третій рушій — не картинка взагалі, а обмір: скільки примітивів і яка габаритна рамка. Це піде в тести, щоб перевіряти, що сцена не виїхала за полотно.
- **Тиждень 5.** Додається зірка.

Разом чотири фігури — коло, прямокутник, трикутник, зірка — і три рушії: SVG, ASCII, обмір. Систему координат домовмося раз і назавжди: фігури живуть у полотні 80 × 40 умовних одиниць, вісь Y дивиться вниз, як заведено в комп'ютерній графіці. Що робити з цими одиницями — клопіт рушія: SVG покладе їх у `viewBox`, ASCII візьме за клітинку знака, обмір просто збере мінімум і максимум.

## Наївний хід: клас на кожну пару

Спокуса очевидна: якщо коло треба вміти малювати трьома способами — хай буде три класи кола. Кожен клас знає свою фігуру й свій носій, усе чесно й прямо. Ось як це виглядає на зірці — найцікавішій із фігур, бо в неї є справжня геометрія:

:::tabs
```py
import math

# НАЇВНО: клас на КОЖНУ пару «фігура × рушій»
class SvgStar:
    def __init__(self, cx, cy, outer, inner, n=5):
        self.cx, self.cy, self.outer, self.inner, self.n = cx, cy, outer, inner, n
    def draw(self, out):
        pts = []
        for i in range(self.n * 2):                        # ← математика зірки, копія №1
            rad = self.outer if i % 2 == 0 else self.inner
            t = math.pi * i / self.n - math.pi / 2         # −π/2, щоб вістря дивилось угору
            pts.append((self.cx + rad * math.cos(t), self.cy + rad * math.sin(t)))
        d = " ".join("%.1f,%.1f" % p for p in pts)
        out.append('<polygon points="%s" fill="none" stroke="black"/>' % d)

class AsciiStar:
    def __init__(self, cx, cy, outer, inner, n=5):
        self.cx, self.cy, self.outer, self.inner, self.n = cx, cy, outer, inner, n
    def draw(self, grid):
        pts = []
        for i in range(self.n * 2):                        # ← ТА САМА математика, копія №2
            rad = self.outer if i % 2 == 0 else self.inner
            t = math.pi * i / self.n - math.pi / 2
            pts.append((self.cx + rad * math.cos(t), self.cy + rad * math.sin(t)))
        for a, b in zip(pts, pts[1:] + [pts[0]]):
            plot_segment(grid, a, b)

# class StatsStar:  ← копія №3, з тим самим циклом і тим самим −π/2
```
```ts
// НАЇВНО: клас на КОЖНУ пару «фігура × рушій»
class SvgStar {
  constructor(private cx: number, private cy: number,
              private outer: number, private inner: number, private n = 5) {}
  draw(out: string[]) {
    const pts: [number, number][] = [];
    for (let i = 0; i < this.n * 2; i++) {                 // ← математика зірки, копія №1
      const rad = i % 2 === 0 ? this.outer : this.inner;
      const t = (Math.PI * i) / this.n - Math.PI / 2;      // −π/2, щоб вістря дивилось угору
      pts.push([this.cx + rad * Math.cos(t), this.cy + rad * Math.sin(t)]);
    }
    const d = pts.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
    out.push(`<polygon points="${d}" fill="none" stroke="black"/>`);
  }
}

class AsciiStar {
  constructor(private cx: number, private cy: number,
              private outer: number, private inner: number, private n = 5) {}
  draw(grid: string[][]) {
    const pts: [number, number][] = [];
    for (let i = 0; i < this.n * 2; i++) {                 // ← ТА САМА математика, копія №2
      const rad = i % 2 === 0 ? this.outer : this.inner;
      const t = (Math.PI * i) / this.n - Math.PI / 2;
      pts.push([this.cx + rad * Math.cos(t), this.cy + rad * Math.sin(t)]);
    }
    for (let i = 0; i < pts.length; i++) plotSegment(grid, pts[i], pts[(i + 1) % pts.length]);
  }
}

// class StatsStar  ← копія №3, з тим самим циклом і тим самим −π/2
```
```cpp
#include <cmath>
#include <format>
#include <numbers>
#include <string>
#include <utility>
#include <vector>

// НАЇВНО: клас на КОЖНУ пару «фігура × рушій»
class SvgStar {
    double cx, cy, outer, inner;
    int n;
public:
    SvgStar(double cx, double cy, double outer, double inner, int n = 5)
        : cx(cx), cy(cy), outer(outer), inner(inner), n(n) {}
    void draw(std::vector<std::string>& out) const {
        std::string d;
        for (int i = 0; i < n * 2; ++i) {                     // ← математика зірки, копія №1
            double rad = (i % 2 == 0) ? outer : inner;
            double t = std::numbers::pi * i / n - std::numbers::pi / 2;  // −π/2, щоб вістря дивилось угору
            d += std::format("{}{:.1f},{:.1f}", i ? " " : "",
                             cx + rad * std::cos(t), cy + rad * std::sin(t));
        }
        out.push_back(std::format("<polygon points=\"{}\" fill=\"none\" stroke=\"black\"/>", d));
    }
};

class AsciiStar {
    double cx, cy, outer, inner;
    int n;
public:
    AsciiStar(double cx, double cy, double outer, double inner, int n = 5)
        : cx(cx), cy(cy), outer(outer), inner(inner), n(n) {}
    void draw(std::vector<std::string>& grid) const {
        std::vector<std::pair<double, double>> pts;
        for (int i = 0; i < n * 2; ++i) {                     // ← ТА САМА математика, копія №2
            double rad = (i % 2 == 0) ? outer : inner;
            double t = std::numbers::pi * i / n - std::numbers::pi / 2;
            pts.push_back({cx + rad * std::cos(t), cy + rad * std::sin(t)});
        }
        for (std::size_t i = 0; i < pts.size(); ++i)
            plot_segment(grid, pts[i], pts[(i + 1) % pts.size()]);   // plot_segment — спільний помічник
    }
};

// class StatsStar  ← копія №3, з тим самим циклом і тим самим −π/2
```
:::

Порахуймо, як росла ця купа по тижнях. У колонці «класів» — рівно те, що лежить у теці:

```
тиждень   фігур S   рушіїв R   класів (S · R)   що дописали
   1         2         1              2         SvgRect, SvgCircle
   2         2         2              4         +Ascii-версії обох      (+1 рушій → +S = +2)
   3         3         2              6         +SvgTriangle, +AsciiTriangle  (+1 фігура → +R = +2)
   4         3         3              9         +Stats-версії всіх трьох      (+1 рушій → +S = +3)
   5         4         3             12         +SvgStar, +AsciiStar, +StatsStar (+1 фігура → +R = +3)
```

Тут видно головне правило наївного ходу: **жодна нова вимога не коштує один клас**. Фігура коштує R класів, рушій коштує S класів, і чим більше вже є, тим дорожча кожна наступна дрібниця. На тижні 5 замовник попросив «ще одну фігуру» — а робота вийшла втричі більша за очікувану, і робити її треба в трьох файлах.

## Справжній рахунок: не класи, а переписана геометрія

Класи — це те, що видно. Але платиш ти не за них.

Придивись до `SvgStar` і `AsciiStar` вище. Кожен — той самий цикл на десять вершин: зовнішній радіус через один, крок π/n, поворот на −π/2, щоб зірка стояла вістрям угору. Формулу вершин зірки написано **тричі** (третій раз — у `StatsStar`). Не тому, що програміст лінивий копіювати менше, а тому, що структура класів не лишила іншого місця: щоб `AsciiStar` намалював зірку, він **мусить** знати, де її кути.

І ось у цьому справжня ціна. Уяви звичайну середу: тестувальник каже, що зірка в прев'ю крива — вістря дивиться праворуч, а не вгору. Ти знаходиш пропущене `− math.pi / 2`… в одному з трьох класів. Виправив у прев'ю — у SVG лишилось. Виправив у SVG — обмір рахує рамку по старих кутах, і тест «не виїхало за полотно» тихо бреше далі.

Формально: класів S·R, і **реалізацій геометрії теж S·R**. Кожна фігура існує в R примірниках знання про себе. Виправлення однієї помилки коштує R правок, і забути хоч одну — норма, а не виняток.

> 🔧 **Навіщо це.** Ознака, за якою вибух видно ще до підрахунку, — **однакові цикли в класах із різними суфіксами**. Якщо `AsciiStar.draw` і `SvgStar.draw` починаються з тих самих п'яти рядків тригонометрії й розходяться лише в останньому рядку, це не «трохи дублювання» — це зрощені осі. Спільне (де в зірки кути) прибито до різного (як покласти лінію на носій), і роз'єднати їх копіюванням неможливо: копія лише множить місця, де живе одна й та сама істина.

## Ідея: дві осі — і замкнений набір примітивів

Перше питання — що тут насправді змінюється нарізно. Відповідь на поверхні: фігури приходять від задачі («треба ще зірку»), рушії — від носія («треба ще прев'ю в терміналі»). Ці два джерела вимог не питають одне одного дозволу: замовник просить зірку, не думаючи, куди її виводитимуть; ти додаєш обмір, не знаючи, які фігури будуть наступні.

Друге питання — котра з осей абстракція, а котра реалізація. Правило: **абстракція ближча до задачі, реалізація — до носія**. Фігура — поняття предметної області; рушій — те, як поняття лягає на конкретний матеріал: текст SVG, сітка знаків, пара чисел. Отже, фігура тримає рушій, а не навпаки. Спробуй навпаки — і рушій муситиме перелічити всі фігури, а це та сама зрощеність, лише перевернута.

І тут третє питання, найважливіше — те, на якому міст найчастіше й ламається. **Які операції має мати рушій?**

Перша, майже автоматична відповідь — по операції на фігуру:

```
Renderer:  drawCircle · drawRect · drawTriangle · drawStar
```

Виглядає невинно, а наслідки — рівно ті, від яких тікали. Додаєш п'яту фігуру — мусиш дописати `drawPentagon` в інтерфейс і **реалізувати його в кожному з трьох рушіїв**. Класів справді стало S+R, зате тіл методів лишилось S·R, і геометрія знову розповзлася по рушіях. Вибух не зник — він переодягнувся: був у назвах класів, став у назвах методів.

Правильний хід — питати не «які фігури в мене є», а «**що взагалі вміє носій**». І тут виявляється диво: усі чотири фігури — і будь-які майбутні — це лише **дві** речі. Ламана (замкнена або ні) та еліпс. Прямокутник — ламана з чотирьох точок. Трикутник — із трьох. Зірка — з десяти. Коло — еліпс із рівними півосями.

```
Renderer:  begin(w, h) · polyline(точки, замкнена) · ellipse(cx, cy, rx, ry) · end()
```

Чотири операції — і, головне, їх **чотири назавжди**: набір визначає не список фігур, а те, що вміє носій. Фігура тепер не «просить намалювати себе» — вона **перекладає себе в примітиви**, і робить це в одному місці на всі рушії.

![Дві половини. Ліворуч товстий інтерфейс: у рамці Renderer перелік drawCircle, drawRect, drawTriangle і drawStar як нова фігура, від нього червоні стрілки до трьох рушіїв SvgRenderer, AsciiRenderer, StatsRenderer, біля кожного підпис плюс одне тіло; унизу підсумок — тіл методів дорівнює S на R, плюс одна фігура означає правку в усіх рушіях. Праворуч примітивний інтерфейс: у рамці Renderer лише begin і end, polyline та ellipse, від нього зелені стрілки до тих самих трьох рушіїв із підписом без змін, а нова фігура входить окремою рамкою Star.draw через polyline на десять точок лише в інтерфейс; унизу підсумок — тіл методів дорівнює R на P, де P стале, плюс одна фігура означає нуль правок у рушіях](img/implementor-interface.svg)

*Делегування саме собою нічого не рятує: міст працює лише тоді, коли набір операцій реалізації замкнений — визначений носієм, а не переліком фігур. Товстий інтерфейс дає ту саму матрицю роботи, просто розкладену по методах замість класів.*

Саме тут міст дає те, заради чого його ставлять: вісь рушіїв стає [відкритою для розширення й закритою для змін](topic:sf-apps/open-closed) — нова фігура додає код, але не змушує чіпати жоден наявний рушій. Причому не з доброї волі автора, а структурно: фігурі просто нічого сказати рушієві, крім `polyline` та `ellipse`.

## Робочий код

Спершу вісь реалізації — рушії. Кожен уміє рівно чотири операції й нічого не знає про фігури: слова «коло» чи «зірка» тут не трапляється жодного разу.

:::tabs
```py
import math
from abc import ABC, abstractmethod

# ── Реалізація: ЯК виводимо (вісь 1) ──────────────────────────
class Renderer(ABC):
    @abstractmethod
    def begin(self, w, h): ...
    @abstractmethod
    def polyline(self, pts, closed): ...
    @abstractmethod
    def ellipse(self, cx, cy, rx, ry): ...
    @abstractmethod
    def end(self): ...


class SvgRenderer(Renderer):
    def begin(self, w, h):
        self.out = ['<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (w, h)]
    def polyline(self, pts, closed):
        d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
        tag = "polygon" if closed else "polyline"
        self.out.append('  <%s points="%s" fill="none" stroke="black"/>' % (tag, d))
    def ellipse(self, cx, cy, rx, ry):
        self.out.append('  <ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" '
                        'fill="none" stroke="black"/>' % (cx, cy, rx, ry))
    def end(self):
        self.out.append("</svg>")
        return "\n".join(self.out)


class AsciiRenderer(Renderer):
    def begin(self, w, h):
        self.w, self.h = w, h
        self.g = [[" "] * w for _ in range(h)]
    def _plot(self, x, y):
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < self.w and 0 <= yi < self.h:
            self.g[yi][xi] = "#"
    def _segment(self, a, b):
        (x1, y1), (x2, y2) = a, b
        steps = max(int(abs(x2 - x1)), int(abs(y2 - y1)), 1) * 2
        for i in range(steps + 1):
            t = i / steps
            self._plot(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
    def polyline(self, pts, closed):
        seq = (pts + [pts[0]]) if closed else pts
        for a, b in zip(seq, seq[1:]):
            self._segment(a, b)
    def ellipse(self, cx, cy, rx, ry):
        steps = max(8, int(4 * (rx + ry)))
        for i in range(steps):
            t = 2 * math.pi * i / steps
            self._plot(cx + rx * math.cos(t), cy + ry * math.sin(t))
    def end(self):
        return "\n".join("".join(row).rstrip() for row in self.g)


class StatsRenderer(Renderer):
    def begin(self, w, h):
        self.n = 0
        self.box = None
    def _grow(self, x, y):
        if self.box is None:
            self.box = [x, y, x, y]
        else:
            self.box[0] = min(self.box[0], x); self.box[1] = min(self.box[1], y)
            self.box[2] = max(self.box[2], x); self.box[3] = max(self.box[3], y)
    def polyline(self, pts, closed):
        self.n += 1
        for x, y in pts:
            self._grow(x, y)
    def ellipse(self, cx, cy, rx, ry):
        self.n += 1
        self._grow(cx - rx, cy - ry); self._grow(cx + rx, cy + ry)
    def end(self):
        x1, y1, x2, y2 = self.box
        return "примітивів: %d; рамка: (%.1f,%.1f)–(%.1f,%.1f)" % (self.n, x1, y1, x2, y2)
```
```ts
type Point = [number, number];

// ── Реалізація: ЯК виводимо (вісь 1) ─────────────────────────
interface Renderer {
  begin(w: number, h: number): void;
  polyline(pts: Point[], closed: boolean): void;
  ellipse(cx: number, cy: number, rx: number, ry: number): void;
  end(): string;
}

class SvgRenderer implements Renderer {
  private out: string[] = [];
  begin(w: number, h: number) {
    this.out = [`<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg">`];
  }
  polyline(pts: Point[], closed: boolean) {
    const d = pts.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
    this.out.push(`  <${closed ? "polygon" : "polyline"} points="${d}" fill="none" stroke="black"/>`);
  }
  ellipse(cx: number, cy: number, rx: number, ry: number) {
    this.out.push(`  <ellipse cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" ` +
                  `rx="${rx.toFixed(1)}" ry="${ry.toFixed(1)}" fill="none" stroke="black"/>`);
  }
  end() { this.out.push("</svg>"); return this.out.join("\n"); }
}

class AsciiRenderer implements Renderer {
  private w = 0;
  private h = 0;
  private g: string[][] = [];
  begin(w: number, h: number) {
    this.w = w; this.h = h;
    this.g = Array.from({ length: h }, () => new Array<string>(w).fill(" "));
  }
  private plot(x: number, y: number) {
    const xi = Math.round(x), yi = Math.round(y);
    if (xi >= 0 && xi < this.w && yi >= 0 && yi < this.h) this.g[yi][xi] = "#";
  }
  private segment([x1, y1]: Point, [x2, y2]: Point) {
    const steps = Math.max(Math.trunc(Math.abs(x2 - x1)), Math.trunc(Math.abs(y2 - y1)), 1) * 2;
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      this.plot(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t);
    }
  }
  polyline(pts: Point[], closed: boolean) {
    const seq = closed ? [...pts, pts[0]] : pts;
    for (let i = 0; i + 1 < seq.length; i++) this.segment(seq[i], seq[i + 1]);
  }
  ellipse(cx: number, cy: number, rx: number, ry: number) {
    const steps = Math.max(8, Math.trunc(4 * (rx + ry)));
    for (let i = 0; i < steps; i++) {
      const t = (2 * Math.PI * i) / steps;
      this.plot(cx + rx * Math.cos(t), cy + ry * Math.sin(t));
    }
  }
  end() { return this.g.map((row) => row.join("").replace(/\s+$/, "")).join("\n"); }
}

class StatsRenderer implements Renderer {
  private n = 0;
  private box: number[] | null = null;
  begin(_w: number, _h: number) { this.n = 0; this.box = null; }
  private grow(x: number, y: number) {
    if (!this.box) { this.box = [x, y, x, y]; return; }
    this.box[0] = Math.min(this.box[0], x); this.box[1] = Math.min(this.box[1], y);
    this.box[2] = Math.max(this.box[2], x); this.box[3] = Math.max(this.box[3], y);
  }
  polyline(pts: Point[], _closed: boolean) { this.n++; for (const [x, y] of pts) this.grow(x, y); }
  ellipse(cx: number, cy: number, rx: number, ry: number) {
    this.n++; this.grow(cx - rx, cy - ry); this.grow(cx + rx, cy + ry);
  }
  end() {
    const [x1, y1, x2, y2] = this.box!;
    return `примітивів: ${this.n}; рамка: (${x1.toFixed(1)},${y1.toFixed(1)})–` +
           `(${x2.toFixed(1)},${y2.toFixed(1)})`;
  }
}
```
```cpp
#include <algorithm>
#include <cmath>
#include <format>
#include <iostream>
#include <memory>
#include <numbers>
#include <string>
#include <vector>

struct Point { double x, y; };

// ── Реалізація: ЯК виводимо (вісь 1) ──────────────────────────
struct Renderer {
    virtual void begin(int w, int h) = 0;
    virtual void polyline(const std::vector<Point>& pts, bool closed) = 0;
    virtual void ellipse(double cx, double cy, double rx, double ry) = 0;
    virtual std::string end() = 0;
    virtual ~Renderer() = default;
};


class SvgRenderer : public Renderer {
    std::vector<std::string> out;
public:
    void begin(int w, int h) override {
        out = {std::format(R"(<svg viewBox="0 0 {} {}" xmlns="http://www.w3.org/2000/svg">)", w, h)};
    }
    void polyline(const std::vector<Point>& pts, bool closed) override {
        std::string d;
        for (std::size_t i = 0; i < pts.size(); ++i)
            d += std::format("{}{:.1f},{:.1f}", i ? " " : "", pts[i].x, pts[i].y);
        out.push_back(std::format(R"(  <{} points="{}" fill="none" stroke="black"/>)",
                                  closed ? "polygon" : "polyline", d));
    }
    void ellipse(double cx, double cy, double rx, double ry) override {
        out.push_back(std::format(
            R"(  <ellipse cx="{:.1f}" cy="{:.1f}" rx="{:.1f}" ry="{:.1f}" fill="none" stroke="black"/>)",
            cx, cy, rx, ry));
    }
    std::string end() override {
        out.push_back("</svg>");
        std::string s;
        for (std::size_t i = 0; i < out.size(); ++i) s += (i ? "\n" : "") + out[i];
        return s;
    }
};


class AsciiRenderer : public Renderer {
    int w = 0, h = 0;
    std::vector<std::string> g;
    void plot(double x, double y) {
        int xi = static_cast<int>(std::lround(x)), yi = static_cast<int>(std::lround(y));
        if (xi >= 0 && xi < w && yi >= 0 && yi < h) g[yi][xi] = '#';
    }
    void segment(Point a, Point b) {
        int steps = std::max({static_cast<int>(std::abs(b.x - a.x)),
                              static_cast<int>(std::abs(b.y - a.y)), 1}) * 2;
        for (int i = 0; i <= steps; ++i) {
            double t = static_cast<double>(i) / steps;
            plot(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t);
        }
    }
public:
    void begin(int w, int h) override {
        this->w = w; this->h = h;
        g.assign(h, std::string(w, ' '));
    }
    void polyline(const std::vector<Point>& pts, bool closed) override {
        std::vector<Point> seq = pts;
        if (closed) seq.push_back(pts[0]);
        for (std::size_t i = 0; i + 1 < seq.size(); ++i) segment(seq[i], seq[i + 1]);
    }
    void ellipse(double cx, double cy, double rx, double ry) override {
        int steps = std::max(8, static_cast<int>(4 * (rx + ry)));
        for (int i = 0; i < steps; ++i) {
            double t = 2 * std::numbers::pi * i / steps;
            plot(cx + rx * std::cos(t), cy + ry * std::sin(t));
        }
    }
    std::string end() override {
        std::string s;
        for (std::size_t r = 0; r < g.size(); ++r) {
            std::string row = g[r];
            row.erase(row.find_last_not_of(' ') + 1);   // rstrip
            s += (r ? "\n" : "") + row;
        }
        return s;
    }
};


class StatsRenderer : public Renderer {
    int n = 0;
    bool has = false;
    double x1 = 0, y1 = 0, x2 = 0, y2 = 0;
    void grow(double x, double y) {
        if (!has) { x1 = x2 = x; y1 = y2 = y; has = true; return; }
        x1 = std::min(x1, x); y1 = std::min(y1, y);
        x2 = std::max(x2, x); y2 = std::max(y2, y);
    }
public:
    void begin(int, int) override { n = 0; has = false; }
    void polyline(const std::vector<Point>& pts, bool) override {
        ++n;
        for (const auto& p : pts) grow(p.x, p.y);
    }
    void ellipse(double cx, double cy, double rx, double ry) override {
        ++n;
        grow(cx - rx, cy - ry);
        grow(cx + rx, cy + ry);
    }
    std::string end() override {
        return std::format("примітивів: {}; рамка: ({:.1f},{:.1f})–({:.1f},{:.1f})",
                           n, x1, y1, x2, y2);
    }
};
```
:::

Зверни увагу на `StatsRenderer`: він не малює нічого. Жодного пікселя, жодного тега. І все ж він повноправний рушій — бо «рушій» тут означає не «той, хто малює», а «той, хто вміє прийняти ламану й еліпс і щось із ними зробити». Ця дрібниця показує, наскільки чисто розчепилися осі: вісь реалізації виявилася ширшою за початкове уявлення про неї, і в неї безкоштовно вліз випадок, якого ніхто не планував.

Тепер вісь абстракції — фігури. Кожна тримає рушій полем (оце поле й є міст) і вміє єдину річ: перекласти себе в примітиви.

:::tabs
```py
# ── Абстракція: ЩО малюємо (вісь 2) ───────────────────────────
class Shape(ABC):
    def __init__(self, r):
        self.r = r                       # ← МІСТ до реалізації
    @abstractmethod
    def draw(self): ...


class Circle(Shape):
    def __init__(self, r, cx, cy, rad):
        super().__init__(r); self.cx, self.cy, self.rad = cx, cy, rad
    def draw(self):
        self.r.ellipse(self.cx, self.cy, self.rad, self.rad)


class Rect(Shape):
    def __init__(self, r, x, y, w, h):
        super().__init__(r); self.x, self.y, self.w, self.h = x, y, w, h
    def draw(self):
        x, y, w, h = self.x, self.y, self.w, self.h
        self.r.polyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], True)


class Triangle(Shape):
    def __init__(self, r, a, b, c):
        super().__init__(r); self.pts = [a, b, c]
    def draw(self):
        self.r.polyline(self.pts, True)


class Star(Shape):
    def __init__(self, r, cx, cy, outer, inner, points=5):
        super().__init__(r)
        self.cx, self.cy, self.outer, self.inner, self.points = cx, cy, outer, inner, points
    def draw(self):
        pts = []
        for i in range(self.points * 2):
            rad = self.outer if i % 2 == 0 else self.inner
            t = math.pi * i / self.points - math.pi / 2
            pts.append((self.cx + rad * math.cos(t), self.cy + rad * math.sin(t)))
        self.r.polyline(pts, True)       # геометрія зірки — ОДИН раз на всі рушії


class Scene:
    def __init__(self, r, shapes):
        self.shapes = shapes
        self.use(r)
    def use(self, r):                    # ← жива заміна рушія на льоту
        self.r = r
        for s in self.shapes:
            s.r = r
    def draw(self, w, h):
        self.r.begin(w, h)
        for s in self.shapes:
            s.draw()
        return self.r.end()
```
```ts
// ── Абстракція: ЩО малюємо (вісь 2) ──────────────────────────
abstract class Shape {
  constructor(public r: Renderer) {}          // ← МІСТ до реалізації
  abstract draw(): void;
}

class Circle extends Shape {
  constructor(r: Renderer, private cx: number, private cy: number, private rad: number) { super(r); }
  draw() { this.r.ellipse(this.cx, this.cy, this.rad, this.rad); }
}

class Rect extends Shape {
  constructor(r: Renderer, private x: number, private y: number,
              private w: number, private h: number) { super(r); }
  draw() {
    const { x, y, w, h } = this;
    this.r.polyline([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], true);
  }
}

class Triangle extends Shape {
  private pts: Point[];
  constructor(r: Renderer, a: Point, b: Point, c: Point) { super(r); this.pts = [a, b, c]; }
  draw() { this.r.polyline(this.pts, true); }
}

class Star extends Shape {
  constructor(r: Renderer, private cx: number, private cy: number,
              private outer: number, private inner: number, private points = 5) { super(r); }
  draw() {
    const pts: Point[] = [];
    for (let i = 0; i < this.points * 2; i++) {
      const rad = i % 2 === 0 ? this.outer : this.inner;
      const t = (Math.PI * i) / this.points - Math.PI / 2;
      pts.push([this.cx + rad * Math.cos(t), this.cy + rad * Math.sin(t)]);
    }
    this.r.polyline(pts, true);               // геометрія зірки — ОДИН раз на всі рушії
  }
}

class Scene {
  private r!: Renderer;
  constructor(r: Renderer, private shapes: Shape[]) { this.use(r); }
  use(r: Renderer) {                          // ← жива заміна рушія на льоту
    this.r = r;
    for (const s of this.shapes) s.r = r;
  }
  draw(w: number, h: number): string {
    this.r.begin(w, h);
    for (const s of this.shapes) s.draw();
    return this.r.end();
  }
}
```
```cpp
// ── Абстракція: ЩО малюємо (вісь 2) ───────────────────────────
class Shape {
public:
    Renderer* r;                              // ← МІСТ до реалізації
    explicit Shape(Renderer* r) : r(r) {}
    virtual void draw() = 0;
    virtual ~Shape() = default;
};

class Circle : public Shape {
    double cx, cy, rad;
public:
    Circle(Renderer* r, double cx, double cy, double rad)
        : Shape(r), cx(cx), cy(cy), rad(rad) {}
    void draw() override { r->ellipse(cx, cy, rad, rad); }
};

class Rect : public Shape {
    double x, y, w, h;
public:
    Rect(Renderer* r, double x, double y, double w, double h)
        : Shape(r), x(x), y(y), w(w), h(h) {}
    void draw() override {
        r->polyline({{x, y}, {x + w, y}, {x + w, y + h}, {x, y + h}}, true);
    }
};

class Triangle : public Shape {
    std::vector<Point> pts;
public:
    Triangle(Renderer* r, Point a, Point b, Point c) : Shape(r), pts{a, b, c} {}
    void draw() override { r->polyline(pts, true); }
};

class Star : public Shape {
    double cx, cy, outer, inner;
    int points;
public:
    Star(Renderer* r, double cx, double cy, double outer, double inner, int points = 5)
        : Shape(r), cx(cx), cy(cy), outer(outer), inner(inner), points(points) {}
    void draw() override {
        std::vector<Point> pts;
        for (int i = 0; i < points * 2; ++i) {
            double rad = (i % 2 == 0) ? outer : inner;
            double t = std::numbers::pi * i / points - std::numbers::pi / 2;
            pts.push_back({cx + rad * std::cos(t), cy + rad * std::sin(t)});
        }
        r->polyline(pts, true);               // геометрія зірки — ОДИН раз на всі рушії
    }
};

class Scene {
    Renderer* r;
    std::vector<std::unique_ptr<Shape>> shapes;
public:
    Scene(Renderer* r, std::vector<std::unique_ptr<Shape>> shapes)
        : shapes(std::move(shapes)) { use(r); }
    void use(Renderer* r) {                   // ← жива заміна рушія на льоту
        this->r = r;
        for (auto& s : shapes) s->r = r;
    }
    std::string draw(int w, int h) {
        r->begin(w, h);
        for (auto& s : shapes) s->draw();
        return r->end();
    }
};
```
:::

Ось той рядок, заради якого все затівалося: `t = math.pi * i / self.points - math.pi / 2`. Він тепер **один**. Не три копії в трьох класах із суфіксами, а одна істина в одному місці. Помилка з вістрям, що дивиться праворуч, тепер виправляється рівно раз — і одразу в SVG, у прев'ю і в обмірі.

## Жива заміна рушія на льоту

Тепер найцікавіше. Побудуймо сцену з чотирьох фігур на SVG-рушії, а потім **не чіпаючи жодної фігури** переведімо її на інший рушій:

:::tabs
```py
svg = SvgRenderer()
scene = Scene(svg, [
    Rect(svg, 2, 2, 76, 36),
    Circle(svg, 16, 20, 10),
    Triangle(svg, (40, 8), (50, 32), (30, 32)),
    Star(svg, 64, 20, 12, 5, 5),
])
print(scene.draw(80, 40))            # SVG

scene.use(AsciiRenderer())           # ← ті самі об'єкти фігур, інший носій
print(scene.draw(80, 40))            # прев'ю в терміналі

scene.use(StatsRenderer())
print(scene.draw(80, 40))            # обмір для тесту
```
```ts
const svg = new SvgRenderer();
const scene = new Scene(svg, [
  new Rect(svg, 2, 2, 76, 36),
  new Circle(svg, 16, 20, 10),
  new Triangle(svg, [40, 8], [50, 32], [30, 32]),
  new Star(svg, 64, 20, 12, 5, 5),
]);
console.log(scene.draw(80, 40));     // SVG

scene.use(new AsciiRenderer());      // ← ті самі об'єкти фігур, інший носій
console.log(scene.draw(80, 40));     // прев'ю в терміналі

scene.use(new StatsRenderer());
console.log(scene.draw(80, 40));     // обмір для тесту
```
```cpp
int main() {
    SvgRenderer svg;
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Rect>(&svg, 2, 2, 76, 36));
    shapes.push_back(std::make_unique<Circle>(&svg, 16, 20, 10));
    shapes.push_back(std::make_unique<Triangle>(&svg, Point{40, 8}, Point{50, 32}, Point{30, 32}));
    shapes.push_back(std::make_unique<Star>(&svg, 64, 20, 12, 5, 5));
    Scene scene(&svg, std::move(shapes));
    std::cout << scene.draw(80, 40) << '\n';    // SVG

    AsciiRenderer ascii;
    scene.use(&ascii);                          // ← ті самі об'єкти фігур, інший носій
    std::cout << scene.draw(80, 40) << '\n';    // прев'ю в терміналі

    StatsRenderer stats;
    scene.use(&stats);
    std::cout << scene.draw(80, 40) << '\n';    // обмір для тесту
}
```
:::

Перший вивід — SVG:

```
<svg viewBox="0 0 80 40" xmlns="http://www.w3.org/2000/svg">
  <polygon points="2.0,2.0 78.0,2.0 78.0,38.0 2.0,38.0" fill="none" stroke="black"/>
  <ellipse cx="16.0" cy="20.0" rx="10.0" ry="10.0" fill="none" stroke="black"/>
  <polygon points="40.0,8.0 50.0,32.0 30.0,32.0" fill="none" stroke="black"/>
  <polygon points="64.0,8.0 66.9,16.0 75.4,16.3 68.8,21.5 71.1,29.7 64.0,25.0 56.9,29.7 59.2,21.5 52.6,16.3 61.1,16.0" fill="none" stroke="black"/>
</svg>
```

Після `scene.use(AsciiRenderer())` ті самі чотири об'єкти дають уже це:

```
  #############################################################################
  #                                                                           #
  #                                                                           #
  #                                                                           #
  #                                                                           #
  #                                                                           #
  #                                     #                       #             #
  #                                     #                       #             #
  #          #######                   # #                     # #            #
  #        ##       ##                 # #                     # #            #
  #       #           #               ## ##                    # #            #
  #      #             #              #   #                   #   #           #
  #     #               #            ##   ##                  #   #           #
  #    #                 #           #     #                 #     #          #
  #    #                 #          ##     ##        #########     #########  #
  #   #                   #         #       #        ##                   ##  #
  #   #                   #         #       #         ##                 ##   #
  #   #                   #        #         #          #               #     #
  #   #                   #        #         #           ##           ##      #
  #   #                   #        #         #            ##         ##       #
  #   #                   #       #           #            #         #        #
  #   #                   #       #           #            #         #        #
  #    #                 #       ##           ##           #         #        #
  #    #                 #       #             #          #    ###    #       #
  #     #               #       ##             ##         #   ## ##   #       #
  #      #             #        #               #         # ##     ## #       #
  #       #           #        ##               ##       ####       ####      #
  #        ##       ##         #                 #       ##           ##      #
  #          #######           #                 #       #             #      #
  #                           #                   #                           #
  #                           #####################                           #
  #                                                                           #
  #                                                                           #
  #                                                                           #
  #                                                                           #
  #                                                                           #
  #############################################################################
```

А після `scene.use(StatsRenderer())` — рядок для тесту:

```
примітивів: 4; рамка: (2.0,2.0)–(78.0,38.0)
```

Три різні світи з одних і тих самих об'єктів. Зверни увагу, що саме сталося в `use()`: він пройшов списком і переписав полю `r` кожної фігури нове значення. Оце й усе перемикання — присвоєння посилання. Ніякого перестворення об'єктів, ніякої перекомпіляції, ніякого `if` за типом носія: фігура як не знала, що таке SVG, так і не знає, а виклик `self.r.ellipse(...)` потрапляє в потрібну реалізацію під час роботи. Спробуй зробити те саме в наївній версії — доведеться викинути всі об'єкти й побудувати їх наново з інших класів, бо там носій зашитий у сам тип.

## Скільки це коштує: поріг окупності

Тепер порахуймо чесно — з усіма типами, а не лише з тими, які зручно згадати. Наївно потрібен спільний інтерфейс `Drawable`, щоб сцена тримала різнорідний список, плюс клас на кожну пару. Мостом потрібні інтерфейс `Renderer`, база `Shape`, S фігур і R рушіїв. `Scene` є в обох варіантах, тож у порівнянні не бере участі:

```
наївно:  класів = S · R + 1
мостом:  класів = S + R + 2
```

Для нашого редактора S = 4, R = 3:

```
наївно:  4 · 3 + 1 = 13 типів,  реалізацій геометрії — 12
мостом:  4 + 3 + 2 =  9 типів,  реалізацій геометрії —  4
```

Але «13 проти 9» — не найцікавіше. Цікавіша умова, за якої міст узагалі вигідний. Він дешевший, коли:

```
S · R + 1  >  S + R + 2
S · R − S − R      >  1
S · R − S − R + 1  >  2
    (S − 1)(R − 1) >  2        ← поріг
```

Ця нерівність говорить речі, які варто вимовити вголос:

- **R = 1** — ліва частина дорівнює нулю й **ніколи** не перевищить двійку. Один-єдиний рушій — і міст не окупиться за жодної кількості фігур, хоч тисячу їх заведи. Вісь, у якої одне значення, — не вісь, а константа.
- **R = 2** — потрібно (S−1)·1 > 2, тобто **S ≥ 4**.
- **R = 3** — досить **S ≥ 3**.

**Умова: два рушії (SVG + ASCII), три фігури — чи ставити міст?**

```
S = 3, R = 2
поріг:  (S − 1)(R − 1) = 2 · 1 = 2
        2 > 2 — ХИБНО → не окупається

перевірка прямим рахунком:
  наївно:  3 · 2 + 1 = 7 типів
  мостом:  3 + 2 + 2 = 7 типів
  рівно — а міст ще й додає рівень непрямості

а тепер +1 фігура:  наївно 9, мостом 8   → міст попереду
     і ще +1 рушій:  наївно 13, мостом 9   → відрив росте
```

Висновок: на трьох фігурах і двох рушіях міст не платить за себе класами. Питання, отже, не «скільки в мене зараз», а «куди воно росте».

![Графік: класів проти кількості фігур S від одного до восьми при трьох рушіях. Червона крива наївного підходу S на R плюс один іде круто вгору через значення 4, 7, 10, 13, 16, 19, 22, 25. Зелена крива мосту S плюс R плюс два росте полого через 6, 7, 8, 9, 10, 11, 12, 13. Криві сходяться в точці сім на сім при двох фігурах; пунктирна вертикаль ділить графік — ліворуч наївно не дорожче, праворуч міст дешевший. Унизу праворуч рамка з умовою: поріг (S−1)(R−1) більше двох; при R рівному одиниці ліва частина нуль, тож міст не окупиться ніколи](img/bridge-crossover.svg)

*Дві прямі з різним нахилом: наївна росте зі швидкістю R класів на фігуру, мостова — одного класу на фігуру. Доки фігур мало, крутіша пряма ще нижча — саме тому міст на старті програє й саме тому його так часто ставлять зарано.*

І одразу застереження, без якого нерівність шкідлива: **класи — груба міра**. Вона рахує те, що легко порахувати, і мовчить про те, за що насправді платять. Навіть у точці «7 проти 7» міст уже виграє — бо реалізацій геометрії там 6 проти 3, і помилку в трикутнику наївно виправляють двічі, а мостом раз. Тож поріг (S−1)(R−1) > 2 читай як **нижню** межу: момент, коли міст вигідний навіть за найгрубішою мірою. За мірою дублювання він стає вигідним раніше.

## Те саме в справжньому рушії: QPainter і QPaintEngine

Іграшка іграшкою, але рівно так побудована графіка Qt — і подивитися на неї варто, бо вона відповідає на питання, які на нашому масштабі не встигають виникнути.

`QPainter` — абстракція, і її інтерфейс **багатий**: `drawLine`, `drawRect`, `drawEllipse`, `drawArc`, `drawChord`, `drawPie`, `drawRoundedRect`, `drawText`, `drawConvexPolygon` — десятки методів, бо це те, чим зручно користуватися.

`QPaintEngine` — реалізація. Документація Qt описує цей клас як абстрактне визначення того, як `QPainter` малює на заданому пристрої на заданій платформі, і інтерфейс тут **вузький і замкнений**: `drawPixmap` (чисто віртуальний), `drawEllipse`, `drawPath`, `drawPolygon`, `drawLines`, `drawRects`, `drawPoints`, `drawImage`, `drawTiledPixmap`, `drawTextItem`, плюс `begin`, `end` і `updateState`. Десятки методів `QPainter` зводяться до цього набору — точнісінько як наші чотири фігури до `polyline` та `ellipse`. Реалізацій Qt дає кілька: растрову (типову для віджетів на Windows, X11 і macOS), OpenGL і друк, а пристрій віддає свою реалізацію через `QPaintDevice::paintEngine()`.

Статус цього твердження варто назвати точно: слова «міст» документація Qt **не вживає** — вона описує механіку, а не патерн. Але структура тут буквально мостова: багата абстракція, вузька ієрархія реалізацій і посилання від першої до другої. Ім'я патерна — читання спільноти, не самоназва Qt.

І дві деталі, яких іграшка не показує.

**Перша — партії.** Придивись до сигнатур: не `drawLine(лінія)`, а `drawLines(масив, кількість)`; не `drawRect`, а `drawRects(масив, кількість)`. Множина тут не випадкова:

```cpp
// по одному примітиву за виклик: 10 000 прямокутників = 10 000 віртуальних викликів
struct PaintEngine {
    virtual void drawRect(const Rect& r) = 0;
    virtual ~PaintEngine() = default;
};

// як у Qt: партія за виклик — один віртуальний виклик на весь масив
struct PaintEngine {
    virtual void drawRects(const Rect* rects, int count) = 0;
    virtual ~PaintEngine() = default;
};
```

Спокуса пояснити це вартістю віртуального виклику — і вона хибна. Виклик крізь [таблицю віртуальних методів](topic:sf-devices/virtual-dispatch-cpp) коштує одиниці наносекунд; десять тисяч таких викликів — частки мілісекунди, ніщо на тлі самої растеризації. Платять не за диспетчеризацію, а за **розірвану партію**: рушій, якому дали масив, може один раз налаштувати стан, пройти дані суцільним проходом і віддати драйверові одну команду; рушієві, якого смикають по одному примітиву, лишається робити те саме десять тисяч разів — і жодного шансу на пакетну відправку в GPU. Міст проводить межу між абстракцією й реалізацією, і **гранулярність цієї межі** визначає, чи зможе реалізація бути швидкою. Проведеш межу по одному примітиву — назавжди відбереш у реалізації право на партію, і жодна оптимізація всередині рушія цього вже не поверне.

**Друга — нерівні реалізації.** У `QPaintEngine` є перелік `PaintEngineFeature` і метод `hasFeature()`: прапорці спроможностей — `Antialiasing`, `AlphaBlend`, `LinearGradientFill`, `RadialGradientFill`, `ConicalGradientFill`, `PorterDuff`, `PainterPaths`, `PixmapTransform`. Абстракція **питає** реалізацію, що та вміє, і має запасний хід: растровий рушій слугує резервом для рушіїв, яким певної спроможності бракує.

Це відповідь на найнеприємніше питання мосту: **що робити, коли реалізації нерівні?** Наш `StatsRenderer` вдало прикидається рівнею, бо ламану й еліпс «вміє» кожен. А от градієнт уміє SVG і не вміє ASCII. Наївний вихід — розширити інтерфейс до найбагатшого рушія, і тоді бідні реалізації повняться заглушками, які тихо нічого не роблять. Другий — обрізати до найбіднішого, і тоді багаті рушії стоять недовикористані. Qt іде третім шляхом: інтерфейс тримає **спільний мінімум**, а над ним — явні прапорці спроможностей і резервний рушій. Питати можна; вдавати — ні. Це варте того, щоб запам'ятати: щойно в мості з'являється операція, яку частина реалізацій «підтримує» порожнім тілом, — інтерфейс проведено не по тому місцю.

## Пастки

**Товстий інтерфейс реалізації — головна.** Тест простий: візьми свій `Renderer` і спитай, чи доведеться його чіпати, коли додаси фігуру. Якщо так — це не міст, а той самий вибух, розмазаний по двох файлах. Ознака в іменах: методи реалізації, названі за поняттями предметної області (`drawInvoice`, `exportUser`), — майже завжди помилка; методи, названі за можливостями носія (`polyline`, `write`, `flush`), — майже завжди правильно.

**Міст — не Стратегія.** Обидва тримають об'єкт полем і делегують йому; кістяк не розрізниш. Різниця не в коді, а в тому, **скільки боків росте**. [Стратегія](topic:sf-apps/strategy) підмінює алгоритм усередині однієї абстракції — сортування швидке чи стійке, стиснення сильне чи швидке: росте лише одна ієрархія, сторона стратегій, а клієнт лишається один. Міст ставлять тоді, коли ростуть **обидві** ієрархії й ростуть нарізно. Практичний тест: спитай, чи побільшає колись абстракцій. Якщо `Shape` — це назавжди один клас, а міняються тільки рушії, у тебе Стратегія, і називати її мостом — лише плутати наступного читача. Ім'я тут не косметика: воно каже, чого чекати від майбутнього коду.

**Хто зводить пару.** Розчепивши осі, ти переклав на когось обов'язок їх з'єднати: тепер `Circle` не створиш, не давши йому рушія. У прикладі це робить руками той, хто складає сцену, — на чотирьох фігурах терпимо. На тридцяти, та ще й коли рушій обирається за платформою, збирання розповзається по всьому коду, і кожне нове місце створення фігури мусить звідкись дістати правильний рушій. Класична відповідь — [фабрика](topic:sf-apps/factory-method) або [впровадження залежностей](topic:sf-apps/dependency-injection): один вузол знає, який рушій сьогодні, решта коду просто просить фігуру. Так само вчинили й у самому каталозі GoF: там віконна абстракція дістає свою реалізацію від абстрактної фабрики `WindowSystem`, а не будує сама. Міст майже завжди приходить у парі з чимось, що вирішує питання «яку реалізацію».

**Один рушій на всіх — і стан у ньому.** У робочому коді всі фігури сцени дивляться на **один** об'єкт рушія, і це навмисно: `AsciiRenderer` тримає сітку знаків, у яку домальовує кожна фігура. Але спільний змінний об'єкт одразу приносить свої правила. Порядок викликів стає значущим: хто малює пізніше, той перекриває. `begin`/`end` належать **сцені**, а не фігурі — фігура, яка сама покличе `begin`, зітре все намальоване до неї. Два потоки, що малюють у той самий рушій, зіпсують сітку. Це не вада мосту, а ціна того, що реалізація має стан, — але ціну треба бачити. Альтернатива, рушій без стану, що повертає рядок на кожен примітив, рятує від цього й одразу відбирає партії, про які йшлося вище. Вибір, а не істина.

**Спотворення носія лікують у реалізації.** Коло радіусом 10 у прев'ю виходить помітно витягнутим угору — знак у терміналі приблизно вдвічі вищий за свою ширину, тож рівна кількість клітин по X і по Y дає овал. Хто це виправляє? Не `Circle`: він не має права знати, що десь унизу знаки не квадратні. Виправляти має `AsciiRenderer` — усередині себе домножити X на два. Це загальне правило межі: тільки-но абстракція починає підправляти координати «бо ASCII», міст протік — і далі вона підправлятиме їх «бо принтер», «бо retina», доки не перетвориться на звалище знання про всі рушії одразу. Тоді осі зрощені знову, лише тихіше, ніж були в наївній версії.

**Непотрібний міст.** Найчастіша помилка — поставити міст там, де другої осі нема. Формула чесно каже: R = 1 → не окупиться ніколи. Якщо рушій сьогодні один і завтра один, `Shape` із полем `Renderer` — це рівень непрямості, за який платять усі читачі коду, а віддачі нема жодної: [YAGNI](topic:sf-apps/dry-kiss-yagni) тут не гасло, а арифметика. Міст ставлять, коли другу вісь **уже видно** — не «раптом колись знадобиться OpenGL», а «наступного кварталу виводимо на принтер, це вже в плані». І розчепити осі пізніше, коли друга справді з'явилася, — цілком нормальний хід: рефакторинг із S·R класів у S+R механічний, хай і нудний. А от прибрати непотрібний міст із коду, який уже обріс, значно важче — він устиг просочитися в кожне місце, де створюють фігуру, і тепер кожне з них передає рушій, який нікому не потрібен.
