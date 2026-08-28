// bench.go — go run bench.go   (драйвер: go get github.com/jackc/pgx/v5)
package main

import (
	"database/sql"
	"fmt"
	"sync"

	_ "github.com/jackc/pgx/v5/stdlib"
)

const (
	dsn     = "postgres://race:race@localhost:5432/race?sslmode=disable"
	clients = 50 // N покупців на ОДИН квиток (тримаємось під max_connections = 100)
	trials  = 20 // скільки разів повторити наліт
)

type strategy func(db *sql.DB, buyer int) bool

// НАЇВНО: read-modify-write, де «рахунок» робить ЗАСТОСУНОК, не SQL.
func naive(db *sql.DB, buyer int) bool {
	var seats int
	db.QueryRow(`SELECT seats_left FROM events WHERE id = 1`).Scan(&seats)
	if seats <= 0 { // рішення на щойно прочитаному — вже, можливо, застарілому — числі
		return false
	}
	newSeats := seats - 1 // рахунок у пам'яті застосунку: 1 − 1 = 0
	db.Exec(`UPDATE events SET seats_left = $1 WHERE id = 1`, newSeats)
	db.Exec(`INSERT INTO bookings (event_id, buyer) VALUES (1, $1)`, buyer)
	return true
}

// ЗАХИЩЕНО: рішення ухвалює СХОВИЩЕ — атомний UPDATE із вартовим.
func guarded(db *sql.DB, buyer int) bool {
	res, err := db.Exec(
		`UPDATE events SET seats_left = seats_left - 1
		   WHERE id = 1 AND seats_left > 0`)
	if err != nil {
		panic(err)
	}
	if n, _ := res.RowsAffected(); n == 0 {
		return false // вартовий 0 > 0 хибний — місць уже немає
	}
	db.Exec(`INSERT INTO bookings (event_id, buyer) VALUES (1, $1)`, buyer)
	return true
}

// Один наліт: скинути стан, випустити clients покупців ОДНОЧАСНО, порахувати продане.
func stampede(db *sql.DB, buy strategy) (counter, sold int) {
	db.Exec(`UPDATE events SET seats_left = 1 WHERE id = 1`)
	db.Exec(`TRUNCATE bookings`)

	start := make(chan struct{}) // «постріл»: закриття каналу будить УСІХ разом
	var ready, done sync.WaitGroup
	ready.Add(clients)
	done.Add(clients)
	for i := 0; i < clients; i++ {
		go func(buyer int) {
			defer done.Done()
			ready.Done() // «я на лінії старту»
			<-start      // ← бар'єр: стоїмо, доки не пролунає постріл
			buy(db, buyer)
		}(i)
	}
	ready.Wait() // усі 50 стоять на лінії
	close(start) // ← постріл: усі 50 кидаються на квиток в одну мить
	done.Wait()

	db.QueryRow(`SELECT seats_left FROM events WHERE id = 1`).Scan(&counter)
	db.QueryRow(`SELECT count(*) FROM bookings`).Scan(&sold)
	return
}

func main() {
	db, err := sql.Open("pgx", dsn)
	if err != nil {
		panic(err)
	}
	defer db.Close()
	if err := db.Ping(); err != nil {
		panic(err)
	}
	// КРИТИЧНО: кожному покупцеві — СВОЄ з'єднання, інакше пул серіалізує
	// їх у чергу й перегони не проявляться (див. пастку про пул).
	db.SetMaxOpenConns(clients)

	fmt.Printf("%-10s %10s %10s %11s\n", "стратегія", "продано", "зайвих", "лічильник")
	for _, s := range []struct {
		name string
		buy  strategy
	}{{"наївно", naive}, {"вартовий", guarded}} {
		totalSold, oversold, lastCounter := 0, 0, 0
		for t := 0; t < trials; t++ {
			counter, sold := stampede(db, s.buy)
			totalSold += sold
			if sold > 1 {
				oversold += sold - 1 // «зайві» квитки понад єдине місце
			}
			lastCounter = counter
		}
		fmt.Printf("%-10s %10d %10d %11d   (за %d нальотів)\n",
			s.name, totalSold, oversold, lastCounter, trials)
	}
}
