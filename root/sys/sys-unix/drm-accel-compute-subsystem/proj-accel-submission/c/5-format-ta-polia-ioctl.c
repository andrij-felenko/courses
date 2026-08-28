struct drm_accel_submit_op {
    __u64 flags;             /* Прапорці подання (наприклад, ACCEL_SUBMIT_FENCE_WAIT) */
    __u64 engine_idx;        /* Індекс обчислювального ядра NPU */
    __u64 cmds_ptr;          /* Вказівник у просторі користувача на масив командних буферів */
    __u32 cmd_count;         /* Кількість командних буферів у масиві */
    __u32 pad;               /* Заповнювальне поле для 64-бітного вирівнювання */
    __u64 in_syncobjs_ptr;   /* Вказівник на масив вхідних syncobj (In-fences) */
    __u32 in_syncobj_count;  /* Кількість вхідних syncobj */
    __u32 out_syncobj_count; /* Кількість вихідних syncobj */
    __u64 out_syncobjs_ptr;  /* Вказівник на масив вихідних syncobj (Out-fences) */
};
