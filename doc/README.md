
# Scpy2 - Python科学计算第二版实例代码集

`scpy2`为Python科学计算第二版的实例代码集，其中的包含许多演示代码以及一些实用的模块。

## Cython

### 多关键字搜索

`scpy2.cython.multisearch.MultiSearch`演示如何对C语言的库进行包装。这里使用的库为[multifast](http://s
ourceforge.net/projects/multifast/)。它能对文本使用多个关键词进行搜索。


    from scpy2.cython import MultiSearch
    
    ms = MultiSearch(["abc", "xyz"])
    print ms.isin("123abcdef")
    print ms.isin("123uvwxyz")
    print ms.isin("123456789")
    
    for pos, pattern in ms.iter_search("123abcdefxyz123"):
        print pos, pattern

    True
    True
    False
    3 abc
    9 xyz
    
