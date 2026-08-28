#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

#define MAX_PARTICIPANTS 4
#define WAL_RECORD_MAGIC 0x3250434Du /* "2PCM" */

/* Типи повідомлень протоколу 2PC */
typedef enum {
    MSG_PREPARE = 1,
    MSG_VOTE_COMMIT = 2,
    MSG_VOTE_ABORT = 3,
    MSG_GLOBAL_COMMIT = 4,
    MSG_GLOBAL_ABORT = 5,
    MSG_ACK = 6
} MessageType;

/* Стани учасника та координатора */
typedef enum {
    STATE_INIT = 0,
    STATE_PREPARING = 1,
    STATE_PREPARED = 2,  /* Стан невизначеності (In-Doubt) */
    STATE_COMMITTED = 3,
    STATE_ABORTED = 4,
    STATE_DONE = 5
} TxState;

/* Бінарний запис у WAL-журналі */
typedef struct {
    uint32_t magic;
    uint32_t tx_id;
    uint32_t state;
    uint32_t crc;
} WalRecord;

/* Структура учасника */
typedef struct {
    int id;
    TxState state;
    int wal_fd;
    char wal_path[64];
    bool inject_crash_in_prepared;
} Participant;

/* Структура координатора */
typedef struct {
    uint32_t tx_id;
    TxState state;
    int wal_fd;
    char wal_path[64];
    int num_participants;
    Participant *participants[MAX_PARTICIPANTS];
} Coordinator;

static void wal_write_state(int fd, uint32_t tx_id, TxState state) {
    WalRecord rec = {
        .magic = WAL_RECORD_MAGIC,
        .tx_id = tx_id,
        .state = (uint32_t)state,
        .crc = tx_id ^ (uint32_t)state
    };
    if (write(fd, &rec, sizeof(rec)) != sizeof(rec)) {
        perror("write WAL");
        exit(EXIT_FAILURE);
    }
    /* Обов'язковий примусовий скид на диск до відправки повідомлень */
    if (fsync(fd) < 0) {
        perror("fsync WAL");
        exit(EXIT_FAILURE);
    }
}

static Participant* participant_create(int id, bool crash_simulation) {
    Participant *p = (Participant*)calloc(1, sizeof(Participant));
    if (!p) return NULL;
    p->id = id;
    p->state = STATE_INIT;
    p->inject_crash_in_prepared = crash_simulation;
    snprintf(p->wal_path, sizeof(p->wal_path), "participant_%d.wal", id);
    p->wal_fd = open(p->wal_path, O_CREAT | O_RDWR | O_APPEND, 0644);
    if (p->wal_fd < 0) {
        perror("open participant WAL");
        free(p);
        return NULL;
    }
    return p;
}

static void participant_destroy(Participant *p) {
    if (p) {
        if (p->wal_fd >= 0) close(p->wal_fd);
        free(p);
    }
}

/* Обробка повідомлень учасником */
static MessageType participant_handle_message(Participant *p, uint32_t tx_id, MessageType msg) {
    switch (msg) {
        case MSG_PREPARE:
            printf("  [Учасник %d] Отримано PREPARE для транзакції %u\n", p->id, tx_id);
            /* Перевірка локальних умов (наявність ресурсів, перевірка обмежень) */
            wal_write_state(p->wal_fd, tx_id, STATE_PREPARED);
            p->state = STATE_PREPARED;
            printf("  [Учасник %d] Стан PREPARED записано у WAL. Замки заблоковано.\n", p->id);
            if (p->inject_crash_in_prepared) {
                printf("  [Учасник %d] 💥 ІМІТАЦІЯ ПАДІННЯ У СТАНІ PREPARED!\n", p->id);
                return MSG_VOTE_ABORT;
            }
            return MSG_VOTE_COMMIT;

        case MSG_GLOBAL_COMMIT:
            printf("  [Учасник %d] Отримано GLOBAL_COMMIT. Фіксація даних.\n", p->id);
            wal_write_state(p->wal_fd, tx_id, STATE_COMMITTED);
            p->state = STATE_COMMITTED;
            /* Звільнення ресурсів і зняття замків */
            return MSG_ACK;

        case MSG_GLOBAL_ABORT:
            printf("  [Учасник %d] Отримано GLOBAL_ABORT. Відкат змін.\n", p->id);
            wal_write_state(p->wal_fd, tx_id, STATE_ABORTED);
            p->state = STATE_ABORTED;
            /* Звільнення ресурсів і зняття замків */
            return MSG_ACK;

        default:
            return MSG_VOTE_ABORT;
    }
}

/* Виконання транзакції координатором */
static bool coordinator_run_tx(Coordinator *c, uint32_t tx_id) {
    c->tx_id = tx_id;
    printf("[Координатор] Початок розподіленої транзакції TX=%u\n", tx_id);

    /* ФАЗА 1: Голосування */
    wal_write_state(c->wal_fd, tx_id, STATE_PREPARING);
    c->state = STATE_PREPARING;
    printf("[Координатор] Фаза 1: розсилка PREPARE до %d учасників...\n", c->num_participants);

    bool all_yes = true;
    for (int i = 0; i < c->num_participants; ++i) {
        MessageType vote = participant_handle_message(c->participants[i], tx_id, MSG_PREPARE);
        if (vote != MSG_VOTE_COMMIT) {
            printf("[Координатор] Учасник %d проголосував проти (VOTE_ABORT)\n", c->participants[i]->id);
            all_yes = false;
        } else {
            printf("[Координатор] Учасник %d проголосував за (VOTE_COMMIT)\n", c->participants[i]->id);
        }
    }

    /* ФАЗА 2: Ухвалення та розсилка рішення */
    if (all_yes) {
        printf("[Координатор] Усі голоси ствердні. Ухвалено рішення: COMMIT.\n");
        wal_write_state(c->wal_fd, tx_id, STATE_COMMITTED);
        c->state = STATE_COMMITTED;

        for (int i = 0; i < c->num_participants; ++i) {
            MessageType ack = participant_handle_message(c->participants[i], tx_id, MSG_GLOBAL_COMMIT);
            if (ack == MSG_ACK) {
                printf("[Координатор] Отримано ACK від учасника %d\n", c->participants[i]->id);
            }
        }
    } else {
        printf("[Координатор] Є голоси проти або збої. Ухвалено рішення: ABORT.\n");
        wal_write_state(c->wal_fd, tx_id, STATE_ABORTED);
        c->state = STATE_ABORTED;

        for (int i = 0; i < c->num_participants; ++i) {
            participant_handle_message(c->participants[i], tx_id, MSG_GLOBAL_ABORT);
        }
    }

    wal_write_state(c->wal_fd, tx_id, STATE_DONE);
    c->state = STATE_DONE;
    printf("[Координатор] Транзакцію TX=%u завершено (DONE).\n\n", tx_id);
    return all_yes;
}

int main(void) {
    Coordinator coord = { .state = STATE_INIT, .num_participants = 2 };
    snprintf(coord.wal_path, sizeof(coord.wal_path), "coordinator.wal");
    coord.wal_fd = open(coord.wal_path, O_CREAT | O_RDWR | O_APPEND, 0644);
    if (coord.wal_fd < 0) {
        perror("open coordinator WAL");
        return 1;
    }

    coord.participants[0] = participant_create(1, false);
    coord.participants[1] = participant_create(2, false);

    /* Тест 1: Успішний двофазний коміт */
    coordinator_run_tx(&coord, 1001);

    /* Тест 2: Відкат через відмову одного з учасників */
    coord.participants[1]->inject_crash_in_prepared = true;
    coordinator_run_tx(&coord, 1002);

    /* Очищення ресурсів */
    participant_destroy(coord.participants[0]);
    participant_destroy(coord.participants[1]);
    close(coord.wal_fd);

    unlink("coordinator.wal");
    unlink("participant_1.wal");
    unlink("participant_2.wal");
    return 0;
}
