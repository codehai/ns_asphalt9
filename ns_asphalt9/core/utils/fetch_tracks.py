import json
import requests
import csv
from collections import OrderedDict

cars = []
r = requests.get(
    "https://www.infoasphalt.com/wp-admin/admin-ajax.php?action=wp_ajax_ninja_tables_public_action&table_id=14635&target_action=get-all-data&default_sorting=old_first&skip_rows=0&limit_rows=0&ninja_table_public_nonce=df6ce4c3f6"
)
data = json.loads(r.text)

tracks_dict = OrderedDict()

# 要保存的数据
rows = [
    ["key", "chapter", "season", "race", "modeen", "locationen", "tracken", "time"],
]


track_options = [
    ["key", "progress", "option", "type"],
]


for d in data:
    key = f'{d["locationen"].replace(" ", "_")}_{d["tracken"].replace(" ", "_")}_{d["time"]}'
    if key not in tracks_dict:
        tracks_dict.update({key: d})
        rows.append(
            [
                key,
                d["chapter"],
                d["season"],
                d["race"],
                d["modeen"],
                d["locationen"],
                d["tracken"],
                d["time"],
            ]
        )
        track_options.append([key, 0, "", 0])

# 使用 CSV 模块保存数据到 CSV 文件
with open("data.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(rows)


with open("track_options.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(track_options)
