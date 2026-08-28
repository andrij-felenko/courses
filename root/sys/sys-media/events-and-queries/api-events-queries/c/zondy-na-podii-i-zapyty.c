typedef enum {
  GST_PAD_PROBE_DROP,      /* далі не пускати; рушій звільнить сам, той, хто слав, дістане TRUE */
  GST_PAD_PROBE_OK,        /* нічого не вирішую, хай працює типова поведінка */
  GST_PAD_PROBE_REMOVE,    /* зняти цей зонд, дані пропустити */
  GST_PAD_PROBE_PASS,      /* блокувальному зонду: пропустити цей елемент і стати на наступному */
  GST_PAD_PROBE_HANDLED    /* я відповів сам; подію звільняю Я, запит вважається успішним */
} GstPadProbeReturn;

#define GST_PAD_PROBE_INFO_EVENT(d)  ...
#define GST_PAD_PROBE_INFO_QUERY(d)  ...
