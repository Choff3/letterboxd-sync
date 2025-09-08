FROM python

ENV LETTERBOXD_USERNAME=''
ENV PLEX_TOKEN=''
ENV PLEX_HOST=''
ENV RADARR_TOKEN=''
ENV RADARR_HOST=''
ENV USER_AGENT=''

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]