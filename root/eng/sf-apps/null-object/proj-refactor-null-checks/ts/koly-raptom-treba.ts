interface Subscription {
  price(): number;
  // ...
  isBillable(): boolean;         // семантичний детектор, не «isNull»
}

class PaidSubscription implements Subscription {
  isBillable(): boolean { return true; }
  // ...
}
class FreeSubscription implements Subscription {
  isBillable(): boolean { return false; }
  // ...
}
