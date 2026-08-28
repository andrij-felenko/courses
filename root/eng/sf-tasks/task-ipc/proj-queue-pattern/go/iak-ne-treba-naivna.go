// ─── антиприклад — НЕ робити так ────────────────────────────────────
var gHasData bool // ← перегін: Sensor пише, Control читає
var gSample int   // ← перегін без м'ютекса

type Cmd struct {
    RelayOn bool
    Level   uint8
}

var gCommand Cmd // ← перегін: Control пише, Actuator читає

// Якби боялись перегонів — довелось би ставити окремий м'ютекс
// на кожну зі змінних: var mxData, mxCmd sync.Mutex
// і Lock/Unlock у кожній ґорутині. Це й є той «спагеті».

func taskSensor() {
    for {
        gSample = analogRead(pinA) // пише без захисту
        gHasData = true            // пише без захисту ← перегін!
        time.Sleep(100 * time.Millisecond)
    }
}

func taskControl() {
    for {
        if gHasData { // читає без захисту ← перегін!
            gHasData = false
            gCommand.RelayOn = gSample > 512 // пише без захисту
        }
        time.Sleep(10 * time.Millisecond)
    }
}
