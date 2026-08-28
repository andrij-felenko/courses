/* wqdemo.c — символьний пристрій із чергою очікування */
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/slab.h>
#include <linux/spinlock.h>
#include <linux/wait.h>
#include <linux/sched.h>
#include <linux/poll.h>
#include <linux/timer.h>
#include <linux/jiffies.h>
#include <linux/uaccess.h>

#define RING_SIZE   4096u   /* степінь двійки: маска замість ділення */
#define CHUNK        256u   /* стільки байтів обслуговує один виклик */

struct wqdemo {
    spinlock_t         lock;    /* захищає кільце; його бере й таймер */
    char              *ring;
    unsigned int       head;    /* куди писати — лічильник, що не обгортається */
    unsigned int       tail;    /* звідки читати */

    wait_queue_head_t  readq;   /* тут сплять ті, кому бракує байтів */
    wait_queue_head_t  writeq;  /* а тут — ті, кому бракує місця */

    struct timer_list  tick;
    unsigned long      seq;

    struct cdev        cdev;
};

static struct wqdemo *dev;
static dev_t          devt;
static struct class  *cls;

static bool exclusive;
module_param(exclusive, bool, 0644);
MODULE_PARM_DESC(exclusive, "читачі стають у чергу виключними: будити по одному");

static unsigned int period_ms;
module_param(period_ms, uint, 0444);
MODULE_PARM_DESC(period_ms, "період таймера в мілісекундах; 0 — таймер вимкнено");
