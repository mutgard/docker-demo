FROM php:7.3-fpm
RUN apt-get update;
RUN docker-php-ext-install mysqli
RUN pecl install -f xdebug
COPY xdebug.ini /usr/local/etc/php/conf.d/xdebug.ini
