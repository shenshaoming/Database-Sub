# Database Sub

#### 介绍
通过自定义的分库分表算法将数据拆分

#### 项目依赖
jpype: 用于调用java代码的框架，pip似乎不好直接下载,可以去这个网站下载 https://www.lfd.uci.edu/~gohlke/pythonlibs/#jpype
mysqlclient: mysql数据库操作框架
redis: 操作redis,该项目中使用redis作为断点等操作


#### 更新说明
2020/8/5 初始版本运行使用自己的hash算法，但是只支持一个算法，不能像sharding jdbc一样，分库是一个算法, 分片是另一个算法
