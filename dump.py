import pandas as pd
import sqlite3
import os

fn = 'prod-points.sqlite'
if not os.path.exists(fn):
    exit()
all_points = pd.read_sql('select * from points where not banned', sqlite3.connect(fn))
all_points['ip'] = ''

all_points.to_sql('points', sqlite3.connect('dump.sqlite'), index=False, if_exists='replace')
