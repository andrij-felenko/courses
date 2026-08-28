-- Таблиця користувачів (сутність облікового запису)
CREATE TABLE users (
    id VARCHAR(64) PRIMARY KEY,          -- Сталий бінарний ID (Base64URL), стійкий до колізій
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Таблиця зареєстрованих ключів доступу (Passkeys)
CREATE TABLE passkey_credentials (
    id VARCHAR(255) PRIMARY KEY,          -- credentialId (Base64URL)
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    public_key_spki BYTEA NOT NULL,       -- Відкритий ключ у форматі DER SubjectPublicKeyInfo
    algorithm INT NOT NULL DEFAULT -7,    -- COSE ідентифікатор алгоритму (-7 = ES256)
    sign_count BIGINT NOT NULL DEFAULT 0,    -- Лічильник підписів для виявлення клонів
    aaguid VARCHAR(36) NOT NULL,          -- Модель автентифікатора (UUID)
    backup_eligible BOOLEAN NOT NULL,     -- Прапорець BE (можливість синхронізації)
    backup_state BOOLEAN NOT NULL,        -- Прапорець BS (синхронізовано у брелок)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE
);

-- Тимчасова таблиця сесійних викликів (челенджів)
CREATE TABLE auth_challenges (
    challenge VARCHAR(64) PRIMARY KEY,    -- Base64URL випадковий рядок (32 байти)
    user_id VARCHAR(64),                  -- NULL для безпарольного входу (Discoverable)
    ceremony_type VARCHAR(16) NOT NULL,   -- 'registration' або 'authentication'
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);
