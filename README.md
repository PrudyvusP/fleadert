# fleadert
Простой инструмент для управления задачами как первый шаг в путь разработчика. Расчитан на использование преимущественно в тех учреждениях, где задачи ставятся устно и (-или) на бумаге.


## Environment variables

* SECRET_KEY;
* KEY_WORD_FOR_BOSS;
* MAIL_SERVER;
* MAIL_USERNAME;
* MAIL_PASSWORD;
* MAIL_DEFAULT_SENDER;
* MAIL_PORT;
* MAIL_USE_SSL

## В случае переключения на ProdConfig в фабрике create_app() потребуется указать еще две переменные окружения  

* MYSQL_USER;
* MYSQL_PASSWORD;

## Зависимости

Все зависимости отражены в файле `requirements.txt`. Зависимость cryptography==3.4.7 и ее родительские завимимости установлены для исправления ошибки при использовании коннектора pymysql к MySQL.
