import pyexasol
import ssl
c=pyexasol.connect(dsn="172.20.0.2:8563", user="sys", password="exasol", encryption=True, websocket_sslopt={"cert_reqs": ssl.CERT_REQUIRED, "ca_certs": "certs/172.20.0.2/rootCA.crt"})
r=c.execute("SELECT 1")
print(r.fetchall())
