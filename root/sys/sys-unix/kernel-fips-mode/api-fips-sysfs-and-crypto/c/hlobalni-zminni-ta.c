#ifdef CONFIG_CRYPTO_FIPS
extern int fips_enabled;
extern struct atomic_t fips_fail;

void fips_fail_notify(void);
int fips_post_failed(void);
#else
#define fips_enabled 0
static inline void fips_fail_notify(void) {}
static inline int fips_post_failed(void) { return 0; }
#endif
