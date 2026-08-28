interface ActionPlugin {
  readonly kind: string;
  onMotion(ev: MotionEvent, ctx: HubContext): void;   // біжить У процесі хаба, на гарячому шляху
}

class NightWatchPlugin implements ActionPlugin {
  readonly kind = "night-watch";
  onMotion(ev: MotionEvent, ctx: HubContext): void {
    const hour = new Date(ev.at).getHours();
    if (hour < 6 && ctx.home.mode === "away") {
      ctx.light.blink(ev.room, 3);
      ctx.notify.push(`Рух у ${ev.room}, коли нікого немає`);
    }
  }
}
