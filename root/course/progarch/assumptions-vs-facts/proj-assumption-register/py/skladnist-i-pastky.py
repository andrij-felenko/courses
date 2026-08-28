# знак живий, лише коли за ним стежить справжній монітор із власником
WIRED = {
    "A-wifi": "grafana: wifi_drop_ratio > 0.05  (власник: платформа)",
    # A-open-daily — знака ще нікуди не підключено!
}

def unwatched(reg):
    """Прийняті припущення, чий знак ніде не наглядається."""
    return [a.id for a in reg
            if a.state is State.ACCEPTED and a.id not in WIRED]
