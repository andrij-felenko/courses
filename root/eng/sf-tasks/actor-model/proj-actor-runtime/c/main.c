#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

#define MAX_ACTORS 64
#define MSG_BATCH_QUOTA 4

typedef struct Actor Actor;

typedef enum {
    MSG_PING,
    MSG_PONG,
    MSG_DATA,
    MSG_STOP
} MessageType;

typedef struct Message {
    MessageType type;
    int payload;
    uint32_t sender_id;
    struct Message* next;
} Message;

typedef void (*Behavior)(Actor* self, Message* msg);

typedef struct {
    Message* head;
    Message* tail;
    pthread_mutex_t lock;
} Mailbox;

struct Actor {
    uint32_t id;
    int state_value;
    Behavior behavior;
    Mailbox mailbox;
    bool is_active;
    bool is_scheduled;
    struct Actor* next_ready;
};

typedef struct {
    Actor* head;
    Actor* tail;
    pthread_mutex_t lock;
    pthread_cond_t cond;
    bool stop_flag;
} ReadyQueue;

typedef struct {
    Actor* actors[MAX_ACTORS];
    uint32_t actor_count;
    ReadyQueue ready_queue;
    pthread_t workers[4];
    size_t num_workers;
} ActorSystem;

static ActorSystem g_system;

void mailbox_init(Mailbox* mb) {
    mb->head = NULL;
    mb->tail = NULL;
    pthread_mutex_init(&mb->lock, NULL);
}

void mailbox_push(Mailbox* mb, Message* msg) {
    msg->next = NULL;
    pthread_mutex_lock(&mb->lock);
    if (mb->tail) {
        mb->tail->next = msg;
        mb->tail = msg;
    } else {
        mb->head = mb->tail = msg;
    }
    pthread_mutex_unlock(&mb->lock);
}

Message* mailbox_pop(Mailbox* mb) {
    pthread_mutex_lock(&mb->lock);
    Message* msg = mb->head;
    if (msg) {
        mb->head = msg->next;
        if (!mb->head) mb->tail = NULL;
    }
    pthread_mutex_unlock(&mb->lock);
    return msg;
}

void ready_queue_init(ReadyQueue* rq) {
    rq->head = NULL;
    rq->tail = NULL;
    rq->stop_flag = false;
    pthread_mutex_init(&rq->lock, NULL);
    pthread_cond_init(&rq->cond, NULL);
}

void ready_queue_push(ReadyQueue* rq, Actor* actor) {
    pthread_mutex_lock(&rq->lock);
    actor->next_ready = NULL;
    if (rq->tail) {
        rq->tail->next_ready = actor;
        rq->tail = actor;
    } else {
        rq->head = rq->tail = actor;
    }
    pthread_cond_signal(&rq->cond);
    pthread_mutex_unlock(&rq->lock);
}

Actor* ready_queue_pop(ReadyQueue* rq) {
    pthread_mutex_lock(&rq->lock);
    while (!rq->head && !rq->stop_flag) {
        pthread_cond_wait(&rq->cond, &rq->lock);
    }
    if (rq->stop_flag && !rq->head) {
        pthread_mutex_unlock(&rq->lock);
        return NULL;
    }
    Actor* actor = rq->head;
    rq->head = actor->next_ready;
    if (!rq->head) rq->tail = NULL;
    pthread_mutex_unlock(&rq->lock);
    return actor;
}

void actor_send(uint32_t target_id, MessageType type, int payload, uint32_t sender_id) {
    if (target_id >= g_system.actor_count) return;
    Actor* target = g_system.actors[target_id];
    if (!target || !target->is_active) return;

    Message* msg = (Message*)malloc(sizeof(Message));
    msg->type = type;
    msg->payload = payload;
    msg->sender_id = sender_id;

    mailbox_push(&target->mailbox, msg);

    pthread_mutex_lock(&target->mailbox.lock);
    bool should_schedule = !target->is_scheduled;
    target->is_scheduled = true;
    pthread_mutex_unlock(&target->mailbox.lock);

    if (should_schedule) {
        ready_queue_push(&g_system.ready_queue, target);
    }
}

void ping_behavior(Actor* self, Message* msg);
void pong_behavior(Actor* self, Message* msg);

void ping_behavior(Actor* self, Message* msg) {
    if (msg->type == MSG_PONG) {
        printf("[Ping Actor %u] Отримано PONG (раунд %d)\n", self->id, msg->payload);
        if (msg->payload >= 5) {
            printf("[Ping Actor %u] Ліміт раундів досягнуто. Зупинка.\n", self->id);
            actor_send(msg->sender_id, MSG_STOP, 0, self->id);
            self->is_active = false;
        } else {
            usleep(100000);
            actor_send(msg->sender_id, MSG_PING, msg->payload + 1, self->id);
        }
    }
}

void pong_behavior(Actor* self, Message* msg) {
    if (msg->type == MSG_PING) {
        printf("[Pong Actor %u] Отримано PING (%d), надсилаю PONG\n", self->id, msg->payload);
        usleep(100000);
        actor_send(msg->sender_id, MSG_PONG, msg->payload, self->id);
    } else if (msg->type == MSG_STOP) {
        printf("[Pong Actor %u] Отримано команду STOP. Завершення.\n", self->id);
        self->is_active = false;
    }
}

void* worker_thread_func(void* arg) {
    (void)arg;
    while (true) {
        Actor* actor = ready_queue_pop(&g_system.ready_queue);
        if (!actor) break;

        size_t processed = 0;
        while (processed < MSG_BATCH_QUOTA) {
            Message* msg = mailbox_pop(&actor->mailbox);
            if (!msg) break;

            if (actor->is_active && actor->behavior) {
                actor->behavior(actor, msg);
            }
            free(msg);
            processed++;
        }

        pthread_mutex_lock(&actor->mailbox.lock);
        if (actor->mailbox.head && actor->is_active) {
            ready_queue_push(&g_system.ready_queue, actor);
        } else {
            actor->is_scheduled = false;
        }
        pthread_mutex_unlock(&actor->mailbox.lock);
    }
    return NULL;
}

uint32_t actor_spawn(Behavior init_behavior, int initial_state) {
    uint32_t id = g_system.actor_count++;
    Actor* actor = (Actor*)malloc(sizeof(Actor));
    actor->id = id;
    actor->state_value = initial_state;
    actor->behavior = init_behavior;
    actor->is_active = true;
    actor->is_scheduled = false;
    actor->next_ready = NULL;
    mailbox_init(&actor->mailbox);

    g_system.actors[id] = actor;
    return id;
}

void system_init(size_t workers) {
    g_system.actor_count = 0;
    g_system.num_workers = workers;
    ready_queue_init(&g_system.ready_queue);
    for (size_t i = 0; i < workers; ++i) {
        pthread_create(&g_system.workers[i], NULL, worker_thread_func, NULL);
    }
}

void system_shutdown(void) {
    pthread_mutex_lock(&g_system.ready_queue.lock);
    g_system.ready_queue.stop_flag = true;
    pthread_cond_broadcast(&g_system.ready_queue.cond);
    pthread_mutex_unlock(&g_system.ready_queue.lock);

    for (size_t i = 0; i < g_system.num_workers; ++i) {
        pthread_join(g_system.workers[i], NULL);
    }
}

int main(void) {
    printf("Запуск системи акторів...\n");
    system_init(2);

    uint32_t ping_pid = actor_spawn(ping_behavior, 0);
    uint32_t pong_pid = actor_spawn(pong_behavior, 0);

    // Ініціюємо перший PING
    actor_send(pong_pid, MSG_PING, 1, ping_pid);

    sleep(2);
    system_shutdown();
    printf("Систему акторів зупинено коректно.\n");
    return 0;
}
