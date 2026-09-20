type SecurityTestHarness struct {
	repo    *InMemorySecurityZoneRepository
	spy     *ActuatorEventSpy
	useCase ArmSecurityZoneUseCase
	lastRes ArmSecurityZoneResult
}

func (h *SecurityTestHarness) GivenZone(id, pin string, open bool) {
	_ = h.repo.Save(nil, &SecurityZone{ID: id, PinCode: pin, HasOpenSensors: open})
}

func (h *SecurityTestHarness) WhenArming(id, pin string) {
	h.lastRes, _ = h.useCase.Execute(nil, ArmSecurityZoneCommand{ZoneID: id, PinCode: pin})
}

func (h *SecurityTestHarness) ThenStatusIs(exp ArmZoneStatus) bool {
	return h.lastRes.Status == exp
}

func (h *SecurityTestHarness) ThenHasEvent(evt string) bool {
	for _, e := range h.spy.EmittedEvents {
		if e == evt { return true }
	}
	return false
}
