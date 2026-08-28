// Порівнюємо СУТЬ, а не сирий вихід: нормалізуємо все, що законно різне
function sameNotification(a: Notification, b: Notification): boolean {
  const canon = (n: Notification) => ({
    to: n.to,
    body: n.body.trim(),
    // мітку часу й згенерований id викидаємо — вони МУСЯТЬ різнитися
    attachments: [...n.attachments].sort(),   // порядок несуттєвий → сортуємо
  });
  return JSON.stringify(canon(a)) === JSON.stringify(canon(b));
}
