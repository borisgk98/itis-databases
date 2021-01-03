import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


plt.bar(["cassandra-0", "cassandra-1", "cassandra-2"], [86683, 85550, 87682], color=['r', 'g', 'b'], alpha=0.75)
plt.xlabel('Cassandra node')
plt.ylabel('Rows count')
plt.grid(True)

plt.savefig("histogram.png")
