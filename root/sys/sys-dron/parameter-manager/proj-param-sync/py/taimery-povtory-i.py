    def tick(self, now):
        if self.awaiting_list:                        # борт ще не озвався жодного разу
            if now < self.list_deadline:
                return
            if self.list_attempts > LIST_RETRIES:
                self.give_up = True
                return
            self._send_request_list()
            self.list_attempts += 1
            self.list_deadline = now + LIST_SILENCE
            return

        if not self.batch_on:
            if now < self.silence_deadline:           # потік іде — таймер тиші відсунуто
                return
            self.batch_on = True                      # замовк: вмикаємо добір

        for key, deadline in list(self.in_flight.items()):
            if now >= deadline:
                del self.in_flight[key]               # місце в пачці звільнилося
                self._ask(key[0], key[1], now)
        self._refill(now)

    def _ask(self, comp_id, index, now):
        """Спробувати номер ще раз — або здатися на ньому назавжди."""
        tries = self.waiting[comp_id].get(index)
        if tries is None:
            return                                    # уже приїхав, поки ми чекали

        tries += 1
        if tries > TRIES_PER_INDEX:                   # шоста спроба — досить
            self.failed[comp_id].add(index)
            del self.waiting[comp_id][index]
            return

        self.waiting[comp_id][index] = tries
        self._send_request_read(comp_id, index)
        self.in_flight[(comp_id, index)] = now + READ_ACK

    def _refill(self, now):
        """Дотягти пачку до десяти запитів у польоті, беручи діри за номерами."""
        for comp_id in list(self.waiting):
            for index in sorted(self.waiting[comp_id]):   # копія: _ask може стерти запис
                if len(self.in_flight) >= BATCH:
                    return                                # пачка повна
                if (comp_id, index) in self.in_flight:
                    continue                              # уже в польоті
                self._ask(comp_id, index, now)

    def _send_request_list(self):
        self.conn.mav.param_request_list_send(self.sys, mavutil.mavlink.MAV_COMP_ID_ALL)

    def _send_request_read(self, comp_id, index):
        # param_index тут int16: −1 означає «шукай за іменем», тож за номером
        # доступні лише перші 32768 параметрів.
        self.conn.mav.param_request_read_send(self.sys, comp_id, b"", index)
