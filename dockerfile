# To build the image from this dockerfile: docker image build -t data-driver .
# To run the container: docker run -i data-driver SCRIPT_OPTIONS < CONFIG_FILE_NAME > OUTPUT_FILE_NAME
#     For example: docker run -i data-driver -n 3 < examples/simple_config.json > out.json

FROM python:3.10

WORKDIR /driver

RUN pip install python-dateutil \
  && pip install kafka-python \
  && pip install confluent-kafka \
  && pip install sortedcontainers \
  && pip install numpy

COPY DruidDataDriver.py .

ENTRYPOINT [ "python", "./DruidDataDriver.py"]
