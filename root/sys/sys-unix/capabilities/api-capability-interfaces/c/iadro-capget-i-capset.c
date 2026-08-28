typedef struct __user_cap_header_struct {
    __u32 version;      /* яку версію структури даних вживаємо */
    int   pid;          /* 0 = сам потік */
} *cap_user_header_t;

typedef struct __user_cap_data_struct {
    __u32 effective;
    __u32 permitted;
    __u32 inheritable;
} *cap_user_data_t;
