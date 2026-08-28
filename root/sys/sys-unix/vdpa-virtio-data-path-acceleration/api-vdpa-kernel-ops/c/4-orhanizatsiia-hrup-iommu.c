/* Обидві команди — GET_VRING_GROUP і SET_GROUP_ASID — передають той самий
   загальний об'єкт vhost, а зміст полів залежить від команди: */
struct vhost_vring_state {
    unsigned int index; /* GET_VRING_GROUP: індекс черги; SET_GROUP_ASID: індекс групи */
    unsigned int num;   /* GET_VRING_GROUP: номер групи (заповнює ядро); SET_GROUP_ASID: ASID */
};

struct vhost_vdpa_iova_range {
    __u64 first; /* Перша допустима віртуальна адреса I/O */
    __u64 last;  /* Остання допустима віртуальна адреса I/O */
};
