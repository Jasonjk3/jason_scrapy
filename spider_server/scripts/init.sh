# linux 从机初始化脚本
apt-get update
apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
apt-get update
apt-get install -y docker-ce
echo '{ "insecure-registries":["192.168.1.138:8003"] }' >> /etc/docker/daemon.json
systemctl restart docker
docker swarm join --token SWMTKN-1-1gd69ukava9zpwcw11iynidj182efpfjtngk8dni5f71oenvr2-4x7lza54aspv8t92e0onmv19i 192.168.1.138:2377


# chmod +x init.sh 把这个文件设置为可自行文件，并运行
