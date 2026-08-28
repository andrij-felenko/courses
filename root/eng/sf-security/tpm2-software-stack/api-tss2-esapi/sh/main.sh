# 1. Генерація Primary Key у Owner ієрархії
tpm2_createprimary -C o -g sha256 -G rsa -c primary.ctx

# 2. Розрахунок дайджесту політики для регістрів PCR 0 та 7
tpm2_createpolicy --policy-pcr -l sha256:0,7 -L policy.digest

# 3. Створення та запечатування ключа шифрування диска
tpm2_create -C primary.ctx -u secret.pub -r secret.priv -L policy.digest -i luks_pass.key

# 4. Завантаження запечатаного об'єкта у віртуальний простір TPM
tpm2_load -C primary.ctx -u secret.pub -r secret.priv -c secret.ctx

# 5. Відкриття сесії політики, підтвердження стану PCR та розпечатування
tpm2_startauthsession --policy-session -S session.ctx
tpm2_policypcr -S session.ctx -l sha256:0,7
tpm2_unseal -c secret.ctx -p session:session.ctx
tpm2_flushcontext session.ctx
