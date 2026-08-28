// Rust Daemon: цикл демона на libbpf-rs
// (у справжньому scx_rustland цю обв'язку дає crate scx_rustland_core
//  з типом BpfScheduler, який ховає і кільцевий буфер, і карту рішень)
use anyhow::Result;
use libbpf_rs::{Map, MapCore, MapFlags, RingBufferBuilder};
use std::collections::VecDeque;
use std::sync::mpsc;
use std::time::Duration;

#[repr(C)]
struct TaskQueuedEvent {
    pid: i32,
    cpu: i32,
    flags: u64,
}

fn run(ringbuf_map: &Map, decision_map: &Map) -> Result<()> {
    let mut task_queue: VecDeque<i32> = VecDeque::new();
    let (tx, rx) = mpsc::channel::<i32>();

    // Обробник кільцевого буфера лише перекидає pid у канал демона:
    // усе впорядкування робиться поза ним
    let mut builder = RingBufferBuilder::new();
    builder.add(ringbuf_map, move |data: &[u8]| {
        if data.len() >= std::mem::size_of::<TaskQueuedEvent>() {
            let ev = unsafe { &*(data.as_ptr() as *const TaskQueuedEvent) };
            let _ = tx.send(ev.pid);
        }
        0
    })?;
    let ringbuf = builder.build()?;

    println!("[scx_rustland] Демон користувача Rust успішно запущено.");

    loop {
        // 1. Вичитати накопичені події enqueue
        ringbuf.poll(Duration::from_millis(1))?;
        while let Ok(pid) = rx.try_recv() {
            task_queue.push_back(pid);
        }

        // 2. Записати рішення для вільного CPU у cpu_decision_map
        if let Some(pid) = task_queue.pop_front() {
            let cpu: u32 = 0; // тут стоїть вибір CPU власним алгоритмом
            decision_map.update(&cpu.to_ne_bytes(), &pid.to_ne_bytes(), MapFlags::ANY)?;
        }
    }
}
