#define _GNU_SOURCE
#include <arpa/inet.h>
#include <errno.h>
#include <ifaddrs.h>
#include <net/if.h>
#include <netinet/in.h>
#include <poll.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

#define DISC_GROUP    "239.7.7.7"
#define DISC_PORT     7711
#define PROTO_VER     1
#define HDR_LEN       40
#define PKT_MAX       512
#define REC_TTL_S     120        /* час життя запису в чужій таблиці, с */
#define ANN_PERIOD_S  40         /* період оголошень — третина життя запису */
#define REPLY_MIN_MS  20
#define REPLY_MAX_MS  120
#define RESCAN_MS     30000      /* як часто перебирати інтерфейси наново */
#define MAX_IFS       16
#define MAX_PEERS     256
#define STATE_PATH    "/var/lib/discoveryd/id"

enum { PKT_ANNOUNCE = 1, PKT_QUERY = 2, PKT_BYE = 3 };

struct self  { uint8_t id[16]; uint32_t incarnation; uint16_t port, caps; char name[64]; };
struct iface { unsigned index; char name[IF_NAMESIZE]; struct in_addr addr; };

static struct self        me;
static struct iface       ifs[MAX_IFS];
static int                nifs;
static int                sock;
static struct sockaddr_in group;

static uint64_t t_announce;    /* коли наступне оголошення */
static uint64_t t_answer;      /* 0 = відкладеної відповіді нема */
static uint64_t asked_ms;      /* коли надійшов запит, на який ми ще не відповіли */
static uint64_t answered_ms;   /* коли наш повний стан востаннє був в ефірі */
