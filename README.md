# PowerBank Sharing - Energo


[![pipeline status](https://gitlab.informatics.ru/alexkoritsa/powerbank-sharing/badges/master/pipeline.svg)](https://gitlab.informatics.ru/alexkoritsa/powerbank-sharing/commits/master)

> Если у Вас вдруг разрядился телефон или планшет, а у Вас с собой ничего нет - Вам срочно нужен PowerBank!

  - Простой и понятный функционал
  - Легко найти благодаря карте
  - Крутой фидбэк

### Как запускать проект

```sh
$ git clone git@gitlab.informatics.ru:alexkoritsa/powerbank-sharing.git
$ cd powerbank-sharing
$ python3 manage.py makemigrations
$ python3 manage.py migrate
$ python3 manage.py runserver
```

**Теперь вы можете использовать наш сайт по ссылке:** `http://localhost:8000/`