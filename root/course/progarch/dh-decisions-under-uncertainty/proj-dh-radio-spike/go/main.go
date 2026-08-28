package main

import (
	"context"
	"encoding/binary"
	"log"
	"time"

	"github.com/shimmeringbee/zigbee"
	"github.com/shimmeringbee/zstack"
)

// Той самий шов — але Go-демон на краю живе ПОДІЯМИ, не await'ами.
type DevicePort interface {
	SetRelay(ctx context.Context, dev string, on bool) error
	// читання температури приходить асинхронно, окремою подією — див. цикл нижче
}

const (
	clusterOnOff = 0x0006 // on=0x01, off=0x00
	clusterTemp  = 0x0402 // measured_value: int16, СОТІ °C (2000 = 20.00)
)

// Адаптер тримає стек і мапу «ім'я хаба → IEEE-адреса радіо». Усе про Zigbee — тут.
type ZigbeeAdapter struct {
	z    *zstack.ZStack
	ieee map[string]zigbee.IEEEAddress
	seq  byte
}

func (a *ZigbeeAdapter) SetRelay(ctx context.Context, dev string, on bool) error {
	cmd := byte(0x00) // off
	if on {
		cmd = 0x01 // on
	}
	a.seq++
	// ZCL-кадр складаємо майже вручну: [frame control 0x01 = cluster-specific | seq | cmd].
	// У молодого Go-стека ти ближче до дроту, ніж у zigpy — і це теж факт про край.
	frame := []byte{0x01, a.seq, cmd}
	return a.z.SendNodeMessage(ctx, a.ieee[dev], clusterOnOff, 1 /*src ep*/, 1 /*dst ep*/, frame)
}

func main() {
	ctx := context.Background()

	// 1. Реальний координатор (TI Z-Stack через shimmeringbee/zstack; API молодий).
	//    serialPort — відкритий /dev/ttyUSB0 (напр. github.com/tarm/serial).
	z := zstack.New(serialPort, nil)
	if err := z.Initialise(ctx, &zigbee.NetworkConfiguration{ /* канал, PAN ID, ключ */ }); err != nil {
		log.Fatal(err)
	}
	port := &ZigbeeAdapter{z: z, ieee: map[string]zigbee.IEEEAddress{}}

	// 2. Парування — відчиняємо вікно й КРУТИМО ЦИКЛ ПОДІЙ, чекаючи залізо.
	if err := z.PermitJoin(ctx, true); err != nil {
		log.Fatal(err)
	}
	log.Println("[спайк] вікно відчинено — тисни кнопку парування НА ДАВАЧІ")

	deadline := time.Now().Add(90 * time.Second)
	for time.Now().Before(deadline) {
		event, err := z.ReadEvent(ctx)
		if err != nil {
			log.Fatal(err)
		}
		switch e := event.(type) {

		case zigbee.NodeJoinEvent: // залізо приєдналося — те, чого дошка не покаже
			log.Printf("[парування] приєднався %v", e.Node.IEEEAddress)
			eps, _ := z.QueryNodeEndpoints(ctx, e.Node.IEEEAddress)
			log.Printf("[парування] endpoint'ів: %d", len(eps))
			port.ieee["temp-1"] = e.Node.IEEEAddress // (у спайку — руками)

		case zigbee.NodeIncomingMessageEvent: // звіт давача приходить СЮДИ
			m := e.IncomingMessage.ApplicationMessage
			if m.ClusterID == clusterTemp && len(m.Data) >= 2 {
				// zcl-пакет дав би measured_value як int16; тут — читаємо СИРІ 2 байти LE.
				raw := int16(binary.LittleEndian.Uint16(m.Data[len(m.Data)-2:]))
				log.Printf("[драйвер] сире=%d → %.2f °C", raw, float64(raw)/100) // чесність драйвера
				if float64(raw)/100 < 20.0 {          // одне правило — теж за швом
					_ = port.SetRelay(ctx, "temp-1", true)
				}
			}
		}
	}
	log.Println("[спайк] вікно 90 с вийшло — рахуємо, скільки приєдналось")
}
