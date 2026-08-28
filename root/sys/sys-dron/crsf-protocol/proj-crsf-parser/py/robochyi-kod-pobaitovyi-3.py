    # Проштовхнути ОДИН байт із UART. Кличе self.dispatch, коли кадр цілий.
    def push(self, byte):
        if self.state == CrsfState.ST_SYNC:
            # Викидаємо все, крім старту. Це і є (ре)синхронізація.
            if byte == CRSF_SYNC_BYTE:
                self.state = CrsfState.ST_LEN

        elif self.state == CrsfState.ST_LEN:
            # Перша перевірка: довжина мусить бути в діапазоні.
            if byte < CRSF_LEN_MIN or byte > CRSF_LEN_MAX:
                # Це не довжина, а сміття → назад у пошук старту.
                # Тонкість: якщо цей байт САМ є 0xC8, він міг бути справжнім
                # стартом. Тому не просто ST_SYNC, а обробимо його як старт:
                self.state = CrsfState.ST_LEN if byte == CRSF_SYNC_BYTE else CrsfState.ST_SYNC
                return
            self.buf[0] = byte   # збережемо довжину в буфер (стане в пригоді)
            self.need   = byte   # стільки байтів тіла ще прийде
            self.got    = 0
            self.state  = CrsfState.ST_BODY

        elif self.state == CrsfState.ST_BODY:
            # Добираємо тіло. buf[0] — довжина, buf[1..] — тип+дані+CRC.
            self.buf[1 + self.got] = byte
            self.got += 1
            if self.got < self.need:
                return   # кадр іще не повний — чекаємо наступних байтів

            # Кадр повний. Перевіряємо CRC над типом+даними (без самого CRC).
            type_and_payload = self.buf[1:1 + self.need - 1]   # тип+дані
            crc_calc = crsf_crc8(type_and_payload)
            crc_recv = self.buf[1 + self.need - 1]             # останній байт

            if crc_calc == crc_recv:
                # Цілий кадр! Віддаємо тіло (тип+дані+CRC) диспетчеру.
                self.dispatch(self.buf[1:1 + self.need])
            # І збіг, і промах ведуть в один бік: новий кадр з чистого аркуша.
            self.reset()
