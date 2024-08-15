FROM ubuntu:latest 

RUN mkdir ./app
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata
  
RUN apt -qq update --fix-missing && \
    apt -qq install -y git \
    mediainfo \
    
   
    python3 \
    ffmpeg \
    python3-pip

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD bash start.sh
