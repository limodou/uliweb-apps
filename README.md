# Uliweb-APPS

用于收集各种可复用的功能. 它基于 Uliweb-Layout, Uliweb-UI. 并且自带一个demo.

# Demo 启动

要运行 Demo 需要先将源码下载到本地,用使用git clone. 

缺省会使用 sqlite 数据库,如果想更换数据库,可以在demo/apps下创建 local_settings.ini按照ORM
数据库的连接要求,添加 `ORM/CONNECTION` 连接信息.

然后执行:

```
pip install -r requirements.txt
uliweb syncdb -v
uliweb dbinit uliweb.rbac
```

初始化之后,就可以在本地启动开发服务器了:

```
uliweb runserver --thread
```