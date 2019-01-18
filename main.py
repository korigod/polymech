import matplotlib.pyplot as plt

from polymech import compression
from polymech.sources import kechekyan


dataset = kechekyan('test.xlsx')
results = compression.analyze(dataset)
print(results)
plt.plot(*results.trimmed_dataset.T)
plt.plot(*zip(results.young_modulus.first_point, results.young_modulus.second_point), 'r-')
plt.plot(results.yield_point.timestamp, results.yield_point.force, 'ro')
plt.show()
