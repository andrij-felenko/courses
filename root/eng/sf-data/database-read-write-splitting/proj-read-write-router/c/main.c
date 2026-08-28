#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <ctype.h>
#include <time.h>
#include <pthread.h>

#define MAX_REPLICAS 16
#define MAX_SQL_SNIPPET 64
#define MAX_LAG_THRESHOLD_MS 2000
#define STICKY_WINDOW_SEC 3

typedef uint64_t lsn_t;

typedef enum {
    QUERY_UNKNOWN = 0,
    QUERY_READ,              /* Простий SELECT */
    QUERY_READ_LOCKING,      /* SELECT ... FOR UPDATE / LOCK IN SHARE MODE */
    QUERY_WRITE,             /* INSERT, UPDATE, DELETE, REPLACE */
    QUERY_TX_BEGIN,          /* BEGIN, START TRANSACTION */
    QUERY_TX_COMMIT,         /* COMMIT */
    QUERY_TX_ROLLBACK,       /* ROLLBACK */
    QUERY_SESSION_MUTATION   /* SET @var, SET SESSION, CREATE TEMPORARY */
} query_type_t;

typedef enum {
    NODE_PRIMARY = 0,
    NODE_REPLICA
} node_role_t;

typedef struct {
    int id;
    char host[64];
    int port;
    node_role_t role;
    bool is_healthy;
    lsn_t last_applied_lsn;
    uint32_t lag_ms;
    uint64_t active_connections;
} db_node_t;

typedef struct {
    int client_id;
    bool in_transaction;
    bool session_polluted;
    lsn_t last_write_lsn;
    time_t last_write_timestamp;
    int pinned_node_id; /* -1, якщо не прив'язаний */
} client_session_t;

typedef struct {
    db_node_t primary;
    db_node_t replicas[MAX_REPLICAS];
    size_t replica_count;
    size_t rr_index;
    pthread_mutex_t lock;
} router_cluster_t;

/* Допоміжна функція нормалізації рядків для лексичного аналізу */
static const char* skip_whitespace(const char* s) {
    while (*s && isspace((unsigned char)*s)) s++;
    return s;
}

static bool str_starts_with_ci(const char* s, const char* prefix) {
    while (*prefix) {
        if (tolower((unsigned char)*s) != tolower((unsigned char)*prefix)) {
            return false;
        }
        s++;
        prefix++;
    }
    return true;
}

/* Швидкий аналізатор типу SQL-запиту */
query_type_t classify_sql(const char* sql) {
    if (!sql) return QUERY_UNKNOWN;
    const char* p = skip_whitespace(sql);

    /* Ігнорування SQL-коментарів /* ... */ */
    while (*p == '/' && *(p + 1) == '*') {
        const char* end_comment = strstr(p + 2, "*/");
        if (!end_comment) return QUERY_UNKNOWN;
        p = skip_whitespace(end_comment + 2);
    }

    if (str_starts_with_ci(p, "BEGIN") || str_starts_with_ci(p, "START TRANSACTION")) {
        return QUERY_TX_BEGIN;
    }
    if (str_starts_with_ci(p, "COMMIT")) {
        return QUERY_TX_COMMIT;
    }
    if (str_starts_with_ci(p, "ROLLBACK")) {
        return QUERY_TX_ROLLBACK;
    }
    if (str_starts_with_ci(p, "INSERT") || str_starts_with_ci(p, "UPDATE") ||
        str_starts_with_ci(p, "DELETE") || str_starts_with_ci(p, "REPLACE") ||
        str_starts_with_ci(p, "ALTER")  || str_starts_with_ci(p, "DROP") ||
        str_starts_with_ci(p, "CREATE TABLE") || str_starts_with_ci(p, "TRUNCATE") ||
        str_starts_with_ci(p, "WITH ")) {
        return QUERY_WRITE;
    }
    if (str_starts_with_ci(p, "SET ") || str_starts_with_ci(p, "CREATE TEMPORARY")) {
        return QUERY_SESSION_MUTATION;
    }
    if (str_starts_with_ci(p, "SELECT")) {
        /* Перевірка на блокуючі конструкції FOR UPDATE або LOCK IN SHARE MODE */
        const char* upper_sql = p;
        if (strstr(upper_sql, "FOR UPDATE") != NULL ||
            strstr(upper_sql, "for update") != NULL ||
            strstr(upper_sql, "LOCK IN SHARE MODE") != NULL ||
            strstr(upper_sql, "lock in share mode") != NULL ||
            strstr(upper_sql, "FOR SHARE") != NULL ||
            strstr(upper_sql, "for share") != NULL) {
            return QUERY_READ_LOCKING;
        }
        return QUERY_READ;
    }

    return QUERY_WRITE; /* Безпечний дефолт: невідомі команди направляємо на Primary */
}

/* Ініціалізація кластера */
void router_init(router_cluster_t* cluster, const char* p_host, int p_port) {
    memset(cluster, 0, sizeof(router_cluster_t));
    cluster->primary.id = 0;
    snprintf(cluster->primary.host, sizeof(cluster->primary.host), "%s", p_host);
    cluster->primary.port = p_port;
    cluster->primary.role = NODE_PRIMARY;
    cluster->primary.is_healthy = true;
    cluster->primary.last_applied_lsn = 1000;
    cluster->primary.lag_ms = 0;

    pthread_mutex_init(&cluster->lock, NULL);
}

bool router_add_replica(router_cluster_t* cluster, const char* host, int port) {
    pthread_mutex_lock(&cluster->lock);
    if (cluster->replica_count >= MAX_REPLICAS) {
        pthread_mutex_unlock(&cluster->lock);
        return false;
    }
    size_t idx = cluster->replica_count;
    cluster->replicas[idx].id = (int)(idx + 1);
    snprintf(cluster->replicas[idx].host, sizeof(cluster->replicas[idx].host), "%s", host);
    cluster->replicas[idx].port = port;
    cluster->replicas[idx].role = NODE_REPLICA;
    cluster->replicas[idx].is_healthy = true;
    cluster->replicas[idx].last_applied_lsn = 1000;
    cluster->replicas[idx].lag_ms = 0;
    cluster->replica_count++;
    pthread_mutex_unlock(&cluster->lock);
    return true;
}

/* Вибір вузла для читання за алгоритмом Round-Robin з перевіркою здоров'я та LSN */
static db_node_t* select_healthy_replica(router_cluster_t* cluster, lsn_t required_lsn) {
    if (cluster->replica_count == 0) {
        return &cluster->primary;
    }

    size_t attempts = cluster->replica_count;
    while (attempts > 0) {
        size_t idx = cluster->rr_index % cluster->replica_count;
        cluster->rr_index++;
        attempts--;

        db_node_t* rep = &cluster->replicas[idx];
        if (rep->is_healthy && rep->lag_ms <= MAX_LAG_THRESHOLD_MS) {
            /* Перевірка причинної узгодженості: репліка мусить наздогнати потрібний LSN */
            if (required_lsn == 0 || rep->last_applied_lsn >= required_lsn) {
                return rep;
            }
        }
    }

    /* Якщо всі репліки відстають або нездорові — fallback на Primary */
    return &cluster->primary;
}

/* Головний диспетчер маршрутизації */
db_node_t* route_query(router_cluster_t* cluster, client_session_t* session, const char* sql) {
    query_type_t qtype = classify_sql(sql);
    time_t now = time(NULL);

    pthread_mutex_lock(&cluster->lock);

    /* 1. Обробка транзакційного стану */
    if (qtype == QUERY_TX_BEGIN) {
        session->in_transaction = true;
        session->pinned_node_id = cluster->primary.id;
        pthread_mutex_unlock(&cluster->lock);
        return &cluster->primary;
    }

    if (qtype == QUERY_TX_COMMIT || qtype == QUERY_TX_ROLLBACK) {
        session->in_transaction = false;
        session->pinned_node_id = -1;
        pthread_mutex_unlock(&cluster->lock);
        return &cluster->primary;
    }

    /* 2. Якщо клієнт усередині активної транзакції — ЖОРСТКИЙ PIN на Primary */
    if (session->in_transaction) {
        pthread_mutex_unlock(&cluster->lock);
        return &cluster->primary;
    }

    /* 3. Операції запису та блокуючого читання — завжди Primary */
    if (qtype == QUERY_WRITE || qtype == QUERY_READ_LOCKING) {
        session->last_write_timestamp = now;
        cluster->primary.last_applied_lsn += 10;
        session->last_write_lsn = cluster->primary.last_applied_lsn;
        pthread_mutex_unlock(&cluster->lock);
        return &cluster->primary;
    }

    /* 4. Забруднення сесії (SET @var) — прив'язка до Primary */
    if (qtype == QUERY_SESSION_MUTATION) {
        session->session_polluted = true;
        pthread_mutex_unlock(&cluster->lock);
        return &cluster->primary;
    }

    /* 5. Чисте читання (QUERY_READ) */
    if (qtype == QUERY_READ) {
        /* Перевірка ліпкого часового вікна (Sticky Window) після останнього запису */
        if (session->last_write_timestamp > 0 &&
            (now - session->last_write_timestamp) < STICKY_WINDOW_SEC) {
            db_node_t* target = select_healthy_replica(cluster, session->last_write_lsn);
            pthread_mutex_unlock(&cluster->lock);
            return target;
        }

        /* Звичайне розвантажувальне читання без строгих вимог до свіжості */
        db_node_t* target = select_healthy_replica(cluster, 0);
        pthread_mutex_unlock(&cluster->lock);
        return target;
    }

    pthread_mutex_unlock(&cluster->lock);
    return &cluster->primary;
}

void router_destroy(router_cluster_t* cluster) {
    pthread_mutex_destroy(&cluster->lock);
}
