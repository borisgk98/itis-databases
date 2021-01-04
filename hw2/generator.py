from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from names import get_full_name
import sys

auth_provider = PlainTextAuthProvider(username='admin', password='cassPass1234')
cluster = Cluster(["192.168.2.166"], port=9042,auth_provider=auth_provider)
session = cluster.connect()
session.set_keyspace('test3')

insert = session.prepare("insert into test3.TEST3(id, name) values (?, ?)")

n = 10**7
k = 2*10**6
total_ins = 0
for id in range(1 + k, k + n + 1):
    try:
        session.execute(insert, [id, get_full_name()])
        total_ins+=1
        print(total_ins, " ok")
    except Exception as e:
        print(e)

sys.exit(0)
