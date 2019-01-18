import matplotlib.pyplot as plt

from polymech import compression
from polymech.sources import kechekyan


dataset = kechekyan('test.xlsx')
results = compression.analyze(dataset, 14, 40, 5)
print(results)
plt.plot(*results.processed_dataset.T)
plt.plot(*zip(results.young_modulus.first_point, results.young_modulus.second_point), 'r-')
plt.plot(results.yield_point.elongation, results.yield_point.tension, 'ro')
plt.show()
