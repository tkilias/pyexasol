docker network create -d bridge pyexasol-test-network
IP_PREFIX=$(docker network inspect pyexasol-test-network | grep Gateway | cut -f 4 -d '"' | cut -f 1,2,3 -d ".")
IP="${IP_PREFIX}.2"
SUBNET="${IP}/24"
echo $SUBNET

mkdir exa
pushd exa
mkdir etc
pushd etc
docker run --net pyexasol-test-network --rm -i --privileged  exasol/docker-db:7.0.3 -q init-sc --template --num-nodes 1 -p > EXAConf
sed -i "s/Checksum = .*$/Checksum = COMMIT/g" EXAConf
sed -i "s#PrivateNet = .*\$#PrivateNet = $SUBNET#g" EXAConf
sed -i "s#Cert = .*\$#Cert = /tmp/certs/cert.crt#g" EXAConf
sed -i "s#CertKey = .*\$#CertKey = /tmp/certs/cert.key#g" EXAConf
sed -i "s#CertAuth = .*\$#CertAuth = /tmp/certs/rootCA.crt#g" EXAConf
sed -i "s# Size = .*\$# Size = 2GB#g" EXAConf
#sed -i "s#CertVerify = .*\$#CertVerify = required#g" EXAConf
popd

DEVICE_SIZE_IN_MEGABYTES=4000

# Setup directory "exa" with pre-configured EXAConf to attach it to the exasoldb docker container
mkdir -p data/storage
dd if=/dev/zero of=data/storage/dev.1 bs=1M count=1 seek=$DEVICE_SIZE_IN_MEGABYTES
popd


bash create_certificates.sh "$IP"
docker rm -f pyexasol-test-db-container
docker run --net pyexasol-test-network --rm -d --privileged -v "$PWD/certs/$IP:/tmp/certs" -v "$PWD/exa:/exa" --name pyexasol-test-db-container exasol/docker-db:7.0.3
