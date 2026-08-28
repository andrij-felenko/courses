// --- логіка домену: жодної згадки про вендора, лише порт ---
func saveReceipt(store ObjectStore, o Order) error {
	return store.Put("orders/"+o.ID+"/receipt.json", renderReceipt(o))
}

func loadLastOrder(store ObjectStore, customer string) (*Order, error) {
	keys, err := store.List("orders/" + customer + "/")
	if err != nil {
		return nil, err
	}
	if len(keys) == 0 {
		return nil, nil
	}
	sort.Strings(keys) // ключі впорядкуємо самі
	bytes, found, err := store.Get(keys[len(keys)-1])
	if err != nil || !found {
		return nil, err
	}
	order := parseOrder(bytes)
	return &order, nil
}
