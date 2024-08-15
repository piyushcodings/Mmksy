FROM python:3.9

RUN apt -qq update && apt -qq install -y git wget ffmpeg
WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app
COPY . . 

RUN pip3 install -r requirements.txt 
EXPOSE 80
CMD ["python3","-m","uploader"]
