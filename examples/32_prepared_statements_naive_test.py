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

def generate_dataset(num_rows):
    columns = [
                [i for i in range(num_rows)],
                [hashlib.sha224(str(i).encode("utf-8")).hexdigest() for i in range(num_rows)],
                [i%2==0 for i in range(num_rows)]
            ]
    df = pd.DataFrame({'c1':columns[0],'c2':columns[1],'c3':columns[2]})
    return df

def create_connection(json):
    C=pyexasol.connect(dsn=config.dsn, user=config.user, password=config.password, schema=config.schema, json_lib=json)
    C.set_autocommit(False)
    C.execute("CREATE OR REPLACE TABLE PREPARED_STATEMENT_INSERT(c1 int, c2 VARCHAR(100), c3 boolean);")
    return C

def import_via_import_from_pandas(num_rows, json, run):
    df = generate_dataset(num_rows)
    C = create_connection(json)
    stopwatch = Stopwatch()
    C.import_from_pandas(df,'PREPARED_STATEMENT_INSERT')
    C.commit()
    stopwatch.stop()
    C.close()
    print("%s,import_from_pandas,%s,%s,%s"%(run, json, num_rows, str(stopwatch.duration)),flush=True)

def import_via_prepared_statement(num_rows, num_iterations, json, run):
    df = generate_dataset(num_rows)
    partitions = [] 
    for i in range(num_iterations):
        partition_size = num_rows//num_iterations
        partition_start = i*partition_size
        partition_end = (i+1)*partition_size
        partition_df = df.iloc[partition_start:partition_end]
        partition = [partition_df[column].tolist() for column in  partition_df.columns]
        partitions.append(partition)
    C = create_connection(json)
    stopwatch = Stopwatch()
    rep=C.req({
        'command': 'createPreparedStatement',
        'sqlText': 'insert into PREPARED_STATEMENT_INSERT values (?,?,?)'
        })['responseData']
    for i in range(num_iterations):
        C.req({
            'command': 'executePreparedStatement',
            'statementHandle': rep['statementHandle'],
            'numColumns': rep['parameterData']['numColumns'],
            'numRows': partition_size,
            'columns': rep['parameterData']['columns'],
            'data': partitions[i]
            })
    C.commit()
    stopwatch.stop()
    C.close()
    print("%s,prepared_statement,%s,%s/%s,%s"%(run, json, num_rows, num_iterations, str(stopwatch.duration)),flush=True)

for run in range(10):
    for json in ["json","ujson","rapidjson"]:
        for row_power in range(0,7):
            num_rows = 10 ** row_power
            import_via_import_from_pandas(num_rows,json,run)
            for iterations_power in range(0,max(1,row_power-1)):
                num_iterations = 10 ** iterations_power 
                import_via_prepared_statement(num_rows,num_iterations,json,run)
