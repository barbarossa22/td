-- To use it:
-- 1. login into MySQL as root
--      mysql -u root -p
-- 2. run this script
--      source <path to the file>/init_mysql_db.sql

DROP USER 'TDDB_ADMIN'@'localhost';
CREATE USER 'TDDB_ADMIN'@'localhost' IDENTIFIED BY '789456123';

DROP DATABASE IF EXISTS TDDB;
CREATE DATABASE IF NOT EXISTS TDDB CHARACTER SET utf8;

GRANT ALL ON TDDB.* TO 'TDDB_ADMIN'@'localhost';

USE TDDB;


CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip VARCHAR(15),
    username VARCHAR(64) NOT NULL UNIQUE,
    password VARCHAR(256) NOT NULL,
    groups VARCHAR(64) NOT NULL
);
