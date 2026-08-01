# ⚙️ Термостат у робочому коді: пасивне подання, тест без екрана й керівний контролер поряд

Пасивне подання легко переказати й важко зробити правильно. Щойно на екрані опиняється не одна цифра, а кілька речей, які мусять мінятися разом, головне рішення виявляється не в тому, які команди має контракт подання, а в тому, **коли і як презентер їх викликає**. Тож зберемо термостат цілком — модель, контракт екрана, презентер, справжнє подання, фальшивку й тест, що ганяє весь застосунок без жодного віджета, — а поряд поставимо той самий екран на керівному контролері й порахуємо, чого коштує кожен варіант.

## Задача: п'ять видимих фактів з одного числа

Екран з одним написом нічого не доводить: там будь-яка розкладка виглядає охайно. Відчути пасивне подання можна лише там, де з одного числа росте кілька видимих наслідків одразу.

```
Екран термостата:
  напис        «23°»                          ← бажана температура
  смужка       гарячий / спокійний / холодний колір
  кнопка «−»   згасла на 5°
  кнопка «+»   згасла на 30°
  рядок стану  «Тримає 23°» / «Вище не можна: 30°» / «Нижче не можна: 5°»

Правило моделі: бажана температура ∈ [5, 30], крок ±1.
Кольори:       > 24 → #c0392b   < 18 → #2457d6   інакше → #6b7280
```

П'ять фактів, і всі п'ять — функція від одного числа. Отут і живе цілий клас помилок, який не ловиться ні компілятором, ні винятком.

Уяви: тримали «+», доки не вперлися в стелю. Напис каже «30°», смужка почервоніла — а кнопка «+» жива, і внизу все ще «Тримає 29°». Нічого не впало, жоден виняток не полетів. Екран просто бреше, і бреше тихо.

Причина не в неуважності автора. Коли обробник події править поля поіменно, він щоразу мусить пригадати повний список наслідків. А список росте: додали режим «відпустка» — і кожен обробник має про нього дізнатися. Шляхів до екрана стає стільки, скільки подій помножити на поля, і забутого шляху не видно нізвідки — він не помилка, він просто відсутність рядка.

## Ідея: не латати поля, а малювати кадр

Тому в презентері має бути **рівно одна дорога до подання** — функція, що з поточного стану моделі виводить увесь видимий кадр. Кожна подія робить дві речі: просить модель змінитися і кличе цю функцію. Ніхто більше подання не торкається.

Тоді забути поле неможливо за побудовою: кадр або цілий, або його нема. Шляхів уже не «події × поля», а один; додаючи нову видиму річ, ти правиш одне місце й одразу бачиш усі її випадки поруч.

Здається марнотратним переписувати п'ять речей через одну змінену. Але екран міняється в людському темпі — кілька подій на секунду, — і п'ять присвоєнь на кожну з них не важать нічого. Якщо в кадрі колись з'явиться довгий список, дорогою стане робота віджета, а не рішення презентера; лікують це в поданні — порівняти й оновити точково, — не повертаючи рішень назад в обробники.

![Той самий дотик «+» на 29°: латка лишає два поля застарілими, кадр малює всі п'ять з одного числа](/book/programming/software-design/model-view-presenter/img/frame-vs-patch.svg)
*Ліворуч поля правили поіменно з обробника — цифра й колір оновилися, а кнопка «+» і рядок стану відстали; праворуч презентер вивів увесь кадр з одного `t = 30`, і відстати нема чому.*

Звідси й два правила для самого контракту подання, обидва з тієї самої причини — не пустити рішення назад у ту половину, якої тест не бачить.

**Команди говорять про екран, не про предмет.** `showTemperature(text)`, а не `show(thermostat)`: якщо в подання передати модель, воно мусить знати її будову й саме дібрати, що звідти показати, — і ця дрібна думка вже поза тестом. З тієї ж причини команда зветься `setPlusEnabled(false)`, а не `atMaximum(true)`: у другому випадку подання вирішує, як саме виглядає «на стелі», а це рішення — про те, що побачить людина.

**Рядки приїжджають готовими.** Не число з градусами, а вже складений напис «23°». Інакше формат — знак градуса, роздільник дробу, «°C» проти «°F» — живе у віджеті, і жоден тест його не звірить.

## Робочий код: модель, контракт, презентер

Модель нічого не знає про екран і сама стереже свою межу — обрізає значення, а не сподівається, що хтось перевірить до неї.

Пишемо двома мовами, якими такі екрани й пишуть: TypeScript — сьогоднішній клієнт, Java — дім цієї розкладки з часів Swing, GWT і раннього Android. Ідіоми різні, будова однакова.

:::tabs
```ts
// ── Модель: єдина, хто знає правило меж. Про екран — ані слова.
class Thermostat {
  static readonly MIN = 5;
  static readonly MAX = 30;
  private value = 22;

  get target(): number { return this.value; }

  nudge(delta: number): void {
    this.value = Math.max(Thermostat.MIN, Math.min(Thermostat.MAX, this.value + delta));
  }
}

// ── Контракт екрана: п'ять команд і один сигнал назовні.
interface ThermostatView {
  showTemperature(text: string): void;   // готовий рядок, не число
  showBarColor(hex: string): void;
  setMinusEnabled(on: boolean): void;
  setPlusEnabled(on: boolean): void;
  showStatus(text: string): void;
  onNudge(handler: (delta: number) => void): void;
}

const HOT = "#c0392b", COLD = "#2457d6", CALM = "#6b7280";

// ── Презентер: одна дорога до подання — render().
class ThermostatPresenter {
  constructor(
    private readonly view: ThermostatView,
    private readonly model: Thermostat,
  ) {}

  start(): void {
    this.view.onNudge(delta => {
      this.model.nudge(delta);   // межу обріже сама модель
      this.render();             // і одразу — свіжий кадр цілком
    });
    this.render();               // перший кадр малюємо самі, до будь-якого дотику
  }

  /** Увесь екран як функція від стану моделі. Інших шляхів до подання нема. */
  private render(): void {
    const t = this.model.target;
    this.view.showTemperature(`${t}°`);
    this.view.showBarColor(t > 24 ? HOT : t < 18 ? COLD : CALM);
    this.view.setMinusEnabled(t > Thermostat.MIN);
    this.view.setPlusEnabled(t < Thermostat.MAX);
    this.view.showStatus(
      t >= Thermostat.MAX ? `Вище не можна: ${t}°`
      : t <= Thermostat.MIN ? `Нижче не можна: ${t}°`
      : `Тримає ${t}°`);
  }
}
```
```java
import java.util.function.IntConsumer;

// ── Модель: єдина, хто знає правило меж. Про екран — ані слова.
final class Thermostat {
    static final int MIN = 5, MAX = 30;
    private int value = 22;

    int target() { return value; }

    void nudge(int delta) {
        value = Math.max(MIN, Math.min(MAX, value + delta));
    }
}

// ── Контракт екрана: п'ять команд і один сигнал назовні.
interface ThermostatView {
    void showTemperature(String text);   // готовий рядок, не число
    void showBarColor(String hex);
    void setMinusEnabled(boolean on);
    void setPlusEnabled(boolean on);
    void showStatus(String text);
    void onNudge(IntConsumer handler);
}

// ── Презентер: одна дорога до подання — render().
final class ThermostatPresenter {
    static final String HOT = "#c0392b", COLD = "#2457d6", CALM = "#6b7280";

    private final ThermostatView view;
    private final Thermostat model;

    ThermostatPresenter(ThermostatView view, Thermostat model) {
        this.view = view;
        this.model = model;
    }

    void start() {
        view.onNudge(delta -> {
            model.nudge(delta);   // межу обріже сама модель
            render();             // і одразу — свіжий кадр цілком
        });
        render();                 // перший кадр малюємо самі, до будь-якого дотику
    }

    /** Увесь екран як функція від стану моделі. Інших шляхів до подання нема. */
    private void render() {
        int t = model.target();
        view.showTemperature(t + "°");
        view.showBarColor(t > 24 ? HOT : t < 18 ? COLD : CALM);
        view.setMinusEnabled(t > Thermostat.MIN);
        view.setPlusEnabled(t < Thermostat.MAX);
        view.showStatus(t >= Thermostat.MAX ? "Вище не можна: " + t + "°"
                      : t <= Thermostat.MIN ? "Нижче не можна: " + t + "°"
                      : "Тримає " + t + "°");
    }
}
```
:::

Дві дрібниці в презентері варті окремого слова.

Підписка живе в `start()`, а не в конструкторі. По-перше, конструктор, що роздає посилання на ще недобудований об'єкт, — джерело дивних падінь. По-друге, підписці потрібна пара: те, що вмикається, колись доведеться вимкнути, і симетрична точка для цього має бути видима. По-третє, саме тут природно лягає **перший кадр**: якщо його не намалювати, екран стоїть порожній, доки людина чогось не натисне.

І презентер не будує собі подання — його приносять ззовні, у конструкторі. Це та сама [ін'єкція залежностей](book:programming/dependency-injection), і без неї весь задум не працює: тест не має де вставити свою реалізацію, якщо об'єкт створює її сам.

## Справжнє подання: жодного `if` на весь клас

Тепер найцікавіше — код екрана, який не має права ні на одну думку.

:::tabs
```ts
// Справжнє подання: тільки віджети. Ні арифметики, ні умов, ні складання рядків.
class ThermostatScreen implements ThermostatView {
  constructor(private readonly root: HTMLElement) {}

  private el<T extends HTMLElement>(cls: string): T {
    return this.root.querySelector<T>("." + cls)!;
  }

  showTemperature(text: string): void { this.el("temp").textContent = text; }
  showBarColor(hex: string): void     { this.el("bar").style.background = hex; }
  setMinusEnabled(on: boolean): void  { this.el<HTMLButtonElement>("minus").disabled = !on; }
  setPlusEnabled(on: boolean): void   { this.el<HTMLButtonElement>("plus").disabled = !on; }
  showStatus(text: string): void      { this.el("status").textContent = text; }

  onNudge(handler: (delta: number) => void): void {
    this.el("minus").addEventListener("click", () => handler(-1));
    this.el("plus").addEventListener("click", () => handler(+1));
  }
}
```
```java
import javax.swing.*;
import java.awt.*;
import java.util.function.IntConsumer;

// Справжнє подання: тільки віджети. Ні арифметики, ні умов, ні складання рядків.
final class ThermostatPanel extends JPanel implements ThermostatView {
    private final JLabel  temp   = new JLabel("", SwingConstants.CENTER);
    private final JPanel  bar    = new JPanel();
    private final JButton minus  = new JButton("−");
    private final JButton plus   = new JButton("+");
    private final JLabel  status = new JLabel("", SwingConstants.CENTER);

    public void showTemperature(String text) { temp.setText(text); }
    public void showBarColor(String hex)     { bar.setBackground(Color.decode(hex)); }
    public void setMinusEnabled(boolean on)  { minus.setEnabled(on); }
    public void setPlusEnabled(boolean on)   { plus.setEnabled(on); }
    public void showStatus(String text)      { status.setText(text); }

    public void onNudge(IntConsumer handler) {
        minus.addActionListener(e -> handler.accept(-1));
        plus.addActionListener(e -> handler.accept(+1));
    }
}
```
:::

Придивись до форми цього класу: кожен метод — один рядок, і в жодному нема ні умови, ні обчислення, ні склеювання рядка. Переклад типів дозволений — `Color.decode("#c0392b")` перетворює рядок на те, що вміє віджет, — але вибору кольору тут нема, колір уже приїхав готовим.

> 🔧 **Навіщо це.** З цього виходить перевірка, яку видно очима, без жодної теорії: **розгорни клас подання й пошукай у ньому `if`, арифметику й складання рядків**. Знайшов — рішення втекло назад у ту половину, яку тест не бачить, і саме там воно колись розійдеться з рештою екрана. Ця перевірка сувора рівно настільки, наскільки треба: у класі вище нема жодного `if`, і тому про саме подання нема чого питати — воно не може помилитися, бо йому нема де.

## Тест: увесь застосунок без жодного віджета

Фальшиве подання реалізує той самий контракт, але замість пікселів тримає **останній кадр** — п'ять полів, які презентер у нього поклав.

Те, що воно тримає саме кадр, а не журнал викликів, — рішення, а не дрібниця. Дублер, що записує послідовність викликів, робить тест чутливим до того, **як** презентер малює: переставив два рядки в `render()` — і тест червоний, хоча екран той самий. Дублер, що тримає стан, звіряє те, що людина побачила б. Це давня межа між перевіркою стану і перевіркою взаємодій — про те, коли доречна яка, є окремий розбір, [дублери як рішення дизайну](guide:progarch/test-doubles-when); для екрана майже завжди доречний стан.

:::tabs
```ts
// ── Фальшиве подання: не малює нічого, лише тримає останній кадр.
class FakeView implements ThermostatView {
  temp = ""; color = ""; status = "";
  minusEnabled = true; plusEnabled = true;
  press: (delta: number) => void = () => { throw new Error("ніхто не підписався на дотики"); };

  showTemperature(text: string) { this.temp = text; }
  showBarColor(hex: string)     { this.color = hex; }
  setMinusEnabled(on: boolean)  { this.minusEnabled = on; }
  setPlusEnabled(on: boolean)   { this.plusEnabled = on; }
  showStatus(text: string)      { this.status = text; }
  onNudge(handler: (delta: number) => void) { this.press = handler; }
}

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error("не збіглося: " + what);
}

function screenUnderTest(): FakeView {
  const view = new FakeView();
  new ThermostatPresenter(view, new Thermostat()).start();
  return view;
}

// 1. Кадр існує ще до першого дотику.
{
  const v = screenUnderTest();
  check(v.temp === "22°", "перший напис");
  check(v.status === "Тримає 22°", "перший рядок стану");
  check(v.plusEnabled && v.minusEnabled, "обидві кнопки живі посередині шкали");
}

// 2. Один дотик веде ввесь кадр, а не саму цифру.
{
  const v = screenUnderTest();
  v.press(+1);
  check(v.temp === "23°", "напис після «+»");
  check(v.color === CALM, "колір у спокійній зоні");
  check(v.status === "Тримає 23°", "рядок стану після «+»");
}

// 3. Стеля: модель не пускає далі, кнопка гасне, рядок стану міняє тон.
{
  const v = screenUnderTest();
  for (let i = 0; i < 20; i++) v.press(+1);   // 22 → 30, а далі нікуди
  check(v.temp === "30°", "напис на стелі");
  check(v.plusEnabled === false, "«+» на стелі згасла");
  check(v.minusEnabled === true, "«−» на стелі жива");
  check(v.status === "Вище не можна: 30°", "рядок стану на стелі");
  check(v.color === HOT, "колір на стелі");
}

console.log("усі перевірки пройшли — жодного віджета не створено");
```
```java
import java.util.function.IntConsumer;

// ── Фальшиве подання: не малює нічого, лише тримає останній кадр.
final class FakeView implements ThermostatView {
    String temp = "", color = "", status = "";
    boolean minusEnabled = true, plusEnabled = true;
    IntConsumer press = d -> { throw new IllegalStateException("ніхто не підписався на дотики"); };

    public void showTemperature(String text) { temp = text; }
    public void showBarColor(String hex)     { color = hex; }
    public void setMinusEnabled(boolean on)  { minusEnabled = on; }
    public void setPlusEnabled(boolean on)   { plusEnabled = on; }
    public void showStatus(String text)      { status = text; }
    public void onNudge(IntConsumer handler) { press = handler; }
}

final class PassiveViewDemo {
    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("не збіглося: " + what);
    }

    static FakeView screenUnderTest() {
        FakeView view = new FakeView();
        new ThermostatPresenter(view, new Thermostat()).start();
        return view;
    }

    public static void main(String[] args) {
        // 1. Кадр існує ще до першого дотику.
        FakeView v1 = screenUnderTest();
        check("22°".equals(v1.temp), "перший напис");
        check("Тримає 22°".equals(v1.status), "перший рядок стану");
        check(v1.plusEnabled && v1.minusEnabled, "обидві кнопки живі посередині шкали");

        // 2. Один дотик веде ввесь кадр, а не саму цифру.
        FakeView v2 = screenUnderTest();
        v2.press.accept(+1);
        check("23°".equals(v2.temp), "напис після «+»");
        check(ThermostatPresenter.CALM.equals(v2.color), "колір у спокійній зоні");
        check("Тримає 23°".equals(v2.status), "рядок стану після «+»");

        // 3. Стеля: модель не пускає далі, кнопка гасне, рядок стану міняє тон.
        FakeView v3 = screenUnderTest();
        for (int i = 0; i < 20; i++) v3.press.accept(+1);   // 22 → 30, а далі нікуди
        check("30°".equals(v3.temp), "напис на стелі");
        check(!v3.plusEnabled, "«+» на стелі згасла");
        check(v3.minusEnabled, "«−» на стелі жива");
        check("Вище не можна: 30°".equals(v3.status), "рядок стану на стелі");
        check(ThermostatPresenter.HOT.equals(v3.color), "колір на стелі");

        System.out.println("усі перевірки пройшли — жодного віджета не створено");
    }
}
```
:::

Перевірки тут навмисне голі — у справжньому проєкті це JUnit або Vitest, і від назви каркаса не міняється нічого. Важливе інше: третій випадок — рівно той, на якому ламається латання полів. Він проходить за мілісекунди, не піднімає вікна, не чекає анімації — його можна ганяти на складальному сервері, де графічної підсистеми немає зовсім.

І зверни увагу, чого тут **нема**: жодного `wait`, жодного пошуку кнопки за назвою, жодного скриншота. Тест звертається до застосунку тими самими словами, якими з ним говорить екран.

## Скільки коштує пасивність

Ціна пасивного подання — не такти, а рядки. Кожен видимий факт лишає слід у чотирьох місцях: команда в контракті, її реалізація у справжньому поданні, поле у фальшивці й рядок у `render()`.

```
Один видимий факт ≈ 4 рядки «водопроводу»:
  контракт        showStatus(text)
  подання         status.setText(text)
  фальшивка       this.status = text
  render()        view.showStatus(...)

Наш екран: 5 фактів → ≈ 20 рядків, з яких жоден нічого не вирішує.
```

Це і є та балакучість, за яку пасивне подання лають. Помнож на форму з тридцятьма полями — і водопровід стане більшим за логіку.

Тут же й межа розумного розміру контракту. П'ять команд читаються з одного погляду; сорок означають, що екран робить забагато, і фальшивку до нього ліньки писати навіть тим, хто любить тести. Знак, що екран пора ділити на частини — кожна зі своїм контрактом і своїм презентером, — з'являється раніше, ніж здається.

## Той самий екран на керівному контролері

Керівний контролер торгує частиною цієї балакучості. Просте — те, що є прямим відбитком одного поля моделі, — подання бере на себе; складне лишається презентерові.

Щоб подання могло взяти цифру саме, модель мусить уміти сказати «я змінилася» — тобто стати спостережуваною, з підпискою в дусі [спостерігача](book:programming/observer). Стала ниточка «цей напис завжди показує це число» і зветься [прив'язкою даних](book:programming/data-binding).

```ts
// Модель тепер сама повідомляє про зміну — без цього прив'язки не буває.
class ObservableThermostat extends Thermostat {
  private readonly listeners: Array<() => void> = [];

  onChange(listener: () => void): void { this.listeners.push(listener); }

  nudge(delta: number): void {
    const before = this.target;
    super.nudge(delta);
    if (this.target !== before) this.listeners.forEach(fn => fn());
  }
}

// Контракт екрана схуд: цифру презентер більше не диктує.
interface SupervisedView {
  showBarColor(hex: string): void;
  setMinusEnabled(on: boolean): void;
  setPlusEnabled(on: boolean): void;
  showStatus(text: string): void;
  onNudge(handler: (delta: number) => void): void;
}

// Подання само тримає ниточку від числа моделі до напису.
class BoundThermostatScreen extends ThermostatScreen implements SupervisedView {
  constructor(root: HTMLElement, model: ObservableThermostat) {
    super(root);
    const paint = () => this.showTemperature(`${model.target}°`);
    model.onChange(paint);
    paint();
  }
}

// Презентер лишає собі тільки те, де є що вирішувати.
class SupervisingController {
  constructor(
    private readonly view: SupervisedView,
    private readonly model: Thermostat,
  ) {}

  start(): void {
    this.view.onNudge(delta => { this.model.nudge(delta); this.render(); });
    this.render();
  }

  private render(): void {
    const t = this.model.target;
    this.view.showBarColor(t > 24 ? HOT : t < 18 ? COLD : CALM);
    this.view.setMinusEnabled(t > Thermostat.MIN);
    this.view.setPlusEnabled(t < Thermostat.MAX);
    this.view.showStatus(
      t >= Thermostat.MAX ? `Вище не можна: ${t}°`
      : t <= Thermostat.MIN ? `Нижче не можна: ${t}°`
      : `Тримає ${t}°`);
  }
}
```

Порахуймо чесно, що змінилося.

| що міряємо | пасивне подання | керівний контролер |
|---|---|---|
| команд у контракті | 5 | 4 |
| фактів, які бачить тест із фальшивкою | 5 з 5 | 4 з 5 |
| хто зв'язує напис із числом | презентер, щоразу вручну | прив'язка, раз назавжди |
| що додалося натомість | — | спостережувана модель і сама прив'язка |
| що може розійтися тихо | нічого: кадр цілий | напис — і тест цього не побачить |

Висновок виходить не той, якого чекаєш. На **одному** прямому полі прив'язка коштує більше, ніж заощаджує: підписка в моделі й ниточка в поданні — це більше коду, ніж один рядок у `render()`. Вигравати вона починає тоді, коли збігаються дві умови: прямих полів десяток і каркас дає прив'язку задарма — тоді ти не пишеш ні підписки, ні ниточки, а платиш лише тим, що ці поля зникають з-під тесту. Доведена до кінця, ця торгівля стає окремою розкладкою — [MVVM](book:programming/model-view-viewmodel), де прив'язок стільки, що презентер перетворюється на об'єкт, з якого екран сам себе читає.

Ознака, за якою ділити, коротка: **прив'язуй те, у чому нема жодного `if`**. Прямий, безумовний відбиток одного поля — віддай поданню. Усе, де є поріг, умова, вибір слова чи формату, який колись перепишуть, — лишай презентерові, бо саме це й ламається, і саме це має бачити тест.

## Луна: подання чує власний голос

Тепер додай на екран поле, куди температуру можна ввести руками. У контракті з'явиться пара:

```
showTargetField(text: string)                  // презентер кладе значення в поле
onTargetTyped(handler: (text: string) => void) // поле доповідає, що там набрали
```

І тут пасивне подання показує свою найпідступнішу пастку. `render()` кладе в поле «23». Віджет чесно повідомляє: «текст змінився». Обробник вирішує, що це людина набрала, просить модель змінитися, кличе `render()`, той знову кладе текст у поле — і так, доки не скінчиться стек.

![Коло луни: render кладе текст у поле, поле повідомляє про зміну, обробник знову кличе render](/book/programming/software-design/model-view-presenter/img/echo-loop.svg)
*Коло замикається тому, що віджет не розрізняє, хто змінив текст — людина чи презентер. Сторож усередині подання розриває коло: поки подання пише саме, воно мовчить.*

Найгірше в цій пастці те, що вона залежить від платформи. У Swing `setText()` міняє документ поля, а разом з ним будить `DocumentListener` — програмна зміна нічим не відрізняється від набраної. У WinForms присвоєння `Text` піднімає `TextChanged`; від нескінченного кола там часом рятує оптимізація «те саме значення — події нема», але спиратися на неї не можна, бо варто формату злегка змінитися — і вона перестає рятувати. А в браузері `input.value = "23"` не піднімає ні `input`, ні `change`: DOM навмисне розрізняє зміну від людини й зміну з коду. Той самий на вигляд правильний презентер в одному середовищі працює, а в іншому падає зі стеком.

Лікують це в поданні, і саме там, де хвороба:

```java
final class TargetField {                      // усередині подання
    private final JTextField field = new JTextField();
    private boolean pushing = false;           // «зараз пишу я, а не людина»

    void show(String text) {
        pushing = true;
        try { field.setText(text); }
        finally { pushing = false; }
    }

    void onTyped(Consumer<String> handler) {
        field.getDocument().addDocumentListener(new TextChangeListener(() -> {
            if (!pushing) handler.accept(field.getText());   // луну назовні не пускаємо
        }));
    }
}
```

Прапорець мусить жити в поданні, не в презентері. Це властивість віджета, а не логіки; винесеш його в презентер — і фальшивці доведеться вдавати ще й цю дивину, а презентер почне знати, на чому його малюють. Контракт від цього не міняється зовсім: назовні подання й далі просто виконує команду й доповідає про те, що зробила людина.

## Кадр б'є по руках: каретка й фокус

Друга пастка росте з тієї самої правильної звички малювати весь кадр. Людина набирає в полі «2», презентер відповідає кадром і кладе туди своє значення — каретка стрибає в кінець, а половина набраного зникає. У Swing `setText()` заміняє вміст документа цілком; у браузері присвоєння `value` робить те саме.

Правило просте: **не перемальовуй те, що зараз у руках людини**. Перевірку ставлять у поданні, поруч із віджетом:

```ts
showTargetField(text: string): void {
  const input = this.el<HTMLInputElement>("target");
  if (document.activeElement === input) return;   // поле зараз у людини — не чіпаємо
  input.value = text;
}
```

Формально це `if` у поданні — і правило «жодного `if`» ніби порушене. Насправді ні: заборонені рішення про те, **що** показати, а тут вирішується, чи безпечно взагалі торкатися віджета зараз. Це знання про віджет, а не про предмет, і жити воно має саме тут.

## Презентер переживає екран

Підписка без пари рано чи пізно кусає. На Android екран помирає від повороту телефона, у настільному застосунку — коли закрили вкладку; а презентер живе далі, бо на нього хтось посилається. Звідси два лиха одразу: презентер тримає ціле дерево віджетів, і воно не збирається сміттярем, а перший же кадр після смерті екрана малюється в порожнечу.

Тому підписка має віддавати спосіб від неї відмовитися, а презентер — мати `stop()`, симетричний до `start()`:

```ts
interface ThermostatView {
  // …команди…
  onNudge(handler: (delta: number) => void): () => void;   // повертає «відписатися»
}

class ThermostatPresenter {
  private off: (() => void) | null = null;

  start(): void {
    this.off = this.view.onNudge(delta => { this.model.nudge(delta); this.render(); });
    this.render();
  }

  stop(): void {
    this.off?.();     // відпустили подання: ні подій звідти, ні посилань на нього
    this.off = null;
  }
}
```

`stop()` кличе той, хто володіє екраном, у мить його смерті. А `this.off === null` заодно стає простою відповіддю на питання «чи є ще куди малювати» — і ця відповідь знадобиться зараз же.

## Коли модель повільна, кадр обростає станами

Дотягни задачу до правди: справжній термостат не міняє число в пам'яті, а посилає команду котлові по мережі. Виклик стає повільним і може не вдатися — отже, на екрані з'являються ще два стани, «чекаємо» і «не вийшло». Робота з таким викликом — звичайне [асинхронне очікування](book:programming/async-await), і в презентері воно виглядає так:

```ts
private token = 0;                       // мітка найсвіжішого дотику
private busy = false;
private error: string | null = null;

private async nudge(delta: number): Promise<void> {
  const mine = ++this.token;
  this.busy = true; this.error = null;
  this.render();                         // кадр «надсилаю…» — одразу, ще до відповіді
  try {
    await this.model.nudge(delta);       // тут — розмова з котлом
  } catch {
    if (mine === this.token) this.error = "Котел не відповідає";
  }
  if (mine !== this.token) return;       // поки чекали, встиг новіший дотик — цей кадр застарів
  if (!this.off) return;                 // екран уже закрили — малювати нікуди
  this.busy = false;
  this.render();
}
```

Дві перевірки перед останнім кадром — не перестраховка, а два справжні випадки. Людина тисне «+» двічі поспіль; відповіді приходять у будь-якому порядку, і без мітки повільніша перша відповідь затре собою свіжішу другу. А закритий екран — це те саме `stop()`: відповідь, що приїхала після смерті подання, малювати нікуди.

Далі найважливіше. Обидва нові стани не розповзаються по обробниках — вони просто входять у кадр:

```ts
private render(): void {
  const t = this.model.target;
  this.view.showTemperature(`${t}°`);
  this.view.showBarColor(t > 24 ? HOT : t < 18 ? COLD : CALM);
  this.view.setMinusEnabled(!this.busy && t > Thermostat.MIN);
  this.view.setPlusEnabled(!this.busy && t < Thermostat.MAX);
  this.view.showStatus(
    this.busy ? "Надсилаю…"
    : this.error ?? (t >= Thermostat.MAX ? `Вище не можна: ${t}°`
                   : t <= Thermostat.MIN ? `Нижче не можна: ${t}°`
                   : `Тримає ${t}°`));
}
```

Один стан — одна правка в одній функції, і всі його наслідки видно поруч. А тест дістає новий випадок задарма: підсунь моделі повільну відповідь, звір кадр «надсилаю…» з погашеними кнопками, дай відповіді приїхати — і звір кадр після неї. Так само без вікна, без циклу подій і без жодного віджета.
