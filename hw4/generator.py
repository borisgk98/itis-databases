from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from names import get_full_name
from random import randrange
import sys

auth_provider = PlainTextAuthProvider(username='admin', password='cassPass1234')
cluster = Cluster(["192.168.2.166"], port=9042,auth_provider=auth_provider)
session = cluster.connect()
session.set_keyspace('hw4')

insert = session.prepare("insert into hw4.empl(id, dept_name, name) VALUES (?, ?, ?)")

n = 10**5
k = 0
total_ins = 0
deps = ["BI", "HR", "IT", "AD", "M", "MO", "ML", "DS", "X"]
for id in range(1 + k, k + n + 1):
    try:
        v = [id, deps[randrange(0, len(deps))], get_full_name()]
        session.execute(insert, v)
        total_ins += 1
        print(total_ins, " (ok): ", v)
    except Exception as e:
        print(e)

sys.exit(0)
