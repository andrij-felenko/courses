use scx_utils::{scx_ops_attach, scx_ops_load, scx_ops_open};
use std::mem::MaybeUninit;

fn start() -> anyhow::Result<()> {
    let builder = BpfSkelBuilder::default();       // згенерований скелет
    let mut open_object = MaybeUninit::uninit();

    let open_skel = scx_ops_open!(builder, &mut open_object, my_ops)?;
    let mut skel = scx_ops_load!(open_skel, my_ops, uei)?;
    let _link = scx_ops_attach!(skel, my_ops)?;    // планувальник активний

    Ok(())
}
