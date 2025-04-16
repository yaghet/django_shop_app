FROM python:3.13

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

ADD https://astral.sh/uv/install.sh /uv-installer.sh

RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"


WORKDIR /app
ADD . /app

ENV DJANGO_SETTINGS_MODULE=mysite.settings

RUN uv sync

CMD ["uv", "run", "online-shop/manage.py", "runserver", "0.0.0.0:8000"]