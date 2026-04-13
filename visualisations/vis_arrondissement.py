'''
    Distribution spatiale des crimes par arrondissement (PDQ)
'''

import os
import json
import plotly.express as px
import plotly.colors as pc
import dash
from dash import dcc, html, Input, Output, State

import preprocess

_DIR         = os.path.dirname(os.path.dirname(__file__))
GEOJSON_PATH = os.path.join(_DIR, 'assets', 'data', 'limitespdq_wgs84.geojson')

COLORSCALE = [[0, 'white'], [0.0001, '#fee5d9'], [0.5, '#fc4e2a'], [1, '#67000d']]

# GeoJSON des PDQ — Source : Ville de Montréal – Données ouvertes
# https://donnees.montreal.ca/dataset/limites-pdq-spvm
with open(GEOJSON_PATH, encoding='utf-8') as f:
    pdq_geojson = json.load(f)


def get_figure(counts, label_cat):
    max_crimes = counts['Nombre de crimes'].max()

    fig = px.choropleth_map(
        counts,
        geojson=pdq_geojson,
        locations='PDQ',
        featureidkey='properties.PDQ',
        color='Nombre de crimes',
        color_continuous_scale=COLORSCALE,
        range_color=(0, max_crimes),
        map_style='carto-positron',
        zoom=9.5,
        center={'lat': 45.55, 'lon': -73.62},
        opacity=0.7,
        hover_data={'Quartier': True},
    )

    fig.update_traces(
        hovertemplate=(
            '<b>%{customdata[0]}</b><br>'
            'PDQ %{location}<br>'
            'Crimes : %{z:,}<extra></extra>'
        )
    )

    fig.update_layout(
        title=dict(text=f'<b>{label_cat}</b> — 2015–2025', x=0.5, font=dict(size=15)),
        margin={'r': 0, 't': 48, 'l': 40, 'b': 40},
        coloraxis_colorbar=dict(title='Crimes'),
        dragmode=False,
        map=dict(style='carto-positron', bearing=0),
        paper_bgcolor='#f0eeda',
    )

    return fig, max_crimes


def create_layout(df_pdq):
    categories = sorted(df_pdq[df_pdq['PDQ'] != '50']['CATEGORIE'].unique().tolist())
    return html.Div([
        html.Div(
            style={'width': '380px', 'margin': '0 auto 16px'},
            children=[
                html.Label(
                    'Catégorie de crime',
                    style={'fontWeight': 'bold', 'marginBottom': '6px', 'display': 'block'},
                ),
                dcc.Dropdown(
                    id='arrondissement-cat-dropdown',
                    options=[{'label': 'Toutes catégories', 'value': '__all__'}]
                            + [{'label': c, 'value': c} for c in categories],
                    value='__all__',
                    clearable=False,
                    searchable=False,
                ),
            ],
        ),

        html.Div(
            style={'textAlign': 'right', 'marginBottom': '6px'},
            children=[
                html.Button(
                    '⌖ Retour à Montréal',
                    id='arrondissement-reset-btn',
                    style={
                        'fontSize': '13px',
                        'fontFamily': 'Space Mono, monospace',
                        'color': '#AD1F3E',
                        'backgroundColor': '#f0eeda',
                        'border': '1px solid #AD1F3E',
                        'borderRadius': '4px',
                        'padding': '5px 12px',
                        'cursor': 'pointer',
                    }
                ),
            ]
        ),

        dcc.Loading(type='circle', color='#AD1F3E', children=[
            dcc.Graph(id='arrondissement-choropleth-map', style={'height': '560px'},
                      config={'scrollZoom': False, 'displayModeBar': False}),
        ]),

        html.Div(
            style={
                'border': '1px solid #ddd', 'borderRadius': '8px',
                'padding': '12px 20px', 'marginTop': '12px',
                'backgroundColor': '#f9f9f9',
                'display': 'flex', 'alignItems': 'center', 'gap': '16px',
            },
            children=[
                html.Div(
                    id='arrondissement-metro-color-square',
                    style={'width': '36px', 'height': '36px', 'borderRadius': '4px', 'border': '1px solid #ccc'},
                ),
                html.Div([
                    html.Span(
                        'PDQ 50 — Réseau du métro de Montréal',
                        style={'fontWeight': 'bold', 'display': 'block'},
                    ),
                    html.Span(id='arrondissement-metro-count', style={'fontSize': '14px', 'color': '#444'}),
                ]),
            ],
        ),
    ])


def register_callbacks(app, df_pdq):
    df_arrondissement = df_pdq[df_pdq['PDQ'] != '50'].copy()
    df_metro          = df_pdq[df_pdq['PDQ'] == '50'].copy()

    @app.callback(
        Output('arrondissement-choropleth-map', 'figure'),
        Output('arrondissement-metro-count', 'children'),
        Output('arrondissement-metro-color-square', 'style'),
        Input('arrondissement-cat-dropdown', 'value'),
        Input('arrondissement-reset-btn', 'n_clicks'),
        State('arrondissement-choropleth-map', 'figure'),
    )
    def update_map(selected_cat, n_clicks, current_figure):
        from dash import ctx
        # Reset view only — no data change needed
        if ctx.triggered_id == 'arrondissement-reset-btn' and current_figure:
            current_figure['layout']['map'] = {
                'center': {'lat': 45.55, 'lon': -73.62},
                'zoom': 9.5,
                'style': 'carto-positron',
                'bearing': 0,
            }
            return current_figure, dash.no_update, dash.no_update

        filtered       = df_arrondissement if selected_cat == '__all__' else df_arrondissement[df_arrondissement['CATEGORIE'] == selected_cat]
        metro_filtered = df_metro          if selected_cat == '__all__' else df_metro[df_metro['CATEGORIE'] == selected_cat]
        metro_count    = len(metro_filtered)
        metro_text     = f"{metro_count:,} infraction{'s' if metro_count > 1 else ''} enregistrée{'s' if metro_count > 1 else ''}"

        counts = preprocess.count_by_pdq(filtered, pdq_geojson)
        label_cat = 'Toutes catégories' if selected_cat == '__all__' else selected_cat
        fig, max_crimes = get_figure(counts, label_cat)

        metro_color  = pc.sample_colorscale(COLORSCALE, min(metro_count / max_crimes, 1.0))[0]
        square_style = {'width': '36px', 'height': '36px', 'borderRadius': '4px',
                        'border': '1px solid #ccc', 'backgroundColor': metro_color}

        return fig, metro_text, square_style
