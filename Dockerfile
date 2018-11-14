FROM python:3.6.6

WORKDIR /usr/src/app

COPY Requirements.txt ./
RUN pip install --no-cache-dir -r Requirements.txt

COPY plrc/ ./plrc/
COPY plrc_project/ ./plrc_project/
RUN pip install --no-cache-dir -r plrc_project/requirements.txt

COPY swagger-ui/ ./swagger-ui/

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

RUN mkdir -p ./results
RUN chmod 777 ./results
VOLUME ./results

RUN mkdir -p ./graph
RUN chmod 777 ./graph
VOLUME ./graph

EXPOSE 4200

CMD ["./startup.sh"]
