FROM php:7.2-apache

#install required libraries and tools
RUN set -eu && apt-get update
RUN apt-get -y install unzip libpng-dev libjpeg-dev libmcrypt-dev \
    && rm -rf /var/lib/apt/lists/* \
    && docker-php-ext-configure gd --with-png-dir=/usr --with-jpeg-dir=/usr \
    && docker-php-ext-install gd mbstring mysqli zip \
    && pecl install mcrypt-1.0.1 \
    && docker-php-ext-enable mcrypt

WORKDIR /var/www/html

#set environment variables
ENV OPENCART_FILE opencart.zip
ENV OPENCART_URL https://github.com/opencart/opencart/releases/download/3.0.3.3/opencart-3.0.3.3.zip

#install opencart
RUN curl -sSL ${OPENCART_URL} -o ${OPENCART_FILE} \
    && unzip ${OPENCART_FILE} 'upload/*' \
    && mv /var/www/html/upload/* /var/www/html/ \
    && rm -r /var/www/html/upload/ \
    && mv config-dist.php config.php \
    && mv admin/config-dist.php admin/config.php \
    && rm ${OPENCART_FILE} \
    && chown -R www-data:www-data /var/www

#copy paystack opencart plugin
COPY . /var/www/html/
