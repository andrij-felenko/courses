// «один + глобально»: пакетна функція time.Now() — теж глобальний доступ
func (s *SubscriptionService) Renew(sub *Subscription) {
    if time.Now().After(sub.ExpiresAt) {        // прихована залежність від часу
        sub.MarkExpired()
    }
}

// «один + передають руками»: годинник — це інтерфейс, який дають ззовні
type Clock interface{ Now() time.Time }

type SubscriptionService2 struct{ clock Clock }

func (s *SubscriptionService2) Renew(sub *Subscription) {
    if s.clock.Now().After(sub.ExpiresAt) {     // залежність на видноті
        sub.MarkExpired()
    }
}
// у тесті передають застиглий годинник, що завжди повертає 2030-01-01
