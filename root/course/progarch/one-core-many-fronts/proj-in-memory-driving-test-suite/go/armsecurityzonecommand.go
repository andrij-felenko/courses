package core

import "context"

type ArmSecurityZoneCommand struct {
	ZoneID  string
	PinCode string
}

type ArmZoneStatus int

const (
	ArmZoneStatusSuccess ArmZoneStatus = iota
	ArmZoneStatusInvalidPin
	ArmZoneStatusSensorOpen
	ArmZoneStatusZoneNotFound
)

type ArmSecurityZoneResult struct {
	Status ArmZoneStatus
	ZoneID string
}

type ArmSecurityZoneUseCase interface {
	Execute(ctx context.Context, cmd ArmSecurityZoneCommand) (ArmSecurityZoneResult, error)
}
