// --- adapter_b.go: єдине місце, що знає SDK вендора B ---
import (
	"errors"
	"vendorb" // тип вендора живе ЛИШЕ в цьому файлі
)

type VendorBStore struct {
	svc *vendorb.BlobService
}

func NewVendorBStore(container string) (*VendorBStore, error) {
	svc, err := vendorb.Connect(container)
	if err != nil {
		return nil, NewStoreError("vendorB connect: " + err.Error())
	}
	return &VendorBStore{svc: svc}, nil
}

func (s *VendorBStore) Put(key string, bytes []byte) error {
	if err := s.svc.Upload(key, bytes); err != nil { // повертає err при збої
		return NewStoreError("vendorB put: " + err.Error())
	}
	return nil
}

func (s *VendorBStore) Get(key string) ([]byte, bool, error) {
	b, err := s.svc.Download(key)
	if errors.Is(err, vendorb.ErrNotFound) {
		return nil, false, nil // приводимо до нашого правила
	}
	if err != nil {
		return nil, false, NewStoreError("vendorB get: " + err.Error())
	}
	return b.Bytes(), true, nil
}

func (s *VendorBStore) List(prefix string) ([]string, error) {
	names, err := s.svc.ListBlobs(prefix)
	if err != nil {
		return nil, NewStoreError("vendorB list: " + err.Error())
	}
	return names, nil
}
