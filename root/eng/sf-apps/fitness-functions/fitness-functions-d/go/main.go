func ratchet(current, baseline int) (bool, int) {
	if current > baseline {
		// регресія: порушень побільшало — ворота падають
		return false, baseline
	}
	// поступ (або без змін): планка тісниться до досягнутого, ніколи назад
	if current < baseline {
		baseline = current
	}
	return true, baseline
}
