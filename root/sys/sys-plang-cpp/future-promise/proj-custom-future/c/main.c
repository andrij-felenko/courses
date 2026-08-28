/* POSIX C Реалізація одноразового каналу (pthread_mutex + pthread_cond) */
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdbool.h>
#include <string.h>

/* Спільний стан у купі */
typedef struct {
    pthread_mutex_t mutex;
    pthread_cond_t  cond;
    int             ref_count;
    bool            ready;
    bool            has_error;
    int             value;
    char            error_msg[128];
} c_shared_state;

/* Виробник (Promise) */
typedef struct {
    c_shared_state* state;
} c_promise;

/* Споживач (Future) */
typedef struct {
    c_shared_state* state;
} c_future;

/* Створення нового каналу обміну */
static c_shared_state* create_shared_state(void) {
    c_shared_state* st = (c_shared_state*)malloc(sizeof(c_shared_state));
    if (!st) return NULL;
    
    pthread_mutex_init(&st->mutex, NULL);
    pthread_cond_init(&st->cond, NULL);
    st->ref_count = 2; /* 1 для promise, 1 для future */
    st->ready = false;
    st->has_error = false;
    st->value = 0;
    st->error_msg[0] = '\0';
    return st;
}

static void release_shared_state(c_shared_state* st) {
    if (!st) return;
    
    pthread_mutex_lock(&st->mutex);
    st->ref_count--;
    int current_refs = st->ref_count;
    pthread_mutex_unlock(&st->mutex);
    
    if (current_refs == 0) {
        pthread_cond_destroy(&st->cond);
        pthread_mutex_destroy(&st->mutex);
        free(st);
    }
}

/* Ініціалізація каналу */
void c_promise_init(c_promise* p, c_future* f) {
    c_shared_state* st = create_shared_state();
    p->state = st;
    f->state = st;
}

/* Запис значення у канал */
void c_promise_set_value(c_promise* p, int val) {
    if (!p->state) return;
    
    pthread_mutex_lock(&p->state->mutex);
    if (!p->state->ready) {
        p->state->value = val;
        p->state->ready = true;
        pthread_cond_signal(&p->state->cond);
    }
    pthread_mutex_unlock(&p->state->mutex);
}

/* Запис помилки у канал */
void c_promise_set_error(c_promise* p, const char* err) {
    if (!p->state) return;
    
    pthread_mutex_lock(&p->state->mutex);
    if (!p->state->ready) {
        p->state->has_error = true;
        strncpy(p->state->error_msg, err, sizeof(p->state->error_msg) - 1);
        p->state->ready = true;
        pthread_cond_signal(&p->state->cond);
    }
    pthread_mutex_unlock(&p->state->mutex);
}

/* Звільнення promise */
void c_promise_destroy(c_promise* p) {
    if (p->state) {
        pthread_mutex_lock(&p->state->mutex);
        if (!p->state->ready) {
            p->state->has_error = true;
            strncpy(p->state->error_msg, "broken_promise", sizeof(p->state->error_msg) - 1);
            p->state->ready = true;
            pthread_cond_signal(&p->state->cond);
        }
        pthread_mutex_unlock(&p->state->mutex);
        
        release_shared_state(p->state);
        p->state = NULL;
    }
}

/* Очікування та читання значення */
int c_future_get(c_future* f, bool* ok_out, char* err_buf, size_t err_buf_sz) {
    if (!f->state) {
        if (ok_out) *ok_out = false;
        return -1;
    }
    
    pthread_mutex_lock(&f->state->mutex);
    while (!f->state->ready) {
        pthread_cond_wait(&f->state->cond, &f->state->mutex);
    }
    
    int res = 0;
    if (f->state->has_error) {
        if (ok_out) *ok_out = false;
        if (err_buf && err_buf_sz > 0) {
            strncpy(err_buf, f->state->error_msg, err_buf_sz - 1);
        }
    } else {
        if (ok_out) *ok_out = true;
        res = f->state->value;
    }
    
    pthread_mutex_unlock(&f->state->mutex);
    return res;
}

void c_future_destroy(c_future* f) {
    if (f->state) {
        release_shared_state(f->state);
        f->state = NULL;
    }
}
