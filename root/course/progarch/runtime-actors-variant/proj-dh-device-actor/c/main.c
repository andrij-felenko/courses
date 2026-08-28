#include <pthread.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>

/* ── типи повідомлень (як у Go, тільки зворотний канал — руками) ── */
typedef enum { TICK, SET_THRESHOLD, COMMAND, QUERY } MsgKind;

typedef struct { bool on; double threshold; } Snapshot;

/* зворотний канал для QUERY: місце під відповідь + власний замок готовності */
typedef struct {
	Snapshot        snap;
	bool            ready;
	pthread_mutex_t lock;
	pthread_cond_t  cond;
} ReplyChan;

typedef struct {
	MsgKind    kind;
	double     threshold;   // для SET_THRESHOLD
	bool       force_on;    // для COMMAND
	ReplyChan *reply;       // для QUERY — канал лежить у самому повідомленні
} Msg;

/* ── ЧИСТЕ ЯДРО: той самий гістерезис із мертвою зоною ±0.5 ── */
static bool decide(double reading, double threshold, bool on) {
	if (reading < threshold - 0.5) return true;   // холодно — гріти
	if (reading > threshold + 0.5) return false;  // тепло — не гріти
	return on;                                     // мертва зона — тримати як було
}

/* ── СКРИНЬКА З ДНОМ. Того, що в Elixir/Go дармове, у C немає:
   кільцевий буфер + замок + умовну змінну будуємо самі. ── */
#define MAILBOX_CAP 64
typedef struct {
	Msg   buf[MAILBOX_CAP];
	int   head, tail, len;
	bool  closed;
	pthread_mutex_t lock;       // ← замок береже саму ЧЕРГУ, а не стан актора
	pthread_cond_t  not_empty;
} Mailbox;

// політика переповнення: відкинути надлишок (не блокувати джерело)
static bool mailbox_offer(Mailbox *mb, Msg m) {
	pthread_mutex_lock(&mb->lock);
	if (mb->len == MAILBOX_CAP) {          // повна → свідомо кидаємо
		// backpressure-варіант: тут чекати на умовній not_full, а не кидати
		pthread_mutex_unlock(&mb->lock);
		return false;
	}
	mb->buf[mb->tail] = m;
	mb->tail = (mb->tail + 1) % MAILBOX_CAP;
	mb->len++;
	pthread_cond_signal(&mb->not_empty);
	pthread_mutex_unlock(&mb->lock);
	return true;
}

// дістати одне (блокуємось, поки порожньо) — «одне повідомлення за раз»
static bool mailbox_take(Mailbox *mb, Msg *out) {
	pthread_mutex_lock(&mb->lock);
	while (mb->len == 0 && !mb->closed)
		pthread_cond_wait(&mb->not_empty, &mb->lock);
	if (mb->len == 0) { pthread_mutex_unlock(&mb->lock); return false; }
	*out = mb->buf[mb->head];
	mb->head = (mb->head + 1) % MAILBOX_CAP;
	mb->len--;
	pthread_mutex_unlock(&mb->lock);
	return true;
}

/* давач: 0 і значення в out; отруєний повертає -1 («замкнуло»). У C нема
   винятків, тож «крах» тут — це чесний код помилки, а не raise/panic */
typedef struct { const char *id; int (*sensor)(double *out); } Device;
static int  good_sensor(double *o)     { *o = 18.5; return 0; }
static int  poisoned_sensor(double *o) { (void)o; return -1; }
static void actuate(const char *id, bool on) { (void)id; (void)on; } // увімкнути нагрівач

/* ── ТІЛО АКТОРА: приватний стан = локальні змінні, одне повідомлення за раз.
   Повертає 0 при штатному закритті скриньки, -1 при збої (отруйний тік). ── */
static int run_actor(Device d, Mailbox *mb) {
	bool   on = false;           // ← бачить лише цей потік → замок НЕ потрібен
	double threshold = 20.0;
	Msg m;
	while (mailbox_take(mb, &m)) {            // ← одне за раз
		switch (m.kind) {
		case TICK: {
			double reading;
			if (d.sensor(&reading) != 0)      // отруєний давач «падає» тут
				return -1;                    // → сигнал наглядачеві: збій
			on = decide(reading, threshold, on);
			actuate(d.id, on);
			break;
		}
		case SET_THRESHOLD: threshold = m.threshold; break;
		case COMMAND:       on = m.force_on;         break;
		case QUERY:                                   // відповідь — зворотним каналом
			pthread_mutex_lock(&m.reply->lock);
			m.reply->snap  = (Snapshot){ .on = on, .threshold = threshold };
			m.reply->ready = true;
			pthread_cond_signal(&m.reply->cond);
			pthread_mutex_unlock(&m.reply->lock);
			break;
		}
	}
	return 0;                                  // скриньку закрито — штатний вихід
}

/* ── НАГЛЯДАЧ: окремий потік. Перезапускає run_actor ІЗ ЧИСТОГО СТАНУ
   (свіжі локальні змінні на кожному вході) + межа інтенсивності ВРУЧНУ.
   Увага: ловить лише КООПЕРАТИВНИЙ збій — actor повернув -1. Справжній
   крах у C (segfault, abort) валить УВЕСЬ процес: recover, як у Go, тут
   немає ЗОВСІМ — це і є нульова підтримка акторів на рівні мови. ── */
typedef struct { Device dev; Mailbox *mb; } SupArgs;

static void *supervise(void *arg) {
	SupArgs *a = arg;
	int fails = 0; time_t since = time(NULL);
	for (;;) {
		if (run_actor(a->dev, a->mb) == 0) return NULL;   // штатне завершення
		if (time(NULL) - since > 5) { fails = 0; since = time(NULL); } // вікно скинулось
		if (++fails > 3) {            // ← інакше отрута дасть ВІЧНИЙ цикл рестарту
			fprintf(stderr, "[sup] %s: 3 падіння за 5 с — КАРАНТИН\n", a->dev.id);
			return NULL;
		}
		fprintf(stderr, "[sup] %s впав — рестарт #%d з чистого стану\n", a->dev.id, fails);
	}
}

static Mailbox *start_device(Device d) {
	Mailbox *mb = calloc(1, sizeof *mb);
	pthread_mutex_init(&mb->lock, NULL);
	pthread_cond_init(&mb->not_empty, NULL);
	SupArgs *a = malloc(sizeof *a);
	*a = (SupArgs){ .dev = d, .mb = mb };
	pthread_t tid;
	pthread_create(&tid, NULL, supervise, a);   // наглядач у власному потоці
	pthread_detach(tid);
	return mb;
}

/* ── ДОКАЗ ІЗОЛЯЦІЇ: отруєний і здоровий термостати поруч ── */
int main(void) {
	Mailbox *ok  = start_device((Device){ .id = "therm_ok",  .sensor = good_sensor });
	Mailbox *bad = start_device((Device){ .id = "therm_bad", .sensor = poisoned_sensor });

	mailbox_offer(ok,  (Msg){ .kind = TICK });   // гріє (18.5 < 19.5)
	mailbox_offer(bad, (Msg){ .kind = TICK });   // впаде; наглядач підніме ЛИШЕ його

	ReplyChan rc = { .ready = false };            // зворотний канал збираємо руками
	pthread_mutex_init(&rc.lock, NULL);
	pthread_cond_init(&rc.cond, NULL);
	mailbox_offer(ok, (Msg){ .kind = QUERY, .reply = &rc });

	pthread_mutex_lock(&rc.lock);
	while (!rc.ready) pthread_cond_wait(&rc.cond, &rc.lock);   // чекаємо на відповідь
	pthread_mutex_unlock(&rc.lock);
	printf("{on=%d threshold=%.1f}\n", rc.snap.on, rc.snap.threshold); // {on=1 threshold=20.0} ← сусід живий
	return 0;
}
