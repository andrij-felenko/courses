// «один + глобально»: логіка сама лізе по глобальний годинник
class SystemClock {
  private static inst: SystemClock | null = null;
  static instance(): SystemClock {
    return (SystemClock.inst ??= new SystemClock());
  }
  now(): Date { return new Date(); }
}

class SubscriptionService {
  renew(sub: Subscription) {
    const now = SystemClock.instance().now();   // прихована залежність від часу
    if (now > sub.expiresAt) sub.markExpired();
  }
}

// «один + передають руками»: годинник приходить явно, його видно в конструкторі
interface Clock { now(): Date; }

class SubscriptionService2 {
  constructor(private clock: Clock) {}          // залежність на видноті
  renew(sub: Subscription) {
    if (this.clock.now() > sub.expiresAt) sub.markExpired();
  }
}
// у тесті:  new SubscriptionService2({ now: () => new Date("2030-01-01") })
