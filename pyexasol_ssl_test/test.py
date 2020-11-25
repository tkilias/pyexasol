import pyexasol
import ssl
import websocket
from pathlib import Path
import ssl

with open("database-ip.txt") as f:
    ip = f.read().strip()
rootca_file = Path("certs/rootCA.crt")
if not rootca_file.exists():
    raise Exception("rootca not exists")
dsn=f"{ip}:8563"
print(dsn)
c=pyexasol.connect(dsn=dsn, user="sys", password="exasol", encryption=True, websocket_sslopt={"cert_reqs": ssl.CERT_REQUIRED, "ca_certs": str(rootca_file)})
r=c.execute("SELECT 1")
print(r.fetchall())


