import pyexasol
import ssl
import websocket
from pathlib import Path
import ssl
#c=pyexasol.connect(dsn="172.20.0.2:8563", user="sys", password="exasol", encryption=True, websocket_sslopt={"cert_reqs": ssl.CERT_REQUIRED, "ca_certs": "certs/172.20.0.2/rootCA.crt"}, debug=True)
#r=c.execute("SELECT 1")
#print(r.fetchall())

host="wss://172.20.0.2:8563"
rootca_file = Path("certs/172.20.0.2/rootCA.crt")
if not rootca_file.exists():
    raise Exception("rootca not exists")
c=pyexasol.connect(dsn="172.20.0.2:8563", user="sys", password="exasol", encryption=True, websocket_sslopt={"cert_reqs": ssl.CERT_REQUIRED, "ca_certs": "certs/172.20.0.2/rootCA.crt"}, debug=True)
r=c.execute("SELECT 1")
print(r.fetchall())

#ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
#ssl_context.load_verify_locations(rootca_file)

#ws = websocket.create_connection(host, sslopt={"cert_reqs": ssl.CERT_REQUIRED, "ca_certs": str(rootca_file)})
#ws = websocket.create_connection(host, sslopt={"cert_reqs": ssl.CERT_NONE, "ca_certs": str(rootca_file)})
#ws = websocket.create_connection(host, ssl=ssl_context)

#print(ws)
