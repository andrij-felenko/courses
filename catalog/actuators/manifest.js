/* manifest — «Виконавчі та сигнальні» (тип "catalog"). Схема — AUTHORING.md §2 (v6). Заведено з hardware-інвентарю. */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "catalog", slug: "actuators", title: "Виконавчі та сигнальні",
  sections: [
    { slug: "motors", title: "Мотори", scope: "Двигуни постійного струму, безколекторні та електромагнітні лінійні (соленоїдні) приводи.",
      topics: [
        { slug: "n20-motor", title: "N20 мікромотор з редуктором", basic: { status: "done" }, detailed: { status: "pending" }, hist: [{ file: "hist-n20-name.md", status: "done" }], math: [{ file: "math-gear-torque.md", status: "done" }], proj: [{ file: "proj-drive-n20.md", status: "done" }] },
        { slug: "bldc-motor", title: "Безколекторний мотор (BLDC)", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-esc-control.md", status: "done" }] },
        { slug: "jf-0530b-solenoid", title: "Соленоїд JF-0530B (12 В, push-pull)", basic: { status: "done" }, detailed: { status: "pending" }, hist: [{ file: "hist-freewheeling-diode.md", status: "done" }], proj: [{ file: "proj-drive-solenoid.md", status: "done" }] },
      ] },
    { slug: "servos", title: "Серва", scope: "Сервоприводи з керуванням за положенням.",
      topics: [
        { slug: "sg90-servo", title: "Tower Pro SG90 — мікросерво 9g", basic: { status: "done" }, detailed: { status: "pending" }, hist: [{ file: "hist-servo-standard.md", status: "done" }], proj: [{ file: "proj-servo-api.md", status: "done" }] },
        { slug: "hd-1370a-servo", title: "Power HD HD-1370A — серво", basic: { status: "done" }, detailed: { status: "empty" }, proj: [{ file: "proj-drive.md", status: "done" }] },
        { slug: "powerhd-family", title: "Родина Power HD (HuiDa RC) — серва й мотори", basic: { status: "done" }, detailed: { status: "empty" }, hist: [{ file: "hist-powerhd-brand.md", status: "done" }], proj: [{ file: "proj-pick-servo.md", status: "done" }] },
      ] },
    { slug: "steppers", title: "Крокові", scope: "Крокові двигуни.",
      topics: [
        { slug: "28byj-48-stepper", title: "28BYJ-48 — кроковий мотор (5V)", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-arduino-api.md", status: "done" }] },
      ] },
    { slug: "fans", title: "Вентилятори", scope: "Охолодження.",
      topics: [
        { slug: "fan-5v", title: "5V безколекторні вентилятори", basic: { status: "done" }, detailed: { status: "pending" }, hist: [{ file: "hist-4wire-pwm.md", status: "done" }], proj: [{ file: "proj-fan-control.md", status: "done" }] },
      ] },
    { slug: "signaling", title: "Сигнальні", scope: "Світло- й звуковипромінювачі: LED, зумери, лазери.",
      topics: [
        { slug: "led-5mm-kit", title: "Набір 5мм світлодіодів", basic: { status: "done" }, detailed: { status: "empty" }, hist: [{ file: "hist-first-visible-led.md", status: "done" }], math: [{ file: "math-led-resistor.md", status: "done" }] },
        { slug: "ky-016-rgb", title: "KY-016 — RGB-світлодіод", basic: { status: "done" }, detailed: { status: "pending" }, math: [{ file: "math-color-mixing.md", status: "done" }], proj: [{ file: "proj-rgb-control.md", status: "done" }] },
        { slug: "ky-009-rgb-smd", title: "KY-009 — RGB SMD-модуль", basic: { status: "done" }, detailed: { status: "empty" }, proj: [{ file: "proj-ky009-color.md", status: "done" }] },
        { slug: "ky-034-flash", title: "KY-034 — 7-кольоровий миготливий LED", basic: { status: "done" }, detailed: { status: "empty" }, hist: [{ file: "hist-self-flashing-led.md", status: "done" }], proj: [{ file: "proj-ky034-blink.md", status: "done" }] },
        { slug: "ky-027-magic-cup", title: "KY-027 — Magic Light Cup", basic: { status: "done" }, detailed: { status: "empty" }, hist: [{ file: "hist-mercury-to-ball.md", status: "done" }], proj: [{ file: "proj-magic-cup.md", status: "done" }] },
        { slug: "ky-006-buzzer", title: "KY-006 — пасивний зумер", basic: { status: "done" }, detailed: { status: "empty" }, proj: [{ file: "proj-ky006-buzzer.md", status: "done" }] },
        { slug: "ky-012-buzzer", title: "KY-012 — активний зумер", basic: { status: "done" }, detailed: { status: "empty" }, proj: [{ file: "proj-blink-beep.md", status: "done" }] },
        { slug: "buzzer-standalone", title: "Зумер (окремий)", basic: { status: "done" }, detailed: { status: "pending" }, hist: [{ file: "hist-piezo-buzzer.md", status: "done" }], proj: [{ file: "proj-buzzer-drive.md", status: "done" }] },
        { slug: "ky-008-laser", title: "KY-008 — лазерний модуль", basic: { status: "done" }, detailed: { status: "pending" }, proj: [{ file: "proj-laser-control.md", status: "done" }] },
      ] },
  ]
});
