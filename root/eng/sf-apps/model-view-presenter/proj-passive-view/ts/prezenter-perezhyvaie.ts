interface ThermostatView {
  // …команди…
  onNudge(handler: (delta: number) => void): () => void;   // повертає «відписатися»
}

class ThermostatPresenter {
  private off: (() => void) | null = null;

  start(): void {
    this.off = this.view.onNudge(delta => { this.model.nudge(delta); this.render(); });
    this.render();
  }

  stop(): void {
    this.off?.();     // відпустили подання: ні подій звідти, ні посилань на нього
    this.off = null;
  }
}
