/* C Implementation: Singleflight Request Coalescer */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

typedef struct singleflight_call {
    char key[64];
    char result[256];
    bool is_done;
    pthread_mutex_t mutex;
    pthread_cond_t cond;
    struct singleflight_call *next;
} singleflight_call_t;

typedef struct {
    singleflight_call_t *head;
    pthread_mutex_t table_mutex;
} singleflight_group_t;

void singleflight_group_init(singleflight_group_t *group) {
    group->head = NULL;
    pthread_mutex_init(&group->table_mutex, NULL);
}

bool singleflight_execute(
    singleflight_group_t *group,
    const char *key,
    void (*fetch_fn)(const char *key, char *out_buf, size_t buf_size),
    char *out_result,
    size_t result_size
) {
    pthread_mutex_lock(&group->table_mutex);

    /* Search for an existing active call for the same key */
    singleflight_call_t *curr = group->head;
    while (curr != NULL) {
        if (strcmp(curr->key, key) == 0) {
            /* Active call found! Wait for its result */
            pthread_mutex_unlock(&group->table_mutex);
            
            pthread_mutex_lock(&curr->mutex);
            while (!curr->is_done) {
                pthread_cond_wait(&curr->cond, &curr->mutex);
            }
            strncpy(out_result, curr->result, result_size - 1);
            out_result[result_size - 1] = '\0';
            pthread_mutex_unlock(&curr->mutex);
            return false; /* Joined an existing request (Coalesced) */
        }
        curr = curr->next;
    }

    /* No active call found: create new entry */
    singleflight_call_t *call = (singleflight_call_t *)malloc(sizeof(singleflight_call_t));
    strncpy(call->key, key, sizeof(call->key) - 1);
    call->is_done = false;
    pthread_mutex_init(&call->mutex, NULL);
    pthread_cond_init(&call->cond, NULL);
    call->next = group->head;
    group->head = call;

    pthread_mutex_unlock(&group->table_mutex);

    /* Execute the actual fetch operation (Only once!) */
    fetch_fn(key, call->result, sizeof(call->result));

    /* Broadcast result to all waiting threads */
    pthread_mutex_lock(&call->mutex);
    call->is_done = true;
    pthread_cond_broadcast(&call->cond);
    pthread_mutex_unlock(&call->mutex);

    /* Copy result to caller output */
    strncpy(out_result, call->result, result_size - 1);
    out_result[result_size - 1] = '\0';

    /* Remove from tracking table and free memory */
    pthread_mutex_lock(&group->table_mutex);
    singleflight_call_t **pptr = &group->head;
    while (*pptr != NULL) {
        if (*pptr == call) {
            *pptr = call->next;
            break;
        }
        pptr = &(*pptr)->next;
    }
    pthread_mutex_unlock(&group->table_mutex);

    pthread_mutex_destroy(&call->mutex);
    pthread_cond_destroy(&call->cond);
    free(call);

    return true; /* Executed origin fetch */
}
