FROM antonapetrov/uvicorn-gunicorn-fastapi:python3.9-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONIOENCODING='utf-8'
ENV LANG='C.UTF-8'
ENV MODULE_NAME=api.main
WORKDIR /app

# install Poetry (separate step to make faster rebuilds)
RUN pip install --disable-pip-version-check --no-cache-dir -q wheel \
    pip install --disable-pip-version-check --no-cache-dir -q poetry crcmod

COPY pyproject.toml /app/
COPY poetry.lock /app/

# the extra delete steps here probably aren't needed, but good to have available
RUN poetry install --no-root --only main \
  && rm -r /root/.cache/pypoetry/cache /root/.cache/pypoetry/artifacts/ \
  && apt-get autoremove -yqq \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY . /app
