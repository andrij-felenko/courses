// Чи потягне мотор-редуктор задане навантаження на вихідному валу?
// motorTorque, loadTorque — Н·м;  ratio — передавальне число (>1 = сповільнення);
// eff — ККД редуктора (0..1, напр. 0.9)
func GearmotorCanPull(motorTorque, ratio, eff, loadTorque float64) bool {
	outTorque := motorTorque * ratio * eff // реальний момент на вихідному валу
	return outTorque >= loadTorque         // з урахуванням втрат у редукторі
}

// приклад: мотор 0.02 Н·м, мотор-редуктор «1:40», ККД 0.9, навантаження 0.6 Н·м
// GearmotorCanPull(0.02, 40.0, 0.9, 0.6) -> true   (0.72 >= 0.6)
