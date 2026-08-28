/* include/uapi/linux/virtio_ring.h — розділена черга */
#define VRING_DESC_F_NEXT             1   /* маска: ланцюг триває, номер у полі next  */
#define VRING_DESC_F_WRITE            2   /* маска: у цей буфер пише пристрій         */
#define VRING_DESC_F_INDIRECT         4   /* маска: буфер сам є таблицею дескрипторів */

#define VRING_USED_F_NO_NOTIFY        1   /* пристрій → драйверові: не кікай          */
#define VRING_AVAIL_F_NO_INTERRUPT    1   /* драйвер → пристроєві: не переривай       */

/* упакована черга */
#define VRING_PACKED_DESC_F_AVAIL     7   /* НОМЕР БІТА, не маска: 1 << 7  = 0x0080   */
#define VRING_PACKED_DESC_F_USED     15   /* НОМЕР БІТА, не маска: 1 << 15 = 0x8000   */
#define VRING_PACKED_EVENT_F_WRAP_CTR 15  /* НОМЕР БІТА в структурі придушення подій  */

#define VRING_PACKED_EVENT_FLAG_ENABLE  0x0  /* не маски, а ЗНАЧЕННЯ поля desc_event_flags */
#define VRING_PACKED_EVENT_FLAG_DISABLE 0x1
#define VRING_PACKED_EVENT_FLAG_DESC    0x2  /* будити на конкретній позиції; потребує EVENT_IDX */
