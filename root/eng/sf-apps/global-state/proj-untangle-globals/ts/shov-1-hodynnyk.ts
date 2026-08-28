export interface Clock {
  now(): Date;
}

export const systemClock: Clock = {
  now: () => new Date(),
};

export class FixedClock implements Clock {
  constructor(private readonly moment: Date) {}
  now(): Date {
    return new Date(this.moment);   // копія: тест не зможе зіпсувати еталон
  }
}
