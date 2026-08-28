#define MEDIA_ENT_FL_DEFAULT       (1U << 0)   /* типова сутність своєї функції */
#define MEDIA_ENT_FL_CONNECTOR     (1U << 1)   /* не блок, а рознім на платі */

#define MEDIA_PAD_FL_SINK          (1U << 0)   /* вхід: пад приймає дані */
#define MEDIA_PAD_FL_SOURCE        (1U << 1)   /* вихід: пад віддає дані */
#define MEDIA_PAD_FL_MUST_CONNECT  (1U << 2)   /* без увімкненого зв'язку не запуститься */

#define MEDIA_LNK_FL_ENABLED       (1U << 0)   /* дані течуть; єдине, що можна міняти */
#define MEDIA_LNK_FL_IMMUTABLE     (1U << 1)   /* розведено в кремнії, завжди ввімкнено */
#define MEDIA_LNK_FL_DYNAMIC       (1U << 2)   /* можна перемикати під час знімання */

#define MEDIA_LNK_FL_LINK_TYPE     (0xf << 28)          /* маска типу зв'язку */
#  define MEDIA_LNK_FL_DATA_LINK      (0U << 28)        /* пад → пад */
#  define MEDIA_LNK_FL_INTERFACE_LINK (1U << 28)        /* інтерфейс → сутність */
#  define MEDIA_LNK_FL_ANCILLARY_LINK (2U << 28)        /* фізичний зв'язок, 6.1 */
