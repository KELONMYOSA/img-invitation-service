FROM python:3.11-slim as builder

RUN pip install poetry
RUN poetry self add poetry-plugin-export

COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt --without=dev > requirements.txt \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*

COPY src /app/src
COPY storage /app/storage
COPY .env main.py /app/

ENTRYPOINT ["python", "main.py"]
