// Спільний контракт: усе, що вміє винести вирок про одну вісь системи.
interface Verdict {
  readonly passed: boolean;
  readonly detail: string;               // куди дивитися, коли не пройшло
}

interface FitnessFunction {
  readonly name: string;
  readonly axis: string;                 // яку вісь системи стереже
  run(): Verdict | Promise<Verdict>;     // синхронна (структура) чи асинхронна (вимір)
}
