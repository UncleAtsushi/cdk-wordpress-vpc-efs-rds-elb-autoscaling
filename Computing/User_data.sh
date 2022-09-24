#!/bin/bash

MY_REGION="us-east-1"       # Set the AWS Region you deploy
WP_SITENAME="TestBlog"      # Web Site Name for WordPress
WP_USERNAME="wpuser"        # Admin User Name for WordPress
WP_PASSWORD="*************" # Admin Password for WordPress
WP_EMAIL="test@test.com"    # Email Address for WordPress
WP_DBNAME="wordpress"       # Database Name for WordPress in MySQL

# Get EFS ID
EFS_ID=$(aws efs describe-file-systems --region ${MY_REGION} | \
    grep FileSystemId | cut -d':' -f2 | tr -d '\042 ,')

# Get username, password and hostname of MySQL
DB_USERNAME=$(aws secretsmanager get-secret-value --secret-id wp-dev-secret-rds --region ${MY_REGION} | \
    grep SecretString | cut -d'\' -f22 | tr -d '\042')
DB_PASSWORD=$(aws secretsmanager get-secret-value --secret-id wp-dev-secret-rds --region ${MY_REGION} | \
    grep SecretString | cut -d'\' -f4 | tr -d '\042')
DB_HOSTNAME=$(aws secretsmanager get-secret-value --secret-id wp-dev-secret-rds --region ${MY_REGION} | \
    grep SecretString | cut -d'\' -f18 | tr -d '\042')

# Get DNS name of ELB
ELB_DNSNAME=$(aws elbv2 describe-load-balancers --region ${MY_REGION} | \
    grep DNSName | cut -d':' -f2 | tr -d '\042 ,')

# Uninstall mariadb-libs and Install Apache
sudo yum -y remove mariadb-libs \
    && sudo yum -y update \
    && sudo yum -y install httpd \
    && sudo systemctl start httpd \
    && sudo systemctl enable httpd

# install php8.0 and wp-cli
sudo amazon-linux-extras install -y php8.0 \
    && sudo curl -O "https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar" \
    && sudo chmod +x wp-cli.phar \
    && sudo mv wp-cli.phar /usr/local/bin/wp

# Make Document root Directory and mount efs on it
sudo mkdir -p /var/www/html/ \
    && sudo yum install -y amazon-efs-utils \
    && $(echo "mount -t efs -o tls ${EFS_ID}:/ /var/www/html") \
    && sudo yum -y install "https://dev.mysql.com/get/mysql80-community-release-el7-6.noarch.rpm"

# Disable MySQL5.7 and enable MySQL8.0
sudo yum-config-manager --disable mysql80-community \
    && sudo yum-config-manager --enable mysql57-community \
    && sudo rpm --import "https://repo.mysql.com/RPM-GPG-KEY-mysql-2022" \
    && sudo yum -y install mysql-community-client

# Change files permission, download wordpress module and set params of wordpress
sudo chown apache:apache /var/www/html/ \
    && sudo -u apache /usr/local/bin/wp core download --locale=ja --path=/var/www/html \
    && $(echo "sudo -u apache /usr/local/bin/wp core config \
        --dbname=$WP_DBNAME --dbuser=$DB_USERNAME --dbpass=$DB_PASSWORD --dbhost=$DB_HOSTNAME \
        --path=/var/www/html") \
    && sudo -u apache /usr/local/bin/wp db create --path=/var/www/html \
    && $(echo "sudo -u apache /usr/local/bin/wp core install --url=$ELB_DNSNAME --title=$WP_SITENAME \
        --admin_user=$WP_USERNAME --admin_password=$WP_PASSWORD --admin_email=$WP_EMAIL \
        --path=/var/www/html")

# Set auto mount setting to /etc/fstab
sudo echo "${EFS_ID}:/ /var/www/html/ efs defaults,_netdev 0 0" | sudo tee -a /etc/fstab >/dev/null

# Restart Apache
sudo systemctl restart httpd