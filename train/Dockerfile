FROM tensorflow/tensorflow:latest-py3-jupyter
COPY requirements.txt /tf
RUN apt-get update && apt-get install -y libsm6 libxext6 libxrender-dev python-opencv
RUN pip install -r requirements.txt
EXPOSE 9999
CMD jupyter-notebook --port=9999 --no-browser --ip=0.0.0.0 --allow-root --NotebookApp.token=''
