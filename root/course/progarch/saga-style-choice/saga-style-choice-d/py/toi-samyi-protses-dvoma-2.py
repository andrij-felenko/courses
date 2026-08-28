# ОРКЕСТРАЦІЯ: увесь процес — в одному місці, читається як розповідь.
async def enroll_device(home_id, device_id):
    undo = []
    try:
        await registry.reserve(device_id, home_id);   undo.append(lambda: registry.unreserve(device_id))
        await hub.push_config(home_id, device_id);    undo.append(lambda: hub.wipe_config(home_id, device_id))
        await billing.start_meter(home_id, device_id); undo.append(lambda: billing.stop_meter(home_id, device_id))
    except Exception:
        for step in reversed(undo):  await step()      # компенсації — точно у зворотному порядку
        raise
