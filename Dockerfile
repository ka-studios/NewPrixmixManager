# super lightweight alpine
FROM alpine:latest
# install stuff (do we really need ttf-dejavu?)
RUN apk update && apk add --no-cache \
    dbus \
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
    firefox
RUN mkdir -p /var/log/supervisor
# boilerplate
RUN mkdir -p /home/prixmix/.vnc
RUN adduser -D -g "" prixmix && \
    echo "prixmix:pxmxpwd" | chpasswd && \
    chown -R prixmix:prixmix /home/prixmix && \
    echo pxmxpwd0 | vncpasswd -f > /home/prixmix/.vnc/passwd && \
    chown -R prixmix:prixmix /home/prixmix && \
    chmod 600 /home/prixmix/.vnc/passwd
# shush its the vnc password
RUN mkdir -p /home/prixmix/.config/openbox
# boilerplate
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
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor.conf"]
