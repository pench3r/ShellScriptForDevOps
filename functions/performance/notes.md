## 关于进程和线程

一般地，任务（作业）分为CPU密集型和IO密集型，什么样的类型决定了应该选择使用什么样的库和方法。

1. CPU密集型(也叫作计算型) --> 需要并行 --> 用多进程 --> 高消耗CPU --> from multiprocessing import Pool

2. IO密集型 --> 需要并发 --> 用多线程 --> 低消耗CPU --> from multiprocessing.pool import ThreadPool

多进程是并发，多线程是并行，如果要尽快完成大批量任务，可以使用多进程多线程（开启多个进程，每个进程开启多个线程）

Tips: 在Python3中可以利用[concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html)
实现并行计算，使用ProcessPoolExecutor实现多进程（充分地利用每一个CPU核心，但进程数不建议超过CPU核心数量），处理计算密集型任务，
使用ThreadPoolExecutor实现多线程（线程数可以超过CPU核心数量），处理IO密集型任务。

Tips：如何判断CPU密集型还是IO密集型，所有操作是通过CPU和内存内的数据完成的，则这一般是CPU密集型（如计算哈希），
反之，产生IO的操作一般是IO密集型（如下载文件）

## 其他相关知识收集
[出处来源](https://www.cnblogs.com/derek1184405959/p/8449923.html)
```text
1.一个cpu一次只能执行一个任务，多个cpu同时可以执行多个任务
2.一个cpu一次只能执行一个进程，其它进程处于非运行状态
3.进程里包含的执行单元叫线程，一个进程可以包含多个线程
4.一个进程的内存空间是共享的，每个进程里的线程都可以使用这个共享空间
5.一个线程在使用这个共享空间的时候，其它的线程必须等待（阻塞状态）
6.互斥锁作用就是防止多个线程同时使用这块内存空间，先使用的线程会将空间上锁，其它的线程处于等待状态。等锁开了才能进
7.进程：表示程序的一次执行
8.线程：CPU运算的基本调度单位
9.GIL（全局锁）：python里的执行通行证，而且只有一个。拿到通行证的线程就可以进入CPU执行任务。没有GIL的线程就不能执行任务
10.python的多线程适用于大量密集的I/O处理
11.python的多进程适用于大量的密集并行计算
```

## 关于线程池的大小(ideal thread pool size)

https://engineering.zalando.com/posts/2019/04/how-to-set-an-ideal-thread-pool-size.html

```text
Number of threads = Number of Available Cores * (1 + Wait time / Service time)
```

**Waiting time** - is the time spent waiting for IO bound tasks to complete, say waiting for HTTP response from remote service.

**Service time** - is the time spent being busy, say processing the HTTP response, marshaling/unmarshaling, any other transformations etc.
 
 