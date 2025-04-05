import streamlit as st
import duckdb
import gdown
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

# Set page configuration as the first Streamlit call
st.set_page_config(layout="wide")

DB_FILE = "nbl.db"
FILE_ID = st.secrets["FILE_ID"]

sql_result = """
select * from gamelog_result
where team = 'ZER'
"""
sql_adv = """
select *
from team_stats_gamelog
"""
@st.cache_data
def load_data():
    # Download the database file
    gdown.download(f"https://drive.google.com/uc?id={FILE_ID}", DB_FILE, quiet=False)
    con = duckdb.connect(DB_FILE)
    gl = con.execute(sql_result).fetchdf()
    con.close()
    return gl
@st.cache_data
def load_data_advanced():
    # Download the database file
    gdown.download(f"https://drive.google.com/uc?id={FILE_ID}", DB_FILE, quiet=False)
    con = duckdb.connect(DB_FILE)
    adv = con.execute(sql_adv).fetchdf()
    con.close()
    return adv

gl = load_data()
df_adv = load_data_advanced()
st.header('ZER Postgame Report')

gl['Game Choice'] = gl['DATE'] + ': ' + gl['opp_team']
gl['WL'] = np.where(gl['win'] == 1, 'W', 'L')
games = gl['Game Choice'].unique()

selected_game = st.selectbox("Select a game", games)

# Display the selected game
st.write("You selected:", selected_game)

df = gl[gl['Game Choice'] == selected_game]
header_str = 'Game Number: ' + str(df['game_number'].iloc[0]) + ' / Opponent: ' + df['opp_team'].iloc[0]
subheader_str = ('POSTGAME REPORT | ' + df['DATE'].iloc[0] + ' | ' + df['WL'].iloc[0]
                 + ': ' + str(df['FINAL'].iloc[0]) + '-' + str(df['opp_final'].iloc[0]))
# POSTGAME REPORT | 01/10/2020 vs UTA | L: 92-109
st.header(header_str)
st.write(subheader_str)

line1 = [df['1'].iloc[0], df['2'].iloc[0], df['3'].iloc[0], df['4'].iloc[0], df['OT'].iloc[0]]
line2 = [df['opp_1'].iloc[0], df['opp_2'].iloc[0], df['opp_3'].iloc[0], df['opp_4'].iloc[0], df['opp_ot'].iloc[0]]
line3 = [x - y for x, y in zip(line1, line2)]

quarter_chart = {
    "ZER Points": line1,
    "Opponent Points": line2,
    "Net Points": line3
}

chrt = pd.DataFrame(quarter_chart, index=['Q1', 'Q2', 'Q3', 'Q4', 'QOT'])

gameid = df['GAMEID'].iloc[0]
# df_adv = adv[adv['GAMEID'] == gameid]

df_adv['off_EFG'] = (df_adv['fgm'] + .5*df_adv['3fgm'])/df_adv['fga']
df_adv['off_TOV'] = df_adv['tov']/(df_adv['fga'] + df_adv['fta']*.44 + df_adv['tov'])
df_adv['off_OREB'] = df_adv['off']/(df_adv['off'] + df_adv['def'])
df_adv['off_FTR'] = df_adv['ftm']/df_adv['fga']
df_adv['off_AST'] = df_adv['ast']/df_adv['fgm']

df_adv['def_EFG'] = (df_adv['opp_fgm'] + .5*df_adv['opp_3fgm'])/df_adv['opp_fga']
df_adv['def_TOV'] = df_adv['opp_tov']/(df_adv['opp_fga'] + df_adv['opp_fta']*.44 + df_adv['opp_tov'])
df_adv['def_OREB'] = df_adv['opp_off']/(df_adv['opp_off'] + df_adv['def'])
df_adv['def_FTR'] = df_adv['opp_ftm']/df_adv['opp_fga']
df_adv['def_AST'] = df_adv['opp_ast']/df_adv['opp_fgm']

df_adv['row_number_off_efg'] = df_adv['off_EFG'].rank(method='first', ascending=True).astype(int)
df_adv['row_number_off_tov'] = df_adv['off_TOV'].rank(method='first', ascending=False).astype(int)
df_adv['row_number_off_oreb'] = df_adv['off_OREB'].rank(method='first', ascending=True).astype(int)
df_adv['row_number_off_ftr'] = df_adv['off_FTR'].rank(method='first', ascending=True).astype(int)
df_adv['row_number_off_ast'] = df_adv['off_AST'].rank(method='first', ascending=True).astype(int)
df_adv['row_number_off_rtg'] = df_adv['ORTG'].rank(method='first', ascending=True).astype(int)


df_adv['row_number_def_efg'] = df_adv['def_EFG'].rank(method='first', ascending=False).astype(int)
df_adv['row_number_def_tov'] = df_adv['def_TOV'].rank(method='first', ascending=True).astype(int)
df_adv['row_number_def_oreb'] = df_adv['def_OREB'].rank(method='first', ascending=False).astype(int)
df_adv['row_number_def_ftr'] = df_adv['def_FTR'].rank(method='first', ascending=False).astype(int)
df_adv['row_number_def_ast'] = df_adv['def_AST'].rank(method='first', ascending=False).astype(int)
df_adv['row_number_def_rtg'] = df_adv['DRTG'].rank(method='first', ascending=False).astype(int)

df_adv['percentile_rank_off_efg'] = df_adv['row_number_off_efg'].rank(method='min', pct=True)
df_adv['percentile_rank_off_tov'] = df_adv['row_number_off_tov'].rank(method='min', pct=True)
df_adv['percentile_rank_off_oreb'] = df_adv['row_number_off_oreb'].rank(method='min', pct=True)
df_adv['percentile_rank_off_ftr'] = df_adv['row_number_off_ftr'].rank(method='min', pct=True)
df_adv['percentile_rank_off_ast'] = df_adv['row_number_off_ast'].rank(method='min', pct=True)
df_adv['percentile_rank_off_rtg'] = df_adv['row_number_off_rtg'].rank(method='min', pct=True)

df_adv['percentile_rank_def_efg'] = df_adv['row_number_def_efg'].rank(method='min', pct=True)
df_adv['percentile_rank_def_tov'] = df_adv['row_number_def_tov'].rank(method='min', pct=True)
df_adv['percentile_rank_def_oreb'] = df_adv['row_number_def_oreb'].rank(method='min', pct=True)
df_adv['percentile_rank_def_ftr'] = df_adv['row_number_def_ftr'].rank(method='min', pct=True)
df_adv['percentile_rank_def_ast'] = df_adv['row_number_def_ast'].rank(method='min', pct=True)
df_adv['percentile_rank_def_rtg'] = df_adv['row_number_def_rtg'].rank(method='min', pct=True)

df_display = df_adv[(df_adv['GAMEID'] == gameid) & (df_adv['TEAM'] == 'ZER')]

adv_display = pd.DataFrame(columns = ['Advanced Stats', 'Offense Percentile', 'Defense Percentile', 'Offense Value', 'Defense Value'])
adv_display.loc[0] = ['Rating'
    , df_display['percentile_rank_off_rtg'].iloc[0]
    , df_display['percentile_rank_def_rtg'].iloc[0]
    , df_display['ORTG'].iloc[0]
    , df_display['DRTG'].iloc[0]]

adv_display.loc[1] = ['Shooting (eFG%)'
    , df_display['percentile_rank_off_efg'].iloc[0]
    , df_display['percentile_rank_def_efg'].iloc[0]
    , df_display['off_EFG'].iloc[0]
    , df_display['def_EFG'].iloc[0]]

adv_display.loc[2] = ['Rebounding (OREB%)'
    , df_display['percentile_rank_off_oreb'].iloc[0]
    , df_display['percentile_rank_def_oreb'].iloc[0]
    , df_display['off_OREB'].iloc[0]
    , df_display['def_OREB'].iloc[0]]

adv_display.loc[3] = ['Turnover (TOV%)'
    , df_display['percentile_rank_off_tov'].iloc[0]
    , df_display['percentile_rank_def_tov'].iloc[0]
    , df_display['off_TOV'].iloc[0]
    , df_display['def_TOV'].iloc[0]]

adv_display.loc[4] = ['Free Throws (FT%)'
    , df_display['percentile_rank_off_ftr'].iloc[0]
    , df_display['percentile_rank_def_ftr'].iloc[0]
    , df_display['off_FTR'].iloc[0]
    , df_display['def_FTR'].iloc[0]]

adv_display.loc[5] = ['Assist (AST%)'
    , df_display['percentile_rank_off_ast'].iloc[0]
    , df_display['percentile_rank_def_ast'].iloc[0]
    , df_display['off_AST'].iloc[0]
    , df_display['def_AST'].iloc[0]]

custom_cmap = LinearSegmentedColormap.from_list("red_white_green", ["red", "white", "green"])

numeric_cols = adv_display.select_dtypes(include=['number']).columns
formatters = {col: "{:.2f}".format for col in numeric_cols}

styled_df = (
    adv_display.style
      .format(formatters)   # Rounds all numeric columns to 2 decimals
      .background_gradient(
          cmap=custom_cmap,
          subset=["Offense Percentile", "Defense Percentile"],
          vmin=0,
          vmax=1
      )
)

st.write(styled_df)

# Create and display the line chart
st.line_chart(chrt)
