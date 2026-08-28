// BPF kernel space - C only (виняток §5 AUTHORING: простір ядра Linux)
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

// 1. Оголошення застарілого Perf Event Array
struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(int));
    __uint(value_size, sizeof(int));
    __uint(max_entries, 0); // 0 означає автовизначення за кількістю ядер CPU
} perf_map SEC(".maps");

// 2. Оголошення сучасного BPF Ring Buffer
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 1024 * 1024); // 1 МБ заповнюваного буфера для всіх CPU
} ringbuf_map SEC(".maps");
