-- Політика доступу з урахуванням tenant_id ТА ролі користувача
CREATE POLICY tenant_abac_policy ON devices
    FOR ALL
    TO app_user
    USING (
        tenant_id = current_setting('app.current_tenant', true)
        AND (
            current_setting('app.current_user_role', true) = 'admin'
            OR (current_setting('app.current_user_role', true) = 'operator' AND status != 'archived')
            OR (created_by = current_setting('app.current_user_id', true))
        )
    );
