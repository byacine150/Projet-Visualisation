'''
    Heatmap des crimes par mois et par année, avec délimitation des saisons.
'''

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from template import THEME
import preprocess

MOIS = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']

SAISONS = [
    {'x': 0.06,  'text': 'Hiver'},
    {'x': 0.31,  'text': 'Printemps'},
    {'x': 0.56,  'text': 'Été'},
    {'x': 0.81,  'text': 'Automne'},
]

# Indices des mois qui débutent une nouvelle saison (après Mar, Juin, Sep)
SEASON_BOUNDARIES = ['Mar', 'Juin', 'Sep']

COLORSCALE = [
    [0,    '#ffffff'],  # white — minimum crimes
    [0.3,  '#f5c0c8'],  # light pink
    [0.6,  '#AD1F3E'],  # theme red
    [1,    '#3d0010'],  # near-black crimson — peak
]


def get_figure(pivot):
    years = pivot.index.tolist()

    fig = make_subplots(
        rows=len(years),
        cols=1,
        subplot_titles=[str(y) for y in years],
        vertical_spacing=0.05,
    )

    for i, year in enumerate(years):
        row_data = pivot.loc[year].tolist()
        row_min = min(row_data)
        row_max = max(row_data)
        show_colorbar = (i == 0)

        fig.add_trace(
            go.Heatmap(
                z=[row_data],
                x=MOIS,
                y=[''],
                colorscale=COLORSCALE,
                zmin=row_min,
                zmax=row_max,
                showscale=show_colorbar,
                colorbar=dict(
                    title=dict(
                        text='Crimes',
                        font=dict(family='Space Mono, monospace', size=12),
                    ),
                    tickfont=dict(family='Space Mono, monospace', size=11),
                    len=0.3,
                    y=0.92,
                ) if show_colorbar else None,
                hovertemplate=(
                    f'<b>Année :</b> {year}<br>'
                    '<b>Mois :</b> %{x}<br>'
                    '<b>Total crimes :</b> %{z:,}'
                    '<extra></extra>'
                ),
            ),
            row=i + 1,
            col=1,
        )

        for boundary in SEASON_BOUNDARIES:
            fig.add_vline(
                x=boundary,
                line_width=2,
                line_color='#4a90d9',
                opacity=0.8,
                row=i + 1,
                col=1,
            )

    for ann in SAISONS:
        fig.add_annotation(
            x=ann['x'],
            y=1.07,
            xref='paper',
            yref='paper',
            text=f"<b>{ann['text']}</b>",
            showarrow=False,
            bgcolor='#AD1F3E',
            bordercolor='#AD1F3E',
            borderpad=5,
            font=dict(family='Space Mono, monospace', size=13, color='white'),
        )

    fig.update_xaxes(
        side='bottom',
        tickfont=dict(family='Space Mono, monospace', size=11),
    )
    fig.update_yaxes(showticklabels=False)

    for i in range(len(years)):
        fig.layout.annotations[i].font.family = 'Space Mono, monospace'
        fig.layout.annotations[i].font.size = 15
        fig.layout.annotations[i].font.color = '#AD1F3E'
        fig.layout.annotations[i].text = f"<b>{years[i]}</b>"

    fig.update_layout(
        height=80 * len(years) + 180,
        title=dict(
            text='Total des crimes à Montréal par mois (2015–2024)',
            font=dict(family='Space Mono, monospace', size=16, color=THEME['font_color']),
            x=0.5,
            xanchor='center',
        ),
        font=dict(family='Space Mono, monospace', color=THEME['font_color']),
        dragmode=False,
        plot_bgcolor=THEME['background_color'],
        paper_bgcolor=THEME['background_color'],
        margin=dict(t=180, l=60, r=40, b=40),
    )

    return fig


def create_layout(pivot):
    return html.Div(style={'padding': '20px 0'}, children=[
        html.P(
            'Filtrez par catégorie en cliquant sur la légende du graphique de l\'évolution par année ci-dessus.',
            style={
                'fontSize': '13px',
                'color': '#921F2E',
                'fontStyle': 'italic',
                'fontFamily': 'Space Mono, monospace',
                'marginBottom': '8px',
            }
        ),
        dcc.Graph(
            id='crimes-saison-heatmap',
            figure=get_figure(pivot),
            config=dict(
                scrollZoom=False,
                showTips=False,
                displayModeBar=False,
            ),
        )
    ])


def register_callbacks(app, df):
    @app.callback(
        Output('crimes-saison-heatmap', 'figure'),
        Input('crime-rate-chart', 'restyleData'),
        State('crime-rate-chart', 'figure'),
    )
    def sync_heatmap(restyle_data, area_figure):
        if area_figure is None or restyle_data is None:
            raise PreventUpdate

        visible_categories = [
            trace['name'] for trace in area_figure['data']
            if trace.get('visible', True) not in [False, 'legendonly']
        ]

        categories = visible_categories if visible_categories else None
        pivot = preprocess.prepare_monthly_crime_data(df, categories=categories)
        return get_figure(pivot)
