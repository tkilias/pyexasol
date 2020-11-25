#!/bin/bash

DOCKER_DB_VERSION=7.0.3
DEVICE_SIZE_IN_MEGABYTES=4000
SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

function create_docker_network {
  docker network create -d bridge pyexasol-test-network
  IP_PREFIX=$(docker network inspect pyexasol-test-network | grep Gateway | cut -f 4 -d '"' | cut -f 1,2,3 -d ".")
  IP="${IP_PREFIX}.2"
  SUBNET="${IP}/24"
  echo "$IP" > database-ip.txt 
}

function create_and_change_exaconf {
  docker run --net pyexasol-test-network --rm -i --privileged  "exasol/docker-db:$DOCKER_DB_VERSION" -q init-sc --template --num-nodes 1 -p > EXAConf
  sed -i "s/Checksum = .*$/Checksum = COMMIT/g" EXAConf
  sed -i "s#PrivateNet = .*\$#PrivateNet = $SUBNET#g" EXAConf
  sed -i "s# Size = .*\$# Size = 2GB#g" EXAConf
  sed -i "s#\[DB : DB1]#[DB : DB1]\n    Params = -tlsPrivateKeyPath=/exa/etc/certs/cert.key -tlsCertificatePath=/exa/etc/certs/cert.crt #g" EXAConf
}

function create_file_device {
  mkdir -p data/storage
  dd if=/dev/zero of=data/storage/dev.1 bs=1M count=1 seek=$DEVICE_SIZE_IN_MEGABYTES
}

function create_docker_volume {
  mkdir exa
  pushd exa
  mkdir etc
  pushd etc
  create_and_change_exaconf
  bash "$SCRIPT_DIR/create_certificates.sh" "$IP"
  ls -l
  popd
  create_file_device
  popd

  docker volume create pyexasol-test-volume
  docker run --rm -v "$PWD/exa:/exa" -v "pyexasol-test-volume:/volume" busybox sh -c "cp -r  /exa/* /volume; chown -R 500:500 /volume/etc/certs; chmod 600 /volume/etc/certs/*; chmod 700 /volume/etc/certs/"

  cp -r exa/etc/certs .
}

bash "$SCRIPT_DIR/cleanup.sh"
create_docker_network
create_docker_volume

docker run --net "pyexasol-test-network" --rm -d --privileged -v "pyexasol-test-volume:/exa" --name "pyexasol-test-db-container" "exasol/docker-db:$DOCKER_DB_VERSION"
