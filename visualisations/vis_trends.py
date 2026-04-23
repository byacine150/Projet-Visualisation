'''
    Crime trends in Montreal — proportions by category (2015-2025)
'''

import plotly.graph_objects as go
import dash
import preprocess
from dash import dcc, html, Input, Output, State
from template import THEME

VIOLENT = {'Vols qualifiés', 'Infractions entrainant la mort'}

LABELS = {
    'Vol dans / sur véhicule à moteur': 'Vol dans véhicule',
    'Introduction':                      'Introduction',
    'Méfait':                            'Méfait',
    'Vol de véhicule à moteur':          'Vol de véhicule',
    'Vols qualifiés':                    'Vols qualifiés',
    'Infractions entrainant la mort':    'Infractions mortelles',
}

COLORS = {
    'Introduction':                      '#185FA5',
    'Méfait':                            '#1D9E75',
    'Vol dans / sur véhicule à moteur':  '#5DCAA5',
    'Vol de véhicule à moteur':          '#378ADD',
    'Vols qualifiés':                    '#D85A30',
    'Infractions entrainant la mort':    '#F5C4B3',
}

COLOR_PROPERTY   = COLORS['Introduction']
COLOR_VIOLENT = COLORS['Vols qualifiés']

def get_figure(pct, visible_categories=None):
    '''
    Builds a line chart showing the proportion of crimes by category.

    Args:
        pct: DataFrame with proportions of crimes by category and year.
        visible_categories: Optional set of categories to show.
    Returns:
        A plotly Figure.
    '''
    
    years = pct.index.tolist()
    categories = list(pct.columns)
    
    property_categories = [c for c in categories if c not in VIOLENT]
    violent_categories = [c for c in categories if c in VIOLENT]
    ordered_categories = property_categories + violent_categories
    
    fig = go.Figure()
    
    for cat in ordered_categories:
        is_violent = cat in VIOLENT
        color = COLORS.get(cat, THEME['font_color'])
        visible = True if visible_categories is None else (cat in visible_categories)
        
        fig.add_trace(go.Scatter(
            x=years,
            y=pct[cat].tolist(),
            mode='lines+markers',
            name=LABELS.get(cat, cat),
            legendgroup='violent' if is_violent else 'biens',
            legendgrouptitle=dict(
                text='Crimes violents' if is_violent else 'Crimes contre les biens',
                font=dict(family='Space Mono, monospace', size=11,
                          color=COLOR_VIOLENT if is_violent else COLOR_PROPERTY),
            ),
            line=dict(
                color=color,
                width=3 if is_violent else 2,
                dash='solid' if is_violent else 'dot',
            ),
            marker=dict(size=6, color=color),
            visible=True if visible else 'legendonly',
            hovertemplate=(
                f'<b>{LABELS.get(cat, cat)}</b><br>'
                '%{x}: %{y:.1f} %<extra></extra>'
            )
        ))
        
    fig.update_layout(
        template='custom',
        title=dict(
            text='<b>Tendances des crimes à Montréal</b> (2015-2025)',
            font=dict(family='Space Mono, monospace', size=16, color=THEME['font_color']),
            x=0.5,
            xanchor='center',
        ),
        font=dict(family='Space Mono, monospace', color=THEME['font_color']),
        xaxis=dict(
            title='Année',
            tickvals=years,
            ticktext=[str(y) for y in years],
            tickfont=dict(family='Space Mono, monospace', size=11),
            showgrid=False,
        ),
        yaxis=dict(
            title=dict(
                text='Pourcentage (%)',
                font=dict(family='Space Mono, monospace', size=12),
            ),
            ticksuffix=' %',
            range=[0, 50],
            tickfont=dict(family='Space Mono, monospace', size=11),
            gridcolor='rgba(0,0,0,0.08)',
        ),
        legend=dict(
            title=dict(
                text='Cliquez pour filtrer<br>',
                font=dict(family='Space Mono, monospace', size=12, color='#921F2E'),
            ),
            font=dict(family='Space Mono, monospace', size=11),
            orientation='v',
            yanchor='middle', y=0.5,
            xanchor='left',  x=1.02,
            tracegroupgap=16,
            groupclick='toggleitem',
        ),
        hovermode='x unified',
        plot_bgcolor=THEME['background_color'],
        paper_bgcolor=THEME['background_color'],
        height=520,
        margin=dict(r=200, t=60, l=80, b=40),
    )
 
    return fig

def create_layout(pct):
    return html.Div(style={'padding': '20px 0'}, children=[
        html.Div(
            **{'aria-label': 'Graphique en courbes des tendances de proportion de chaque catégorie de crime à Montréal entre 2015 et 2025. L\'axe vertical représente le pourcentage de chaque catégorie sur le total annuel des infractions. Les crimes contre les biens (introduction, méfait, vol dans ou sur véhicule, vol de véhicule) sont en pointillés ; les crimes violents (vols qualifiés, infractions entraînant la mort) sont en trait plein. La proportion d\'introductions par effraction a fortement augmenté entre 2019 et 2023. Utilisez les boutons sous le graphique pour filtrer par groupe.'},
            role='img',
            children=[
                dcc.Graph(
                    id='tendances-line-chart',
                    figure=get_figure(pct),
                    config=dict(
                        scrollZoom=False,
                        showTips=False,
                        displayModeBar=False,
                    ),
                )
            ],
        ),
        html.Div(
            style={
                'display': 'flex',
                'justifyContent': 'center',
                'marginTop': '12px',
                'gap': '12px',
            },
            children=[
                html.Button('Tous', id='tendances-btn-all', n_clicks=0),
                html.Button('Crimes contre les biens', id='tendances-btn-property', n_clicks=0),
                html.Button('Crimes violents', id='tendances-btn-violent', n_clicks=0),
            ],
        ),
    ])
    
def register_callbacks(app, pct):
    cats = list(pct.columns)
 
    property_categories = {c for c in cats if c not in VIOLENT}
    violent_categories  = {c for c in cats if c in VIOLENT}
 
    @app.callback(
        Output('tendances-line-chart', 'figure'),
        Output('tendances-btn-all', 'style'),
        Output('tendances-btn-property', 'style'),
        Output('tendances-btn-violent', 'style'),
        Input('tendances-btn-all', 'n_clicks'),
        Input('tendances-btn-property', 'n_clicks'),
        Input('tendances-btn-violent', 'n_clicks'),
    )
    def update_chart(n_all, n_property, n_violent):
        from dash import ctx
 
        btn_base = {
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
            'fontWeight': 'bold',
        }
        btn_active = {
            **btn_base,
            'backgroundColor': THEME['font_color'],
            'color': THEME['background_color'],
        }
 
        triggered = ctx.triggered_id
 
        if triggered == 'tendances-btn-property':
            return (get_figure(pct, visible_categories=property_categories),
                    btn_base, btn_active, btn_base)
        elif triggered == 'tendances-btn-violent':
            return (get_figure(pct, visible_categories=violent_categories),
                    btn_base, btn_base, btn_active)
        else:
            return (get_figure(pct),
                    btn_active, btn_base, btn_base)
        