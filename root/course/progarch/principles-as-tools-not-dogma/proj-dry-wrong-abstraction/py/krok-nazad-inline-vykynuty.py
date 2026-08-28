def notify_motion(ev: MotionEvent) -> None:
    text = f"Рух у зоні «{ev.zone}» о {time(ev.at)} — небезпека {ZONE_RISK.get(ev.zone, 0)}"
    send_via("sms", text)
    send_via("push", text)
    schedule_repeat(text, ["sms", "push"])       # доки власник не підтвердить

def notify_offline(ev: OfflineEvent) -> None:
    text = (f"Пристрій «{ev.device}» офлайн о {time(ev.at)} "
            f"— останній зв'язок {since_min(ev.at)} хв тому")
    send_via("push", text)                        # тихий одноразовий
