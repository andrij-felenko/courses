type Kind = "motion" | "offline" | "lowbat";

// метод відростив ще й параметр zone і третій kind
function notify(kind: Kind, subject: string, zone: string, at: number): void {
  // 1) тіло тексту — розвилка на kind
  let text: string;
  if (kind === "motion")        text = `Рух у зоні «${zone}» о ${time(at)}`;
  else if (kind === "offline")  text = `Пристрій «${subject}» офлайн о ${time(at)}`;
  else                          text = `Батарея «${subject}» сідає`;

  // 2) хвіст тексту — знову розвилка на kind
  if (kind === "motion")   text += ` — небезпека ${ZONE_RISK[zone] ?? 0}`;
  if (kind === "offline")  text += ` — останній зв'язок ${sinceMin(at)} хв тому`;

  // 3) канали — розвилка
  const channels = kind === "motion" ? ["sms", "push"] : ["push"];

  // 4) повтор — розвилка
  const repeat = kind === "motion";

  for (const ch of channels) sendVia(ch, text);
  if (repeat) scheduleRepeat(text, channels);
}
