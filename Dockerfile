FROM python

ENV LETTERBOXD_USERNAME=''
ENV PLEX_TOKEN=''
ENV PLEX_HOST=''

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]