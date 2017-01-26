-- 1. Switch to postgres account:
--        sudo -i -u postgres
-- 2. Run Postgres interactive shell:
--        psql
-- 3. Execute this script:
--        \i <path_to_the_file>/create_postgres_db.sql

REVOKE ALL ON DATABASE "TDDB" FROM "TDDB_ADMIN";
DROP USER IF EXISTS "TDDB_ADMIN";
CREATE USER "TDDB_ADMIN" WITH PASSWORD '789456123';

DROP DATABASE IF EXISTS "TDDB";
CREATE DATABASE "TDDB";
GRANT ALL ON DATABASE "TDDB" TO "TDDB_ADMIN";

\c "TDDB";

CREATE TABLE "Users" (
    id serial PRIMARY KEY,
    ip varchar(15) NOT NULL
);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "TDDB_ADMIN";