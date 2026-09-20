package core

import "context"

type SecurityZone struct {
	ID             string
	PinCode        string
	HasOpenSensors bool
	IsArmed        bool
}

type SecurityZoneRepository interface {
	FindByID(ctx context.Context, id string) (*SecurityZone, error)
	Save(ctx context.Context, zone *SecurityZone) error
}

type ActuatorEventBus interface {
	PublishEvent(ctx context.Context, eventType string, payload string) error
}

type InMemorySecurityZoneRepository struct {
	zones map[string]*SecurityZone
}

func NewInMemorySecurityZoneRepository() *InMemorySecurityZoneRepository {
	return &InMemorySecurityZoneRepository{zones: make(map[string]*SecurityZone)}
}

func (r *InMemorySecurityZoneRepository) FindByID(_ context.Context, id string) (*SecurityZone, error) {
	z, ok := r.zones[id]
	if !ok {
		return nil, nil
	}
	return z, nil
}

func (r *InMemorySecurityZoneRepository) Save(_ context.Context, zone *SecurityZone) error {
	r.zones[zone.ID] = zone
	return nil
}

type ActuatorEventSpy struct {
	EmittedEvents []string
}

func (s *ActuatorEventSpy) PublishEvent(_ context.Context, eventType string, payload string) error {
	s.EmittedEvents = append(s.EmittedEvents, eventType+":"+payload)
	return nil
}
