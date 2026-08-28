#undef TRACE_SYSTEM
#define TRACE_SYSTEM sample_subsys

#if !defined(_TP_SAMPLE_EVENTS_H) || defined(TRACE_HEADER_MULTI_READ)
#define _TP_SAMPLE_EVENTS_H

#include <linux/tracepoint.h>

TRACE_EVENT(sample_sensor_read,
    TP_PROTO(int sensor_id, int raw_value, const char *label),
    TP_ARGS(sensor_id, raw_value, label),
    TP_STRUCT__entry(
        __field(int, sensor_id)
        __field(int, raw_value)
        __string(label, label)
    ),
    TP_fast_assign(
        __entry->sensor_id = sensor_id;
        __entry->raw_value = raw_value;
        __assign_str(label, label);
    ),
    TP_printk("sensor_id=%d raw_val=%d label=%s",
              __entry->sensor_id, __entry->raw_value, __get_str(label))
);

#endif /* _TP_SAMPLE_EVENTS_H */

/* Цей розділ обов'язково розміщується ПОЗА межами блоку #ifndef _TP_SAMPLE_EVENTS_H */
#include <trace/define_trace.h>
