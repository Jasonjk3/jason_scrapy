# 从ubuntu_py38 镜像开始构建
FROM ubuntu_py38
# 维护者
MAINTAINER jasonforjob
# 将爬虫文件复制到/code
ADD . /code/

# 切换工作目录
WORKDIR /code/


COPY scrapyd.conf /etc/scrapyd/

# 暴露端口
EXPOSE 6800

# 安装依赖
RUN pip3 install -r requirements.txt
RUN ["chmod", "777", "run.sh"]
ENTRYPOINT ["./run.sh"]

