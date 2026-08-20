# ⚙️ Децукрування async/await: побудова скінченного автомата корутини

Ключові слова `async` та `await` не змінюють архітектуру системного циклу подій. Вони є компіляторною трансформацією — синтаксичним цукром, що перетворює лінійний текст процедури на низькорівневий безстековий скінченний автомат (англ. *stackless finite state machine*).

Ця трансформація виконується на етапі компіляції (у C#, Rust, C++20) або всередині рушія віртуальної машини (V8 у Node.js/Chromium, SpiderMonkey у Firefox). Розуміння внутрішньої будови автомата дозволяє точно передбачати накладні витрати на виділення пам'яті, поведінку винятків та відстежувати приховані витоки ресурсів у високонавантажених асинхронних сервісах.

## Задача: асинхронне завантаження та підсумовування

Розглянемо типову бізнес-задачу: завантажити профіль клієнта за ідентифікатором, отримати список його рахунків, послідовно прочитати залишок на кожному рахунку та підсумувати баланс. У разі збою мережі операція повинна перехопити помилку та повернути безпечне значення за замовчуванням.

У високорівневому синтаксисі `async/await` код виглядає оманливо просто, приховуючи складну механіку розриву стеку:

```ts
async function calculateTotalBalance(userId: string): Promise<number> {
  try {
    const profile = await fetchProfile(userId);
    let total = 0;
    for (const accId of profile.accountIds) {
      const balance = await fetchAccountBalance(accId);
      total += balance;
    }
    return total;
  } catch (err) {
    console.error("Помилка розрахунку:", err);
    return 0;
  }
}
```

Для програміста цей фрагмент читається як суцільна послідовність дій. Проте для процесора цей код не може бути виконаний як звичайна функція: між рядком запиту профілю та рядком ініціалізації циклу минають десятки мілісекунд очікування мережевої відповіді, під час яких системний потік зобов'язаний обслуговувати інші запити.

## Анатомія компіляторного децукрування

Щоб виконати цей код неблокуючим чином, компілятор розбирає синтаксичне дерево функції (AST) та генерує три фундаментальні низькорівневі структури:

### 1. Кадр корутини у динамічній пам'яті (Heap Frame)

У звичайній функції локальні змінні (`profile`, `total`, `accId`, індекс циклу `i`) розміщуються на системному стеку процесора у межах одного стекового кадру (stack frame). Проте коли функція зустрічає `await`, вона змушена повернути керування викликачу негайно. Стековий кадр безповоротно знищується.

Щоб локальні змінні пережили розмотування стеку, компілятор виносить їх у спеціальний об'єкт у купі (Heap Frame). Розмір цього кадру фіксується під час компіляції й містить:
- Поточний стан автомата (`state: number`).
- Вхідні аргументи функції (`userId`).
- Усі локальні змінні, час життя яких перетинає бодай одну точку `await`.
- Посилання на обіцянку (Promise/Future), яку функція віддала зовнішньому викликачу при першому призупиненні.
- Вказівники на контексти перехоплення винятків (таблиця блоків `try/catch`).

### 2. Розрізання графа потоку керування (Control Flow Slicing)

Компілятор розрізає тіло процедури у кожній точці призупинення `await`. Кожен неподільний сегмент коду між двома очікуваннями перетворюється на окрему гілку `case` у числовому автоматі переходів:
- **Стан 0 (Start)**: вхід у функцію, валідація аргументів, ініціація запиту `fetchProfile`. Перехід у стан 1 та миттєвий вихід (`yield / return`).
- **Стан 1 (AfterProfile)**: обробка отриманого профілю, ініціалізація лічильника `total = 0` та перевірка умови входу в цикл `for`. Якщо масив порожній — прямий перехід до фіналу; якщо ні — запуск `fetchAccountBalance` для першого рахунку, перехід у стан 2 та вихід.
- **Стан 2 (AfterBalance)**: додавання отриманого балансу до накопичувача `total`, збільшення індексу циклу, перевірка наступної ітерації. Якщо рахунки ще є — повторний запит і повернення в стан 2; якщо масив вичерпано — перехід у фінальний стан.
- **Стан 3 (Completed)**: завершення роботи, передача результату в зовнішній проміс через `resolve(total)`.

### 3. Диспетчер відновлення (Resume Dispatcher)

Автомат містить єдину точку входу — метод `resume(value, error)`. Саме цей метод передається як зворотний виклик у чергу мікрозадач або внутрішній колбек підвішеного проміса. Коли мережевий сокет отримує відповідь, цикл подій викликає `resume`, передаючи отримані байти або об'єкт помилки, а перемикач `switch (state)` миттєво спрямовує виконання до потрібного фрагмента коду.

## Робоча реалізація автомата станів

Нижче наведено децукровану версію мовами TypeScript та C++. Кожен приклад містить повну структуру кадру стану, диспетчеризацію кроків та обробку збоїв без використання ключових слів `async/await`.

:::tabs
```ts
// Стан автомата корутини
enum State {
  Start = 0,
  AfterProfile = 1,
  AfterBalance = 2,
  Completed = 3
}

class CalculateTotalBalanceStateMachine {
  // Кадр збереження локального стану (Heap Frame)
  public state: State = State.Start;
  private userId: string;
  private profile: { accountIds: string[] } | null = null;
  private total: number = 0;
  private loopIndex: number = 0;

  // Вихідний проміс для повернення результату викликачу
  public promise: Promise<number>;
  private resolve!: (val: number) => void;
  private reject!: (err: unknown) => void;

  constructor(userId: string) {
    this.userId = userId;
    this.promise = new Promise<number>((res, rej) => {
      this.resolve = res;
      this.reject = rej;
    });
  }

  // Головний крок виконання автомата (Resume Dispatcher)
  public resume(result?: unknown, error?: unknown): void {
    try {
      if (error) {
        // Якщо надійшла помилка від асинхронної дії — переходимо в блок catch
        throw error;
      }

      while (this.state !== State.Completed) {
        switch (this.state) {
          case State.Start: {
            this.state = State.AfterProfile;
            const promise = fetchProfile(this.userId);
            // Призупинення: підписуємо наш же автомат на продовження
            promise.then(
              (res) => this.resume(res, undefined),
              (err) => this.resume(undefined, err)
            );
            return; // Звільняємо системний потік для циклу подій
          }

          case State.AfterProfile: {
            this.profile = result as { accountIds: string[] };
            this.total = 0;
            this.loopIndex = 0;
            this.state = State.AfterBalance;

            // Перевірка умови циклу
            if (this.loopIndex >= this.profile.accountIds.length) {
              this.state = State.Completed;
              this.resolve(this.total);
              return;
            }

            const accId = this.profile.accountIds[this.loopIndex];
            const promise = fetchAccountBalance(accId);
            promise.then(
              (res) => this.resume(res, undefined),
              (err) => this.resume(undefined, err)
            );
            return;
          }

          case State.AfterBalance: {
            const balance = result as number;
            this.total += balance;
            this.loopIndex++;

            // Наступна ітерація або завершення циклу
            if (this.loopIndex < this.profile!.accountIds.length) {
              const nextAccId = this.profile!.accountIds[this.loopIndex];
              const promise = fetchAccountBalance(nextAccId);
              promise.then(
                (res) => this.resume(res, undefined),
                (err) => this.resume(undefined, err)
              );
              return;
            }

            this.state = State.Completed;
            this.resolve(this.total);
            return;
          }
        }
      }
    } catch (err) {
      // Імітація блоку catch(err)
      console.error("Помилка розрахунку в автоматі:", err);
      this.state = State.Completed;
      this.resolve(0); // Безпечне значення за замовчуванням
    }
  }
}

// Функція-обгортка для виклику децукрованого автомата
function calculateTotalBalanceDesugared(userId: string): Promise<number> {
  const machine = new CalculateTotalBalanceStateMachine(userId);
  machine.resume(); // Запуск першого кроку
  return machine.promise;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <functional>
#include <exception>

// Числові стани автомата корутини
enum class State {
    Start = 0,
    AfterProfile = 1,
    AfterBalance = 2,
    Completed = 3
};

struct Profile {
    std::vector<std::string> accountIds;
};

// Сигнатури асинхронних неблокуючих сервісів
void asyncFetchProfile(const std::string& userId, 
                       std::function<void(const Profile&)> onSuccess,
                       std::function<void(std::exception_ptr)> onError);

void asyncFetchAccountBalance(const std::string& accId, 
                              std::function<void(double)> onSuccess,
                              std::function<void(std::exception_ptr)> onError);

// Кадр корутини у динамічній пам'яті (Heap Frame)
class CalculateTotalBalanceFrame : public std::enable_shared_from_this<CalculateTotalBalanceFrame> {
public:
    State state = State::Start;
    std::string userId;
    Profile profile;
    double total = 0.0;
    size_t loopIndex = 0;

    std::function<void(double)> onComplete;
    std::function<void(std::exception_ptr)> onFailure;

    explicit CalculateTotalBalanceFrame(std::string id,
                                        std::function<void(double)> onComp,
                                        std::function<void(std::exception_ptr)> onFail)
        : userId(std::move(id)), onComplete(std::move(onComp)), onFailure(std::move(onFail)) {}

    void resumeSuccessProfile(const Profile& p) {
        profile = p;
        state = State::AfterProfile;
        step();
    }

    void resumeSuccessBalance(double balance) {
        total += balance;
        loopIndex++;
        state = State::AfterBalance;
        step();
    }

    void resumeError(std::exception_ptr ex) {
        // Імітація обробника catch
        std::cerr << "Помилка розрахунку балансу (перехоплено в автоматі)\n";
        state = State::Completed;
        if (onComplete) {
            onComplete(0.0); // Повернення безпечного значення за замовчуванням
        }
    }

    void step() {
        try {
            switch (state) {
                case State::Start: {
                    auto self = shared_from_this();
                    asyncFetchProfile(userId,
                        [self](const Profile& p) { self->resumeSuccessProfile(p); },
                        [self](std::exception_ptr ex) { self->resumeError(ex); }
                    );
                    return; // Призупинення, вихід з поточного виклику
                }

                case State::AfterProfile:
                case State::AfterBalance: {
                    if (loopIndex < profile.accountIds.size()) {
                        const std::string& accId = profile.accountIds[loopIndex];
                        auto self = shared_from_this();
                        asyncFetchAccountBalance(accId,
                            [self](double bal) { self->resumeSuccessBalance(bal); },
                            [self](std::exception_ptr ex) { self->resumeError(ex); }
                        );
                        return; // Призупинення до відповіді на наступний рахунок
                    }

                    // Усі рахунки успішно опрацьовано
                    state = State::Completed;
                    if (onComplete) {
                        onComplete(total);
                    }
                    return;
                }

                case State::Completed:
                    return;
            }
        } catch (...) {
            resumeError(std::current_exception());
        }
    }
};

void runDesugaredBalanceCalculation(const std::string& userId,
                                   std::function<void(double)> callback) {
    auto frame = std::make_shared<CalculateTotalBalanceFrame>(
        userId, std::move(callback), nullptr
    );
    frame->step();
}
```
:::

## Покрокове простеження виконання (Trace Walkthrough)

Щоб наочно побачити, як кадр автомата мандрує в часі крізь чергу циклу подій, простежимо виконання сценарію для користувача з двома рахунками `["acc_A", "acc_B"]`:

1. **Тік 0 (Синхронний старт)**:
   - Створюється екземпляр `CalculateTotalBalanceStateMachine` у купі.
   - `state = State.Start`, `userId = "u_101"`.
   - Викликається `resume()`. Стан змінюється на `AfterProfile`.
   - Запускається мережевий виклик `fetchProfile("u_101")`.
   - Метод повертає управління викликачу з незрілим `Promise<number>`.
   - Фізичний стек процесора повністю звільняється. Потік вільний.

2. **Тік 1 (Через 30 мс, прихід профілю)**:
   - Мережевий сокет сигналізує про готовність даних.
   - Цикл подій викликає зворотний виклик `resume({ accountIds: ["acc_A", "acc_B"] })`.
   - Перемикач `switch` потрапляє у гілку `case State.AfterProfile`.
   - Змінна `total` ініціалізується нулем, `loopIndex = 0`.
   - Ініціюється запит балансу першого рахунку `fetchAccountBalance("acc_A")`.
   - `state` стає `AfterBalance`. Автомат знову виконує вихід із потоку.

3. **Тік 2 (Через 20 мс, баланс рахунку A = 150)**:
   - Цикл подій викликає `resume(150)`.
   - Перемикач потрапляє у `case State.AfterBalance`.
   - `total` стає `150`, `loopIndex` збільшується до `1`.
   - Оскільки `loopIndex < 2`, автомат читає `acc_B` і запускає `fetchAccountBalance("acc_B")`.
   - Вихід із потоку.

4. **Тік 3 (Через 25 мс, баланс рахунку B = 250)**:
   - Цикл подій викликає `resume(250)`.
   - `total` стає `400`, `loopIndex` стає `2`.
   - Умова `loopIndex < 2` хибна. Цикл завершено.
   - `state` стає `Completed`. Викликається `this.resolve(400)`.
   - Зовнішній проміс переходить у стан `fulfilled`, повідомляючи клієнта.
   - Кадр автомата більше ніким не утримується і видаляється збирачем сміття (Garbage Collector).

## Архітектурні підводні камені децукрування

Знання структури автомата захищає від трьох типових системних проблем:

1. **Приховані витоки пам'яті через підвислі проміси**: якщо будь-яка проміжна асинхронна функція (наприклад, `fetchAccountBalance`) зависає через втрату мережевого пакета і не має встановленого тайм-ауту, кадр корутини залишається у пам'яті навічно. Оскільки він утримує посилання на всі локальні змінні, виникає поступове вичерпання оперативної пам'яті сервера.
2. **Тиск на збирач сміття (GC Pressure)**: у високочастотних сервісах створення об'єкта кадру на кожен мікрозапит породжує мільйони короткоживучих алокацій у динамічній пам'яті. У C++20 корутинах компілятор застосовує оптимізацію HALO (Heap Allocation Elision Optimization), щоб замінити купу стеком, якщо час життя корутини строго вкладений у викликача, проте у динамічних мовах (JS/Python) алокація в купі є неминучою платою за асинхронність.
3. **Неможливість збереження регістрів процесора**: оптимізатор компілятора не може утримувати гарячі змінні у швидких регістрах CPU крізь виклики `await`. Перед кожною паузою всі регістрові змінні обов'язково скидаються у поля структури кадру в оперативній пам'яті.
