FROM python:3.6
WORKDIR /rec_api
ADD ./requirements.txt /rec_api/requirements.txt
RUN pip3 install -r requirements.txt
ADD . /rec_api
