FROM nginx/unit:1.20.0-python3.7
COPY requirements.txt /config/requirements.txt
RUN apt update && apt install -y python3-pip sqlite3 libsqlite3-dev        \
    && pip3 install -r /config/requirements.txt                            \
    && /usr/bin/sqlite3 /db/user.db					   \
    && apt remove -y python3-pip                                           \
    && apt autoremove --purge -y                                           \
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*.list
