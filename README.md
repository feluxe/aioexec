
# aioexec

## Description

Aioexec is a simple and intuitive interface around the `concurrent.futures` package and asyncio's `loop.run_in_executor` method.


## Overview

With asyncio you usually run an executor something like this:

```python
import aysncio
from concurrent.futures import ProcessPoolExecutor

# ...

loop = asyncio.get_event_loop()

foo = await loop.run_in_executor(
    ProcessPoolExecutor(5), lambda: my_func(foo='baz')
    )
```

With aioexec you would do the same like this:

```python
import aysncio
from aioexec import Procs

# ...

foo = await Procs(5).call(my_func, foo='baz') 
```

You can also call a batch of functions in an executor like this:

```python
import asyncio as aio
from aioexec import Procs, Call

my_values = await aio.gather(
    *Procs(5).batch(
        Call(my_func, foo='1'),
        Call(my_func, foo='2'),
        Call(my_func, foo='3'),
    )
```

This plays nicely with list comprehensions:

```python
my_values = await aio.gather(
    *Procs(10).batch(
        Call(my_func, foo=i) for i in range(0, 10)
    )
```

The same stuff works for Threads as well:

```python
import asyncio as aio
from aioexec import Threads

foo = await Threads(1).call(my_func, foo='baz') 

```

If necessary, you can pass an event loop to the executors like this:

```python
foo = await Threads(5, my_loop).call(my_func, foo='baz') 
foo = await Procs(5, my_loop).call(my_func, foo='baz') 
```




