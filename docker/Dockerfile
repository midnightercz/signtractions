FROM fedora:latest as INSTALL
LABEL quay.expires-after=2d
RUN mkdir -p /workspace/signtractions
COPY --exclude=./dist --exclude=htmlcov --exclude=.pytest_cache --exclude=dist --exclude=view . /workspace/signtractions/
RUN microdnf install -y npm redis git gcc krb5-devel python3-devel git python3-qpid-proton openssl-devel tar https://github.com/sigstore/cosign/releases/download/v2.2.4/cosign-2.2.4-1.x86_64.rpm
RUN pip install --prefix /usr/ certifi krb5 

FROM INSTALL as BUILD

ADD docker/entry_point.sh /entry_point.sh
RUN chmod +x /entry_point.sh
ADD docker/redis.conf /etc/redis/redis.conf
ADD docker/certs/* /etc/pki/ca-trust/source/anchors/

FROM BUILD as CERTS

RUN update-ca-trust
ENV REQUESTS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.trust.crt
RUN mkdir /userdata
VOLUME /userdata
RUN mkdir /redis_data
VOLUME /redis_data

RUN redis-server /etc/redis/redis.conf

FROM CERTS as PYTRACTIONS

WORKDIR /workspace/
RUN git clone https://github.com/midnightercz/pytractions.git@v0.0.10
WORKDIR /workspace/pytractions
RUN ls /workspace/pytractions
RUN pip install --prefix /usr/ -r requirements.txt
RUN pip install --prefix /usr/ .

FROM PYTRACTIONS as SIGNTRACTIONS

WORKDIR /workspace
RUN ls /workspace/signtractions/
RUN pip install --prefix /usr/ -r /workspace/signtractions/requirements.txt
RUN pip install --prefix /usr/ -v /workspace/signtractions/

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

