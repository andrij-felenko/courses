    def on_param_value(self, comp_id, m, now):
        # ArduPilot ллє незапитані значення ще ДО відповіді на запит списку,
        # і номера в них немає — поле дорівнює 65535.
        if m.param_index == 65535 and self.awaiting_list:
            return

        if comp_id not in self.total:                   # перше значення від компонента
            self.total[comp_id] = m.param_count
            self.waiting[comp_id] = {i: 0 for i in range(m.param_count)}

        # pymavlink уже зібрав ім'я з 16 байтів і прибрав хвіст із нулів
        self.got[comp_id][m.param_id] = (m.param_value, m.param_type)

        self.awaiting_list = False
        self.silence_deadline = now + STREAM_SILENCE    # таймер тиші — з нуля

        if m.param_index < self.total[comp_id]:         # викреслюємо комірку
            self.waiting[comp_id].pop(m.param_index, None)
            self.in_flight.pop((comp_id, m.param_index), None)

        if self.batch_on:
            self._refill(now)   # місце звільнилося — одразу беремо наступну діру
