-- To use it:
-- 1. login into MySQL as root
--      mysql -u root -p
-- 2. run this script
--      source <path to the file>/init_db.sql
-- 3. grant all rights on this DB for your work user
--      CREATE USER '<user_name>'@'localhost' IDENTIFIED BY '<password>';
--      GRANT ALL ON CYCLINGDB.* TO '<user_name>'@'localhost';

DROP DATABASE IF EXISTS TDDB;
CREATE DATABASE IF NOT EXISTS TDDB CHARACTER SET utf8;

USE TDDB;


CREATE TABLE Users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip VARCHAR(15)
);

CREATE TABLE Items(
    id INT AUTO_INCREMENT PRIMARY KEY,
    item VARCHAR(256),
    owner_id INT NOT NULL,
    CONSTRAINT OwnerFK
    FOREIGN KEY (owner_id)
    REFERENCES Users(id)
    ON DELETE CASCADE
);