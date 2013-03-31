-- Grant access to current tables and views
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO duagg;
-- Now make sure that's also available on new tables and views by default
ALTER DEFAULT PRIVILEGES
    IN SCHEMA public -- omit this line to make a default across all schemas
    GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLES 
TO duagg;

-- Now do the same for sequences
GRANT SELECT, USAGE ON ALL SEQUENCES IN SCHEMA public TO duagg;

ALTER DEFAULT PRIVILEGES
    IN SCHEMA public -- omit this line to make a default across all schemas
    GRANT SELECT, USAGE
ON SEQUENCES 
TO duagg;
