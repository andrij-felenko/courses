// Rust Реалізація завантажувача з використанням фреймворку scx_utils
use anyhow::Result;
use scx_utils::{scx_ops_attach, scx_ops_load, scx_ops_open, uei_read};
use std::mem::MaybeUninit;
use std::thread;
use std::time::Duration;

fn main() -> Result<()> {
    let builder = BpfSkelBuilder::default();        // згенерований скелет scx_simple
    let mut open_object = MaybeUninit::uninit();

    // Відкриття, завантаження та підключення struct_ops до ядра
    let open_skel = scx_ops_open!(builder, &mut open_object, simple_ops)?;
    let mut skel = scx_ops_load!(open_skel, simple_ops, uei)?;
    let link = scx_ops_attach!(skel, simple_ops)?;  // планувальник активний

    println!("[Loader Rust] BPF-планувальник успішно підключено до ядра.");
    thread::sleep(Duration::from_secs(2));

    // Знімаємо struct_ops і читаємо причину, з якої ядро зупинило планувальник
    drop(link);
    let uei = uei_read!(&skel, uei)?;
    println!("[Loader Rust] Завершення демона; перезапуск потрібен: {}", uei.should_restart());
    Ok(())
}
