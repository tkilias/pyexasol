"""
Example 32
Test Prepared Statements
"""

import pyexasol
import pprint
import _config as config
import hashlib
from stopwatch import Stopwatch
import pandas as pd

numrows=10000
columns = [
            [i for i in range(numrows)],
            [hashlib.sha224(str(i).encode("utf-8")).hexdigest() for i in range(numrows)],
            [i%2==0 for i in range(numrows)]
        ]
df = pd.DataFrame({'c1':columns[0],'c2':columns[1],'c3':columns[2]})
print(df)

#pprint.pprint(columns)

C=pyexasol.connect(dsn=config.dsn, user=config.user, password=config.password, schema=config.schema)
C.execute("CREATE OR REPLACE TABLE PREPARED_STATEMENT_INSERT(c1 int, c2 VARCHAR(100), c3 boolean);")
stopwatch = Stopwatch()
C.import_from_pandas(df,'PREPARED_STATEMENT_INSERT')
C.close()
print("import via import_from_pandas of rows %s took %s"%(numrows, str(stopwatch)))

C=pyexasol.connect(dsn=config.dsn, user=config.user, password=config.password, schema=config.schema)
C.execute("CREATE OR REPLACE TABLE PREPARED_STATEMENT_INSERT(c1 int, c2 VARCHAR(100), c3 boolean);")
stopwatch = Stopwatch()
rep=C.req({
    'command': 'createPreparedStatement',
    'sqlText': 'insert into PREPARED_STATEMENT_INSERT values (?,?,?)'
    })['responseData']
C.req({
    'command': 'executePreparedStatement',
    'statementHandle': rep['statementHandle'],
    'numColumns': rep['parameterData']['numColumns'],
    'numRows': numrows,
    'columns': rep['parameterData']['columns'],
    'data': columns
    })
C.close()
print("import via prepared statement of rows %s took %s"%(numrows, str(stopwatch)))
