// Чи потягне привід задане навантаження через редуктор?
// motorTorque, loadTorque — Н·м;  ratio — передавальне число (>1 = сповільнення);
// eff — ККД редуктора (0..1, напр. 0.9)
function driveCanPull(motorTorque, ratio, eff, loadTorque) {
  const outTorque = motorTorque * ratio * eff;   // реальний момент на виході
  return outTorque >= loadTorque;                // з урахуванням втрат
}

// приклад виклику: мотор 0.02 Н·м, редуктор 1:40, ККД 0.9, навантаження 0.6 Н·м
// driveCanPull(0.02, 40.0, 0.9, 0.6) -> true  (0.72 >= 0.6)
