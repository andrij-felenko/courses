// --- adapter_a.go: єдине місце, що знає SDK вендора A ---
import "vendora" // тип вендора живе ЛИШЕ в цьому файлі

type VendorAStore struct {
	cli *vendora.Client
}

func NewVendorAStore(bucket string) *VendorAStore {
	return &VendorAStore{cli: vendora.NewClient(bucket)}
}

func (s *VendorAStore) Put(key string, bytes []byte) error {
	if st := s.cli.Write(key, bytes); st != vendora.OK {
		return NewStoreError("vendorA put: " + vendora.Str(st))
	}
	return nil
}

func (s *VendorAStore) Get(key string) ([]byte, bool, error) {
	buf, st := s.cli.Read(key)
	if st == vendora.NotFound {
		return nil, false, nil // не помилка!
	}
	if st != vendora.OK {
		return nil, false, NewStoreError("vendorA get: " + vendora.Str(st))
	}
	return buf, true, nil
}

func (s *VendorAStore) List(prefix string) ([]string, error) {
	var out []string
	for _, obj := range s.cli.Enumerate(prefix) { // SDK сам гортає сторінки
		out = append(out, obj.Key())
	}
	return out, nil
}
