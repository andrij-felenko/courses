Kind = Literal["motion", "offline", "lowbat"]

# метод відростив ще й параметр zone і третій kind
def notify(kind: Kind, subject: str, zone: str, at: float) -> None:
    # 1) тіло тексту — розвилка на kind
    if kind == "motion":
        text = f"Рух у зоні «{zone}» о {time(at)}"
    elif kind == "offline":
        text = f"Пристрій «{subject}» офлайн о {time(at)}"
    else:
        text = f"Батарея «{subject}» сідає"

    # 2) хвіст тексту — знову розвилка на kind
    if kind == "motion":
        text += f" — небезпека {ZONE_RISK.get(zone, 0)}"
    if kind == "offline":
        text += f" — останній зв'язок {since_min(at)} хв тому"

    # 3) канали — розвилка
    channels = ["sms", "push"] if kind == "motion" else ["push"]

    # 4) повтор — розвилка
    repeat = kind == "motion"

    for ch in channels:
        send_via(ch, text)
    if repeat:
        schedule_repeat(text, channels)
