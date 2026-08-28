// bench.c — cc bench.c $(pkg-config --cflags --libs libpq) -lpthread -o bench && ./bench
#include <libpq-fe.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#define DSN     "postgres://race:race@localhost:5432/race"
#define CLIENTS 50   // N покупців на ОДИН квиток (тримаємось під max_connections = 100)
#define TRIALS  20   // скільки разів повторити наліт

typedef bool (*strategy)(PGconn *conn, int buyer);

static void run(PGconn *c, const char *sql) { PQclear(PQexec(c, sql)); }

// НАЇВНО: read-modify-write, де «рахунок» робить ЗАСТОСУНОК, не SQL.
static bool naive(PGconn *c, int buyer) {
	PGresult *r = PQexec(c, "SELECT seats_left FROM events WHERE id = 1");
	int seats = atoi(PQgetvalue(r, 0, 0));   // читаємо: 1
	PQclear(r);
	if (seats <= 0)                          // рішення на щойно прочитаному (застарілому) числі
		return false;
	char sql[128];
	snprintf(sql, sizeof sql,                // рахунок у пам'яті застосунку: 1 − 1 = 0
	         "UPDATE events SET seats_left = %d WHERE id = 1", seats - 1);
	run(c, sql);                             // пишемо обчислене, БЕЗ перевірки в SQL
	snprintf(sql, sizeof sql,
	         "INSERT INTO bookings (event_id, buyer) VALUES (1, %d)", buyer);
	run(c, sql);
	return true;
}

// ЗАХИЩЕНО: рішення ухвалює СХОВИЩЕ — атомний UPDATE із вартовим.
static bool guarded(PGconn *c, int buyer) {
	PGresult *r = PQexec(c,
	    "UPDATE events SET seats_left = seats_left - 1 "
	    "WHERE id = 1 AND seats_left > 0");   // вартовий усередині оператора
	bool got = atoi(PQcmdTuples(r)) == 1;     // скільки рядків змінив UPDATE
	PQclear(r);
	if (!got)
		return false;                         // 0 рядків → місць немає
	char sql[128];
	snprintf(sql, sizeof sql,
	         "INSERT INTO bookings (event_id, buyer) VALUES (1, %d)", buyer);
	run(c, sql);
	return true;
}

typedef struct {
	pthread_barrier_t *gate;   // спільний бар'єр: усі стартують РАЗОМ
	strategy buy;
	int buyer;
} client;

static void *one_buyer(void *p) {
	client *a = p;
	// КОЖЕН покупець — СВОЄ з'єднання (libpq в autocommit: кожен крок фіксується одразу)
	PGconn *c = PQconnectdb(DSN);
	pthread_barrier_wait(a->gate);   // ← бар'єр: останній прибулець пускає всіх 50 в ОДНУ мить
	a->buy(c, a->buyer);
	PQfinish(c);
	return NULL;
}

// Один наліт: скинути стан, випустити CLIENTS покупців ОДНОЧАСНО, порахувати продане.
static void stampede(PGconn *admin, strategy buy, int *counter, int *sold) {
	run(admin, "UPDATE events SET seats_left = 1 WHERE id = 1");
	run(admin, "TRUNCATE bookings");

	pthread_barrier_t gate;
	pthread_barrier_init(&gate, NULL, CLIENTS);   // усі CLIENTS зустрічаються тут і рушають РАЗОМ
	pthread_t th[CLIENTS];
	client arg[CLIENTS];
	for (int i = 0; i < CLIENTS; i++) {
		arg[i] = (client){ &gate, buy, i };
		pthread_create(&th[i], NULL, one_buyer, &arg[i]);
	}
	for (int i = 0; i < CLIENTS; i++)
		pthread_join(th[i], NULL);            // чекаємо, доки всі покупці добіжать

	pthread_barrier_destroy(&gate);

	PGresult *r = PQexec(admin, "SELECT seats_left FROM events WHERE id = 1");
	*counter = atoi(PQgetvalue(r, 0, 0));     // зіпсовний лічильник — йому не віримо
	PQclear(r);
	r = PQexec(admin, "SELECT count(*) FROM bookings");
	*sold = atoi(PQgetvalue(r, 0, 0));        // чесний свідок: скільки квитків насправді пішло
	PQclear(r);
}

int main(void) {
	PGconn *admin = PQconnectdb(DSN);
	if (PQstatus(admin) != CONNECTION_OK) {
		fprintf(stderr, "не під'єднався: %s", PQerrorMessage(admin));
		return 1;
	}
	struct { const char *name; strategy buy; } strat[] = {
		{ "наївно", naive }, { "вартовий", guarded }
	};
	printf("%-10s %10s %10s %11s\n", "стратегія", "продано", "зайвих", "лічильник");
	for (int s = 0; s < 2; s++) {
		int total_sold = 0, oversold = 0, last_counter = 0;
		for (int t = 0; t < TRIALS; t++) {
			int counter, sold;
			stampede(admin, strat[s].buy, &counter, &sold);
			total_sold += sold;
			if (sold > 1)
				oversold += sold - 1;         // «зайві» квитки понад єдине місце
			last_counter = counter;
		}
		printf("%-10s %10d %10d %11d   (за %d нальотів)\n",
		       strat[s].name, total_sold, oversold, last_counter, TRIALS);
	}
	PQfinish(admin);
	return 0;
}
