# Starting 

## From docker 

Forward this steps(in console) for start bot

1. One

```
docker build -t telegram-bot:latest .
```

2. Two

```
docker run -d --name telegram-bot-container telegram-bot:latest
```

3. Success!

## From Python (Only 3.11.x and older)

1. Install requirements.txt

```
pip install -r requirements.txt
```

2. Start the bot 

```
python3 main.py
```
