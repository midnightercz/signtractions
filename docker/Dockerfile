FROM signtractions:base
LABEL quay.expires-after=2d

ARG SOURCE=""
COPY ${SOURCE} /workspace/
COPY build-requirements.txt /workspace/signtractions/

RUN tar -xvzf /workspace/signtractions-*.tar.gz -C /workspace/signtractions

ADD docker/entry_point.sh /entry_point.sh
RUN chmod +x /entry_point.sh

WORKDIR /workspace/
RUN git clone --branch v0.0.10 https://github.com/midnightercz/pytractions.git
WORKDIR /workspace/pytractions
RUN ls /workspace/pytractions
RUN pip install --prefix /usr/ -r requirements.txt
RUN pip install --prefix /usr/ .

WORKDIR "/workspace/signtractions/"
RUN pip install --prefix /usr/ -r build-requirements.txt
RUN ls /workspace/signtractions/signtractions-*
RUN ls /workspace/signtractions/signtractions-*/signtractions/
RUN (cd /workspace/signtractions/signtractions-* ; python -m signtractions.generate_entry_points)
RUN (cd /workspace/signtractions/signtractions-* ; pip install --prefix /usr/ . )

WORKDIR /workspace/pytractions/traction-runner-webui/frontend
RUN npm install 
WORKDIR /workspace/pytractions/traction-runner-webui/backend
RUN npm install 
WORKDIR /workspace/pytractions/traction-runner-webui/
RUN npm install 

WORKDIR /
CMD ["/entry_point.sh"]


EXPOSE 4200
EXPOSE 3000
EXPOSE 6379

ENV NG_HOST="0.0.0.0"
ENV NG_PORT=4200
ENV BACKEND_HOST="0.0.0.0"
ENV BACKEND_PORT=3000

