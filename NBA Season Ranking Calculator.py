import pandas as pd
import numpy as np
import csv

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 100)
pd.set_option("display.width", None)

try:
    df = pd.read_csv("Player per Game.csv", low_memory=False)
    awards = pd.read_csv("Player Award Shares.csv", low_memory=False)
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
    0.35 * df.get('z_pts_per_game', 0) +
    0.25 * df.get('z_ast_per_game', 0) +
    0.25 * df.get('z_trb_per_game', 0) +
    0.125 * df.get('z_stl_per_game', 0) +
    0.125 * df.get('z_blk_per_game', 0) -
    0.10 * df.get('z_tov_per_game', 0)
)


'''df['player_score'] = (
    df.get('z_pts_per_game', 0) +
    df.get('z_ast_per_game', 0) +
    df.get('z_trb_per_game', 0) +
    df.get('z_stl_per_game', 0) +
    df.get('z_blk_per_game', 0) -
    df.get('z_tov_per_game', 0)
)
'''


'''df['player_score'] = (
    0.35 * df.get('pts_per_game', 0) +
    0.25 * df.get('ast_per_game', 0) +
    0.25 * df.get('trb_per_game', 0) +
    0.125 * df.get('stl_per_game', 0) +
    0.125 * df.get('blk_per_game', 0) -
    0.10 * df.get('tov_per_game', 0)
)
'''
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

