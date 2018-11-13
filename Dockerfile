FROM python:3.6.6

WORKDIR /usr/src/app

COPY Requirements.txt ./
COPY plrc_project/requirements.txt ./
RUN pip install --no-cache-dir -r Requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY plrc/ ./plrc/
COPY swagger-ui/ ./swagger-ui/
COPY graph/ ./graph/

COPY server.py 		./server.py
COPY config.json 	./config.json
COPY swagger.json 	./swagger.json
COPY VERSION 		./VERSION
COPY startup.sh         ./startup.sh
RUN chmod 777 ./startup.sh && \
    sed -i 's/\r//' ./startup.sh

RUN mkdir -p ./logs
RUN chmod 777 ./logs
VOLUME ./logs

RUN mkdir -p ./images
RUN chmod 777 ./images
VOLUME ./images

EXPOSE 4200

CMD ["./startup.sh"]
