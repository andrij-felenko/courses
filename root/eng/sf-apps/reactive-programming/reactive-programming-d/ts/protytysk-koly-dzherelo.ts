interface Subscription {
  request(n: number): void;   // споживач: «готовий прийняти ще n»
  cancel(): void;
}

interface Subscriber<T> {
  onSubscribe(sub: Subscription): void;
  onNext(value: T): void;
  onComplete(): void;
  onError(e: unknown): void;
}

// повільний споживач: бере по одному, обробляє, лише тоді просить наступне
const slowConsumer: Subscriber<number> = {
  onSubscribe(sub) {
    this.sub = sub;
    sub.request(1);                 // спершу прошу лише одне
  },
  onNext(value) {
    heavyProcess(value);            // повільна робота
    this.sub!.request(1);           // осилив — тепер прошу ще одне
  },
  onComplete() { console.log("готово"); },
  onError(e) { console.error(e); },
} as Subscriber<number> & { sub?: Subscription };
