FROM python:3.10.6-slim
RUN apt-get update
# installing system dependencies for building and installing libraries (GCC for example)
RUN apt-get install -y build-essential
# setting PYTHONUNBUFFERED to a value different from 0 ensures that the python output i.e. the stdout and stderr streams are sent straight to terminal (e.g. your container log) 
ENV PYTHONUNBUFFERED=1
# setting Lang env var For standard language support
ENV LANG C.UTF-8
# Symbolic links to pip and python for ease of use in the cli
RUN ln -sf /usr/bin/pip3 /usr/bin/pip
RUN ln -sf /usr/bin/python3 /usr/bin/python
# upgrading package manager
RUN pip install --upgrade pip
# RUN pip install --upgrade setuptools
# setting the working directory to the project folder
WORKDIR /
COPY requirements.txt  ./
# Installing project dependencies
RUN pip install -r requirements.txt 
RUN playwright install chromium
RUN playwright install-deps chromium
COPY . ./
CMD [ "python","main.py" ]