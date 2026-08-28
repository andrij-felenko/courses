private token = 0;                       // мітка найсвіжішого дотику
private busy = false;
private error: string | null = null;

private async nudge(delta: number): Promise<void> {
  const mine = ++this.token;
  this.busy = true; this.error = null;
  this.render();                         // кадр «надсилаю…» — одразу, ще до відповіді
  try {
    await this.model.nudge(delta);       // тут — розмова з котлом
  } catch {
    if (mine === this.token) this.error = "Котел не відповідає";
  }
  if (mine !== this.token) return;       // поки чекали, встиг новіший дотик — цей кадр застарів
  if (!this.off) return;                 // екран уже закрили — малювати нікуди
  this.busy = false;
  this.render();
}
