class FreshnessGuard implements Sensor {   // обгортка над портом Sensor — той самий інтерфейс
  private last: number | null = null;      // останнє число, якому повірили
  private same = 0;                        // скільки разів ПОСПІЛЬ воно повторилось
  constructor(private inner: Sensor, private staleAfter = 3) {}

  read(): Reading {
    const r = this.inner.read();
    if (!r.ok) { this.same = 0; return r; }   // уже чесний збій — лічильник з нуля
    this.same = r.celsius === this.last ? this.same + 1 : 0;
    this.last = r.celsius;
    if (this.same >= this.staleAfter)         // застій переріс дозволене → «не вірю»
      return { celsius: r.celsius, ok: false };
    return r;
  }
}
