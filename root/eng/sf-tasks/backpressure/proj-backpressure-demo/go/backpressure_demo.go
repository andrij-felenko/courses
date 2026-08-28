// backpressure_demo.go — один конвеєр, два прогони.
//   go run backpressure_demo.go unbounded      // черга без стелі
//   go run backpressure_demo.go bounded 32     // черга зі стелею 32
package main

import (
	"fmt"
	"os"
	"runtime"
	"strconv"
	"sync"
	"time"
)

const (
	produceEvery = 2 * time.Millisecond  // виробник: не швидше ніж 500 елементів/с
	handleCost   = 20 * time.Millisecond // споживач: рівно 50 елементів/с
	payloadSize  = 1024                  // ~1 КіБ вантажу на елемент
	runFor       = 20 * time.Second
)

// Job — одиниця роботи. born — мить створення, ще до черги:
// саме від неї, а не від миті, коли елемент дістали з черги, лічимо затримку.
type Job struct {
	id      int
	born    time.Time
	payload []byte // вантаж: він і займатиме пам'ять, поки елемент чекає
}

// queue — єдине, що відрізняє два прогони. Усе інше в програмі — спільне.
type queue interface {
	put(Job)           // покласти: може блокувати, а може й ні — у цьому вся інтрига
	take() (Job, bool) // узяти; false = чергу закрито й вичерпано
	length() int       // скільки лежить просто зараз
	close()
}
