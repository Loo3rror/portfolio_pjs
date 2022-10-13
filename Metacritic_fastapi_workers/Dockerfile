FROM python:3.9

WORKDIR /

COPY . .

EXPOSE 8000

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn","meta_request:meta_app","-w","6","-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]