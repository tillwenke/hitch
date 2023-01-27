import pandas as pd
import numpy as np
import folium
import json
import folium.plugins
import sqlite3
import os
import sys
from branca.element import Element

LIGHT = 'light' in sys.argv

def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km

fn = 'prod-points.sqlite' if os.path.exists('prod-points.sqlite') else 'points.sqlite'
points = pd.read_sql('select * from points where not banned', sqlite3.connect(fn))
print(len(points))

points.loc[points.id.isin(range(1000000,1040000)), 'comment'] = points.loc[points.id.isin(range(1000000,1040000)), 'comment'].str.encode("cp1252",errors='ignore').str.decode('utf-8', errors='ignore')

points.datetime = pd.to_datetime(points.datetime)
points['text'] = points['comment'] + '\n\n―' + points['name'].fillna('Anonymous') + points.datetime.dt.strftime(', %B %Y').fillna('')

rads = points[['lon', 'lat', 'dest_lon', 'dest_lat']].values.T

points['distance'] = haversine_np(*rads)

groups = points.groupby(['lat', 'lon'])

places = groups[['country']].first()
places['rating'] = groups.rating.mean().round()
places['wait'] = points[~points.wait.isnull()].groupby(['lat', 'lon']).wait.mean()
places['distance'] = points[~points.distance.isnull()].groupby(['lat', 'lon']).distance.mean()
places['text'] = groups.text.apply(lambda t: '\n\n'.join(t.dropna()))

if LIGHT:
    places = places[(places.text.str.len() > 0) | ~places.distance.isnull()]

places['country_group'] = places.country.replace(['BE', 'NL', 'LU'], 'BNL')
places.country_group = places.country_group.replace(['CH', 'AT', 'LI'], 'ALP')
places.country_group = places.country_group.replace(['SI', 'HR', 'BA', 'ME', 'MK', 'AL', 'RS', 'TR'], 'BAL')
places.country_group = places.country_group.replace(['SK', 'HU'], 'SKHU')
places.country_group = places.country_group.replace('MC', 'FR')

places.reset_index(inplace=True)
# make sure high-rated are on top
places.sort_values('rating', inplace=True, ascending=False)

m = folium.Map(prefer_canvas=True, control_scale=True)

callback = """\
function (row) {
    var marker;
    var color = {1: 'red', 2: 'orange', 3: 'yellow', 4: 'lightgreen', 5: 'lightgreen'}[row[2]];
    var opacity = {1: 0.3, 2: 0.4, 3: 0.6, 4: 0.8, 5: 0.8}[row[2]];
    var point = new L.LatLng(row[0], row[1])
    marker = L.circleMarker(point, {radius: 5, weight: 1 + 1 * (row[2] == 5), fillOpacity: opacity, color: 'black', fillColor: color});

    marker.on('click', function(e) {
        if ($$('#topbar').innerHTML) return

        points = [point]
        var sidebar = document.querySelector('#sidebar')

        setTimeout(() => {
            sidebar.innerHTML = `<h3>${row[0].toFixed(5)}, ${row[1].toFixed(5)}</h3><div id='spot-summary'></div><h4>Comments</h4><div id='spot-text'></div><div><button>Review this spot</button></div>`
            $$('#spot-summary').innerText = `Rating: ${row[2].toFixed(0)}/5
Waiting time in minutes: ${Number.isNaN(row[4]) ? '-' : row[4].toFixed(0)}
Ride distance in km: ${Number.isNaN(row[5]) ? '-' : row[5].toFixed(0)}`

            $$('#spot-text').innerText = row[3];
            if (!row[3] && Number.isNaN(row[5])) sidebar.innerHTML += '<i>No comments/ride info. To hide points like this, check out the <a href=/light.html>lightweight map</a>.</i>'
        },100)

        L.DomEvent.stopPropagation(e)
    })

    // if(row[2] >= 4) marker.bringToFront()

    return marker;
};
"""

for country, group in places.groupby('country_group'):
    cluster = folium.plugins.FastMarkerCluster(group[['lat', 'lon', 'rating', 'text', 'wait', 'distance']].values, disableClusteringAtZoom=7, spiderfyOnMaxZoom=False, bubblingMouseEvents=False, callback=callback).add_to(m)

folium.plugins.Geocoder(position='topleft', add_marker=False).add_to(m)

html = m.get_root().header

html.add_child(folium.Element("<title>Hitchmap - Find hitchhiking spots on a map - Add new spots</title>"))
html.add_child(folium.Element('<link rel="icon" type="image/x-icon" href="favicon.ico">'))
html.add_child(folium.Element('<link rel="manifest" href="/manifest.json">'))

html.add_child(folium.Element(f"""
<script>
{open('map.js').read()}
</script>
"""))
html.add_child(folium.Element(f"""
<style>
{open('style.css').read()}
</style>
"""))

outname = 'light.html' if LIGHT else 'index.html'

m.save(outname)

with open(outname) as f:
    newText=f.read().replace('</body>', '')

with open(outname, "w") as f:
    f.write(newText + '\n</body>')
