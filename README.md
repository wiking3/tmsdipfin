# Описание Диплома:

  Приложение Dnevnik преподавателя предназначено для ведения учета выполнения домешних заданий студентов. 
  Написано на Flask c БД mysql 8.0 через python-библиотеку SQLAclhemy.
  Предполагается разворачивание внутри сети компании через инструменты  Gitlab CI/CD + Ansible.
  Реализован балансировщик на базе nginx+keepalived на серверах группы frondents. Докерезировано. Используется 2 сервера в качестве backend и 2 в качестве frontend. Динамически генерируется .env файл, копируется на сервера роли backend для docker-compose и в конце деплоя удаляется. Все пароли/ключи хранятся в переменных Gitlab CI.


Запуск приложение проихводится через отдельный  BASH-скрипт flask-entrypoint.sh : 
Инициализация БД : 
  <span style="color:red"> `flask db init ` </span>
  <span style="color:red">  flask db migrate -m 'create initial tables' </span>
  <span style="color:red">  flask db upgrade   </span>
  
 Также создаются учетные записи пользователей teacher1-2, student1-2, admin :
  flask create-user teacher1 "$DNEVNIK_TEACHER_PASS" teacher
  flask create-user teacher2 "$DNEVNIK_TEACHER_PASS" teacher
  flask create-user student1 "$DNEVNIK_STUDENT_PASS" student
  flask create-user student2 "$DNEVNIK_STUDENT_PASS" student
  flask create-user admin "$DNEVNIK_ADMIN_PASS" admin

 Запуск приложения : flask run --host 0.0.0.0 --port 5000
  
  Нужны следующие requirements : Flask==2.3.3, Flask-SQLAlchemy==3.0.5 , Flask-Migrate==4.0.5 ,Flask-Login, Flask-WTF , flask_pagedown
bcrypt, mysqlclient==2.2.8 , markdown , python-dotenv , PyMySQL==1.1.0 , cryptography==42.0.8 , pylint ,click.

 Ansible-выполняет через плейбуки следующие задачи : 
 -setup-user-ansible - создает на всех сервера пользователя ansible и копирует публичный ключ ansible_id_rsa.
 -install-docker - устанавливает докер на сервера роли backends.
 -deploy-nginx - устанавливает nginx на сервера роли frontend и настраивает через шаблон j2.
 -frontend-ha - устанавливает keepalived и настраивает через шаблон j2. 
 -conf-iptabels  - на сервера роли frontends настраивает iptables (разрешает tcp/22, tcp/80, tcp/443, VRRP, icmp).
 -install-zabbix - установка zabbix-agent2 на все сервера (4 шт). 

 В инфрастуктуре используется 4 сервера : 
  HOSTB1: 192.168.100.123
  HOSTB2: 192.168.100.124
  HOSTF1: 192.168.100.121
  HOSTF2: 192.168.100.122
  runner1 : 192.168.100.116  - (docker executor) - для деплоя приложения на сервера HOSTB1-B2
  RUN4SHELL : 192.168.100.131 - (shell executor) - для выполнения ansible playbook - для настройки инфраструктуры.
  
