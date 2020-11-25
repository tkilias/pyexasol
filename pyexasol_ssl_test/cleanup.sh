docker rm -f pyexasol-test-db-container
docker volume rm pyexasol-test-volume
docker network rm pyexasol-test-network
rm -r exa
rm -r certs
rm database-ip.txt
