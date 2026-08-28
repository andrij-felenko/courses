-- Встановлюємо унікальний симетричний ключ орендаря для поточної транзакції
SELECT set_config('app.tenant_encryption_key', 'kms_key_tenant_101_secret', true);

-- Вставка даних із прозорим шифруванням pgcrypto
INSERT INTO devices (tenant_id, name, status, secret_token)
VALUES (
    current_setting('app.current_tenant'),
    'Front Door Lock',
    'active',
    pgp_sym_encrypt('unlock_code_9876', current_setting('app.tenant_encryption_key'))
);

-- Читання зашифрованих даних
SELECT 
    name, 
    pgp_sym_decrypt(secret_token, current_setting('app.tenant_encryption_key')) AS secret_token 
FROM devices;
