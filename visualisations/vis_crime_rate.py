import plotly.express as px
from dash import dcc, html
from template import THEME


def get_figure(df_crime_rate):
    categories = df_crime_rate['CATEGORIE'].unique().tolist()
    colors = {cat: THEME['bar_colors'][i % len(THEME['bar_colors'])]
                for i, cat in enumerate(categories)}

    fig = px.area(
        df_crime_rate,
        x='Annee',
        y='Taux_100k',
        color='CATEGORIE',
        color_discrete_map=colors,
        labels={
            'Taux_100k': 'Infractions par 100k habitants',
            'Annee': 'Année',
            'CATEGORIE': 'Type d\'infraction'
        },
        hover_data={'Annee': False},
        title='Évolution de la criminalité par 100 000 habitants à Montréal (2015–2024)',
        template='custom',
        markers=True,
    )

    fig.update_traces(
        hovertemplate=(
            '<b>Type d\'infraction :</b> %{fullData.name}<br>'
            '<b>Taux :</b> %{y:.1f} infractions / 100k hab.'
            '<extra></extra>'
        )
    )

    fig.update_layout(
        hovermode='x unified',
        font=dict(family='Space Mono, monospace', color=THEME['font_color']),
        title_font=dict(family='Space Mono, monospace', size=16, color=THEME['font_color']),
        xaxis=dict(dtick=1, showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        legend=dict(
            title=dict(
                text='Cliquez pour filtrer<br>',
                font=dict(family='Space Mono, monospace', size=12, color='#921F2E'),
            ),
            font=dict(family='Space Mono, monospace', size=12),
            orientation='v',
            yanchor='middle',
            y=0.5,
            xanchor='left',
            x=1.02,
        ),
        margin=dict(t=60, b=40, l=60, r=220),
    )

    return fig


def create_layout(df_crime_rate):
    return html.Div(style={'padding': '20px 0'}, children=[
        html.Div(
            **{'aria-label': 'Graphique en aires de l\'évolution du taux de criminalité par 100 000 habitants à Montréal de 2015 à 2024, réparti par catégorie d\'infraction : vol dans ou sur véhicule à moteur, introduction, méfait, vol de véhicule à moteur, vols qualifiés, et infractions entraînant la mort. Le taux global a diminué jusqu\'en 2020, puis a fortement augmenté jusqu\'en 2023 avant de redescendre. Cliquez sur la légende pour afficher ou masquer une catégorie.'},
            role='img',
            children=[
                dcc.Graph(
                    id='crime-rate-chart',
                    figure=get_figure(df_crime_rate),
                    config=dict(
                        scrollZoom=False,
                        showTips=False,
                        showAxisDragHandles=False,
                        doubleClick=False,
                        displayModeBar=False,
                    ),
                    style={'height': '500px'},
                )
            ],
        )
    ])
