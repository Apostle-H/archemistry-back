CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
DECLARE root_path VARCHAR(255) := '/tmp/db_init/configs/';
BEGIN
    -- MATCH_ELEMENT INITIALIZATION (START)
    CREATE TEMP TABLE match_element_temp (
        title VARCHAR(255),
        row_number SERIAL
    );

    EXECUTE 'COPY match_element_temp (title) FROM ' || quote_literal(root_path || 'db_match_element.csv')
                || ' DELIMITER '','' CSV HEADER';

    INSERT INTO match_element (uuid, title)
    SELECT
        ('00000000-0000-0000-0000-' || LPAD(CAST(row_number AS VARCHAR), 12, '0'))::UUID,
        title
    FROM match_element_temp;

    DROP TABLE match_element_temp;
    -- MATCH_ELEMENT INITIALIZATION (END)

    -- SHOP_ENERGY_ITEM INITIALIZATION (START)
    CREATE TEMP TABLE shop_energy_item_temp (
        type INT,
        amount INT,
        cost INT
    );

    EXECUTE 'COPY shop_energy_item_temp (type, amount, cost) FROM ' || quote_literal(root_path || 'db_shop_energy_item.csv')
                || ' DELIMITER '','' CSV HEADER';

    INSERT INTO shop_energy_item (uuid, type, amount, cost)
    SELECT
        gen_random_uuid(), type, amount, cost
    FROM shop_energy_item_temp;

    DROP TABLE shop_energy_item_temp;
    -- SHOP_ENERGY_ITEM INITIALIZATION (END)

    -- TASK (Daily) INITIALIZATION (START)
    CREATE TEMP TABLE daily_task_temp (
        type INT,
        description VARCHAR(255),
        target_value INT,
        reward_type INT,
        reward INT
    );

    EXECUTE 'COPY daily_task_temp (type, description, target_value, reward_type, reward) FROM ' || quote_literal(root_path || 'db_daily_task.csv')
                || ' DELIMITER '','' CSV HEADER';

    INSERT INTO task (uuid, type, description, target_value, reward_type, reward)
    SELECT
        gen_random_uuid(), type, description, target_value, reward_type, reward
    FROM daily_task_temp;

    DROP TABLE daily_task_temp;
    -- TASK (Daily) INITIALIZATION (END)
END$$;