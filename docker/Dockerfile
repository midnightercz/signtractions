FROM localhost/pytractions:latest
COPY ./requirements.txt /
RUN microdnf install -y krb5-devel gcc python3-devel git python3-qpid-proton openssl-devel tar
RUN pip install --prefix /usr/ gssapi krb5 certifi
RUN pip install --prefix /usr/ -r /requirements.txt
COPY dist/*.tar.gz /
RUN tar -xvzf /*.tar.gz
RUN pip -v install sign-tractions-0.0.1/
#RUN pip install sign-tractions-0.0.1.tar.gz
ADD https://certs.corp.redhat.com/certs/2022-IT-Root-CA.pem /etc/pki/ca-trust/source/anchors/2022-IT-Root-CA.pem
ADD https://certs.corp.redhat.com/certs/2015-IT-Root-CA.pem /etc/pki/ca-trust/source/anchors/2015-IT-Root-CA.pem
RUN update-ca-trust
ENV REQUESTS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.trust.crt
RUN mkdir /userdata
VOLUME /userdata
ENTRYPOINT ["/bin/bash"]
