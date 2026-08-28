import asyncio

def render(self, template, data):
    result = self._control.render(template, data)   # користувач отримує ЦЕ негайно

    if self._flags.sampled("render-shadow-percent", template):
        # Нова доганяє в тіні поза гарячим шляхом — латентності користувачеві не додає.
        async def shadow_run():
            try:
                shadow = self._candidate.render(template, data)
                if shadow != result:
                    self._log.mismatch(template=template, control=result, candidate=shadow)
            except Exception as err:
                self._log.candidate_threw(template=template, error=err)
        asyncio.get_event_loop().create_task(shadow_run())
    return result   # не чекаємо на тінь
