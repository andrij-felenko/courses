function notifyMotion(ev: MotionEvent): void {
  const text = `Рух у зоні «${ev.zone}» о ${time(ev.at)} — небезпека ${ZONE_RISK[ev.zone] ?? 0}`;
  sendVia("sms", text);
  sendVia("push", text);
  scheduleRepeat(text, ["sms", "push"]);       // доки власник не підтвердить
}

function notifyOffline(ev: OfflineEvent): void {
  const text =
    `Пристрій «${ev.device}» офлайн о ${time(ev.at)} — останній зв'язок ${sinceMin(ev.at)} хв тому`;
  sendVia("push", text);                        // тихий одноразовий
}
