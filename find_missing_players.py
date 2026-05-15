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
    """
    Returns:
        dict[guid] = player_data
    """
    return {player["guid"]: player for player in data["data"]}


all_missing = []

for region, bracket in FILES:
    old_file = OLD_DIR / f"ironforgepro_{region}_{bracket}_{OLD_DATE}.json"
    new_file = NEW_DIR / f"ironforgepro_{region}_{bracket}_{NEW_DATE}.json"

    print(f"\n=== Checking {region.upper()} {bracket} ===")

    old_data = load_json(old_file)
    new_data = load_json(new_file)

    old_players = build_player_map(old_data)
    new_players = build_player_map(new_data)

    missing_guids = set(old_players.keys()) - set(new_players.keys())

    missing_players = []

    for guid in missing_guids:
        p = old_players[guid]

        row = {
            "region": region.upper(),
            "bracket": bracket,
            "guid": p.get("guid"),
            "name": p.get("name"),
            "server": p.get("server"),
            "faction": p.get("faction"),
            "class": p.get("class"),
            "spec": p.get("spec"),
            "race": p.get("race"),
            "rating": p.get("rating"),
            "ranking": p.get("ranking"),
            "wins": p.get("stats", {}).get("w"),
            "losses": p.get("stats", {}).get("l"),
            "winrate": p.get("stats", {}).get("wr"),
        }

        missing_players.append(row)
        all_missing.append(row)

    missing_players.sort(key=lambda x: x["rating"], reverse=True)

    print(f"Missing players: {len(missing_players)}")

    for p in missing_players:
        name = str(p.get("name") or "Unknown")
        cls = str(p.get("class") or "Unknown")
        spec = str(p.get("spec") or "Unknown")
        rating = p.get("rating") or 0
        ranking = p.get("ranking") or 0

        print(
            f'{name:20} '
            f'{cls:10} '
            f'{spec:10} '
            f'Rating={rating} '
            f'Rank={ranking}'
        )

    # Write per-bracket CSV
    csv_path = OUTPUT_DIR / f"missing_{region}_{bracket}.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "region",
                "bracket",
                "guid",
                "name",
                "server",
                "faction",
                "class",
                "spec",
                "race",
                "rating",
                "ranking",
                "wins",
                "losses",
                "winrate",
            ],
        )

        writer.writeheader()
        writer.writerows(missing_players)

    print(f"Saved: {csv_path}")


# Combined CSV
combined_csv = OUTPUT_DIR / "all_missing_players.csv"

all_missing.sort(key=lambda x: x["rating"], reverse=True)

# Deduplicate by character name
unique_missing = {}

for player in all_missing:
    name = (player.get("name") or "").lower()

    if not name:
        continue

    # Keep highest-rated occurrence
    if name not in unique_missing:
        unique_missing[name] = player
    else:
        if player["rating"] > unique_missing[name]["rating"]:
            unique_missing[name] = player

all_missing = list(unique_missing.values())

with open(combined_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(
        csvfile,
        fieldnames=[
            "region",
            "bracket",
            "guid",
            "name",
            "server",
            "faction",
            "class",
            "spec",
            "race",
            "rating",
            "ranking",
            "wins",
            "losses",
            "winrate",
        ],
    )

    writer.writeheader()
    writer.writerows(all_missing)

print("\n===================================")
print(f"TOTAL missing players: {len(all_missing)}")
print(f"Combined CSV saved to: {combined_csv}")
print("Done.")