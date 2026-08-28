// Актор-пристрій: приватний стан, скринька-канал, одне повідомлення за раз.
type Msg interface{}
type Tick struct{}
type SetThreshold struct{ C float64 }
type Query struct{ Reply chan Snapshot }
type Snapshot struct{ On bool; Threshold float64 }

func deviceActor(mailbox <-chan Msg) {
    // приватний стан — його бачить ЛИШЕ ця горутина, тому й замок не потрібен
    var on bool
    threshold := 20.0
    for msg := range mailbox {          // ← одне повідомлення за раз
        switch m := msg.(type) {
        case Tick:
            reading := readSensor()
            on = decide(reading, threshold, on)   // те саме чисте ядро
            actuate(on)
        case SetThreshold:
            threshold = m.C
        case Query:
            m.Reply <- Snapshot{On: on, Threshold: threshold}   // відповідь — теж повідомленням
        }
    }
}
// надіслати: mailbox <- Tick{}   /   mailbox <- SetThreshold{C: 22}
