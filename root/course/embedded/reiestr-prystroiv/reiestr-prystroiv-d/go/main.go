package main

import (
	"fmt"
	"strings"
	"sync"
	"time"
)

// HardwareIdentity містить незмінні апаратні атрибути
type HardwareIdentity struct {
	SiliconUID      string `json:"silicon_uid"`
	HWRevision      string `json:"hw_revision"`
	MACAddress      string `json:"mac_address"`
	CertFingerprint string `json:"cert_fingerprint"`
}

// SystemState містить динамічний стан телеметрії
type SystemState struct {
	FirmwareVersion string    `json:"firmware_version"`
	IsOnline        bool      `json:"is_online"`
	RSSIdBm         int       `json:"rssi_dbm"`
	BatterySoC      float64   `json:"battery_soc"`
	LastSeen        time.Time `json:"last_seen"`
}

// DeviceEntity описує паспорт сутності в реєстрі
type DeviceEntity struct {
	DeviceUUID string            `json:"device_uuid"`
	Hardware   HardwareIdentity  `json:"hardware"`
	System     SystemState       `json:"system"`
	Tags       map[string]string `json:"tags"`
}

func (d *DeviceEntity) GetAttribute(path string) (string, bool) {
	switch path {
	case "sys.firmware_version":
		return d.System.FirmwareVersion, true
	case "sys.is_online":
		return fmt.Sprintf("%t", d.System.IsOnline), true
	case "hw.revision":
		return d.Hardware.HWRevision, true
	default:
		if strings.HasPrefix(path, "tags.") {
			tagKey := strings.TrimPrefix(path, "tags.")
			val, ok := d.Tags[tagKey]
			return val, ok
		}
	}
	return "", false
}

// Expression — інтерфейс дерева предикатів
type Expression interface {
	Evaluate(device *DeviceEntity) bool
}

type ComparisonExpr struct {
	AttrPath  string
	Op        string // "==", "!=", "<", ">"
	TargetVal string
}

func (c *ComparisonExpr) Evaluate(device *DeviceEntity) bool {
	val, ok := device.GetAttribute(c.AttrPath)
	if !ok {
		return false
	}
	switch c.Op {
	case "==":
		return val == c.TargetVal
	case "!=":
		return val != c.TargetVal
	case "<":
		return val < c.TargetVal
	case ">":
		return val > c.TargetVal
	}
	return false
}

type AndExpr struct {
	Left  Expression
	Right Expression
}

func (a *AndExpr) Evaluate(device *DeviceEntity) bool {
	return a.Left.Evaluate(device) && a.Right.Evaluate(device)
}

// DeviceRegistry реалізує потокобезпечне сховище та рушій вибірок
type DeviceRegistry struct {
	mu       sync.RWMutex
	devices  map[string]*DeviceEntity
	tagIndex map[string][]string
}

func NewDeviceRegistry() *DeviceRegistry {
	return &DeviceRegistry{
		devices:  make(map[string]*DeviceEntity),
		tagIndex: make(map[string][]string),
	}
}

func (r *DeviceRegistry) RegisterDevice(dev DeviceEntity) {
	r.mu.Lock()
	defer r.mu.Unlock()

	id := dev.DeviceUUID
	for k, v := range dev.Tags {
		idxKey := k + "=" + v
		r.tagIndex[idxKey] = append(r.tagIndex[idxKey], id)
	}
	r.devices[id] = &dev
}

func (r *DeviceRegistry) UpdateFirmware(uuid, newFw string) {
	r.mu.Lock()
	defer r.mu.Unlock()

	if dev, ok := r.devices[uuid]; ok {
		dev.System.FirmwareVersion = newFw
		dev.System.LastSeen = time.Now()
	}
}

func (r *DeviceRegistry) QueryDevices(query Expression) []string {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var matched []string
	for id, dev := range r.devices {
		if query.Evaluate(dev) {
			matched = append(matched, id)
		}
	}
	return matched
}

func main() {
	registry := NewDeviceRegistry()

	// Реєстрація пристроїв парку
	registry.RegisterDevice(DeviceEntity{
		DeviceUUID: "dev-uuid-001",
		Hardware:   HardwareIdentity{SiliconUID: "CHIP-96-01", HWRevision: "revB"},
		System:     SystemState{FirmwareVersion: "v2.1.3", IsOnline: true, BatterySoC: 0.88},
		Tags:       map[string]string{"env": "prod", "site": "dnipro-14", "role": "meter"},
	})

	registry.RegisterDevice(DeviceEntity{
		DeviceUUID: "dev-uuid-002",
		Hardware:   HardwareIdentity{SiliconUID: "CHIP-96-02", HWRevision: "revA"},
		System:     SystemState{FirmwareVersion: "v2.1.3", IsOnline: true, BatterySoC: 0.95},
		Tags:       map[string]string{"env": "prod", "site": "kyiv-02", "role": "meter"},
	})

	registry.RegisterDevice(DeviceEntity{
		DeviceUUID: "dev-uuid-003",
		Hardware:   HardwareIdentity{SiliconUID: "CHIP-96-03", HWRevision: "revB"},
		System:     SystemState{FirmwareVersion: "v2.2.0", IsOnline: true, BatterySoC: 0.75},
		Tags:       map[string]string{"env": "prod", "site": "dnipro-14", "role": "meter"},
	})

	// Декларативний фільтр для OTA: env == prod AND hw == revB AND fw < v2.2.0
	targetQuery := &AndExpr{
		Left: &ComparisonExpr{AttrPath: "tags.env", Op: "==", TargetVal: "prod"},
		Right: &AndExpr{
			Left:  &ComparisonExpr{AttrPath: "hw.revision", Op: "==", TargetVal: "revB"},
			Right: &ComparisonExpr{AttrPath: "sys.firmware_version", Op: "<", TargetVal: "v2.2.0"},
		},
	}

	fmt.Println("=== Цільова динамічна вибірка для OTA (Go) ===")
	targets := registry.QueryDevices(targetQuery)
	for _, id := range targets {
		fmt.Printf("Цільовий вузол: %s\n", id)
	}

	// Оновлення прошивки
	fmt.Println("\n[OTA] Оновлення вузла dev-uuid-001 до v2.2.0...")
	registry.UpdateFirmware("dev-uuid-001", "v2.2.0")

	postTargets := registry.QueryDevices(targetQuery)
	fmt.Printf("Пристроїв у черзі після оновлення: %d\n", len(postTargets))
}
