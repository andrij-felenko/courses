use libbpf_rs::RingBufferBuilder;
use std::time::Duration;

fn poll_events(map: &libbpf_rs::Map) -> anyhow::Result<()> {
    let mut builder = RingBufferBuilder::new();

    builder.add(map, |data: &[u8]| {
        // Безпечна інтерпретація сирих байтів у структуру події
        if data.len() >= std::mem::size_of::<SchedEvent>() {
            let event = unsafe { &*(data.as_ptr() as *const SchedEvent) };
            println!("Отримано подію для PID: {}", event.pid);
        }
        0
    })?;
    let ringbuf = builder.build()?;

    loop {
        // Опитування буфера з тайм-аутом 10 мілісекунд
        ringbuf.poll(Duration::from_millis(10))?;
    }
}
