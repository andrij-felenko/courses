/* echo_epoll.c — той самий протокол: один потік, epoll і O_NONBLOCK.
 * gcc -O2 -Wall -Wextra -o echo_epoll echo_epoll.c
 */
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <unistd.h>

#define PORT      9000
#define MAX_BODY  (64u * 1024u)
#define MAX_OUT   (1u << 20)      /* стеля вихідної черги: 1 МіБ на з'єднання */
#define MAX_EV    64

enum phase { PH_HEADER, PH_BODY };

struct conn {
    int        fd;
    enum phase phase;         /* колишня адреса повернення в serve()        */

    char       hdr[4];        /* колишня локальна hdr                       */
    size_t     hdr_got;       /* колишні p/n усередині read_full(заголовок) */

    char      *body;          /* колишній malloc у кадрі serve()            */
    size_t     body_len;      /* колишня локальна len                       */
    size_t     body_got;      /* колишні p/n усередині read_full(тіло)      */

    char      *out;           /* вихідна черга — у блокуючій версії не існувала */
    size_t     out_cap;
    size_t     out_len;
    size_t     out_off;       /* колишні p/n усередині write_full           */

    int        want_write;    /* чи стоїть EPOLLOUT у масці просто зараз    */
};
