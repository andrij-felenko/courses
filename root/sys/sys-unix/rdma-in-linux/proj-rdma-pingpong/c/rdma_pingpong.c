/*
 * rdma_pingpong.c — Повний варіант мовою C (POSIX / libibverbs / librdmacm)
 * Збірка: gcc -O2 rdma_pingpong.c -o rdma_pingpong -lrdmacm -libverbs
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <rdma/rdma_cma.h>

#define TEST_BUFFER_SIZE 1024

// Власний вихідний протокол для Out-Of-Band обміну R_Key та віртуальною адресою
struct RdmaBufferExchange {
    uint64_t remote_addr;
    uint32_t rkey;
};

static void run_server(const char *port) {
    struct rdma_event_channel *ec = rdma_create_event_channel();
    struct rdma_cm_id *listen_id = NULL, *client_id = NULL;
    struct rdma_cm_event *event = NULL;

    struct addrinfo hints = { .ai_family = AF_INET, .ai_socktype = SOCK_STREAM, .ai_flags = AI_PASSIVE };
    struct addrinfo *res = NULL;
    getaddrinfo(NULL, port, &hints, &res);

    rdma_create_id(ec, &listen_id, NULL, RDMA_PS_TCP);
    rdma_bind_addr(listen_id, res->ai_addr);
    freeaddrinfo(res);
    rdma_listen(listen_id, 1);

    printf("[Server] Очікування з'єднання на порту %s...\n", port);
    rdma_get_cm_event(ec, &event);
    client_id = event->id;
    rdma_ack_cm_event(event);

    struct ibv_pd *pd = ibv_alloc_pd(client_id->verbs);
    struct ibv_cq *cq = ibv_create_cq(client_id->verbs, 10, NULL, NULL, 0);

    struct ibv_qp_init_attr qp_attr = {
        .send_cq = cq,
        .recv_cq = cq,
        .qp_type = IBV_QPT_RC,
        .cap = { .max_send_wr = 10, .max_recv_wr = 10, .max_send_sge = 1, .max_recv_sge = 1 }
    };
    rdma_create_qp(client_id, pd, &qp_attr);

    char *buffer = (char *)calloc(1, TEST_BUFFER_SIZE);
    struct ibv_mr *mr = ibv_reg_mr(pd, buffer, TEST_BUFFER_SIZE,
                                   IBV_ACCESS_LOCAL_WRITE | IBV_ACCESS_REMOTE_WRITE);

    // Готуємо Send-буфер для передачі R_Key та адреси клієнту
    struct RdmaBufferExchange ex = {
        .remote_addr = (uint64_t)buffer,
        .rkey = mr->rkey
    };
    struct ibv_mr *ex_mr = ibv_reg_mr(pd, &ex, sizeof(ex), IBV_ACCESS_LOCAL_WRITE);

    struct ibv_sge sge = { .addr = (uint64_t)&ex, .length = sizeof(ex), .lkey = ex_mr->lkey };
    struct ibv_send_wr wr = {
        .wr_id = 1, .sg_list = &sge, .num_sge = 1,
        .opcode = IBV_WR_SEND, .send_flags = IBV_SEND_SIGNALED
    }, *bad_wr = NULL;

    struct rdma_conn_param conn_param = {};
    rdma_accept(client_id, &conn_param);
    rdma_get_cm_event(ec, &event); // RDMA_CM_EVENT_ESTABLISHED
    rdma_ack_cm_event(event);

    // Надсилаємо свої ключі клієнту
    ibv_post_send(client_id->qp, &wr, &bad_wr);

    struct ibv_wc wc;
    while (ibv_poll_cq(cq, 1, &wc) == 0); // Очікування завершення Send

    printf("[Server] Метадані передано. Очікування RDMA Write від клієнта...\n");
    sleep(2); // Даємо час клієнту виконати RDMA Write безпосередньо у буфер

    printf("[Server] Вміст буфера після RDMA Write: '%s'\n", buffer);

    ibv_dereg_mr(ex_mr);
    ibv_dereg_mr(mr);
    free(buffer);
    rdma_destroy_qp(client_id);
    ibv_destroy_cq(cq);
    ibv_dealloc_pd(pd);
    rdma_destroy_id(client_id);
    rdma_destroy_id(listen_id);
    rdma_destroy_event_channel(ec);
}

static void run_client(const char *ip, const char *port) {
    struct rdma_event_channel *ec = rdma_create_event_channel();
    struct rdma_cm_id *id = NULL;
    struct rdma_cm_event *event = NULL;

    struct addrinfo hints = { .ai_family = AF_INET, .ai_socktype = SOCK_STREAM };
    struct addrinfo *res = NULL;
    getaddrinfo(ip, port, &hints, &res);

    rdma_create_id(ec, &id, NULL, RDMA_PS_TCP);
    rdma_resolve_addr(id, NULL, res->ai_addr, 2000);
    freeaddrinfo(res);

    rdma_get_cm_event(ec, &event); // EVENT_ADDR_RESOLVED
    rdma_ack_cm_event(event);

    rdma_resolve_route(id, 2000);
    rdma_get_cm_event(ec, &event); // EVENT_ROUTE_RESOLVED
    rdma_ack_cm_event(event);

    struct ibv_pd *pd = ibv_alloc_pd(id->verbs);
    struct ibv_cq *cq = ibv_create_cq(id->verbs, 10, NULL, NULL, 0);

    struct ibv_qp_init_attr qp_attr = {
        .send_cq = cq, .recv_cq = cq, .qp_type = IBV_QPT_RC,
        .cap = { .max_send_wr = 10, .max_recv_wr = 10, .max_send_sge = 1, .max_recv_sge = 1 }
    };
    rdma_create_qp(id, pd, &qp_attr);

    // Реєструємо буфер прийому метаданих
    struct RdmaBufferExchange ex = {};
    struct ibv_mr *ex_mr = ibv_reg_mr(pd, &ex, sizeof(ex), IBV_ACCESS_LOCAL_WRITE);
    struct ibv_sge recv_sge = { .addr = (uint64_t)&ex, .length = sizeof(ex), .lkey = ex_mr->lkey };
    struct ibv_recv_wr recv_wr = { .wr_id = 2, .sg_list = &recv_sge, .num_sge = 1 }, *bad_recv_wr = NULL;

    ibv_post_recv(id->qp, &recv_wr, &bad_recv_wr);

    struct rdma_conn_param conn_param = {};
    rdma_connect(id, &conn_param);
    rdma_get_cm_event(ec, &event); // ESTABLISHED
    rdma_ack_cm_event(event);

    struct ibv_wc wc;
    while (ibv_poll_cq(cq, 1, &wc) == 0); // Очікування прийому R_Key

    printf("[Client] Отримано віддалену адресу: 0x%lx, R_Key: 0x%x\n", ex.remote_addr, ex.rkey);

    // Локальний буфер з повідомленням для запису на сервер
    char *local_msg = strdup("Привіт від RDMA Клієнта через Zero-Copy Write!");
    struct ibv_mr *local_mr = ibv_reg_mr(pd, local_msg, strlen(local_msg) + 1, IBV_ACCESS_LOCAL_WRITE);

    struct ibv_sge send_sge = { .addr = (uint64_t)local_msg, .length = (uint32_t)strlen(local_msg) + 1, .lkey = local_mr->lkey };
    struct ibv_send_wr write_wr = {
        .wr_id = 3, .sg_list = &send_sge, .num_sge = 1,
        .opcode = IBV_WR_RDMA_WRITE, .send_flags = IBV_SEND_SIGNALED,
        .wr.rdma = { .remote_addr = ex.remote_addr, .rkey = ex.rkey }
    }, *bad_write_wr = NULL;

    printf("[Client] Виконання RDMA Write...\n");
    ibv_post_send(id->qp, &write_wr, &bad_write_wr);

    while (ibv_poll_cq(cq, 1, &wc) == 0); // Очікування підтвердження від HCA
    printf("[Client] RDMA Write успішно виконано в апаратурі!\n");

    ibv_dereg_mr(local_mr);
    free(local_msg);
    ibv_dereg_mr(ex_mr);
    rdma_destroy_qp(id);
    ibv_destroy_cq(cq);
    ibv_dealloc_pd(pd);
    rdma_disconnect(id);
    rdma_destroy_id(id);
    rdma_destroy_event_channel(ec);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s server <port> OR %s client <ip> <port>\n", argv[0], argv[0]);
        return 1;
    }
    if (strcmp(argv[1], "server") == 0) {
        run_server(argv[2]);
    } else if (strcmp(argv[1], "client") == 0) {
        run_client(argv[2], argv[3]);
    }
    return 0;
}
