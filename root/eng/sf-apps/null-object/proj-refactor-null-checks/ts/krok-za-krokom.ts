const FREE: Subscription = new FreeSubscription();   // спільний, про нього — нижче

class Account {
  constructor(
    readonly name: string,
    private sub: Subscription,          // ніколи не null
  ) {}
  // ...методи — на кроці 5
}

// єдине місце, де вирішуємо: підставити FREE замість null
function accountFor(name: string, sub: Subscription | null): Account {
  return new Account(name, sub ?? FREE);
}
