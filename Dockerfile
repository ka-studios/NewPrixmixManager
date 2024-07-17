# super lightweight alpine
FROM alpine:latest
# install stuff (do we really need ttf-dejavu?)
RUN apk update && apk add --no-cache \
    dbus \
    apache2 \
    ttf-dejavu \
    bash \
    supervisor \
    tigervnc \
    xvfb \
    openbox \
    xauth \
    xrandr \
    wget \
    git \
    novnc \
    py3-xdg \
    curl \
    openssl \
    firefox
RUN mkdir -p /var/log/supervisor
# boilerplate
RUN mkdir -p /home/prixmix/.vnc
RUN adduser -D -g "" prixmix && \
    echo "prixmix:pxmxpwd0" | chpasswd && \
    chown -R prixmix:prixmix /home/prixmix && \
    echo pxmxpwd0 | vncpasswd -f > /home/prixmix/.vnc/passwd && \
    chown -R prixmix:prixmix /home/prixmix && \
    chmod 600 /home/prixmix/.vnc/passwd
# shush its the vnc password
RUN mkdir -p /home/prixmix/.config/openbox
# boilerplate
#RUN echo "geometry=1920x1080" > /home/prixmix/.vnc/config
RUN echo "exec firefox \$URL" > /home/prixmix/.config/openbox/autostart
# autostart firefox
COPY supervisord.conf /etc/supervisor.conf
EXPOSE 5904 6080
COPY self.pem /home/prixmix/self.pem
# ssl for novnc
WORKDIR /home/prixmix
USER root
# copy policies file
COPY policies.json /usr/lib/firefox/distribution/policies.json
# preload hosts file
COPY hosts /etc/hosts
#RUN rm -f /var/www/html/index.html
#COPY blocked.html /var/www/html/index.html
#COPY snakeoil.pem /etc/ssl/certs/ssl-cert-snakeoil.pem
#COPY snakeoil.key /etc/ssl/private/ssl-cert-snakeoil.key
#RUN a2enmod ssl
#RUN cp /etc/apache2/sites-available/default-ssl.conf /etc/apache2/sites-available/000-default.conf
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor.conf"]
