FROM python:3.6-alpine
ENV PYTHONIOENCODING utf-8

COPY . /code/
RUN pip install flake8

RUN pip install -r /code/requirements.txt

WORKDIR /data/


CMD ["python", "-u", "/code/component.py"]
