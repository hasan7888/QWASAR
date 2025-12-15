from collections import defaultdict
import re

def parse_txt(path_file):
    plays = []
    with open(path_file, "r", encoding="utf-8") as file:
        for line in file:
            data = line.strip().split("|")
            play = {
                "period": data[0],
                "remaining": data[1],
                "relevant_team": data[2],
                "away_team": data[3],
                "home_team": data[4],
                "away_score": data[5],
                "home_score": data[6],
                "description": data[7]
            }
            plays.append(play)
    return plays

def players_stats(plays):
    l=[]
    stats = defaultdict(lambda: {
        "player_name": "",
        "FG": 0, "FGA": 0, "FG%": 0,
        "3P": 0, "3PA": 0, "3P%": 0,
        "FT": 0, "FTA": 0, "FT%": 0,
        "ORB": 0, "DRB": 0, "TRB": 0,
        "AST": 0, "STL": 0, "BLK": 0,
        "TOV": 0, "PF": 0, "PTS": 0
    })
    result = defaultdict(lambda: {"name": ""})

    for play in plays:
        descr = play["description"]
        pattern = r"(\S\.\s\S+?)(?=\s|$)"
        if "Turnover by" in descr:
            player_match = re.search(f'Turnover by {pattern}', descr)
            if player_match:
                player = player_match.group(1)
                stats[player]["player_name"] = player
                stats[player]["TOV"] += 1
                if player not in result:
                    result[player]["name"] = play["relevant_team"]

        
        if "steal by" in descr:
            player_match = re.search(f'steal by {pattern}', descr)
            if player_match:
                player = player_match.group(1)
                stats[player]["player_name"] = player
                stats[player]["STL"] += 1
                if player not in result:
                    if play["relevant_team"] == "OKLAHOMA_CITY_THUNDER":
                        result[player]["name"] = "GOLDEN_STATE_WARRIORS"
                    elif play["relevant_team"] == "GOLDEN_STATE_WARRIORS":
                        result[player]["name"] = "OKLAHOMA_CITY_THUNDER"

        if "makes 2-pt" in descr:
            player_match = re.search(r'([A-Z]\.\s[A-Za-z]+?)\smakes 2-pt', descr)
            if player_match:
                player = player_match.group(1)
                stats[player]["player_name"] = player
                stats[player]["FG"] += 1
                stats[player]["FGA"] += 1
                stats[player]["PTS"] += 2
                if player not in result:
                    result[player]["name"] = play["relevant_team"]

        if "misses 2-pt" in descr:
            player_match = re.search(r'([A-Z]\.\s[A-Za-z]+?)\smisses 2-pt', descr)
            if player_match:
                player = player_match.group(1)
                stats[player]["player_name"] = player
                stats[player]["FGA"] += 1
                if player not in result:
                    result[player]["name"] = play["relevant_team"]

        if "makes 3-pt" in descr:
            player_match = re.search(r'(\S\.\s\S+?)\smakes 3-pt', descr)
            if player_match:
                player = player_match.group(1)
                stats[player]["player_name"] = player
                stats[player]["FG"] += 1
                stats[player]["FGA"] += 1
                stats[player]["3P"] += 1
                stats[player]["3PA"] += 1
                stats[player]["PTS"] += 3
                if player not in result:
                    result[player]["name"] = play["relevant_team"]

        if "misses 3-pt" in descr:
            player_match = re.search(r'([A-Z]\.\s[A-Za-z]+?)\smisses 3-pt', descr)
            if player_match:
                player = player_match.group(1)
                stats[player]["player_name"] = player
                stats[player]["FGA"] += 1
                stats[player]["3PA"] += 1
                if player not in result:
                    result[player]["name"] = play["relevant_team"]


        if "makes free throw" in descr:
                player_match = re.findall(f"{pattern} makes free throw", descr)
                if player_match:
                    player = player_match[0]
                    stats[player]["player_name"] = player
                    stats[player]["FT"] += 1
                    stats[player]["FTA"] += 1  
                    stats[player]["PTS"] += 1
                    if player not in result:
                        result[player]["name"] = play["relevant_team"]

        if "misses free throw" in descr:
            player_match = re.findall(f"{pattern} misses free throw", descr)
            if player_match:
                player = player_match[0]
                stats[player]["player_name"] = player
                stats[player]["FTA"] += 1
                if player not in result:
                    result[player]["name"] = play["relevant_team"]

        if "Offensive rebound by" in descr:
            player_match = re.search(r'Offensive rebound by ([A-Z]\.\s[A-Za-z]+?)', descr)
            if player_match:
                player = player_match.group(1)
                stats[player]["player_name"] = player
                stats[player]["ORB"] += 1
                stats[player]["TRB"] += 1
                if player not in result:
                    result[player]["name"] = play["relevant_team"]
        if "Offensive foul by" in descr:
            player_match = re.search(r'Offensive foul by ([A-Z]\.\s[A-Za-z]+?)', descr)
            if player_match:
                player = player_match.group(1)
                stats[player]["player_name"] = player
                stats[player]["PF"] += 1
                if player not in result:
                    result[player]["name"] = play["relevant_team"]
                

        if "Clear path foul by" in descr:
            player_match = re.search(r'Clear path foul by ([A-Z]\.\s[A-Za-z]+?)', descr)
            if player_match:
                player = player_match.group(1)
                stats[player]["player_name"] = player
                stats[player]["PF"] += 1
                if player not in result:
                    if play["relevant_team"] == "OKLAHOMA_CITY_THUNDER":
                        result[player]["name"] = "GOLDEN_STATE_WARRIORS"
                    elif play["relevant_team"] == "GOLDEN_STATE_WARRIORS":
                        result[player]["name"] = "OKLAHOMA_CITY_THUNDER"

        if "Defensive rebound by" in descr:
            player_match = re.search(r'Defensive rebound by ([A-Z]\.\s[A-Za-z]+?)', descr)
            if player_match:
                player = player_match.group(1)
                stats[player]["player_name"] = player
                stats[player]["DRB"] += 1
                stats[player]["TRB"] += 1
                if player not in result:
                    result[player]["name"] = play["relevant_team"]         

        if "assist by" in descr:
            player_match = re.search(r'assist by ([A-Z]\.\s[A-Za-z]+?)', descr)
            if player_match:
                player = player_match.group(1)
                stats[player]["player_name"] = player
                stats[player]["AST"] += 1
                if player not in result:
                    result[player]["name"] = play["relevant_team"]
        

        if "block by" in descr:
            player_match = re.search(r'block by ([A-Z]\.\s[A-Za-z]+?)', descr)
            if player_match:
                player = player_match.group(1)
                stats[player]["player_name"] = player
                stats[player]["BLK"] += 1
                if player not in result:
                    if play["relevant_team"] == "OKLAHOMA_CITY_THUNDER":
                        result[player]["name"] = "GOLDEN_STATE_WARRIORS"
                    elif play["relevant_team"] == "GOLDEN_STATE_WARRIORS":
                        result[player]["name"] = "OKLAHOMA_CITY_THUNDER"

        if "Shooting foul by" in descr:
            player_match = re.search(r'Shooting foul by ([A-Z]\.\s[A-Za-z]+)', descr)
            if player_match:
                player = player_match.group(1)
                stats[player]["player_name"] = player
                stats[player]["PF"] += 1
                if player not in result:
                    if play["relevant_team"] == "OKLAHOMA_CITY_THUNDER":
                        result[player]["name"] = "GOLDEN_STATE_WARRIORS"
                    elif play["relevant_team"] == "GOLDEN_STATE_WARRIORS":
                        result[player]["name"] = "OKLAHOMA_CITY_THUNDER" 

        if "Personal foul by" in descr:
            player_match = re.search(r'Personal foul by ([A-Z]\.\s[A-Za-z]+)', descr)
            if player_match:
                player = player_match.group(1)
                stats[player]["player_name"] = player
                stats[player]["PF"] += 1
                if player not in result:
                    if play["relevant_team"] == "OKLAHOMA_CITY_THUNDER":
                            result[player]["name"] = "GOLDEN_STATE_WARRIORS"
                    elif play["relevant_team"] == "GOLDEN_STATE_WARRIORS":
                            result[player]["name"] = "OKLAHOMA_CITY_THUNDER"
        if "Loose ball foul by" in descr:
             player_match = re.search(r'Loose ball foul by ([A-Z]\.\s[A-Za-z]+)', descr)
             if player_match:
                player = player_match.group(1)
                stats[player]["player_name"] = player
                stats[player]["PF"] += 1
                if player not in result:
                    result[player]["name"] = play["relevant_team"]


    for player in stats:
        if stats[player]["FGA"] != 0:
            stats[player]["FG%"] = round(stats[player]["FG"] / stats[player]["FGA"] * 100, 1)
        if stats[player]["3PA"] != 0:
            stats[player]["3P%"] = round(stats[player]["3P"] / stats[player]["3PA"] * 100, 1)
        if stats[player]["FTA"] != 0:  
            stats[player]["FT%"] = round(stats[player]["FT"] / stats[player]["FTA"] * 100, 1)
    
    del result["D. Schr"]
    l.append(result)
    l.append(stats)
    return l


def home_away_team(result, stats):
    dictionary = {
        "home_team": {"name": "", "players_data": []},
        "away_team": {"name": "", "players_data": []}
    }

    for player, team in result.items():
        team_name = team ["name"]
        player_stats = stats[player]  

        if team_name == "GOLDEN_STATE_WARRIORS":
            dictionary["home_team"]["name"] = team_name
            dictionary["home_team"]["players_data"].append(player_stats)
        else:
            dictionary["away_team"]["name"] = team_name
            dictionary["away_team"]["players_data"].append(player_stats)

    return dictionary

def print_nba_game_stats(team_dict):
    headers = ["Players","FG","FGA","FG%","3P","3PA","3P%","FT","FTA","FT%","ORB","DRB","TRB","AST","STL","BLK","TOV","PF","PTS"]
    print("\t".join(headers))
    totals = defaultdict(int)

    for p in team_dict["players_data"]:
        row = [p["player_name"]] + [str(p[h]) if not isinstance(p[h], float) else f"{p[h]:.3f}" if p[h]!=0 else "" for h in headers[1:]]
        print("\t".join(row))
        for h in ["FG","FGA","3P","3PA","FT","FTA","ORB","DRB","TRB","AST","STL","BLK","TOV","PF","PTS"]:
            totals[h] += p[h]

    # Totals line
    totals["FG%"] = f"{totals['FG']/totals['FGA']:.3f}" if totals["FGA"] else ""
    totals["3P%"] = f"{totals['3P']/totals['3PA']:.3f}" if totals["3PA"] else ""
    totals["FT%"] = f"{totals['FT']/totals['FTA']:.3f}" if totals["FTA"] else ""

    total_row = ["Team Totals"] + [str(totals.get(h,"")) for h in headers[1:]]
    print("\t".join(total_row))







path_file = r"C:\Users\web4j\Documents\g.txt"
plays = parse_txt(path_file)
result,stats=players_stats(plays)[0],players_stats(plays)[1]
team_dict=home_away_team(result,stats)
team_dict=team_dict['home_team']
print( print_nba_game_stats(team_dict))