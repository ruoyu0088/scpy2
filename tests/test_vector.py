from scpy2.cython.vector import Vector
import numpy as np

def test_vector():
    a = np.random.rand(20)
    b = np.random.rand(20)
    av = Vector(a)
    bv = Vector(b)
    assert list(av) == list(a)
    assert list(av + 5.6) == list(a + 5.6)
    assert list(7.8 + av) == list(a + 7.8)
    assert list(av + bv) == list(a + b)
    av += bv
    assert list(av) == list(a + b)