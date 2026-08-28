type Vendor int

const (
	VendorA Vendor = iota
	VendorB
)

// Єдине місце, що знає обидва адаптери. Уся решта коду бачить лише
// ObjectStore. Переїзд на іншого вендора = змінити конфіг, а не логіку.
func MakeStore(v Vendor, target string) (ObjectStore, error) {
	switch v {
	case VendorA:
		return NewVendorAStore(target), nil
	case VendorB:
		return NewVendorBStore(target)
	}
	return nil, NewStoreError("unknown vendor")
}

func main() {
	store, err := MakeStore(VendorA, "orders-bucket") // ← лише тут
	if err != nil {
		log.Fatal(err)
	}
	// Переїзд на B: MakeStore(VendorB, "orders-container").
	// saveReceipt / loadLastOrder не змінюються ВЗАГАЛІ.
	_ = saveReceipt(store, someOrder)
}
