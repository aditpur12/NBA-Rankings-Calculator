import pandas as pd
import numpy as np
import csv

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 100)
pd.set_option("display.width", None)

weights = {
  "points": 0.35,
    "assists": 0.25,
    "rebounds": 0.25,
    "steals": 0.125,
    "blocks": 0.125,
    "turnovers": -0.10  
}

print("\nCustomize your stat weights (press Enter to keep default):")
for stat, default in weights.items():
    try:
        user = input(f"Weight for {stat} (default = {default}): ")
        weights[stat] = float(user)
    except ValueError:
        print(f"Invalid input for {stat}, keeping default {default}")

try:
    df = pd.read_csv("Player per Game.csv", low_memory=False)
    awards = pd.read_csv("Player Award Shares.csv", low_memory=False)
    allStar = pd.read_csv("All-Star Selections.csv", low_memory=False)
    print("Data loaded successfully!")
except Exception as e:
    print(f"Error loading data: {e}")
    quit()

#STATS
# Normalize statistics using z-scores to account for the change in the game's pacing
stats_to_normalize = [
    'pts_per_game', 'ast_per_game', 'trb_per_game', 'blk_per_game', 'stl_per_game', 'tov_per_game'
]

for stat in stats_to_normalize:
    if stat in df.columns and df[stat].std() != 0:
        df[f'z_{stat}'] = (df[stat] - df[stat].mean()) / df[stat].std()
    else:
        df[f'z_{stat}'] = 0


df['player_score'] = (
    weight["points"] * df.get('z_pts_per_game', 0) +
    weight["assists"] * df.get('z_ast_per_game', 0) +
    weight["rebounds"] * df.get('z_trb_per_game', 0) +
    weight["steal"] * df.get('z_stl_per_game', 0) +
    weight["block"] * df.get('z_blk_per_game', 0) +
    weight["turnover"] * df.get('z_tov_per_game', 0)
)

#Awards
award_weights = {
    "nba mvp": 0.5,
    "nba dpoy": 0.25,
    "nba roy": 0.1,
    "nba smoy": 0.05
}

for _, row in awards.iterrows():
    weight = award_weights.get(row['award'].lower(), 0)
    if weight > 0:
        mask = (df['player_id'] == row['player_id']) & (df['season'] == row['season'])
        df.loc[mask, 'player_score'] += weight * row['share']


#All Star

for _, row in allStar.iterrows():
    mask = (df['player_id'] == row['player_id']) & (df['season'] == row['season'])
    df.loc[mask, 'player_score'] += 0.2
        

# Sort by player score to get rankings
season_rank = df.sort_values('player_score', ascending=False)

# Display top 25 players
print("\n=== NBA All-Time Season Rankings ===")
print("Ranking considers: Points (35%), Assists (25%), Rebounds (25%), Steals (12.5%), Blocks (12.5%), Turnovers (-10%)")
print("=" * 120)

display_columns = ['player','season', 'pos', 'g', 'pts_per_game', 'ast_per_game', 'trb_per_game', 'stl_per_game', 'blk_per_game', 'tov_per_game', 'player_score']
available_columns = [col for col in display_columns if col in df.columns]

top_50 = season_rank[available_columns].head(50)
top_50['rank'] = range(1, len(top_50) + 1)


# Format the display
pd.set_option(
    'display.float_format',
    lambda x: f"{x:,.2f}" if pd.notnull(x) and x % 1 else f"{int(x):,}" if pd.notnull(x) else "0"
)

print(top_50.to_string(index=False, columns=['rank'] + available_columns))

print("\n=== Ranking Complete ===")


'''
Output using default values:
=== NBA All-Time Season Rankings ===
Ranking considers: Points (35%), Assists (25%), Rebounds (25%), Steals (12.5%), Blocks (12.5%), Turnovers (-10%)
========================================================================================================================
 rank                player  season pos  g  pts_per_game  ast_per_game  trb_per_game  stl_per_game  blk_per_game  tov_per_game  player_score
    1       Hakeem Olajuwon    1993   C 82         26.10          3.50            13          1.80          4.20          3.20          3.89
    2        Michael Jordan    1988  SG 82            35          5.90          5.50          3.20          1.60          3.10          3.78
    3        David Robinson    1994   C 80         29.80          4.80         10.70          1.70          3.30          3.20          3.68
    4       Hakeem Olajuwon    1994   C 80         27.30          3.60         11.90          1.60          3.70          3.40          3.60
    5        Michael Jordan    1989  SG 81         32.50             8             8          2.90          0.80          3.60          3.60
    6          Nikola Jokić    2024   C 79         26.40             9         12.40          1.40          0.90             3          3.59
    7      Shaquille O'Neal    2000   C 79         29.70          3.80         13.60          0.50             3          2.80          3.57
    8        David Robinson    1992   C 68         23.20          2.70         12.20          2.30          4.50          2.70          3.56
    9     Russell Westbrook    2017  PG 81         31.60         10.40         10.70          1.60          0.40          5.40          3.55
   10 Giannis Antetokounmpo    2020  PF 63         29.50          5.60         13.60             1             1          3.70          3.54
   11          Nikola Jokić    2022   C 74         27.10          7.90         13.80          1.50          0.90          3.80          3.50
   12         Kevin Garnett    2004  PF 82         24.20             5         13.90          1.50          2.20          2.60          3.49
   13 Giannis Antetokounmpo    2019  PF 72         27.70          5.90         12.50          1.30          1.50          3.70          3.47
   14       Hakeem Olajuwon    1990   C 82         24.30          2.90            14          2.10          4.60          3.90          3.47
   15           Luka Dončić    2024  PG 70         33.90          9.80          9.20          1.40          0.50             4          3.45
   16          LeBron James    2010  SF 76         29.70          8.60          7.30          1.60             1          3.40          3.36
   17            Larry Bird    1985  SF 80         28.70          6.60         10.50          1.60          1.20          3.10          3.35
   18        David Robinson    1995   C 81         27.60          2.90         10.80          1.70          3.20          2.90          3.33
   19          Nikola Jokić    2025   C 70         29.60         10.20         12.70          1.80          0.60          3.30          3.29
   20        Michael Jordan    1990  SG 82         33.60          6.30          6.90          2.80          0.70             3          3.29
   21        David Robinson    1991   C 82         25.60          2.50            13          1.50          3.90          3.30          3.28
   22        Michael Jordan    1987  SG 82         37.10          4.60          5.20          2.90          1.50          3.30          3.28
   23          Nikola Jokić    2021   C 72         26.40          8.30         10.80          1.30          0.70          3.10          3.27
   24          Nikola Jokić    2023   C 69         24.50          9.80         11.80          1.30          0.70          3.60          3.26
   25          LeBron James    2009  SF 81         28.40          7.20          7.60          1.70          1.10             3          3.26
   26         Magic Johnson    1989  PG 77         22.50         12.80          7.90          1.80          0.30          4.10          3.25
   27        Michael Jordan    1991  SG 82         31.50          5.50             6          2.70             1          2.50          3.25
   28         Magic Johnson    1987  PG 80         23.90         12.20          6.30          1.70          0.50          3.80          3.24
   29         Kevin Garnett    2003  PF 82            23             6         13.40          1.40          1.60          2.80          3.23
   30       Hakeem Olajuwon    1989   C 82         24.80          1.80         13.50          2.60          3.40          3.40          3.22
   31          James Harden    2019  PG 78         36.10          7.50          6.60             2          0.70             5          3.21
   32          James Harden    2017  PG 81         29.10         11.20          8.10          1.50          0.50          5.70          3.18
   33          LeBron James    2013  PF 76         26.80          7.30             8          1.70          0.90             3          3.18
   34        Michael Jordan    1993  SG 78         32.60          5.50          6.70          2.80          0.80          2.70          3.18
   35        Michael Jordan    1992  SG 80         30.10          6.10          6.40          2.30          0.90          2.50          3.17
   36   Kareem Abdul-Jabbar    1979   C 80         23.80          5.40         12.80             1             4          3.50          3.16
   37 Giannis Antetokounmpo    2022  PF 67         29.90          5.80         11.60          1.10          1.40          3.30          3.15
   38        David Robinson    1996   C 82            25             3         12.20          1.40          3.30          2.30          3.15
   39           Joel Embiid    2023   C 66         33.10          4.20         10.20             1          1.70          3.40          3.15
   40       Hakeem Olajuwon    1995   C 72         27.80          3.50         10.80          1.80          3.40          3.30          3.10
   41       George McGinnis    1975  PF 79         29.80          6.30         14.30          2.60          0.70          5.30          3.10
   42            Larry Bird    1986  SF 82         25.80          6.80          9.80             2          0.60          3.20          3.10
   43          LeBron James    2018  PF 82         27.50          9.10          8.60          1.40          0.90          4.20          3.09
   44         Julius Erving    1973  SF 71         31.90          4.20         12.20          2.50          1.80          4.60          3.07
   45           Dwyane Wade    2009  SG 79         30.20          7.50             5          2.20          1.30          3.40          3.07
   46          James Harden    2018  SG 72         30.40          8.80          5.40          1.80          0.70          4.40          3.07
   47         Julius Erving    1976  SF 84         29.30             5            11          2.50          1.90          3.70          3.06
   48      Shaquille O'Neal    2001   C 74         28.70          3.70         12.70          0.60          2.80          2.90          3.06
   49           Joel Embiid    2024   C 39         34.70          5.60            11          1.20          1.70          3.80          3.05
   50   Kareem Abdul-Jabbar    1980   C 82         24.80          4.50         10.80             1          3.40          3.60          3.04

=== Ranking Complete ===



'''

