# fleadert
Простой инструмент для управления задачами в командных проектах. Может использоваться в организациях и учреждениях, в которых, например [Redmine](https://www.redmine.org/), вызывает сложности развертывания, поддержки и расширения функционала, а также трудности, связанные с информационной грамотностью работников. Логика работы построена на основных принципах постановки руководством задач в государственных учреждениях - использование письменных распоряжений/резолюций на документах, исполнением которых, как правило, являются другие документы.

Fleadert позиционируется как учебный проект в рамках освоения компетенций, необходимых для виртуозной и мастерской разработки back-end приложений. 

Посмотреть в действии fleadert возможно по [ссылке](http://fleadert.herokuapp.com/), используя:
* собственную учетную запись (после регистрации);
* тестовую запись руководителя - login: boss, password: 123;
* тестовую запись работника - login: test_worker, password: 123.

В целях демонстрации возможностей сервис был развернут на хостинге [Heroku](https://heroku.com) с использованием заранее подготовленной БД формата `.sqlite`. Ввиду особенностей бесплатного хостинга и политики работы с файлами в Heroku, отправляемые в БД данные по результатам POST-запросов сохраняются, но через некоторое время **удаляются**, поэтому если пройти регистрацию, тем самым создав нового пользователя, то он автоматически будет удален из БД спустя промежуток времени.

## Описание архитектуры

Для целесообразного использования fleadert необходима локальная вычислительная сеть или автоматизированная система в защищенном исполнении, имеющая серверную часть на ОС семейства Linux (для проверки использовались [Ubuntu 16.04+](https://ubuntu.com/) и [Debian 10](https://www.debian.org/)) с настроенным DNS, а также установленные браузеры на пользовательских ПК (например, [Mozilla Firefox](https://www.mozilla.org/ru/)).

Fleadert реализован на языке Python на базе микро-фреймворка [Flask](https://palletsprojects.com/p/flask/) с использованием [SQLAlchemy](https://www.sqlalchemy.org/), дизайн написан на [Bootstrap](https://getbootstrap.com/). В качестве WSGI HTTP-сервера используется [Gunicorn](https://gunicorn.org/).
Основная СУБД для работы веб-приложения - [MySQL](https://www.mysql.com/), а для разработки и тестирования - [SQLite](https://www.sqlite.org/). Содержит конфигурационный файл `config.py`, в котором приведены настройки коннекторов к СУБД.

Для отправки почтовых уведомлений в целях демонстрации инструмента используется SMTP-сервер компании ООО "Мэйл.Ру Груп".

## Установка

1. Создать локальную копию репозитория в указанной директории:  
`git clone https://github.com/PrudyvusP/fleadert.git <path/to/dir>`

2. Установить инструмент по работе с виртуальными окружениями, если он еще не установлен:  
`sudo apt-get install virtualenv`

3. Перейти в директорию и создать виртуальное окружение:  
`cd <path/to/dir> && virtualenv <venv_name>`

4. Активировать виртуальное окружение:  
`source <venv_name>/bin/activate`

5. Установить зависимости из файла `requirements.txt`:  
`pip3 install -r requirements.txt`

   5.1. Для установки зависимостей в закрытый контур необходимо скачать whl-пакеты например, через машину, на которой настроен доступ в сеть Интернет, предварительно скопировав `requirements.txt` на эту машину:  
`pip3 wheel --wheel-dir=/path/to/dir -r requirements.txt`

   5.2. Перенести скаченные .whl-пакеты в закрытый контур и в активированном виртуальном окружении установить необходимые зависимости:  
`pip3 install --no-index --find-links=<path/to/dir/with/whl> -r requirements.txt`

6. Для работы с СУБД SQLite можно сразу переходить к шагу 8. 

7. Для работы с СУБД MySQL потребуется создать базу, создать пользователя и дать ему необходимые права:  
```mysql
mysql> CREATE DATABASE fleadert;
mysql> CREATE USER '<user_name>'@'localhost' IDENTIFIED BY '<user_password>';
mysql> GRANT ALL PRIVILEGES ON fleadert.* TO <user_name>'@'localhost;
mysql> FLUSH PRIVILEGES;
```  
   Для проверки работоспособности возможно использовать любой SQL-запрос (за исключением DROP):  
 `mysql> SHOW TABLES FROM fleadert;`
 
   Вывод должен получиться таким:  
   ```
  +--------------------+  
  | Tables_in_fleadert |  
  +--------------------+  
  | alembic_version    |  
  | projects           |  
  | requests           |  
  | tasks              |  
  | user_task          |  
  | users              |  
  +--------------------+  
  6 rows in set (0.01 sec)
```

8. Создать файлы в текущей директории, которые наполнить данными окружения:  
```sh
vim .env
SECRET_KEY=<your secret key>
KEY_WORD_FOR_BOSS=<your key word for granting boss access to account>
остальные переменные окружения из описания
:wq
```
```bash
vim .flaskenv
FLASK_APP=fleadert.py
:wq
```

9. Запустить команду создания миграции и инициализации схемы БД:  
`flask db init`  
`flask db migrate -m 'initial'`  
`flask db upgrade`  

10. Проверить работоспособность сервиса, запустив gunicorn:  
`gunicorn -b localhost:8000 -w 3 fleadert:app --access-logfile -`  

   В командной строке должны появиться сообщения примерно следующего содержания:  
   ```log
   [2021-05-10 10:54:30 +0300] [8437] [INFO] Starting gunicorn 20.1.0
   [2021-05-10 10:54:30 +0300] [8437] [INFO] Listening at: http://127.0.0.1:8000 (8437)
   [2021-05-10 10:54:30 +0300] [8437] [INFO] Using worker: sync
   [2021-05-10 10:54:30 +0300] [8439] [INFO] Booting worker with pid: 8439
   [2021-05-10 10:54:30 +0300] [8440] [INFO] Booting worker with pid: 8440
   [2021-05-10 10:54:30 +0300] [8441] [INFO] Booting worker with pid: 8441
   ```

11. Перейти на http://127.0.0.1:8000 и убедиться, что главная страница отображается корректно.  

12. Если все предыдущие шаги выполнены корректно, то можно настроить веб-приложение как службу systemd:
```sh
vim /etc/systemd/system/fleadert.service
[Unit]
Description=fleadert task tracker
After=network.target
 
[Service]
User=<name_of_linux_user>
WorkingDirectory=</path/to/dir>
ExecStart=<path/to/dir/><name_of_your_venv>/bin/gunicorn -b localhost:8000 -w 3 fleadert:app --access-logfile -
Restart=always

[Install]
WantedBy=multi-user.target
:wq
```
13. Перезагрузить конфигурацию служб и запустить fleadert!  
`sudo systemctl daemon-reload`  
`sudo systemctl start fleadert`  

## Переменные окружения
* FLASK_APP;
* SECRET_KEY;
* KEY_WORD_FOR_BOSS;
* MAIL_SERVER;
* MAIL_USERNAME;
* MAIL_PASSWORD;
* MAIL_DEFAULT_SENDER;
* MAIL_PORT;
* MAIL_USE_SSL

В случае использования MYSQL: 

* MYSQL_USER;
* MYSQL_PASSWORD;

## Тестовые данные

Для быстрого заполнения БД данными, приближенными к реальности, можно использовать скрипт `datatobd.py`, который генерит данные с помощью библиотек `random` и [`Faker`](https://pypi.org/project/Faker/).

## Дополнительно
Зависимость `cryptography==3.4.7` и ее родительские зависимости установлены для исправления [ошибки](https://github.com/PyMySQL/PyMySQL/issues/768) при использовании коннектора `pymysql` к MySQL.

В коде могут присутствовать неоптимальные решения, а также баги, так как приложение тестировалось только вручную по причине неосведомленности разработчика в области написании тестов на текущий момент времени.

## Благодарности
[Команда курса от Stepik Academy 'Flask с нуля'](https://academy.stepik.org/flask)  
[Блог Miguel Grinberg](https://blog.miguelgrinberg.com/index)  
[Видео Anthony Herbert](https://prettyprinted.com/)  

## Мои Контакты
[Telegram](https://web.telegram.org): @prudyvus_p
