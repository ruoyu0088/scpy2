# -*- coding: utf-8 -*-
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.image import BboxImage
from matplotlib.transforms import Bbox, TransformedBbox

img = np.random.randint(0, 255, (100, 200, 3))

print img.shape


ax = plt.subplot()

loc = np.array([[0, 0], [200.0, 100.0]])
bbox0 = Bbox(loc)
bbox = TransformedBbox(bbox0, ax.transData)

bbox_image = BboxImage(bbox)
bbox_image.set_data(img)

ax.add_artist(bbox_image)
bbox_image.bbox._bbox.set_points(loc + [10, 5])
bbox_image.bbox.invalidate()
ax.set_xlim(-10, 210)
ax.set_ylim(-10, 110)
ax.axis("off")
plt.show()