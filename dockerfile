FROM python:3.12-bookworm AS build

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PIP_NO_CACHE_DIR=off \
    POETRY_VERSION=1.7.1

WORKDIR /src

COPY ./src /src/src/
COPY pyproject.toml poetry.lock migrations /src/

RUN pip install "poetry==$POETRY_VERSION"
RUN poetry install --only main

FROM python:3.12-slim-bookworm AS app

COPY --from=build /src/ ./

ENV VIRTUAL_ENV=/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

CMD ["python", "-m", "src.main"]
