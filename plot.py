import logging
from random import choice

import pandas as pd
import plotly.express as px

import config

logger = logging.getLogger(__name__)


def graphs_plotter(df, event, start, end, data_source, aggregation):
    figures = []

    try:

        if data_source != "All":
            df_plot = df[df["filename"].str.contains(data_source)]
        else:
            df_plot = df

        df_plot = df_plot[df_plot["event_label"] == event]

        try:
            if "Hourly".lower() in aggregation.lower():
                df_plot["time"] = df_plot["time"].dt.floor("H")
                # df_plot["time"] = df_plot["time"].dt.round("H")
            elif "Daily".lower() in aggregation.lower():
                df_plot["time"] = df_plot["time"].dt.date

        except Exception as e:
            logging.error(f"Error during aggregation graph : {str(e)}")

        df_plot = df_plot[["time", "event_label", "results_code", "count"]].groupby(
            ["time", "event_label", "results_code"], as_index=False).sum("count")

        df_plot.set_index("time", inplace=True)

        df_plot = df_plot[["results_code", "count"]]

        df_plot = df_plot.loc[pd.to_datetime(start, format="%Y-%m-%d"):
                              pd.to_datetime(end, format="%Y-%m-%d") + pd.Timedelta(days=1) - pd.Timedelta(minutes=1)]

        minimum = min(df_plot.index)
        maximum = max(df_plot.index)
        event_description = config.EVENTS_MAP[event]

        # df_plot['count_rolling'] = df_plot['count'].rolling(window=120).mean()

        fig1 = px.line(df_plot,
                       x=df_plot.index,
                       y=df_plot["count"],
                       color=df_plot["results_code"],
                       title=f"Line Chart. Event: {event_description}. Period: {minimum} - {maximum}. Data Source: {data_source}. Aggregation: {aggregation}",
                       template="plotly_dark"
                       )
        fig1 = legend_names_updater(fig1)
        if aggregation != "Default":
            fig1.update_traces(mode='markers+lines')
        figures.append(fig1)

        fig2 = px.pie(df_plot,
                      names=df_plot.results_code.map(config.RESULTS_MAP),
                      values=df_plot['count'],
                      color_discrete_sequence=choice([px.colors.sequential.Sunsetdark, px.colors.sequential.Jet_r,
                                                      px.colors.sequential.Electric, px.colors.sequential.Plasma]),
                      title=f"Pie Chart. Event: {event_description}. Period: {minimum} - {maximum}. Data Source: {data_source}",
                      hole=0.5,
                      template="plotly_dark"
                      )
        fig2.update_traces(textinfo='percent+label')
        figures.append(fig2)

        df_plot_bar = df_plot[["results_code", "count"]].groupby(
            ["results_code"], as_index=False).sum("count").sort_values(by="count", ascending=False)
        df_plot_bar.results_code = df_plot_bar.results_code.astype(str)
        df_plot_bar = df_plot_bar[::-1]

        fig3 = px.bar(df_plot_bar,
                      y=df_plot_bar["results_code"].map(config.RESULTS_MAP),
                      x=df_plot_bar["count"],
                      color=df_plot_bar["count"],
                      color_continuous_scale=choice(["agsunset", "blackbody", "jet", "armyrose", "viridis", "sunset"]),
                      text_auto=True,
                      title=f"Bar Chart. Event: {event_description}. Period: {minimum} - {maximum}. Data Source: {data_source}",
                      template="plotly_dark",
                      orientation="h"

                      )
        fig3.update_layout(
            yaxis_title="results_code"
        )

        figures.append(fig3)
        logging.info(f"Successfully generated graph : "
                     f"Event_Label={event}.Start={start}.End={end}.Data_Source={data_source}")

    except Exception as e:
        logging.error(f"Error generating graph : "
                      f"Event_Label={event}.Start={start}.End={end}.Data_Source={data_source} : {str(e)}")

    return figures


def legend_names_updater(fig):
    fig.for_each_trace(lambda t:
                       t.update(name=config.RESULTS_MAP[t.name],
                                legendgroup=config.RESULTS_MAP[t.name],
                                hovertemplate=t.hovertemplate.replace(t.name, config.RESULTS_MAP[t.name])
                                )
                       )

    return fig
