import json

# Порівнюємо СУТЬ, а не сирий вихід: нормалізуємо все, що законно різне
def same_notification(a: "Notification", b: "Notification") -> bool:
    def canon(n):
        return {
            "to": n.to,
            "body": n.body.strip(),
            # мітку часу й згенерований id викидаємо — вони МУСЯТЬ різнитися
            "attachments": sorted(n.attachments),   # порядок несуттєвий → сортуємо
        }
    return json.dumps(canon(a), sort_keys=True) == json.dumps(canon(b), sort_keys=True)
