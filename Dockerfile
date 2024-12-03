FROM continuumio/miniconda3:latest as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

COPY environment.yml .

RUN conda env create -f environment.yml

SHELL ["conda", "run", "-n", "dev", "/bin/bash", "-c"]

RUN conda install -c conda-forge uvicorn

WORKDIR /cryptotracker4

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

USER appuser

COPY . .

EXPOSE 8000