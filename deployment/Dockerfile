FROM python:3.9

WORKDIR /app

RUN pip install uv

COPY ./pyproject.toml .
COPY ./uv.lock .

RUN uv sync

COPY . .

CMD ["uv", "run", "fastapi", "run", "src/main.py", "--proxy-headers", "--host", "0.0.0.0", "--port", "8080"]