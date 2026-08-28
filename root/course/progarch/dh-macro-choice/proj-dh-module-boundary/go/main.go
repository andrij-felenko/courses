// Go 1.22 implementation
package main

import (
	"context"
	"fmt"
	"reflect"
	"time"
)

// ── 1. Публічна доменна подія ──
type DeviceStateChangedEvent struct {
	EventID      string
	DeviceID     string
	HomeID       string
	PropertyName string
	OldValue     any
	NewValue     any
	Timestamp    time.Time
}

// ── 2. Публічний DTO та Інтерфейс ──
type DeviceDTO struct {
	ID       string
	HomeID   string
	Model    string
	IsOnline bool
}

type IDeviceRegistryModule interface {
	GetDevice(ctx context.Context, deviceID string) (*DeviceDTO, error)
	ListHomeDevices(ctx context.Context, homeID string) ([]DeviceDTO, error)
}

// ── 3. Внутрішньопроцесна шина подій (InMemoryEventBus) ──
type InMemoryEventBus struct {
	handlers map[reflect.Type][]func(any)
}

func NewInMemoryEventBus() *InMemoryEventBus {
	return &InMemoryEventBus{handlers: make(map[reflect.Type][]func(any))}
}

func Subscribe[T any](bus *InMemoryEventBus, handler func(T)) {
	t := reflect.TypeOf((*T)(nil)).Elem()
	wrapper := func(evt any) {
		handler(evt.(T))
	}
	bus.handlers[t] = append(bus.handlers[t], wrapper)
}

func (bus *InMemoryEventBus) Publish(event any) {
	t := reflect.TypeOf(event)
	if list, ok := bus.handlers[t]; ok {
		for _, h := range list {
			defer func() {
				if r := recover(); r != nil {
					fmt.Printf("[EventBus Error] Recovered from panic: %v\n", r)
				}
			}()
			h(event)
		}
	}
}
