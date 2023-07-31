# To build the image from this dockerfile: docker image build -t datagen:latest .
# To run the container: docker run -d -p 9999:<port to publish> datagen:latest
#     For example: docker run -d -p 9999:9999 datagen:latest

FROM python:3.10

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app

ENV PORT=9999
ENV PYTHONPATH=/app:${PYTHONPATH}

ENTRYPOINT [ "python", "server/index.py" ]

