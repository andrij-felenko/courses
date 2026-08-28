// backpressure_demo_test.go
package main

import (
	"testing"
	"time"
)

// Свідомо повільний споживач — найдешевший доказ, що стеля є.
// З boundedQueue тест проходить. Підстав сюди unboundedQueue — і він упаде
// на першій же перевірці, показавши рівно те, що ми ловимо: виробник
// проштовхнув усе й нічого не помітив.
func TestSlowConsumerHoldsProducerBack(t *testing.T) {
	const capacity, total = 4, 100
	q := newBounded(capacity)

	accepted := make(chan struct{}, total) // позначка на кожен put, що ПОВЕРНУВСЯ
	go func() {
		for i := 0; i < total; i++ {
			q.put(Job{id: i, born: time.Now()})
			accepted <- struct{}{}
		}
		q.close()
	}()

	// Споживача поки що немає взагалі. За 50 мс виробник мусить упертися
	// у стелю: рівно capacity put'ів повернулися, наступний спить усередині.
	time.Sleep(50 * time.Millisecond)
	if got := len(accepted); got > capacity {
		t.Fatalf("у чергу зі стелею %d пролізло %d елементів — стелі немає", capacity, got)
	}

	// Тепер умикаємо повільного споживача: 5 мс на елемент.
	seen, maxLen := 0, 0
	for {
		if n := q.length(); n > maxLen {
			maxLen = n
		}
		if _, ok := q.take(); !ok {
			break
		}
		time.Sleep(5 * time.Millisecond)
		seen++
	}
	if seen != total {
		t.Fatalf("дійшло %d із %d — протитиск не сміє нічого губити", seen, total)
	}
	if maxLen > capacity {
		t.Fatalf("черга роздулася до %d за стелі %d", maxLen, capacity)
	}
}
