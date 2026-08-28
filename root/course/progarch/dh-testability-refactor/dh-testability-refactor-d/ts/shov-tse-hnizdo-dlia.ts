class FakeSensor {                      // фейк: віддає задані виміри, один за одним
  private q: Reading[];
  constructor(...readings: Reading[]) { this.q = readings; }
  read(): Reading { return this.q.shift()!; }
}

class SpyHeater {                       // шпигун: нічого не гріє, лише пам'ятає виклики
  calls: string[] = [];
  on()  { this.calls.push("on"); }
  off() { this.calls.push("off"); }
}
