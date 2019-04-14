#!/bin/bash

openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -sha256 -days 1024 -out ca.crt -subj '/C=US/ST=CA/O=Organization/'

genkey() {
    OUTPEM="${2:-$1.pem}"
    openssl genrsa -out "$OUTPEM" 2048
    openssl req -new -sha256 -key "$OUTPEM" -subj "/C=US/ST=CA/O=Organization/CN=${3:-$1}" -out "$1.csr"
    openssl x509 -req -in "$1.csr" -CA ca.crt -CAkey ca.key -CAcreateserial -days 500 -sha256 >> "$OUTPEM"
    rm "$1.csr"
}

genkey init-p01st.push.apple.com
mkdir -p certs/courier.push.apple.com/
genkey courier.push.apple.com certs/courier.push.apple.com/server.pem *.push.apple.com