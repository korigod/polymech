import math
import matplotlib.pyplot as plt

from polymech import compression
from polymech.sources import kechekyan


dataset = kechekyan('test.xlsx')
diameter_mm = 8.4
cross_section_sq_mm = math.pi * diameter_mm ** 2 / 4
results = compression.analyze(dataset, 13.47, cross_section_sq_mm, 5.0)
print(results)
plt.plot(*results.processed_dataset.T)
plt.plot(*zip(results.young_modulus.first_point, results.young_modulus.second_point), 'r-')
plt.plot(results.yield_point.elongation, results.yield_point.tension, 'ro')
plt.show()
