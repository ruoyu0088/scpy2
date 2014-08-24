from scpy2.cython.multisearch import MultiSearch

text1 = "12334abcdefxyz123423423abc34234"
text2 = "113123d3234234abxy"

ms = MultiSearch(["abc", "xyz"])
print ms.isin(text1)
print ms.isin(text2)

def callback(pattern, pos):
    import traceback
    print pattern, pos
    raise ValueError("error")
    return False

ms.find_positions(text1, callback)
ms.find_positions(text2, callback)