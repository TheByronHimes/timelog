# BASE: a base image with updated packages
FROM python:3.13-alpine AS base
RUN apk upgrade --no-cache --available

# BUILDER: a container to build the service wheel
FROM base AS builder
RUN pip install build
COPY . /service
WORKDIR /service
RUN python -m build

# DEP-BUILDER: a container to (build and) install dependencies
FROM base AS dep-builder
RUN apk update
RUN apk add build-base gcc g++ libffi-dev zlib-dev
RUN apk upgrade --available
WORKDIR /service
COPY --from=builder /service/lock/requirements.txt /service
RUN pip install --no-deps -r requirements.txt

# RUNNER: a container to run the service
FROM base AS runner
WORKDIR /service
RUN rm -rf /usr/local/lib/python3.13
COPY --from=dep-builder /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=builder /service/dist/ /service
RUN pip install --no-deps *.whl
RUN rm *.whl
RUN adduser -D appuser
WORKDIR /home/appuser
USER appuser
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["timelog"]
