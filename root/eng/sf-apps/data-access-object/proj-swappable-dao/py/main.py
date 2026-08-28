def find_by_id(self, id: int) -> Optional[UserRow]:
    sql = "SELECT id, email, role, active FROM users WHERE id = %s"
    try:
        with self._pool.connection() as conn:      # 1) взяти з пулу
            with conn.cursor() as cur:              # 2) курсор
                cur.execute(sql, (id,))             # параметр, не формат-рядок
                row = cur.fetchone()               # 3) прочитати
                return _map(row) if row else None
    except psycopg.Error as e:
        raise DataAccessException(f"find_by_id({id})") from e
    # обидва `with` закриють ресурс на виході — і на винятку теж
