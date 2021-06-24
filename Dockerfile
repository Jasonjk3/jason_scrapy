# 从ubuntu_py38 镜像开始构建
FROM ubuntu_py38
# 维护者
MAINTAINER jasonforjob
# 将爬虫文件复制到/code
ADD . /code/

# 切换工作目录
WORKDIR /code/spider_server

# 安装依赖
RUN pip3 install -r requirements.txt


# 启动容器时使用命令 python main.py 开始爬虫
#CMD ["python", "main.py"]
