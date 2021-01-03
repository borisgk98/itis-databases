from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from names import get_full_name
import sys

auth_provider = PlainTextAuthProvider(username='admin', password='cassPass1234')
cluster = Cluster(["192.168.2.166"], port=9042,auth_provider=auth_provider)
session = cluster.connect()
session.set_keyspace('test')

insert = session.prepare("insert into test.TEST(id, name) values (?, ?)")

n = 10**4
k = 10**6
for id in range(1 + k, k + n + 1):
    session.execute(insert, [id, get_full_name()])

sys.exit(0)
