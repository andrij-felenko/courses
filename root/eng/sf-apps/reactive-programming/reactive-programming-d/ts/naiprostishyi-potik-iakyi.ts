type Observer<T> = {
  next: (value: T) => void;       // нове значення
  complete: () => void;           // потік вичерпано
  error: (e: unknown) => void;    // потік зламався
};

// потік = функція, що приймає спостерігача й починає його годувати
type Stream<T> = (observer: Observer<T>) => () => void;   // повертає «відписку»

// джерело: штовхає 0,1,2,... кожні ms мілісекунд
function interval(ms: number): Stream<number> {
  return (observer) => {
    let n = 0;
    const id = setInterval(() => observer.next(n++), ms);
    return () => clearInterval(id);   // виклич це, щоб зупинити потік
  };
}

const stop = interval(1000)({
  next: (n) => console.log("тік", n),
  complete: () => console.log("кінець"),
  error: (e) => console.error(e),
});
// stop();  // відписка — джерело замовкне
