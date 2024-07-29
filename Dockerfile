FROM python:3.7

ENV PYTHONUNBUFFERED 1

WORKDIR /code/

RUN pip install -r requirements.txt

COPY . /code/
RUN rm pyproject.toml
RUN pip install -e .

RUN useradd flask
RUN chown -R flask /code
USER flask

EXPOSE 8000
CMD exec gunicorn wsgi:app --bind 0.0.0.0:8000 --workers 3
