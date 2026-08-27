FROM python:3.11-alpine

ENV LETTERBOXD_USERNAME=''
ENV PLEX_TOKEN=''
ENV PLEX_HOST=''
ENV BASE_URL='http://letterboxd-list:5000'
ENV CRON_SCHEDULE='30 * * * *'

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "echo \"$CRON_SCHEDULE cd /usr/src/app && python main.py > /proc/1/fd/1 2>&1\" | crontab - && crond -f -l 2"]