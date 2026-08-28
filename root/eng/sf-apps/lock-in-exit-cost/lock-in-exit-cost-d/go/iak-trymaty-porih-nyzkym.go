// Уся прив'язка до постачальника A замкнена ТУТ.
// Жоден інший файл не бачить vendora.*.
type VendorAQueue struct {
	cli *vendora.Client // тип вендора — лише всередині
}

func NewVendorAQueue(url string) (*VendorAQueue, error) {
	cli, err := vendora.Dial(url)
	if err != nil {
		return nil, err
	}
	return &VendorAQueue{cli: cli}, nil
}

func (q *VendorAQueue) Publish(topic, payload string) error {
	m := vendora.Message{} // деталь вендора не витікає назовні
	m.SetChannel(topic)
	m.SetBody(payload)
	return q.cli.Send(m)
}

func (q *VendorAQueue) Consume(timeout time.Duration) (string, bool, error) {
	m, err := q.cli.Poll(timeout)
	if err == vendora.ErrTimeout {
		return "", false, nil
	}
	if err != nil {
		return "", false, err
	}
	return m.Body(), true, nil
}
