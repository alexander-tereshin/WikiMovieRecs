# Movie Recommendation Service / Сервис рекомендации фильмов

[English](#required-packages) | [Русский](#необходимые-пакеты)

## Required Packages

```plain_text
- django
- wikipedia
- scipy
- scikit-learn
- bs4
- requests
- pandas
- psycopg2-binary
- sqlalchemy
- celery
- gunicorn
```

## Running the Application Locally

From the directory containing manage.py (root of the repository), run:

```bash
python manage.py runserver
```

## Service Features

`<URL provided by manage.py when starting>/` - opens an input field. Enter a link to an English Wikipedia article about a movie and select the number of similar movies.
Press enter and wait for the system to redirect to the results page (showing a list of similar movies with links and descriptions).

`<URL provided by manage.py when starting>/train` - train the model. The repository already includes a model pre-trained on 20,000 English movies.
Training is time-consuming (reducing to 10,000 movies speeds up the process. 20,000 was chosen as optimal for resource/quality balance).

## Docker Deployment

1. Build the Docker image:

    ```bash
    docker build -t django-movie-service .
    ```

2. Run the container:

    ```bash
    docker run -p 8000:8000 django-movie-service
    ```

3. Service will be available at: <http://localhost:8000>

## Docker Compose Deployment

1. Start services:

    ```bash
    docker-compose up --build
    ```

2. Web service will be available at: <http://localhost>

3. Nginx will proxy requests to the service on port 8000. Access via:
    - Main interface: <http://localhost/app>
    - Admin panel: <http://localhost/admin>
    - Health Check: <http://localhost/health>

### Using the Service

#### Finding Similar Movies

1. On the main page enter:
    - Link to an English Wikipedia movie article (e.g., <https://en.wikipedia.org/wiki/Gladiator_(2000_film)>)
    - Number of recommendations (1-10)

2. Click "Search" to submit. This creates an async task to process the request.

3. Check task status and results:
    - Task status: <http://localhost/task_status/{task_id}>
    - Successful tasks return a list of similar movies.

4. If model isn't trained, you'll be prompted to visit the training page.

Nginx config proxies requests to the service running on port 8000 (in the `web` container).

## Kubernetes Deployment

### 1. Deploying the Application

Apply configurations:

```bash
kubectl apply -f k8s/ --recursive
```

Directory structure:

```plaintext
├── celery/                     # Celery worker resources
│   └── deployment.yaml         # Celery Deployment
├── db/                         # PostgreSQL resources
│   ├── deployment.yaml         # DB Deployment
│   ├── pvc.yaml                # Persistent Volume Claim
│   └── service.yaml            # DB Service
├── nginx/                      # Nginx resources
│   ├── configmap.yaml          # Nginx Config
│   ├── deployment.yaml         # Nginx Deployment
│   └── service.yaml            # Nginx Service
├── rabbitmq/                   # RabbitMQ resources
│   ├── deployment.yaml         # RabbitMQ Deployment
│   └── service.yaml            # RabbitMQ Service
└── web/                        # Django app resources
    ├── deployment.yaml         # Web app Deployment
    ├── pvc.yaml                # Persistent Volume
    └── service.yaml            # Web Service
```

### 2. Access via Minikube (local testing)

After deployment, access via Nginx:

```bash
minikube tunnel
```

Check assigned external IP:

```bash
kubectl get svc nginx -n highload-project -o wide
```

Example output:

```bash
NAME    TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
nginx   LoadBalancer   10.96.45.217   127.0.0.1     80:32456/TCP   2m
```

Access points:

- Main interface: [http://localhost/app](http://localhost/app)
- Django admin: [http://localhost/admin](http://localhost/admin)
- Health Check: [http://localhost/health](http://localhost/health)

### 3. Using the Service

1. On main page enter:
    - English Wikipedia movie link (e.g., Gladiator)
    - Number of recommendations (1-10)

2. Click "Search" to create async task.

3. Check results:
    - Task status: <http://localhost/app/task_status/{task_id}>
    - Returns list of similar movies when complete.

4. Untrained models prompt to visit training page.

---

## Необходимые пакеты

```plain_text
- django
- wikipedia
- scipy
- scikit-learn
- bs4
- requests
- pandas
- psycopg2-binary
- sqlalchemy
- celery
- gunicorn
```

## Запуск приложения локально

Из папки с manage.py (корень репозитория):

```bash
python manage.py runserver
```

## Функционал сервиса

<ссылка, которую даст вам manage.py при запуске>/ - откроет окно с полем ввода. Туда вводим ссылку на статью(английскую) на википедии о фильме и выбираем число похожих.
Жмем энтер и ждем, пока система перенаправит на страницу с результатами (там будет список похожих фильмов с ссылкой и описанием)
<ссылка, которую даст вам manage.py при запуске>/train - тренировать модель. В репозитории модель уже тренирована на 20000 фильмах с описанием на английском.
Процесс тренировки достаточно длительный(если сократить число фильмов до 10000, то процесс ускорится. Решил использовать 20000, так как это оптимальное число
с точки зрения ресурсов и качества).

## Запуск через Docker

1. Сборка образа:

    ```bash
    docker build -t django-movie-service .
    ```

2. Запуск контейнера:

    ```bash
    docker run -p 8000:8000 django-movie-service
    ```

3. Сервис доступен по: <http://localhost:8000>

## Запуск через Docker Compose

1. Запуск сервисов:

    ```bash
    docker-compose up --build
    ```

2. Веб-сервис доступен по: <http://localhost>

3. Nginx проксирует запросы на порт 8000. Доступ:
    - Основной интерфейс: <http://localhost/app>
    - Админка: <http://localhost/admin>
    - Health Check: <http://localhost/health>

### Использование сервиса

#### Поиск похожих фильмов

1. На главной странице:
    - Ссылка на англоязычную статью (напр., <https://en.wikipedia.org/wiki/Gladiator_(2000_film)>)
    - Количество рекомендаций (1-10)

2. Нажать "Search" для создания асинхронной задачи.

3. Проверка статуса:
    - Статус задачи: <http://localhost/task_status/{task_id}>
    - Результат - список похожих фильмов.

4. Если модель не обучена - предложение перейти на страницу обучения.

Nginx проксирует запросы к сервису на порту 8000 (контейнер `web`).

## Запуск в Kubernetes

### 1. Развертывание

Применить конфигурации:

```bash
kubectl apply -f k8s/ --recursive
```

Структура директории с k8s:

```plaintext
├── celery/                     # Ресурсы Celery
│   └── deployment.yaml         # Деплоймент Celery
├── db/                         # Ресурсы PostgreSQL
│   ├── deployment.yaml         # Деплоймент БД
│   ├── pvc.yaml                # Том
│   └── service.yaml            # Сервис БД
├── nginx/                      # Ресурсы Nginx
│   ├── configmap.yaml          # Конфиг Nginx
│   ├── deployment.yaml         # Деплоймент Nginx
│   └── service.yaml            # Сервис Nginx
├── rabbitmq/                   # Ресурсы RabbitMQ
│   ├── deployment.yaml         # Деплоймент RabbitMQ
│   └── service.yaml            # Сервис RabbitMQ
└── web/                        # Ресурсы Django
    ├── deployment.yaml         # Деплоймент
    ├── pvc.yaml                # Том
    └── service.yaml            # Сервис
```

### 2. Доступ через Minikube

После развертывания:

```bash
minikube tunnel
```

Проверка IP:

```bash
kubectl get svc nginx -n highload-project -o wide
```

Пример вывода:

```bash
NAME    TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
nginx   LoadBalancer   10.96.45.217   127.0.0.1     80:32456/TCP   2m
```

Точки доступа:

- Основной интерфейс: [http://localhost/app](http://localhost/app)
- Админка: [http://localhost/admin](http://localhost/admin)
- Health Check: [http://localhost/health](http://localhost/health)

### 3. Использование сервиса

1. На главной странице:
    - Ссылка на статью (напр., Gladiator)
    - Количество рекомендаций (1-10)

2. Нажать "Search" для создания задачи.

3. Проверка результатов:
    - Статус: <http://localhost/app/task_status/{task_id}>
    - Список похожих фильмов по завершении.

4. Если модель не обучена - предложение перейти на страницу обучения.

[Back to top / Наверх](#movie-recommendation-service--сервис-рекомендации-фильмов)
