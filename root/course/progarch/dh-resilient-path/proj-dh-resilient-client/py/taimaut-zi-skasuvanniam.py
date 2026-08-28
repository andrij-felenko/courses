# Спільна мова помилок: прапорець retryable тече ВГОРУ по стосу.
import asyncio


class TimeoutErr(Exception):
    retryable = True


class Upstream5xx(Exception):
    retryable = True
    def __init__(self, status): super().__init__(f"5xx {status}"); self.status = status


class Upstream4xx(Exception):
    retryable = False
    def __init__(self, status): super().__init__(f"4xx {status}"); self.status = status


def is_retryable(e) -> bool:
    return getattr(e, "retryable", False)


# ТАЙМАУТ: wait_for скасовує внутрішню корутину, а не кидає її напризволяще.
async def with_timeout(seconds, fn):
    try:
        return await asyncio.wait_for(fn(), seconds)
    except asyncio.TimeoutError:
        raise TimeoutErr()


# ПОВТОР: до tries спроб, поки помилка ВАРТА повтору. Останню відмову — кидає далі
# (не ковтає!), тож її бачить запобіжник, що стоїть зовні.
async def with_retry(tries, fn):
    last = None
    for i in range(tries):
        try:
            return await fn()
        except Exception as e:
            last = e
            if not is_retryable(e) or i == tries - 1:
                raise
    raise last
