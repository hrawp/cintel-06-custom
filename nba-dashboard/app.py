import numpy as np

# Import helpers for plotting logic
from plots import color_palette, density_plot, radar_chart

# Import some pre-downloaded data on player careers
from shared import app_dir, careers_df, from_start, gp_max, players_dict, stats, to_end 
from shiny import reactive, req, render
from shiny.express import input, ui
from shinywidgets import render_plotly
from faicons import icon_svg

ui.page_opts(title="NBA Dashboard", fillable=True)

ui.include_css(app_dir / "styles.css")

with ui.sidebar():
    ui.input_selectize(
        "players",
        "Search for players",
        multiple=True,
        choices=players_dict,
        selected=["893", "2544", "201939"],
        width="100%",
    )
    ui.input_slider(
        "games",
        "Career games played",
        value=[300, gp_max],
        min=0,
        max=gp_max,
        step=1,
        sep="",
    )
    ui.input_slider(
        "seasons",
        "Career within years",
        value=[from_start, to_end],
        min=from_start,
        max=to_end,
        step=1,
        sep="",
    )


with ui.layout_columns(col_widths={"sm": 3, "md": 3, "lg": 3}):
    with ui.card(
     #   showcase = icon_svg("sun"),
        theme = "bg-gradient-red-orange"
    ):
        "Player and Points/Game"
        
        @render.data_frame
        def display_dfpt():
      # Use maximum widthS
            dfpt = player_stats()
            dfpt['PTS'] = dfpt['PTS'].round(2)
            return dfpt[['player_name','PTS']]

    with ui.card(
    #    showcase=icon_svg("sun"),
        theme="bg-gradient-red-orange"
    ):
        "Field Goal Percentage"
        
        @render.data_frame
        def display_dfpc():
      # Use maximum widthS
            dfpc = player_stats()
            dfpc['FG_PCT'] = dfpc['FG_PCT'].round(2)
            return dfpc[['FG_PCT']]

    with ui.card(
    #    showcase=icon_svg("sun"),
        theme="bg-gradient-red-orange"
    ):
        "Three Point Percentage"
        
        @render.data_frame
        def display_df3pc():
      # Use maximum widthS
            df3pc = player_stats()
            df3pc['FG3_PCT'] = df3pc['FG3_PCT'].round(2)
            return df3pc[['FG3_PCT']]
        
        
    with ui.card(
     #   showcase=icon_svg("sun"),
        theme="bg-red"
    ):
        "Free Throw Percentage"
        
        @render.data_frame
        def display_dffpc():
      # Use maximum widthS
            dffpc = player_stats()
            dffpc['FT_PCT'] = dffpc['FT_PCT'].round(2)
            return dffpc[['FT_PCT']]
      
    with ui.card(
    #    showcase=icon_svg("sun"),
        theme="bg-gradient-red-orange"
    ):
        "Rebounds"
        
        @render.data_frame
        def display_dfr():
      # Use maximum widthS
            dfr = player_stats()
            dfr['REB'] = dfr['REB'].round(2)
            return dfr[['REB']]

    with ui.card(
    #    showcase=icon_svg("sun"),
        theme="bg-gradient-red-orange"
    ):
        "Assists"
        
        @render.data_frame
        def display_dfa():
      # Use maximum widthS
            dfa = player_stats()
            dfa['AST'] = dfa['AST'].round(2)
            return dfa[['AST']]

    with ui.card(
    #    showcase=icon_svg("sun"),
        theme="bg-gradient-red-orange"
    ):
        "Steals"
        
        @render.data_frame
        def display_dfs():
      # Use maximum widthS
            dfs = player_stats()
            dfs['STL'] = dfs['STL'].round(2)
            return dfs[['STL']]

    with ui.card(
    #    showcase=icon_svg("sun"),
        theme="bg-gradient-red-orange"
    ):
        "Blocks"
        
        @render.data_frame
        def display_dfb():
      # Use maximum widthS
            dfb = player_stats()
            dfb['BLK'] = dfb['BLK'].round(2)
            return dfb[['BLK']]


# Filter the careers data based on the selected games and seasons
@reactive.calc
def careers():
    games = input.games()
    seasons = input.seasons()
    idx = (
        (careers_df["GP"] >= games[0])
        & (careers_df["GP"] <= games[1])
        & (careers_df["from_year"] >= seasons[0])
        & (careers_df["to_year"] <= seasons[1])
    )
    return careers_df[idx]


# Update available players when careers data changes
@reactive.effect
def _():
    players = dict(zip(careers()["person_id"], careers()["player_name"]))
    ui.update_selectize("players", choices=players, selected=input.players())


# Get the stats for the selected players
@reactive.calc
def player_stats():
    players = req(input.players())
    res = careers()
    res = res[res["person_id"].isin(players)]
    res["color"] = np.resize(color_palette, len(players))
    return res


# For each player, get the percentile of each stat
@reactive.calc
def percentiles():
    d = player_stats()

    def apply_func(x):
        for col in stats:
            x[col] = (x[col].values > careers()[col].values).mean()
        return x

    return d.groupby("person_id").apply(apply_func)


# When a player is clicked on the rug plot, add them to the selected players
def on_rug_click(trace, points, state):
    player_id = trace.customdata[points.point_inds[0]]
    selected = list(input.players()) + [player_id]
    ui.update_selectize("players", selected=selected)
