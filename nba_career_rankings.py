import pandas as pd
import numpy as np
import csv

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 100)
pd.set_option("display.width", None)

try:
    df = pd.read_csv("Player Totals.csv", low_memory=False)
    awards = pd.read_csv("Player Award Shares.csv", low_memory=False)
    allStar = pd.read_csv("All-Star Selections.csv", low_memory=False)
    print("Data loaded successfully!")
except Exception as e:
    print(f"Error loading data: {e}")
    quit()


#Find a way to get rid of duplicates
#People who have been traded twice in a season get accounted for twice
#2TM

# Stats

career_stats = df.groupby('player_id').agg({
    'g': 'sum',
    'trb': 'sum',
    'ast': 'sum',
    'stl': 'sum',
    'blk': 'sum',
    'tov': 'sum',
    'pts': 'sum',
    'trp_dbl': 'sum'
}).fillna(0).reset_index()
# print (career_stats.head(1))

stats_to_normalize = [
    'g' , 'trb', 'ast', 'stl', 'blk', 'tov', 'pts'
]

for stat in stats_to_normalize:
    if stat in career_stats.columns and career_stats[stat].std() != 0:
        career_stats[f'z_{stat}'] = (career_stats[stat] - career_stats[stat].mean()) / career_stats[stat].std()
    else:
        career_stats[f'z_{stat}'] = 0


career_stats['career_score'] = (
    0.35 * career_stats.get('z_pts', 0) +
    0.25 * career_stats.get('z_ast', 0) +
    0.25 * career_stats.get('z_trb', 0) +
    0.125 * career_stats.get('z_stl', 0) +
    0.125 * career_stats.get('z_blk', 0) -
    0.10 * career_stats.get('z_tov', 0) +
    0.005 * career_stats.get('trp_dbl', 0)
)


#Awards
award_weights = {
    "nba mvp": 0.5,
    "nba dpoy": 0.35,
    "nba roy": 0.1,
    "nba smoy": 0.05
}

for _, row in awards.iterrows():
    weight = award_weights.get(row['award'].lower(), 0)
    if weight > 0:
        if row['player_id'] in career_stats.index:
            career_stats.loc[row['player_id'], 'career_score'] += weight * row['share']

#All Star

for _, row in allStar.iterrows():
    if row['player_id'] in career_stats.index:
        career_stats.loc[row['player_id'], 'career_score'] += 0.2

# Sort by player score to get rankings
career_rank = career_stats.sort_values('career_score', ascending=False)

# Display top 25 players
print("\n=== NBA All-Time Season Rankings ===")
print("Ranking considers: Points (35%), Assists (25%), Rebounds (25%), Steals (12.5%), Blocks (12.5%), Turnovers (-10%)")
print("=" * 120)

display_columns = [
    'player_id', 'g', 'pts', 'ast', 'trb',
    'stl', 'blk', 'tov', 'trp_dbl', 'career_score'
]
available_columns = [col for col in display_columns if col in career_stats.columns]

top_50 = career_rank[available_columns].head(50)
top_50['rank'] = range(1, len(top_50) + 1)


# Format the display
pd.set_option(
    'display.float_format',
    lambda x: f"{x:,.2f}" if pd.notnull(x) and x % 1 else f"{int(x):,}" if pd.notnull(x) else "0"
)

print(top_50.to_string(index=False, columns=['rank'] + available_columns))

print("\n=== Ranking Complete ===")