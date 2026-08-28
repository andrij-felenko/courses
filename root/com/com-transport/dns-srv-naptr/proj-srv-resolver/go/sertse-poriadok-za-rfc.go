import (
	"context"
	"crypto/tls"
	"errors"
	"fmt"
	"math/rand/v2"
	"net"
	"net/netip"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/miekg/dns" // NAPTR у стандартній бібліотеці немає
)

// Target — одна ціль SRV: куди йти, на який порт і з яким місцем у черзі.
type Target struct {
	Host     string // канонічне ім'я вузла, з крапкою на кінці
	Port     uint16
	Priority uint16
	Weight   uint16
	Addrs    []netip.Addr // заповнюється на третьому кроці ланцюга
}

// orderRFC2782 віддає повний порядок обходу: спершу за пріоритетом,
// а всередині кожного пріоритету — жеребкуванням за вагою.
func orderRFC2782(rrs []Target) []Target {
	sort.SliceStable(rrs, func(i, j int) bool { return rrs[i].Priority < rrs[j].Priority })

	out := make([]Target, 0, len(rrs))
	for i := 0; i < len(rrs); {
		j := i
		for j < len(rrs) && rrs[j].Priority == rrs[i].Priority {
			j++
		}
		group := append([]Target(nil), rrs[i:j]...)
		i = j

		// «У будь-якому порядку» зі специфікації — не декорація: це єдине
		// джерело випадковості для групи, у якій усі ваги нульові.
		rand.Shuffle(len(group), func(a, b int) { group[a], group[b] = group[b], group[a] })

		// Нульові ваги — на початок: лише там їхня наростальна сума дорівнює нулю.
		sort.SliceStable(group, func(a, b int) bool {
			return group[a].Weight == 0 && group[b].Weight != 0
		})

		for len(group) > 0 {
			running := make([]int, len(group))
			sum := 0
			for k, t := range group {
				sum += int(t.Weight)
				running[k] = sum
			}

			r := rand.IntN(sum + 1)            // рівномірне ціле з [0 … sum] ВКЛЮЧНО
			pick := sort.SearchInts(running, r) // перша наростальна сума ≥ r

			out = append(out, group[pick])
			group = append(group[:pick], group[pick+1:]...) // викинули — і рахуємо наново
		}
	}
	return out
}
