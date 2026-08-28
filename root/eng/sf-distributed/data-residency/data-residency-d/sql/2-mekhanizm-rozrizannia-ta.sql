-- Прив'язка діапазонів ключів до локальних регіонів дата-центрів
ALTER TABLE customers CONFIGURE ZONE USING
    num_replicas = 3,
    constraints = '{
        "+region=eu-central-1": 1,
        "+region=eu-west-1": 1,
        "+region=eu-west-3": 1
    }'
    WHERE jurisdiction_code = 'EU_EEA';

ALTER TABLE customers CONFIGURE ZONE USING
    num_replicas = 3,
    constraints = '{
        "+region=us-east-1": 1,
        "+region=us-east-2": 1,
        "+region=us-west-2": 1
    }'
    WHERE jurisdiction_code = 'US_FED';
