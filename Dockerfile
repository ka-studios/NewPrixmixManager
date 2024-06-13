FROM alpine:latest
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
RUN mkdir -p /home/prixmix/.vnc
RUN adduser -D -g "" prixmix && \
    echo "prixmix:pxmxpwd" | chpasswd && \
    chown -R prixmix:prixmix /home/prixmix && \
    echo pxmxpwd0 | vncpasswd -f > /home/prixmix/.vnc/passwd && \
    chown -R prixmix:prixmix /home/prixmix && \
    chmod 600 /home/prixmix/.vnc/passwd
RUN mkdir -p /home/prixmix/.config/openbox
RUN echo "exec firefox" > /home/prixmix/.config/openbox/autostart
COPY supervisord.conf /etc/supervisor.conf
EXPOSE 5904 6080
COPY self.pem /home/prixmix/self.pem
WORKDIR /home/prixmix
USER root
COPY policies.json /usr/lib/firefox/distribution/policies.json
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor.conf"]
