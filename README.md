![Workflow status](https://github.com/taube-a/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
# Проект yamdb_final
## CI/CD для проекта API YAMDB

## Описание

Проект ориентирован на знакомство с методологией непрерывной интеграции. 

В качестве объекта для контейнеризации выбран групповой проект [api_yamdb](https://github.com/taube-a/api_yamdb) (т.к. это ветка проекта, его видимость зависит от оригинального.)

Проект yamdb_final можно использовать как образец струкруы и наполения файлов для настройки автоматической интеграции и поставки проекта. 

## Workflow

+ tests - Проверка кода на соответствие PEP8 (посредством пакета flake8) и запуск pytest для проекта;
+ build_and_push_to_docker_hub - Сборка и доставка образов на Docker Hub;
+ deploy - Деплой проекта на сервер;
+ send_message - Отправка уведомления об успешном развёртывании проекта в Telegram.

## Испльзуемые технологии

+ Docker
+ DockerHub 
+ GitHub Actions
+ Yandex.Cloud
+ Nginx
+ Gunicorn
+ Python 3.7
+ Django 2.2
+ rest_api

Полный перечень библиотек расположен в репозитории по адресу api_yamdb/**requirements.txt**

## Установка и запуск на сервере

1. Создать репозиторий с проектом на GitHub. 

    Проект должен быть настроен для отправки его образа на DockerHub (подробнее см. [проект infra_sp2](https://github.com/taube-a/infra_sp2))

    Структура репозитория:
```
repo_name
├── .git/ 
├── .github/ 
│    └── workflows/ <-- Директория workflow
|          └── workflow_name.yml <-- Файл с инструкциями
├── project_name/ <-- проект, настроенный для развёртывания docker-образа
│    ├── app_name/ <-- Директория приложения app
│    │   └── # Файлы приложения
│    ├── project_name/
│    │   ├── __init__.py
│    │   ├── settings.py
│    │   ├── urls.py
│    │   └── wsgi.py
│    ├── app2_name/ <-- Директория приложения app2
│    │   └── # Файлы приложения
│    ├── static <-- Директория для сборки статических файлов проекта
│    │   └── redoc.yaml
│    ├── templates
│    │   └── redoc.html
|    ├── Dockerfile 
│    ├── manage.py
|    └── requirements.txt 
├── infra/ <-- Директория с файлами для развёртывания инфраструктуры
│    ├── nginx/ 
│    │   └── default.conf
│    ├── .env
|    └── docker-compose.yaml
├── tests/ <-- Тесты для проверки
├── .gitignore
├── pytest.ini
├── README.md
└── setup.cfg <-- Файл конфигурации для тестирования
```

2. Добавить секреты для workflow (Settings - Secrets - Actions secrets):

```
DOCKER_USERNAME - имя пользователя в DockerHub
DOCKER_PASSWORD - пароль пользователя в DockerHub
HOST - ip-адрес сервера
USER - имя пользователя на сервере
SSH_KEY - приватный ssh-ключ пользователя (публичный должен быть на сервере)
PASSPHRASE - кодовая фраза пользователя для ssh-ключа
DB_ENGINE - django.db.backends.postgresql
DB_HOST - db
DB_PORT - 5432
DB_NAME - postgres (по умолчанию)
POSTGRES_USER - postgres (по умолчанию)
POSTGRES_PASSWORD - postgres (по умолчанию)
SECRET_KEY - секретный ключ проекта project_name (см. settings.py)
TELEGRAM_TO - id телеграм-аккаунта, на который будет отсыласться уведомление
TELEGRAM_TOKEN - токен бота, котрый будет отсылать уведомление
EMAIL_HOST - SMTP-сервер для отправки электронных писем приложением
EMAIL_PORT - порт почтового сервера
EMAIL_HOST_USER - email от имени которого будет отсылаться почта
EMAIL_HOST_PASSWORD - палоль от почтового ящика 
```

3. Подготовить Dockerfile для автоматического обновления проекта на DockerHub.

    Код Dockerfile:

```
FROM python:3.7-slim 
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r ./requirements.txt --no-cache-dir
COPY ./ .
CMD ["gunicorn", "project_name.wsgi:application", "--bind", "0:8000" ]
```

4. Отправить проект на DockerHub:

    1. Локально создать образ с нужным названием и тегом:

        ```docker build -t DOCKER_USERNAME/image_name:tag .```

    2. Авторизоваться через консоль:

        ```docker login -u billglasses```
    
    3. Загрузить образ на DockerHub:

        ```docker push DOCKER_USERNAME/image_name:tag```

5. Настроить файл docker-compose.yaml. Он будет разворачивать контейнер web, используя образ проекта на Docker Hub:

    ```
    ...
    web:
        image: DOCKER_USERNAME/image_name:tag
    ...
    ```

5. Установить на сервер Docker:
```
sudo apt install docker.io 
```

6. Установить docker-compose на сервере:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

7. Скопировать файлы docker-compose.yaml и nginx/default.conf из проекта на сервер в home/<USER>/docker-compose.yaml и home/<USER>/nginx/default.conf соответственно.

    + Проверьте, чтобы в файле nginx/default.conf был указан корректный HOST **ВАШЕГО** сервера.

8. Настройте файл workflow_name.yml:

    В workflow должно быть четыре задачи (job):  

    + проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8) и запуск pytest из репозитория;
        
    + сборка и доставка докер-образа для контейнера web на Docker Hub;

    + автоматический деплой проекта на сервер;
        
    + отправка уведомления в Telegram о том, что процесс деплоя успешно завершился.

    Пример workflow_name.yml:

```
name: project_name workflow

on: [push]

jobs:
  tests:
    name: Check for pep8
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python 
      uses: actions/setup-python@v2
      with:
        python-version: 3.7
    - name: Install dependencies
      run: | 
        python -m pip install --upgrade pip 
        pip install flake8 pep8-naming flake8-broken-line flake8-return flake8-isort
        pip install -r project_name/requirements.txt 
    - name: Test with flake8 and django tests
      run: |
        python -m flake8
        cd project_name/
        python manage.py test

  build_and_push_to_docker_hub:
    name: Push Docker image to Docker Hub
    runs-on: ubuntu-latest
    needs: tests
    steps:
      - name: Check out the repo
        uses: actions/checkout@v2 
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v1 
      - name: Login to Docker
        uses: docker/login-action@v1 
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      - name: Push to Docker Hub
        uses: docker/build-push-action@v2 
        with:
          push: true
          context: ./project_name/
          tags: DOCKER_USERNAME/image_name:tag

  deploy:
    name: Project's Deploy
    runs-on: ubuntu-latest
    needs: build_and_push_to_docker_hub
    steps:
      - name: executing remote ssh commands to deploy
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USER }}
          key: ${{ secrets.SSH_KEY }}
          passphrase: ${{ secrets.PASSPHRASE }}
          script: |
            sudo docker-compose stop
            sudo docker-compose rm web
            touch .env
            echo SECRET_KEY=${{ secrets.SECRET_KEY }} >> .env
            echo EMAIL_HOST=${{ secrets.EMAIL_HOST }} >> .env
            echo EMAIL_PORT=${{ secrets.EMAIL_PORT }} >> .env
            echo EMAIL_HOST_USER=${{ secrets.EMAIL_HOST_USER }} >> .env
            echo EMAIL_HOST_PASSWORD=${{ secrets.EMAIL_HOST_PASSWORD }} >> .env
            echo DB_ENGINE=${{ secrets.DB_ENGINE }} >> .env
            echo DB_NAME=${{ secrets.DB_NAME }} >> .env
            echo POSTGRES_USER=${{ secrets.POSTGRES_USER }} >> .env
            echo POSTGRES_PASSWORD=${{ secrets.POSTGRES_PASSWORD }} >> .env
            echo DB_HOST=${{ secrets.DB_HOST }} >> .env
            echo DB_PORT=${{ secrets.DB_PORT }} >> .env
            sudo docker-compose up -d

  send_message:
    name: Notificate in telegram
    runs-on: ubuntu-latest
    needs: deploy
    steps:
    - name: send message
      uses: appleboy/telegram-action@master
      with:
        to: ${{ secrets.TELEGRAM_TO }}
        token: ${{ secrets.TELEGRAM_TOKEN }}
        message: ${{ github.workflow }} успешно выполнен!
```
9. Проект должен запускаться по описанным в проекте адресам.

## После деплоя
**В терминале сервера:**

1. Соберите статические файлы:

```
sudo docker-compose exec web python manage.py collectstatic --no-input
```

2. Применить миграции:

```
sudo docker-compose exec web python manage.py migrate
```

3. Cоздать суперпользователя:

```
sudo docker-compose exec web python manage.py createsuperuser
```

Автор: [Анастасия Таубе](https://github.com/taube-)