# 📋 Виклики подання: структури, прапорці й коди помилок чотирьох драйверів

Тут зібрано точні поля, номери й прапорці того `ioctl`, яким програма віддає драйверові пакет команд, — одразу для чотирьох живих драйверів: amdgpu, i915, msm і Xe. Покладені поруч, вони показують, що розходяться інтерфейси рівно там, де розходяться моделі пам'яті й планування, а в усьому іншому переказують ту саму п'ятірку понять. Джерело — uapi ядра 6.x (`include/uapi/drm/*.h`).

## П'ять речей, які несе будь-яке подання

| що передається | amdgpu | i915 | msm | Xe |
|---|---|---|---|---|
| виклик | `DRM_IOCTL_AMDGPU_CS` | `DRM_IOCTL_I915_GEM_EXECBUFFER2` | `DRM_IOCTL_MSM_GEM_SUBMIT` | `DRM_IOCTL_XE_EXEC` |
| номер (від `DRM_COMMAND_BASE` = `0x40`) | `+0x04` | `+0x29` | `+0x06` | `+0x09` |
| хто виконує | `ctx_id` + `ip_type`/`ring` у шматку IB | `rsvd1` (номер контексту) + біти рушія у `flags` | `queueid` + `MSM_PIPE_*` | `exec_queue_id` |
| де пакет | `va_start` — адреса в просторі контексту | номер об'єкта в масиві + `batch_start_offset` | елемент масиву `cmds` | `address` — адреса в просторі VM |
| перелік буферів | `bo_list_handle` **або** шматок `BO_HANDLES` | масив `exec_object2` — обов'язковий | масив `submit_bo` | **нема** — усе прив'язано наперед через `VM_BIND` |
| вхідні огорожі | шматки `DEPENDENCIES`, `SYNCOBJ_IN`, `SYNCOBJ_TIMELINE_WAIT` | `FENCE_IN` (дескриптор) або `FENCE_ARRAY` (комірки) | `in_syncobjs` | елементи `syncs` без `SIGNAL` |
| вихідна огорожа | `SYNCOBJ_OUT`, `SYNCOBJ_TIMELINE_SIGNAL`, `out.handle` | `FENCE_OUT` (дескриптор) або `FENCE_SIGNAL` у масиві | `fence_fd`, `out_syncobjs` | елементи `syncs` із `SIGNAL` |

Порожня клітинка в рядку Xe — не пропуск, а весь сенс цього драйвера: перелік буферів пішов у окремий виклик `DRM_IOCTL_XE_VM_BIND`, і подання перестало залежати від кількості об'єктів, яких торкається кадр.

## amdgpu: масив шматків

Виклик подання один, а от кількість того, що в нього можна вкласти, росла роками. Тому аргумент влаштовано як список різнорідних шматків (англ. *chunk*), кожен зі своїм номером типу: старе ядро просто не впізнає нового номера й відмовить, а не прочитає чуже поле не за тим зсувом.

```c
/* include/uapi/drm/amdgpu_drm.h */
union drm_amdgpu_cs {
    struct { __u32 ctx_id, bo_list_handle, num_chunks, flags;
             __u64 chunks;   /* ← вказівник на масив ВКАЗІВНИКІВ на шматки */ } in;
    struct { __u64 handle;   /* номер поданого завдання в межах ctx_id     */ } out;
};

struct drm_amdgpu_cs_chunk { __u32 chunk_id; __u32 length_dw; __u64 chunk_data; };
```

Два місця, де програми спотикаються: `chunks` — подвійна непряма адресація (масив `__u64`, кожен елемент якого веде на свою `drm_amdgpu_cs_chunk`), а `length_dw` рахує **подвійні слова**, тобто `sizeof(структури) / 4`, а не байти.

| `chunk_id` | структура даних | навіщо |
|---|---|---|
| `AMDGPU_CHUNK_ID_IB` `0x01` | `drm_amdgpu_cs_chunk_ib` | сам пакет: адреса, довжина, рушій |
| `AMDGPU_CHUNK_ID_FENCE` `0x02` | `drm_amdgpu_cs_chunk_fence { __u32 handle, offset; }` | куди в пам'яті записати номер по завершенні |
| `AMDGPU_CHUNK_ID_DEPENDENCIES` `0x03` | `drm_amdgpu_cs_chunk_dep` | чекати на завдання іншого контексту за його номером |
| `AMDGPU_CHUNK_ID_SYNCOBJ_IN` `0x04` | `drm_amdgpu_cs_chunk_syncobj` | чекати на комірки синхронізації |
| `AMDGPU_CHUNK_ID_SYNCOBJ_OUT` `0x05` | те саме | зарядити комірки вихідною огорожею |
| `AMDGPU_CHUNK_ID_BO_HANDLES` `0x06` | `drm_amdgpu_bo_list_in` | перелік буферів просто в поданні, без наперед створеного списку |
| `AMDGPU_CHUNK_ID_SCHEDULED_DEPENDENCIES` `0x07` | `drm_amdgpu_cs_chunk_dep` | чекати не на виконання, а лише на **подання** залежності |
| `AMDGPU_CHUNK_ID_SYNCOBJ_TIMELINE_WAIT` `0x08` | `drm_amdgpu_cs_chunk_syncobj` | те саме для шкал: у `point` — позначка |
| `AMDGPU_CHUNK_ID_SYNCOBJ_TIMELINE_SIGNAL` `0x09` | те саме | зарядити позначку шкали |
| `AMDGPU_CHUNK_ID_CP_GFX_SHADOW` `0x0a` | `drm_amdgpu_cs_chunk_cp_gfx_shadow` | буфери під збереження стану рушія |

```c
struct drm_amdgpu_cs_chunk_ib {
    __u32 _pad, flags;      /* AMDGPU_IB_FLAG_*                      */
    __u64 va_start;         /* адреса пакета у просторі контексту    */
    __u32 ib_bytes;         /* довжина в БАЙТАХ (на відміну від length_dw) */
    __u32 ip_type;          /* AMDGPU_HW_IP_GFX 0, COMPUTE 1, DMA 2,
                               UVD 3, VCE 4, UVD_ENC 5, VCN_DEC 6,
                               VCN_ENC 7, VCN_JPEG 8, VPE 9          */
    __u32 ip_instance, ring;
};

struct drm_amdgpu_cs_chunk_dep    { __u32 ip_type, ip_instance, ring, ctx_id; __u64 handle; };
struct drm_amdgpu_cs_chunk_syncobj{ __u32 handle, flags; __u64 point; };
```

Із прапорців IB на практиці видно два: `AMDGPU_IB_FLAG_PREEMPT` (`1<<2`) дозволяє витіснити цей пакет, `AMDGPU_IB_FLAGS_SECURE` (`1<<5`) позначає захищений вміст; решта (`CE`, `PREAMBLE`, `TC_WB_NOT_INVALIDATE`, `RESET_GDS_MAX_WAVE_ID`, `EMIT_MEM_SYNC`) — тонкощі, які ставить драйвер простору користувача.

**Мінімальний виклик** — пакет уже лежить у пам'яті й прив'язаний до простору контексту через `DRM_IOCTL_AMDGPU_GEM_VA`:

```c
struct drm_amdgpu_cs_chunk_ib      ib  = { .va_start = va, .ib_bytes = pkt_bytes,
                                           .ip_type  = AMDGPU_HW_IP_GFX };
struct drm_amdgpu_cs_chunk_syncobj sig = { .handle = out_syncobj };

struct drm_amdgpu_cs_chunk chunks[2] = {
    { AMDGPU_CHUNK_ID_IB,          sizeof(ib)  / 4, (uintptr_t)&ib  },
    { AMDGPU_CHUNK_ID_SYNCOBJ_OUT, sizeof(sig) / 4, (uintptr_t)&sig },
};
uint64_t ptrs[2] = { (uintptr_t)&chunks[0], (uintptr_t)&chunks[1] };

union drm_amdgpu_cs cs = { .in = { .ctx_id = ctx_id, .num_chunks = 2,
                                   .chunks = (uintptr_t)ptrs } };

int r = drmIoctl(fd, DRM_IOCTL_AMDGPU_CS, &cs);
/* r == 0 → cs.out.handle — номер завдання; огорожа сама лягла в out_syncobj */
```

## i915: EXECBUFFER2 і поля, що змінили значення

Тут структура одна й незмінна з 2010 року, тому кожне нове поняття доводилося вкладати в наявні поля. Читати цю структуру треба, тримаючи в голові, що половина назв бреше.

```c
struct drm_i915_gem_execbuffer2 {
    __u64 buffers_ptr;         /* масив drm_i915_gem_exec_object2 */
    __u32 buffer_count, batch_start_offset, batch_len;
    __u32 DR1, DR4;            /* мертві з часів DRI1 */
    __u32 num_cliprects;       /* ← довжина масиву огорож при FENCE_ARRAY */
    __u64 cliprects_ptr;       /* ← масив drm_i915_gem_exec_fence або розширення */
    __u64 flags;               /* I915_EXEC_* */
    __u64 rsvd1;               /* ← номер контексту */
    __u64 rsvd2;               /* ← молодші 32 біти: вхідний sync_file fd
                                     старші 32 біти: вихідний sync_file fd */
};
```

Пакет команд i915 не має власного поля: ним служить **останній** об'єкт у масиві `buffers_ptr` — або перший, якщо стоїть `I915_EXEC_BATCH_FIRST` (`1<<18`).

```c
struct drm_i915_gem_exec_object2 {
    __u32 handle, relocation_count;
    __u64 relocs_ptr, alignment;
    __u64 offset;   /* при EXEC_OBJECT_PINNED — адреса, яку ЗАДАЄ програма;
                       інакше ядро вписує сюди поточну, для наступного разу */
    __u64 flags;
    union { __u64 rsvd1; __u64 pad_to_size; };
    __u64 rsvd2;
};
```

| прапорець об'єкта | біт | зміст |
|---|---|---|
| `EXEC_OBJECT_WRITE` | `1<<2` | пакет **пише** в цей буфер — від цього залежить неявна синхронізація з чужими читачами |
| `EXEC_OBJECT_SUPPORTS_48B_ADDRESS` | `1<<3` | об'єкт можна класти вище за 4 ГіБ |
| `EXEC_OBJECT_PINNED` | `1<<4` | адресу обрала програма, ядро не рухає й не править |
| `EXEC_OBJECT_PAD_TO_SIZE` | `1<<5` | зарезервувати за об'єктом ще й дірку до `pad_to_size` |
| `EXEC_OBJECT_ASYNC` | `1<<6` | **не** чекати чужих огорож на цьому буфері — синхронізує програма сама |
| `EXEC_OBJECT_CAPTURE` | `1<<7` | зберегти вміст у дамп, якщо це подання зависне |
| `EXEC_OBJECT_NEEDS_FENCE`, `NEEDS_GTT` | `1<<0`, `1<<1` | спадок старих поколінь |

| прапорець виклику | біт | зміст |
|---|---|---|
| `I915_EXEC_RING_MASK` | `0x3f` | рушій: `RENDER` 1, `BSD` 2, `BLT` 3, `VEBOX` 4 |
| `I915_EXEC_NO_RELOC` | `1<<11` | адреси в `offset` правдиві — правку пропустити |
| `I915_EXEC_HANDLE_LUT` | `1<<12` | у правках адрес номер об'єкта — це індекс у масиві, а не GEM-номер |
| `I915_EXEC_FENCE_IN` / `FENCE_OUT` | `1<<16` / `1<<17` | вхідний і вихідний `sync_file` у половинках `rsvd2` |
| `I915_EXEC_BATCH_FIRST` | `1<<18` | пакет — перший об'єкт масиву, а не останній |
| `I915_EXEC_FENCE_ARRAY` | `1<<19` | `cliprects_ptr` — масив комірок синхронізації |
| `I915_EXEC_FENCE_SUBMIT` | `1<<20` | чекати не на виконання залежності, а лише на її подання |
| `I915_EXEC_USE_EXTENSIONS` | `1<<21` | `cliprects_ptr` веде на ланцюг розширень (зокрема шкали) |

```c
struct drm_i915_gem_exec_fence { __u32 handle; __u32 flags; };
#define I915_EXEC_FENCE_WAIT   (1<<0)   /* дочекатися комірки  */
#define I915_EXEC_FENCE_SIGNAL (1<<1)   /* зарядити комірку    */
```

Щоб `FENCE_OUT` спрацював, кликати треба `DRM_IOCTL_I915_GEM_EXECBUFFER2_WR`: номер команди в нього той самий, а от напрямок — `DRM_IOWR` замість `DRM_IOW`, тобто ядру дозволено писати в структуру назад.

## msm: усе прапорцями

```c
struct drm_msm_gem_submit {          /* DRM_MSM_GEM_SUBMIT = 0x06 */
    __u32 flags;                     /* MSM_PIPE_* | MSM_SUBMIT_* */
    __u32 fence;                     /* out: номер у черзі        */
    __u32 nr_bos, nr_cmds;
    __u64 bos, cmds;
    __s32 fence_fd;                  /* in/out sync_file          */
    __u32 queueid;
    __u64 in_syncobjs, out_syncobjs;
    __u32 nr_in_syncobjs, nr_out_syncobjs, syncobj_stride, pad;
};

struct drm_msm_syncobj { __u32 handle, flags; __u64 point; };  /* MSM_SYNCOBJ_RESET 0x1 */
```

| прапорець | значення | зміст |
|---|---|---|
| `MSM_SUBMIT_NO_IMPLICIT` | `0x80000000` | не чекати чужих огорож на буферах — уся синхронізація явна |
| `MSM_SUBMIT_FENCE_FD_IN` / `_OUT` | `0x40000000` / `0x20000000` | `fence_fd` читається / заповнюється |
| `MSM_SUBMIT_SYNCOBJ_IN` / `_OUT` | `0x08000000` / `0x04000000` | масиви комірок задіяно |
| `MSM_SUBMIT_FENCE_SN_IN` | `0x02000000` | номер у полі `fence` задає програма, а не ядро |

`syncobj_stride` — не надмірність, а спосіб дожити до наступної версії: програма каже, який у неї крок масиву, і ядро зі старшою структурою читає чужі, коротші елементи без перекомпіляції.

## Xe: прив'язка окремо, подання окремо

```c
struct drm_xe_exec {                  /* DRM_XE_EXEC = 0x09, DRM_IOW  */
    __u64 extensions;
    __u32 exec_queue_id, num_syncs;   /* черга виконання й довжина syncs */
    __u64 syncs;                      /* масив drm_xe_sync            */
    __u64 address;                    /* адреса пакета у просторі VM  */
    __u16 num_batch_buffer; __u16 pad[3]; __u64 reserved[2];
};

struct drm_xe_sync {
    __u64 extensions;
    __u32 type;    /* SYNCOBJ 0x0, TIMELINE_SYNCOBJ 0x1, USER_FENCE 0x2 */
    __u32 flags;   /* DRM_XE_SYNC_FLAG_SIGNAL (1<<0): заряджаємо, а не чекаємо */
    union { __u32 handle; __u64 addr; };
    __u64 timeline_value;  __u64 reserved[2];
};
```

Один масив замість трьох різних полів: напрям задає біт `SIGNAL`, а вид — поле `type`. Третій вид, `USER_FENCE`, огорожею DRM не є взагалі — це просто адреса в пам'яті, куди залізо запише число; чекають на неї окремим викликом `DRM_IOCTL_XE_WAIT_USER_FENCE`, не заходячи в підсистему огорож.

Адресний простір наповнює `DRM_IOCTL_XE_VM_BIND` — і він теж бере масив `syncs`, бо прив'язка сама по собі асинхронна:

```c
struct drm_xe_vm_bind_op {
    __u64 extensions; __u32 obj; __u16 pat_index, pad;
    union { __u64 obj_offset, userptr; __s64 cpu_addr_mirror_offset; };
    __u64 range, addr;
    __u32 op;    /* MAP 0x0, UNMAP 0x1, MAP_USERPTR 0x2, UNMAP_ALL 0x3, PREFETCH 0x4 */
    __u32 flags; /* READONLY 1<<0, IMMEDIATE 1<<1, NULL 1<<2, DUMPABLE 1<<3, … */
    __u32 prefetch_mem_region_instance, pad2; __u64 reserved[3];
};
```

`DRM_XE_VM_BIND_FLAG_NULL` створює прив'язку без об'єкта: читання дає нулі, запис зникає. Це дешевий спосіб віддати шейдерові адресу, яка гарантовано не впаде, замість справжнього буфера-заглушки.

## Комірки синхронізації в поданні

Сам об'єкт `drm_syncobj` — спільний для всіх драйверів, і його власні виклики (`DRM_IOCTL_SYNCOBJ_CREATE`, `_HANDLE_TO_FD`, `_WAIT`, `_TIMELINE_WAIT`, `_QUERY`, `_TRANSFER`) розібрано [в описі огорож](book:unix-linux/dma-fence-sync/api-fence-interfaces.md). Різняться драйвери лише тим, як беруть його **всередині подання**:

| | звичайна комірка | шкала (timeline) | вихідна огорожа як дескриптор |
|---|---|---|---|
| amdgpu | `SYNCOBJ_IN` / `SYNCOBJ_OUT` | `SYNCOBJ_TIMELINE_WAIT` / `_SIGNAL`, позначка в `point` | `DRM_IOCTL_AMDGPU_FENCE_TO_HANDLE`, `what = GET_SYNC_FILE_FD` |
| i915 | `FENCE_ARRAY` + `FENCE_WAIT`/`FENCE_SIGNAL` | розширення `TIMELINE_FENCES` при `USE_EXTENSIONS` | `FENCE_OUT` у старших бітах `rsvd2` |
| msm | `in_syncobjs` / `out_syncobjs` | `point` у `drm_msm_syncobj` | `fence_fd` при `FENCE_FD_OUT` |
| Xe | `syncs`, `type = SYNCOBJ` | `type = TIMELINE_SYNCOBJ`, `timeline_value` | окремим `HANDLE_TO_FD` над зарядженою коміркою |

Спільна дрібниця, яка вирішує половину помилок: усі чотири вміють **чекати на ще не подану** роботу — amdgpu через `SCHEDULED_DEPENDENCIES` і `WAIT_FOR_SUBMIT`, i915 через `FENCE_SUBMIT`, Xe й msm через позначку шкали, яку ще ніхто не зарядив. Без цього два потоки, що подають роботу одне одному назустріч, зобов'язані впорядковувати себе самі.

## Контекст, черга й пріоритет

| | створення | пріоритет | межа для непривілейованого |
|---|---|---|---|
| amdgpu | `DRM_IOCTL_AMDGPU_CTX`, `op = AMDGPU_CTX_OP_ALLOC_CTX` | поле `priority`: `VERY_LOW` −1023, `LOW` −512, `NORMAL` 0, `HIGH` 512, `VERY_HIGH` 1023; `UNSET` = −2048 | вище `NORMAL` — потрібен `CAP_SYS_NICE` або права майстра DRM, інакше `-EACCES` |
| i915 | `DRM_IOCTL_I915_GEM_CONTEXT_CREATE_EXT` | `SETPARAM`, `I915_CONTEXT_PARAM_PRIORITY` (`0x6`), суцільний діапазон −1023…1023 | вище нуля — `CAP_SYS_NICE` |
| msm | `DRM_MSM_SUBMITQUEUE_NEW`, `drm_msm_submitqueue` | поле `prio`, **менше число — вищий пріоритет**; стелю дає драйвер (кільця × рівні планувальника) | поза стелею — `-EINVAL` |
| Xe | `DRM_IOCTL_XE_EXEC_QUEUE_CREATE` | розширення `SET_PROPERTY_PRIORITY`: `LOW`, `NORMAL`, `HIGH`, `KERNEL` | вище `NORMAL` — `CAP_SYS_NICE`, інакше `-EPERM`; `KERNEL` програмі недоступний ніколи |

Право на високий пріоритет скрізь спирається на [можливості процесу](book:unix-linux/capabilities), а не на права файла вузла: сам собою відкритий `/dev/dri/renderD128` дає лише право рахувати, не право випереджати сусідів.

## Що бачить програма, коли зламалося

| код | звідки | що сталося |
|---|---|---|
| `-ENODEV` | будь-який `ioctl` після `drm_dev_unplug()` | пристрою більше немає фізично: зовнішній GPU від'єднали, драйвер вивантажили |
| `-ECANCELED` | amdgpu `CS`; Xe `EXEC` | контекст пережив скидання: в amdgpu покоління контексту розійшлося з поколінням його адресного простору, у Xe чергу подання скинуто або її VM забанено |
| `-EIO` | i915 `EXECBUFFER2` | чип заклинено (wedged) або контекст забанено після зависання |
| `-ENOENT` | усі | немає такого контексту чи GEM-номера |
| `-EINVAL` | усі | невідомий прапорець, ненульове `pad`, шматок невідомого типу — головний спосіб, яким ядро каже «твоя програма новіша за це ядро» |
| `-ETIME` | `DRM_IOCTL_SYNCOBJ_WAIT` | вийшов час очікування; сама огорожа жива |
| `-ERESTARTSYS` | очікування | виклик перервано сигналом, треба повторити |

Три перші коди — це одне й те саме для прикладної програми: у Vulkan вони всі стають `VK_ERROR_DEVICE_LOST`, і після них жоден дескриптор старого контексту вже не годиться.

> 🔧 **Навіщо це.** «Пристрій утрачено» не каже, чия провина, — а це різні дії. Якщо винні ви, повторне подання того самого пакета вб'є контекст удруге; якщо ви лише постраждали, повторити варто. Тому кожен драйвер має окремий запит статистики: amdgpu — `AMDGPU_CTX_OP_QUERY_STATE2` (біти `GUILTY`, `VRAMLOST`, `RESET_IN_PROGRESS`, поле `reset_status` зі значеннями `NO_RESET` 0, `GUILTY_RESET` 1, `INNOCENT_RESET` 2, `UNKNOWN_RESET` 3); i915 — `DRM_IOCTL_I915_GET_RESET_STATS`, де `batch_active` рахує втрачені **під час виконання** пакети цього контексту, а `batch_pending` — втрачені в черзі, тобто невинні; msm — `MSM_SUBMITQUEUE_PARAM_FAULTS`; Xe — `DRM_XE_EXEC_QUEUE_GET_PROPERTY_BAN`. Саме на ці числа спираються `GL_ARB_robustness` і `VK_EXT_device_fault`, коли повідомляють програмі, чи скидати їй ресурси, чи мовчки відновлюватися.

Прапорці й `pad` в усіх чотирьох інтерфейсах перевіряються суворо: невідомий біт — це `-EINVAL`, а не мовчазне ігнорування ([правило кодування самого номера команди](book:unix-linux/ioctl-interface/api-ioctl-encoding.md) тут ні до чого — розмір структури в номері збігається, а зміст ядро не влаштовує). Тому обнуляти всю структуру перед заповненням — не гігієна, а умова роботи на ядрі, старшому за вашу програму.
