'''
    Graphique à barres groupées des infractions par catégorie et moment de la journée.
'''

import plotly.graph_objects as go
from dash import dcc, html, Input, Output
from template import THEME

# Mapping moment → label affiché & couleur thématique
MOMENTS = {
    'jour': {'label': 'Jour', 'color': '#e48d3c'},
    'soir': {'label': 'Soir', 'color': '#AD1F3E'},
    'nuit': {'label': 'Nuit', 'color': '#2b2d42'},
}

# Catégories de crimes séparées en deux groupes (propriété / personne)
CRIMES_PROPRIETE = [
    'Vol dans / sur véhicule à moteur',
    'Introduction',
    'Méfait',
    'Vol de véhicule à moteur',
]

CRIMES_PERSONNE = [
    'Vols qualifiés',
    'Infractions entrainant la mort',
]


# Display labels with line breaks for long category names
LABEL_MAP = {
    'Vol dans / sur véhicule à moteur': 'Vol dans/sur<br>véhicule à moteur',
    'Introduction': 'Introduction<br>par effraction',
    'Méfait': 'Vandalisme<br>(Méfait)',
    'Vol de véhicule à moteur': 'Vol de<br>véhicule',
    'Vols qualifiés': 'Vols<br>qualifiés',
    'Infractions entrainant la mort': 'Infractions<br>entraînant la mort',
}


def get_figure(df_moment, filter_mode='all'):
    '''
    Builds a grouped bar chart from the preprocessed moment data.

    Args:
        df_moment: DataFrame with columns [CATEGORIE, QUART, Nombre].
        filter_mode: 'all', 'prop', or 'pers'.
    Returns:
        A plotly Figure.
    '''
    # Order categories: propriété (descending total) then personne (descending total)
    cat_totals = df_moment.groupby('CATEGORIE')['Nombre'].sum()

    prop_cats = [c for c in sorted(CRIMES_PROPRIETE, key=lambda c: cat_totals.get(c, 0), reverse=True)]
    pers_cats = [c for c in sorted(CRIMES_PERSONNE, key=lambda c: cat_totals.get(c, 0), reverse=True)]

    if filter_mode == 'prop':
        ordered_cats = prop_cats
    elif filter_mode == 'pers':
        ordered_cats = pers_cats
    else:
        ordered_cats = prop_cats + pers_cats

    display_labels = [LABEL_MAP.get(c, c) for c in ordered_cats]

    fig = go.Figure()

    for quart, info in MOMENTS.items():
        subset = df_moment[df_moment['QUART'] == quart]
        vals = [subset.loc[subset['CATEGORIE'] == cat, 'Nombre'].values[0]
                if cat in subset['CATEGORIE'].values else 0
                for cat in ordered_cats]

        fig.add_trace(go.Bar(
            name=info['label'],
            x=display_labels,
            y=vals,
            marker_color=info['color'],
            text=[f'{v / 1000:.0f}k' if v >= 1000 else str(v) for v in vals],
            textposition='outside',
            textfont=dict(family='Space Mono, monospace', size=11, color=THEME['font_color']),
            hovertemplate=(
                '<b>%{x}</b><br>'
                'Moment : ' + info['label'] + '<br>'
                'Nombre : %{y:,}'
                '<extra></extra>'
            ),
        ))

    # Dynamic Annotations & Separator
    annotations = []
    shapes = []
    
    if filter_mode == 'all':
        prop_count = len(prop_cats)
        annotations.append(dict(
            text='<b>Crimes contre la propriété</b>',
            x=(prop_count - 1) / 2.0, y=1.12,
            xref='x', yref='paper', showarrow=False,
            font=dict(family='Space Mono, monospace', size=13, color='#888'),
        ))
        
        start_idx = len(prop_cats)
        pers_count = len(pers_cats)
        annotations.append(dict(
             text='<b>Crimes contre la personne</b>',
             x=start_idx + (pers_count - 1) / 2.0, y=1.12,
             xref='x', yref='paper', showarrow=False,
             font=dict(family='Space Mono, monospace', size=13, color='#888'),
        ))
        
        shapes.append(dict(
            type='line',
            x0=len(prop_cats) - 0.5, x1=len(prop_cats) - 0.5,
            y0=0, y1=1,
            xref='x', yref='paper',
            line=dict(color='#bbb', width=1.5, dash='dot')
        ))

    fig.update_layout(
        barmode='group',
        template='custom',
        title=dict(
            text='Infractions criminelles par catégorie et moment de la journée',
            font=dict(family='Space Mono, monospace', size=16, color=THEME['font_color']),
            x=0.5,
            xanchor='center',
        ),
        xaxis=dict(
            title=None,
            tickfont=dict(family='Space Mono, monospace', size=11),
            tickangle=0,
        ),
        yaxis=dict(
            title=dict(
                text="Nombre d'infractions (cumul 2015–2025)",
                font=dict(family='Space Mono, monospace', size=12),
            ),
            tickfont=dict(family='Space Mono, monospace', size=11),
            gridcolor='rgba(0,0,0,0.08)',
            tickformat=',',
        ),
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
        font=dict(family='Space Mono, monospace', color=THEME['font_color']),
        plot_bgcolor=THEME['background_color'],
        paper_bgcolor=THEME['background_color'],
        margin=dict(t=100, b=120, l=80, r=160),
        height=560,
        bargap=0.25,
        bargroupgap=0.08,
        annotations=annotations,
        shapes=shapes,
        transition=dict(duration=800, easing='cubic-in-out'),
    )

    return fig


def create_layout(df_moment):
    '''
    Returns the Dash layout component for this visualisation.
    '''
    return html.Div(style={'padding': '20px 0'}, children=[
        dcc.Graph(
            id='moment-journee-chart',
            figure=get_figure(df_moment, 'all'),
            config=dict(
                scrollZoom=False,
                showTips=False,
                displayModeBar=False,
            ),
        ),
        html.Div(
            style={
                'display': 'flex',
                'justifyContent': 'center',
                'marginTop': '-60px',
                'position': 'relative',
                'zIndex': '10',
                'paddingBottom': '20px',
                'gap': '12px'
            },
            children=[
                html.Div('Toutes les infractions', id='btn-all', n_clicks=0),
                html.Div('Crimes contre la propriété', id='btn-prop', n_clicks=0),
                html.Div('Crimes contre la personne', id='btn-pers', n_clicks=0),
            ]
        )
    ])

def register_callbacks(app, df_moment):
    @app.callback(
        Output('moment-journee-chart', 'figure'),
        Output('btn-all', 'style'),
        Output('btn-prop', 'style'),
        Output('btn-pers', 'style'),
        Input('btn-all', 'n_clicks'),
        Input('btn-prop', 'n_clicks'),
        Input('btn-pers', 'n_clicks'),
    )
    def update_chart(btn_all, btn_prop, btn_pers):
        from dash import ctx
        
        btn_base_style = {
            'padding': '10px 20px',
            'borderRadius': '6px',
            'border': f"1px solid {THEME['font_color']}",
            'backgroundColor': 'transparent',
            'color': THEME['font_color'],
            'fontFamily': 'Space Mono, monospace',
            'fontSize': '14px',
            'cursor': 'pointer',
            'transition': 'all 0.3s ease',
            'userSelect': 'none',
            'textAlign': 'center',
            'fontWeight': 'bold'
        }
        btn_active_style = btn_base_style.copy()
        btn_active_style.update({
            'backgroundColor': THEME['font_color'],
            'color': THEME['background_color']
        })

        triggered_id = ctx.triggered_id
        if triggered_id == 'btn-prop':
            return get_figure(df_moment, 'prop'), btn_base_style, btn_active_style, btn_base_style
        elif triggered_id == 'btn-pers':
            return get_figure(df_moment, 'pers'), btn_base_style, btn_base_style, btn_active_style
        else:
            return get_figure(df_moment, 'all'), btn_active_style, btn_base_style, btn_base_style
