// Контракт шва — незмінний по обидва боки розрізу.
type DeviceStateReader interface {
    Read(ctx context.Context, deviceID string) (DeviceState, error)
}

// ДО: твін — сусідній пакет в одному процесі. Виклик у пам'яті.
type InProcessTwin struct{ twin *TwinModule }

func (t InProcessTwin) Read(ctx context.Context, id string) (DeviceState, error) {
    return t.twin.Snapshot(id), nil               // наносекунди, без мережі
}

// ПІСЛЯ: твін — окремий сервіс. Той самий контракт, інший транспорт.
type RemoteTwin struct {
    http *http.Client
    base string
}

func (t RemoteTwin) Read(ctx context.Context, id string) (DeviceState, error) {
    ctx, cancel := context.WithTimeout(ctx, 200*time.Millisecond) // дедлайн на мережу
    defer cancel()
    body, err := t.get(ctx, t.base+"/devices/"+id+"/state")
    if err != nil {
        return DeviceState{}, err
    }
    return parseState(body)                        // чужі дані — валідуємо на межі
}

// Автоматизації беруть інтерфейс — і не знають, який бік шва живий.
engine := NewAutomationEngine(reader)             // reader DeviceStateReader
