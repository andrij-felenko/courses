use libc::{c_uint, pid_t, syscall, SYS_sched_setattr};
use std::io::Error;
use std::mem;
use std::time::Duration;

#[repr(C)]
#[derive(Default)]
struct SchedAttr {
    size: u32,
    sched_policy: u32,
    sched_flags: u64,
    sched_nice: i32,
    sched_priority: u32,
    sched_runtime: u64,
    sched_deadline: u64,
    sched_period: u64,
}

const SCHED_DEADLINE: u32 = 6;
const SCHED_FLAG_RECLAIM: u64 = 0x02;

fn set_deadline_policy(runtime: Duration, deadline: Duration, period: Duration) -> Result<(), Error> {
    let attr = SchedAttr {
        size: mem::size_of::<SchedAttr>() as u32,
        sched_policy: SCHED_DEADLINE,
        sched_flags: SCHED_FLAG_RECLAIM,
        sched_runtime: runtime.as_nanos() as u64,
        sched_deadline: deadline.as_nanos() as u64,
        sched_period: period.as_nanos() as u64,
        ..Default::default()
    };

    let ret = unsafe {
        syscall(SYS_sched_setattr, 0 as pid_t, &attr as *const SchedAttr, 0 as c_uint)
    };

    if ret < 0 {
        Err(Error::last_os_error())
    } else {
        Ok(())
    }
}

fn main() {
    let runtime = Duration::from_millis(10);
    let period = Duration::from_millis(30);

    if let Err(err) = set_deadline_policy(runtime, period, period) {
        eprintln!("Помилка налаштування політики: {}", err);
        return;
    }

    println!("SCHED_DEADLINE успішно встановлено!");

    for _ in 0..5 {
        /* Обробка циклу реального часу */
        unsafe {
            libc::sched_yield();
        }
    }
}
