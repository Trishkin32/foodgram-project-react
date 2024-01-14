# praktikum_new_diplom
# FoodGram
Продуктовый помощник

### Описание
Готовь в удовольствие! Делись с другими рецептами! 
В этом вам поможет сайт, на котором можно публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 
Удобно!
### Технологии
Python 3.9.10
Django 3.2.3
Django Rest Framework 3.14.0
PostgreSQL 13.10
Docker

#### Развертывание проекта локально:

1. Установите Docker и Docker-compose. Запустите сервис Docker.

2. Склонируйте репозиторий на свой компьютер:
```
    git clone git clone git@github.com:Trishkin32/foodgram-project-react.git
    
    cd foodgram-project-react
```
    

3. Наполните файл .evn своими данными.

4. Разверните проект:
```
    sudo docker compose -f docker-compose.yml up
```
    

5. Выполните миграции:
```
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
    

6. Соберите статические файлы бэкенда и скопируйте их в /backend_static/static/:
```
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
    
    sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```


7. Зарегистрируйтесь и можно приступать к наполнению сайта рецептами!

### Запуск проекта в dev-режиме
Склонируйте репозиторий на свой компьютер:
```
git clone git clone git@github.com:Trishkin32/foodgram-project-react.git
```
- Перейдите в директорию backend-приложения проекта
```
cd foodgram-project-react/backend/
```
- Установите и активируйте виртуальное окружение
```
python3 -m venv venv
```
```
source venv/bin/activate
```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- Выполните миграции
```
python manage.py migrate
```

### Настройка CI/CD

1. Файл workflow уже написан. Он находится в директории

```
foodgram-project-react/.github/workflows/main.yml
```

2. Для адаптации его на своем сервере добавьте секреты в GitHub Actions:

```
DOCKER_USERNAME                # имя пользователя в DockerHub
DOCKER_PASSWORD                # пароль пользователя в DockerHub

HOST                           # ip_address сервера
USER                           # имя пользователя
SSH_KEY                        # приватный ssh-ключ (cat ~/.ssh/id_rsa)
SSH_PASSPHRASE                 # кодовая фраза (пароль) для ssh-ключа

TELEGRAM_TO                    # id телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
TELEGRAM_TOKEN                 # токен бота (получить токен можно у @BotFather, /token, имя бота)
```

### Запросы к API

Теперь вы можете отправлять запросы к api, например, создать пользователя. Пример POST-запроса к api/users/:

```
{
    "email": "user@mail.com",
    "username": "user",
    "password": "user_password",
    "first_name": "user_first_name",
    "last_name": "user_last_name"
}
```

### Автор
Владислав Т
Сайт: https://foodgram32.didns.ru