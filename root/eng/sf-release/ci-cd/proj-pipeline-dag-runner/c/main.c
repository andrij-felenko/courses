#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

#define MAX_JOBS 32
#define MAX_NAME_LEN 64
#define MAX_DEPS 8
#define NUM_WORKERS 4

typedef enum {
    STATUS_PENDING,
    STATUS_READY,
    STATUS_RUNNING,
    STATUS_SUCCESS,
    STATUS_FAILED,
    STATUS_SKIPPED
} job_status_t;

typedef struct {
    char name[MAX_NAME_LEN];
    int duration_ms;
    bool should_fail;
    job_status_t status;
    int in_degree;
    int dep_count;
    int dep_indices[MAX_DEPS];
} job_t;

typedef struct {
    job_t jobs[MAX_JOBS];
    int job_count;
    int ready_queue[MAX_JOBS];
    int ready_head;
    int ready_tail;
    int ready_count;
    int completed_count;
    pthread_mutex_t lock;
    pthread_cond_t cv_ready;
    pthread_cond_t cv_done;
    bool shutdown;
} dag_runner_t;

void runner_init(dag_runner_t *runner) {
    memset(runner, 0, sizeof(*runner));
    pthread_mutex_init(&runner->lock, NULL);
    pthread_cond_init(&runner->cv_ready, NULL);
    pthread_cond_init(&runner->cv_done, NULL);
}

int runner_add_job(dag_runner_t *runner, const char *name, int duration_ms, bool should_fail) {
    if (runner->job_count >= MAX_JOBS) return -1;
    int idx = runner->job_count++;
    strncpy(runner->jobs[idx].name, name, MAX_NAME_LEN - 1);
    runner->jobs[idx].duration_ms = duration_ms;
    runner->jobs[idx].should_fail = should_fail;
    runner->jobs[idx].status = STATUS_PENDING;
    runner->jobs[idx].in_degree = 0;
    runner->jobs[idx].dep_count = 0;
    return idx;
}

void runner_add_dependency(dag_runner_t *runner, int parent_idx, int child_idx) {
    if (parent_idx < 0 || parent_idx >= runner->job_count ||
        child_idx < 0 || child_idx >= runner->job_count) return;
    job_t *child = &runner->jobs[child_idx];
    if (child->dep_count < MAX_DEPS) {
        child->dep_indices[child->dep_count++] = parent_idx;
        child->in_degree++;
    }
}

static void runner_enqueue_ready(dag_runner_t *runner, int job_idx) {
    runner->ready_queue[runner->ready_tail] = job_idx;
    runner->ready_tail = (runner->ready_tail + 1) % MAX_JOBS;
    runner->ready_count++;
    runner->jobs[job_idx].status = STATUS_READY;
    pthread_cond_signal(&runner->cv_ready);
}

static int runner_dequeue_ready(dag_runner_t *runner) {
    if (runner->ready_count == 0) return -1;
    int job_idx = runner->ready_queue[runner->ready_head];
    runner->ready_head = (runner->ready_head + 1) % MAX_JOBS;
    runner->ready_count--;
    return job_idx;
}

static void cascade_skip(dag_runner_t *runner, int failed_idx) {
    for (int i = 0; i < runner->job_count; ++i) {
        job_t *job = &runner->jobs[i];
        if (job->status == STATUS_PENDING || job->status == STATUS_READY) {
            for (int d = 0; d < job->dep_count; ++d) {
                if (job->dep_indices[d] == failed_idx) {
                    job->status = STATUS_SKIPPED;
                    runner->completed_count++;
                    printf("[RUNNER] Job '%s' SKIPPED (upstream '%s' failed)\n",
                           job->name, runner->jobs[failed_idx].name);
                    cascade_skip(runner, i);
                    break;
                }
            }
        }
    }
}

void* worker_thread(void *arg) {
    dag_runner_t *runner = (dag_runner_t*)arg;

    while (1) {
        pthread_mutex_lock(&runner->lock);

        while (runner->ready_count == 0 && !runner->shutdown &&
               runner->completed_count < runner->job_count) {
            pthread_cond_wait(&runner->cv_ready, &runner->lock);
        }

        if (runner->shutdown || runner->completed_count >= runner->job_count) {
            pthread_mutex_unlock(&runner->lock);
            break;
        }

        int job_idx = runner_dequeue_ready(runner);
        if (job_idx < 0) {
            pthread_mutex_unlock(&runner->lock);
            continue;
        }

        job_t *job = &runner->jobs[job_idx];
        job->status = STATUS_RUNNING;
        printf("[RUNNER] Starting job '%s' (duration: %d ms)...\n", job->name, job->duration_ms);
        pthread_mutex_unlock(&runner->lock);

        /* Імітація виконання корисної роботи */
        usleep(job->duration_ms * 1000);
        bool success = !job->should_fail;

        pthread_mutex_lock(&runner->lock);
        runner->completed_count++;

        if (success) {
            job->status = STATUS_SUCCESS;
            printf("[RUNNER] Job '%s' COMPLETED SUCCESS\n", job->name);

            /* Розблокування нащадків */
            for (int i = 0; i < runner->job_count; ++i) {
                job_t *child = &runner->jobs[i];
                if (child->status == STATUS_PENDING) {
                    for (int d = 0; d < child->dep_count; ++d) {
                        if (child->dep_indices[d] == job_idx) {
                            child->in_degree--;
                            if (child->in_degree == 0) {
                                runner_enqueue_ready(runner, i);
                            }
                            break;
                        }
                    }
                }
            }
        } else {
            job->status = STATUS_FAILED;
            printf("[RUNNER] Job '%s' FAILED!\n", job->name);
            cascade_skip(runner, job_idx);
        }

        if (runner->completed_count >= runner->job_count) {
            pthread_cond_broadcast(&runner->cv_ready);
            pthread_cond_signal(&runner->cv_done);
        }

        pthread_mutex_unlock(&runner->lock);
    }
    return NULL;
}

void runner_run(dag_runner_t *runner) {
    pthread_t threads[NUM_WORKERS];

    pthread_mutex_lock(&runner->lock);
    /* Знаходимо початкові задачі з нульовим in-degree */
    for (int i = 0; i < runner->job_count; ++i) {
        if (runner->jobs[i].in_degree == 0) {
            runner_enqueue_ready(runner, i);
        }
    }
    pthread_mutex_unlock(&runner->lock);

    for (int i = 0; i < NUM_WORKERS; ++i) {
        pthread_create(&threads[i], NULL, worker_thread, runner);
    }

    pthread_mutex_lock(&runner->lock);
    while (runner->completed_count < runner->job_count) {
        pthread_cond_wait(&runner->cv_done, &runner->lock);
    }
    runner->shutdown = true;
    pthread_cond_broadcast(&runner->cv_ready);
    pthread_mutex_unlock(&runner->lock);

    for (int i = 0; i < NUM_WORKERS; ++i) {
        pthread_join(threads[i], NULL);
    }

    pthread_mutex_destroy(&runner->lock);
    pthread_cond_destroy(&runner->cv_ready);
    pthread_cond_destroy(&runner->cv_done);
}

int main(void) {
    dag_runner_t runner;
    runner_init(&runner);

    int j_lint    = runner_add_job(&runner, "lint-and-format", 50, false);
    int j_build   = runner_add_job(&runner, "compile-binary", 100, false);
    int j_unit    = runner_add_job(&runner, "unit-tests", 80, false);
    int j_sec     = runner_add_job(&runner, "security-sast", 60, false);
    int j_e2e     = runner_add_job(&runner, "e2e-integration", 120, false);
    int j_package = runner_add_job(&runner, "build-oci-image", 90, false);

    /* Граф залежностей:
     * lint & build -> unit-tests & security-sast -> e2e-integration -> build-oci-image */
    runner_add_dependency(&runner, j_lint, j_unit);
    runner_add_dependency(&runner, j_build, j_unit);
    runner_add_dependency(&runner, j_build, j_sec);
    runner_add_dependency(&runner, j_unit, j_e2e);
    runner_add_dependency(&runner, j_sec, j_e2e);
    runner_add_dependency(&runner, j_e2e, j_package);

    printf("=== Starting DAG Pipeline Runner ===\n");
    runner_run(&runner);
    printf("=== Pipeline Completed ===\n");
    return 0;
}
