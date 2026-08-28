type Reading = { temp: number; humidity: number };

interface Observer {
  update(station: WeatherStation): void;
}

class WeatherStation {
  // Список у ПОРЯДКУ вставки: масив, не Set, — щоб порядок був стабільний
  // і передбачуваний. Дублікати відсікаємо самі при subscribe.
  private observers: Observer[] = [];

  private _reading: Reading = { temp: 0, humidity: 0 };

  // Запобіжник від повторного входу.
  private notifying = false;
  // Позначка, що поки ми сповіщали, стан змінився ще раз.
  private dirty = false;

  subscribe(o: Observer): void {
    if (!this.observers.includes(o)) this.observers.push(o);
  }

  unsubscribe(o: Observer): void {
    const i = this.observers.indexOf(o);
    if (i !== -1) this.observers.splice(i, 1);
  }

  private notify(): void {
    // 1. Прапорець реентрантності: якщо вже йде розсилка — не входимо
    //    вглиб, лише лишаємо мітку «є нові дані» й виходимо.
    if (this.notifying) {
      this.dirty = true;
      return;
    }
    this.notifying = true;
    try {
      // Зовнішній цикл добирає всі зміни, що накопичилися ПІД ЧАС розсилки.
      do {
        this.dirty = false;
        // 2. Копія списку: відписка/підписка з-під update() міняє
        //    this.observers, але не цей знімок — обхід не зламається.
        const snapshot = this.observers.slice();
        for (const o of snapshot) {
          // Пропускаємо тих, кого встигли відписати в цій-таки розсилці.
          if (!this.observers.includes(o)) continue;
          // 3. Ізоляція: чужий виняток не зриває розсилку решті.
          try {
            o.update(this);
          } catch (err) {
            console.error("Спостерігач кинув виняток, пропускаю:", err);
          }
        }
      } while (this.dirty);   // хтось змінив стан у ході — повторимо
    } finally {
      this.notifying = false; // ЗАВЖДИ знімаємо прапорець, навіть при збої
    }
  }

  // Публічні мутатори — єдині двері, крізь які стан змінюється.
  setReading(temp: number, humidity: number): void {
    this._reading = { temp, humidity };
    this.notify();
  }

  get reading(): Reading {
    return { ...this._reading };  // віддаємо копію, не внутрішнє посилання
  }
}
