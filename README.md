
#### 项目目录
```markdown
├── project
    ├── config                          (配置/常量文件)
    │   ├── config.yaml                 (服务配置)
    │   ├── constant.py                 (项目常量)
    │   └── return_code.py              (状态码配置)
    ├── controller                      (业务层)
    ├── core                            (核心组件)
    │   ├── base.py                     (继承/重写类库)
    │   ├── serve.py                    (服务实例/中间件)
    │   └── wrapper.py                  (业务装饰器)
    ├── docs                            (文档目录)
    ├── libs                            (通用函数封装)
    │   ├── bolts.py                    (通用函数方法)
    │   ├── encrypt.py                  (加解密封装)
    │   └── log.py                      (日志封装)
    ├── model                           (模型层)    
    ├── resource                        (静态资源文件)
    ├── router                          (路由层)
    │   └── noobRoute.py                (服务路由/路由中间件)
    ├── script                          (脚本文件)       
    ├── test                            (单元测试)
    ├── utils                           (第三方工具封装)
    │   ├── dbClient.py                 (数据库客户端)
    │   ├── kafkaClient.py              (kafka客户端)
    │   ├── requestClient.py            (请求客户端)
    │   └── uploadFile.py               (上传文件)
    ├── views                           (视图层)
    │   └── noob.py                     (服务视图)
    noobServe.py                        (服务启动文件)
    README.md                           (项目文档)
    requirements.txt                    (依赖包)
```

#### 启动命令
```shell
sanic noobServe:noob_serve --host="0.0.0.0" --port=8003 --workers=1```
