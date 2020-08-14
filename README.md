# Database Sub

#### 介绍
通过自定义的分库分表算法将数据拆分,该项目目前可能存在不稳定的情况，需要大家多多测试，欢迎提出issue.
在公司中，经常会出现由于一开始没有估计好数据库的量，导致后续当数据达到一定量级时，为了能够优化数据库查询效率，进行水平分表或垂直分表
本项目旨在简化水平层次上的分库分表

#### 项目依赖
jpype: 用于调用java代码的框架，pip似乎不好直接下载,可以去这个网站下载 https://www.lfd.uci.edu/~gohlke/pythonlibs/#jpype
mysqlclient: mysql数据库操作框架

#### 使用说明
git clone 项目, 或者直接fork走大发慈悲的改改卑微作者的垃圾代码,提个pull request. 
1. 首先你需要一个python环境, 本人的python环境是python 3.7
2. 安装项目的依赖包， 分别是jpype和mysqlclient, 因为mysqlclient不一定能够通过pip安装， 所以在file文件夹中提供了一个win32版本的安装包
import_packets.bat是专为window用户提供的快速安装两个以来的批处理文件，可以当作没有
3. 修改file/sharding.yml, 和shardingJdbc的配置极为相似，如果不明白可以查看sharding_description.yml中的相关解释
4. 运行main.py

#### 补充说明
为了能够适用各个公司的分库分表算法, 而用到分库分表的人一般都是做Java的朋友，所以我做的例子就是通过jar包调用分库分表算法的.
目前仅支持单分表,且不像sharding jdbc一样，分库是一个算法, 分片是另一个算法。打成
如果你是一个做java的朋友,可以像我一样，将分表算法打成jar包, 放到项目中, 然后修改main.py中的相关代码就可以。
具体的是 main.py中的
```
jpype.startJVM(jpype.getDefaultJVMPath(), "-ea", "-Djava.class.path=hash/snow.jar", convertStrings=False)
```
紧接着在修改 main.py 中的 get_sharding_index方法, 然后就ok了
需要注意的是，目前版本在转移数据之后会将表中原有的数据删除
