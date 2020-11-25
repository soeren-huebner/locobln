FROM nginx/unit:1.20.0-python3.7
COPY requirements.txt /config/requirements.txt
RUN apt update && apt install -y python3-pip                               \
    && pip3 install -r /config/requirements.txt                            \
    && apt remove -y python3-pip                                           \
    && apt autoremove --purge -y                                           \
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*.list
