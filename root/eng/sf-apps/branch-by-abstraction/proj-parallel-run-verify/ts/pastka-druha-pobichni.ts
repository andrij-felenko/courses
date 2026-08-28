// Розчеплюємо: РІШЕННЯ (чисте, звіряємо) окремо від ДІЇ (ефект, не дублюємо)
interface NotificationPlanner {
  plan(order: Order): NotificationPlan;   // кому, що, чи слати — чисте, без ефекту
}

class NotifyService {
  constructor(
    private planner: NotificationPlanner,   // сюди підставляємо ComparingPlanner
    private send: (plan: NotificationPlan) => void,   // ефект — поза звіркою
  ) {}

  notify(order: Order): void {
    const plan = this.planner.plan(order);   // тут стара й нова звіряються В ТІНІ
    this.send(plan);                          // а шлемо РІВНО РАЗ, за планом старої
  }
}
