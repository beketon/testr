FROM arg:latest

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG UID=1001
ARG GID=1001

RUN addgroup --gid "${GID}" --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid "${UID}" --system --group app

COPY ./deployment/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY --chown=app:app . /app

USER app

WORKDIR /app/

ENV PYTHONPATH=/app
ENV NAME=b-express
ENV WORKERS=3
ENV LOG_LEVEL=error
ENV PORT=80

HEALTHCHECK CMD curl --fail http://localhost:$PORT || exit 1

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]