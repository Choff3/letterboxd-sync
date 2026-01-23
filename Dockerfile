FROM python

ENV LETTERBOXD_USERNAME=''
ENV PLEX_TOKEN=''
ENV PLEX_HOST=''
ENV BASE_URL='http://letterboxd-list-radarr.onrender.com'

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]