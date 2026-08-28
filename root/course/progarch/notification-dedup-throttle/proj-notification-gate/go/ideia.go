package gate

import (
	"context"
	"crypto/sha1"
	"encoding/hex"
	"encoding/json"
	"sync"
	"time"
)

// Severity — клас критичності. Його проставляє ДЖЕРЕЛО події, не фільтр.
type Severity int

const (
	Info     Severity = iota // «прошивку оновлено» — агресивно зливаємо, тісна стеля
	Warning                  // «пристрій офлайн» — звичайний конвеєр
	Critical                 // дим · злом · протікання — в обхід усього, негайно
)

// Notification — одне ЛОГІЧНЕ сповіщення (не спроба доставки).
type Notification struct {
	Recipient string    // до кого (id користувача)
	Event     string    // ідентичність ПОДІЇ: "door-open@2026-07-11T07:14" (до хвилини!)
	Class     string    // тема для злиття: "connectivity", "security", "firmware"…
	Channel   string    // "push" | "feed" | "email"
	Severity  Severity
	At        time.Time // час події — для рядка дайджесту
	Text      string    // готовий рядок однієї події
	Holds     int       // скільки разів це вже притримали (для драбини throttling)
}

// Ключ дедупу — відбиток СМИСЛУ: кому + про яку подію + яким каналом.
// Номера спроби тут НЕМА (інакше ретрай матиме інший ключ і дубль просочиться).
func dedupKey(n Notification) string {
	return "dedup:" + sha1hex(n.Recipient+"|"+n.Event+"|"+n.Channel)
}

// Ключ групи — навмисне ГРУБШИЙ: усе, що людина сприйме як одну тему.
func groupKey(n Notification) string {
	return "grp:" + n.Recipient + "|" + n.Class + "|" + n.Channel
}

func sha1hex(s string) string { h := sha1.Sum([]byte(s)); return hex.EncodeToString(h[:]) }
