# Hitchmap
The Map to Hitchhiking the World.


## Description
 
- `show.py` builds the main HTML page. This is where the magic happens.
- `server.py` runs the server
- `dump.py` runs the monthly dump
- `cron.sh` is the crontab running above files
- `hitchmap.conf` is the NGINX configuration

## Installation

```bash
pip install numpy pandas folium
curl https://hitchmap.com/dump.sqlite > points.sqlite

OR

conda install folium
curl https://hitchmap.com/dump.sqlite > points.sqlite
```

# Contributing
Join the conversation about a map for hitchhiking in our [Signal Chat](https://signal.group/#CjQKIDyYgIxcOUCEPYu8-JawC_tv1bcgkAhvbISRZkN45MMVEhBPKVnUzWhl5khm5ybTWi9G).

File an Issue if you think something should be changed.

Just do a Pull Request if you solved an Issue.

