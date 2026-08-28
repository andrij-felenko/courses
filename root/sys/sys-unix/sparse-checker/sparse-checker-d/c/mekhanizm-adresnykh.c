// include/linux/compiler_types.h, форма з номерами просторів (ядра до 5.4 включно)
#ifdef __CHECKER__
# define __user     __attribute__((noderef, address_space(1)))
# define __iomem    __attribute__((noderef, address_space(2)))
# define __rcu      __attribute__((noderef, address_space(4)))
#else
# define __user
# define __iomem
# define __rcu
#endif
