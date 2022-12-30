FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8080

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY app.py /app
COPY src /app/src

COPY submodules /app/submodules
RUN apt-get update || : && apt-get install npm -y
# now installl all node dependencies in the package `app/submodules/corsano-realm-converter/`
RUN cd /app/submodules/corsano-realm-converter && npm install
RUN cd /app

ENV PYTHONPATH "./src"

CMD python app.py
