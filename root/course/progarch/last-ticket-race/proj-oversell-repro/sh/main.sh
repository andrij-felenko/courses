# 1. Підняти Postgres у контейнері (зникне після зупинки — --rm)
docker run --rm -d --name race-pg \
  -e POSTGRES_USER=race -e POSTGRES_PASSWORD=race -e POSTGRES_DB=race \
  -p 5432:5432 postgres:17

# 2. Схема: одне місце + окрема таблиця-СВІДОК проданого
docker exec -i race-pg psql -U race -d race <<'SQL'
CREATE TABLE events   (id int PRIMARY KEY, seats_left int NOT NULL);
CREATE TABLE bookings (id bigserial PRIMARY KEY, event_id int NOT NULL, buyer int NOT NULL);
INSERT INTO events (id, seats_left) VALUES (1, 1);   -- рівно ОДНЕ місце
SQL
