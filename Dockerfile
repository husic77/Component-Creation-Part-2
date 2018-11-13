FROM python:3.6-slim
ENV PYTHONIOENCODING utf-8

COPY . /code/

RUN pip install -r /code/requirements.txt

WORKDIR /data/


CMD ["python", "-u", "/code/component.py"]
