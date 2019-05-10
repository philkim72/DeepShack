FROM tensorflow/tensorflow:latest-py3
COPY requirements.txt ./
COPY main.py ./
RUN apt-get update && apt-get install -y python-opencv
RUN pip install -r requirements.txt
CMD python main.py
