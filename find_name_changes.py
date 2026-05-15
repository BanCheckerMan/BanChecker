import json
import csv
from pathlib import Path

BASE_DIR = Path(r"C:\Users\bancheckerman\Desktop\ban_checker")

OLD_DATE = "20260514"
NEW_DATE = "20260515"

OLD_DIR = BASE_DIR / OLD_DATE
NEW_DIR = BASE_DIR / NEW_DATE

OUTPUT_DIR = BASE_DIR / "results"
OUTPUT_DIR.mkdir(exist_ok=True)

FILES = [
    ("eu", "2v2"),
    ("eu", "3v3"),
    ("eu", "5v5"),
    ("us", "2v2"),
    ("us", "3v3"),
    ("us", "5v5"),
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_player_map(data):
    return {player["guid"]: player for player in data["data"]}


all_name_changes = []

for region, bracket in FILES:
    old_file = OLD_DIR / f"ironforgepro_{region}_{bracket}_{OLD_DATE}.json"
    new_file = NEW_DIR / f"ironforgepro_{region}_{bracket}_{NEW_DATE}.json"

    print(f"\n=== Checking {region.upper()} {bracket} ===")

    old_data = load_json(old_file)
    new_data = load_json(new_file)

    old_players = build_player_map(old_data)
    new_players = build_player_map(new_data)

    name_changes = []

    shared_guids = set(old_players.keys()) & set(new_players.keys())

    for guid in shared_guids:
        old_player = old_players[guid]
        new_player = new_players[guid]

        old_name = old_player.get("name")
        new_name = new_player.get("name")

        if old_name != new_name:
            row = {
                "region": region.upper(),
                "bracket": bracket,
                "guid": guid,
                "old_name": old_name,
                "new_name": new_name,
                "server": new_player.get("server"),
                "class": new_player.get("class"),
                "spec": new_player.get("spec"),
                "rating_old": old_player.get("rating"),
                "rating_new": new_player.get("rating"),
                "ranking_old": old_player.get("ranking"),
                "ranking_new": new_player.get("ranking"),
            }

            name_changes.append(row)
            all_name_changes.append(row)

    print(f"Found name changes: {len(name_changes)}")

    for p in name_changes[:20]:
        print(
            f'{str(p["old_name"]):20} -> '
            f'{str(p["new_name"]):20} '
            f'Rating {p["rating_old"]} -> {p["rating_new"]}'
        )

    csv_path = OUTPUT_DIR / f"name_changes_{region}_{bracket}.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "region",
                "bracket",
                "guid",
                "old_name",
                "new_name",
                "server",
                "class",
                "spec",
                "rating_old",
                "rating_new",
                "ranking_old",
                "ranking_new",
            ],
        )

        writer.writeheader()
        writer.writerows(name_changes)

    print(f"Saved: {csv_path}")


# Combined CSV
combined_csv = OUTPUT_DIR / "all_name_changes.csv"

# Deduplicate by GUID
unique_changes = {}

for player in all_name_changes:
    guid = player["guid"]

    # Keep the highest NEW rating occurrence
    if guid not in unique_changes:
        unique_changes[guid] = player
    else:
        if (player["rating_new"] or 0) > (unique_changes[guid]["rating_new"] or 0):
            unique_changes[guid] = player

all_name_changes = list(unique_changes.values())

with open(combined_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(
        csvfile,
        fieldnames=[
            "region",
            "bracket",
            "guid",
            "old_name",
            "new_name",
            "server",
            "class",
            "spec",
            "rating_old",
            "rating_new",
            "ranking_old",
            "ranking_new",
        ],
    )

    writer.writeheader()
    writer.writerows(all_name_changes)

print("\n===================================")
print(f"TOTAL name changes: {len(all_name_changes)}")
print(f"Combined CSV saved to: {combined_csv}")
print("Done.")