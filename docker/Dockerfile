FROM quay.io/jluza/pytractions:latest
COPY . /workspace
RUN microdnf install -y gcc krb5-devel python3-devel git python3-qpid-proton openssl-devel tar
RUN pip install --prefix /usr/ certifi krb5 
RUN pip install --prefix /usr/ -r workspace/requirements.txt
RUN pip install --prefix /usr/ -v /workspace/
ADD docker/2022-IT-Root-CA.pem /etc/pki/ca-trust/source/anchors/2022-IT-Root-CA.pem
ADD docker/2015-IT-Root-CA.pem /etc/pki/ca-trust/source/anchors/2015-IT-Root-CA.pem
RUN update-ca-trust
ENV REQUESTS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.trust.crt
RUN mkdir /userdata
VOLUME /userdata