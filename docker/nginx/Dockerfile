FROM nginx
ADD server.crt /
ADD server.key /
RUN rm /etc/nginx/conf.d/default.conf
ADD sites-enabled/ /etc/nginx/conf.d