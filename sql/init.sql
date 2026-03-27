CREATE DATABASE IF NOT EXISTS teacher_journal;
CREATE USER IF NOT EXISTS 'journaluser'@'%' IDENTIFIED BY 'journalpass';
GRANT ALL PRIVILEGES ON teacher_journal.* TO 'journaluser'@'%';
FLUSH PRIVILEGES;   # necessary to apply new rights  


