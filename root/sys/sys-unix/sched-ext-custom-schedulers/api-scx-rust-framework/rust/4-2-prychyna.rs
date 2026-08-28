use scx_utils::{uei_exited, uei_read};

fn wait_and_report(skel: &BpfSkel) -> anyhow::Result<()> {
    // Прапорець виставляє ядро в момент вивантаження планувальника
    while !uei_exited!(&skel, uei) {
        std::thread::sleep(std::time::Duration::from_millis(100));
    }

    let uei = uei_read!(&skel, uei)?;
    if uei.should_restart() {
        println!("Ядро попросило перезапустити планувальник");
    }
    Ok(())
}
