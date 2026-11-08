# Landing (site/) built with Node, then served by the stdlib server.py next to the index in data/.
# The index is not in the image: mount data/ at /app/data (see the Coolify storage) so refresh.sh can update it.

FROM node:22-alpine AS site
WORKDIR /site
RUN corepack enable
COPY site/package.json site/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY site/ ./
RUN pnpm build

FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UI_INDEXER_HOST=0.0.0.0 UI_INDEXER_PORT=3040
RUN pip install --no-cache-dir numpy
COPY server.py indexer.py ./
COPY --from=site /site/dist ./site/dist
RUN useradd --create-home app && mkdir -p /app/data && chown app /app/data
USER app
EXPOSE 3040
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:3040/health', timeout=4).status==200 else 1)"
CMD ["python", "server.py"]
