// Один адаптер на БАГАТО джерел: поведінку «як дістати/покласти значення»
// вкладають ЗЗОВНІ — замикачами, а не новим підкласом.
class PluggableAdapter<S, T> {
  constructor(
    private subject: S,
    private get: (s: S) => T,
    private set: (s: S, v: T) => void,
  ) {}
  value(): T { return this.get(this.subject); }
  setValue(v: T): void { this.set(this.subject, v); }
}

// той самий клас пристосовує геть різні об'єкти — без підкласу на кожен:
const nameCell = new PluggableAdapter(person, p => p.fullName,
                                      (p, v) => { p.fullName = v; });
const tempCell = new PluggableAdapter(sensor, s => s.celsius,
                                      (s, v) => { s.celsius = v; });
