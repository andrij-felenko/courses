#define XIDDATASIZE 128 /* максимальний розмір буфера даних */
#define MAXGTRIDSIZE 64 /* максимальний розмір глобального ID */
#define MAXBQUALSIZE 64 /* максимальний розмір кваліфікатора гілки */

struct xid_t {
    long formatID;          /* формат ідентифікатора (-1 = null, 0 = OSI CCR, >0 = вендор) */
    long gtrid_length;      /* довжина глобального ідентифікатора транзакції (1..64) */
    long bqual_length;      /* довжина кваліфікатора гілки транзакції (1..64) */
    char data[XIDDATASIZE]; /* масив байтів: gtrid + bqual */
};
typedef struct xid_t XID;
