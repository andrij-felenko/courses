export class Subscription {
  private status: SubscriptionStatus;
  private planPrice: number;

  constructor(status: SubscriptionStatus, planPrice: number) {
    this.status = status;
    this.planPrice = planPrice;
  }

  public calculateDiscount(promoCode?: string): number {
    if (this.status !== SubscriptionStatus.ACTIVE) {
      throw new Error("Неможливо застосувати знижку до неактивної підписки");
    }
    return promoCode ? this.planPrice * 0.15 : 0;
  }
}
