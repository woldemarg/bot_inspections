## [@business_control_bot](https://t.me/business_control_bot)

### Опис (MVP):
Перевірки бізнесу за даними іnspections.gov.ua.
1. Редагування (додання/видалення) персонального переліку кодів ЄДРПОУ/ІПН.
3. Отримання календаря перевірок за кодами у переліку.<br /><br />
![](https://api.monosnap.com/file/download?id=xwUIP5Snjaq3BvUvgm4AyHcBM9ZSsI)

### Майбутній функціонал:
* Повідомлення із нагадуваннями напередодні перевірок
* Інформування про освітні заходи за напрямом майбутньої перевірки
* Аналітика ризиків під час перевірок

### Джерело даних:
* [inspections.gov.ua API v1.1](http://api.ias.brdo.com.ua/v1_1/manual)
* [специфікація API v1.1](https://docs.google.com/document/d/1YQMEEFf_EtuZMud2OVYeVpi3aDE6lsuUqFrsbzS5RKk/edit)
* Приклад запиту для отримання даних провсі перевірки за кодом ЄДРПОУ/ІПН:
```
http://api.ias.brdo.com.ua/v1_1/inspection?apiKey=<personal_api_key>&code=40075815
```
___

### Корисні лінки/матеріали
* [inline keyboard](https://stackoverflow.com/a/60616915/6025592)
* [deploy docker container on HEROKU](https://atrium.ai/resources/build-and-deploy-a-docker-containerized-python-machine-learning-model-on-heroku)
* [where to host telegram bots](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Where-to-host-Telegram-Bots)
* [deploy bot on Heroku](https://towardsdatascience.com/how-to-deploy-a-telegram-bot-using-heroku-for-free-9436f89575d2)
* [бот для телеграм на Python](https://tproger.ru/translations/telegram-bot-create-and-deploy/)
* [bot + MySQL](https://radiohlam.ru/telegram_bot_4/)
* [bot + SQLite](https://www.codementor.io/@garethdwyer/building-a-chatbot-using-telegram-and-python-part-2-sqlite-databse-backend-m7o96jger)
* [webhook listener with fastapi](https://majornetwork.net/2020/10/webhook-listener-with-fastapi/)
* [database in docker container](https://wkrzywiec.medium.com/database-in-a-docker-container-how-to-start-and-whats-it-about-5e3ceea77e50)
* [docker compose with python and postgre](https://dev.to/stefanopassador/docker-compose-with-python-and-posgresql-33kk)
* [postgre with heroku](https://medium.com/better-programming/how-to-containerize-and-deploy-apps-with-docker-and-heroku-b1c49e5bc070)

___

### Run Docker container locally:
* CLI commands from .\develop:
```
.\ngrok\ngrok http 8080
```
* change in *bot_script.py*
```
HOOK = 'https://8a5e328ee754.ngrok.io'  # as example
```
* CLI commands in new terminal from .\deploy
```
docker build -t bot .
docker run -p 127.0.0.1:8080:5000 bot
# or
docker-compose up
```

### Deploy on Heroku:
* run Docker Desktop (Win10)
* CLI commands from .\deploy:
```
heroku container:login
heroku create
```
* change in *bot_script.py*
```
HOOK = 'https://sleepy-woodland-05300.herokuapp.com/'  # as exampleheroku
```
* uncomment in *bot_dbhelper_ps.py*
```
DATABASE_URL = os.environ['DATABASE_URL']
self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')
```
* CLI commands:
```
heroku git:remote -a sleepy-woodland-05300
git remote -v  # to check
heroku container:push web
heroku container:release web
heroku logs --tail # to check
heroku ps:scale web=0 # stop app
heroku ps:scale web=1 # start app
```
* order *Heroku Postgres* add-on in 'Resources' tab on app's page ([see](https://medium.com/better-programming/how-to-containerize-and-deploy-apps-with-docker-and-heroku-b1c49e5bc070))
___

### Tags
telegram bot, fastapi, docker container, heroku, python, sqlite, postgres, asgi server
