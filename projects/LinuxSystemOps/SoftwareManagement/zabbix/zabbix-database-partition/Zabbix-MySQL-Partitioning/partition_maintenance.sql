USE zabbix;

DROP PROCEDURE IF EXISTS partition_maintenance;

DELIMITER $$
CREATE PROCEDURE `partition_maintenance`(SCHEMA_NAME VARCHAR(32), TABLE_NAME VARCHAR(32), INTERVAL_TYPE VARCHAR(10),
                                         INTERVAL_VALUE INT, CREATE_NEXT_INTERVALS INT, KEEP_DATA_DAYS INT)
BEGIN
    DECLARE _KEEP_DATA_AFTER_TS INT;

    CALL partition_verify(SCHEMA_NAME, TABLE_NAME, INTERVAL_TYPE, INTERVAL_VALUE);
    CALL partition_create(SCHEMA_NAME, TABLE_NAME, INTERVAL_TYPE, INTERVAL_VALUE, CREATE_NEXT_INTERVALS);

    SET _KEEP_DATA_AFTER_TS = UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL KEEP_DATA_DAYS DAY));
    CALL partition_delete(SCHEMA_NAME, TABLE_NAME, _KEEP_DATA_AFTER_TS);
END$$
DELIMITER ;
