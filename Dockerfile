# Base image with headless chrome + chromium + chromedriver
FROM selenium/standalone-chrome as selenium-python-base

USER root
# install python
RUN apt-get update && apt-get install -y \
    python3 python3-pip\
    && rm -rf /var/lib/apt/lists/*

FROM selenium-python-base as install-poetry

ENV POETRY_VERSION=1.2.0
ENV POETRY_HOME=/opt/poetry
ENV POETRY_NO_INTERACTION=1
ENV POETRY_CACHE_DIR=/opt/.cache

# install poetry
RUN apt-get update \
    && apt-get install -y curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && chmod 755 ${POETRY_HOME}/bin/poetry

ENV PATH="$POETRY_HOME/bin:$PATH"

FROM install-poetry as install-requirements

WORKDIR /src
COPY poetry.lock pyproject.toml ./

# create requirements.txt
RUN poetry check
RUN poetry export -f requirements.txt --output requirements.txt

RUN pip install -r requirements.txt
COPY src/ .

FROM install-requirements as final-stage

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

# create directories for storing logs
RUN mkdir "logs" && mkdir "logs/chromedriver"  && mkdir "logs/luxembook"

CMD ["python3", "luxembook.py" , "true"]
