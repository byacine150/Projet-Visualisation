# -*- coding: utf-8 -*-

'''
    File name: app.py
    Course: INF8808
    Python Version: 3.8

    This file is the entry point for our Dash app.
'''

import os

import dash
from dash import html, dcc
import pandas as pd

import preprocess
from visualisations import vis_borough, vis_crime_rate, vis_crimes_season, vis_time_of_day, vis_trends
from template import create_template


app = dash.Dash(__name__)
app.title = 'Crimes Mtl'
app.index_string = '''
<!DOCTYPE html>
<html lang="fr">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

csv_path = os.path.join(os.path.dirname(__file__), 'assets', 'data', 'actes-criminels.csv')
df= pd.read_csv(csv_path)
df_pdq = preprocess.prepare_pdq_data(df)
df_crime_rate = preprocess.prepare_crime_rate_data(df)
df_monthly = preprocess.prepare_monthly_crime_data(df)
df_moment = preprocess.prepare_moment_journee_data(df)
df_tendances = preprocess.prepare_tendances_data(df)

create_template()

app.layout = html.Div(className='app-container', children=[
    html.Header(className='app-header', children=[
        html.Div(className='header-title-row', children=[
            html.Img(src='/assets/favicon.ico', className='header-favicon', alt=''),
            html.H1('Les crimes à Montréal', className='header-title'),
        ]),
        html.H2('Évolution et tendances des infractions', className='header-subtitle')
    ]),

    html.Div(className='main-container', children=[
        html.Aside(className='sidebar', children=[
            html.Nav(className='sidebar-nav', children=[
                html.Ul(children=[
                    html.Li(html.A('Introduction',            href='#introduction-anchor',     className='nav-link')),
                    html.Li(html.A('Crimes par année',            href='#crimes-year-anchor',     className='nav-link')),
                    html.Li(html.A('Crimes par saison',        href='#crimes-period-anchor', className='nav-link')),
                    html.Li(html.A('Crimes par Arrondissement', href='#crimes-district-anchor', className='nav-link')),
                    html.Li(html.A('Crimes par moment de la journée', href='#crimes-moment-anchor', className='nav-link')),
                    html.Li(html.A('Tendances des crimes', href='#crimes-tendances-anchor', className='nav-link')),
                    html.Li(html.A('Conclusion',           href='#conclusion-anchor',      className='nav-link')),
                    html.Li(html.A('Références', href='#sources-anchor', className='nav-link')),
                ])
            ])
        ]),

        html.Main(className='main-content', children=[
            html.Section(id='introduction', className='graph-section', children=[
                html.Div(id='introduction-anchor', className='section-anchor'),
                html.H3('Introduction'),
                html.Div(className='intro-container', children=[
                    html.P("La criminalité est un enjeu majeur pour la sécurité publique de Montréal. La criminalité et la sécurité ont justement été abordés lors des dernières élections municipales de la ville de Montréal. [1] Les partis étaient tous en accord d’avoir une approche plus ferme. Pourtant, les statistiques récentes démontrent une baisse de criminalité au Canada, incluant Montréal. L’analyse des phénomènes de hausse et de baisse est donc considérable. Cela permettrait de  mieux comprendre les dynamiques sociales et économiques qui pourraient influencer les comportements criminels.[2] "),
                    html.P("Dans ce contexte, notre projet s’intéresse principalement à l’évolution temporelle des taux de criminalité à Montréal ainsi que leur répartition géographique. Avec l’aide des techniques de visualisation de données, nous voulons mettre en évidence les tendances des infractions dans la région."),
                    html.P(html.B("La question centrale de ce projet est 'À quoi ressemble le crime à Montréal ?'.")),
                ])
            ]),

            html.Section(id='crimes-year', className='graph-section', children=[
                html.Div(id='crimes-year-anchor', className='section-anchor'),
                html.H3('Crimes par année'),
                html.Div(className='viz-container', children=[
                    html.P('''Le graphe ici représente le nombre de crimes par 100 000 habitants à Montréal de 2015 à 2024, répartis par catégorie d\'infraction.
                    Il permet d\'observer les tendances générales de la criminalité au fil du temps, ainsi que les variations spécifiques à chaque type d\'infraction. 
                    En analysant ce graphique, on peut identifier les périodes de hausse ou de baisse de la criminalité, ainsi que les catégories d\'infractions qui ont le plus évolué au cours de cette période.
                    De plus, en mettant en évidence l'évolution des crimes, il est plus facile de visualiser les causes durant certaines périodes et si le problème s'est aggravé.'''),
                    vis_crime_rate.create_layout(df_crime_rate),
                    html.P('''La première chose que l’on remarque à l’aide de ce graphique est que le nombre total d'infractions commises à Montréal a évolué drastiquement et on peut constater plusieurs phases distinctes entre les années 2015 et 2025. Tout d’abord, les données montrent que la criminalité générale a grandement baissé à partir de 2015 et ce, jusqu’à 2020. Cela est probablement dû à la pandémie qui a fait que les crimes ont baissé pour tous les types d’infractions puisque les gens étaient tous confinés. Puis, à partir de 2021, le nombre total d'infractions à fortement commencé à augmenter pour ensuite atteindre un maximum en 2023 avant de diminuer jusqu’en 2025.'''),
                    html.P('''On observe aussi qu’il y a un pic inhabituel pour les vols de véhicules à moteur entre 2022 à 2024 alors que d’habitude le nombre de types de crime était relativement stable sur les autres années. Cette augmentation des vols de voiture à Montréal est notamment causée par les réseaux criminels organisés qui ciblent l’exportation des voitures via le port de Montréal ainsi qu’à cause de la pénurie de véhicule suite à la pandémie et l’avancement des technologies de clonage de clés de voiture.'''),
                ])
            ]),

            html.Section(id='crimes-category', className='graph-section', children=[
                html.Div(id='crimes-period-anchor', className='section-anchor'),
                html.H3('Crimes par saison'),
                
                html.Div(className='viz-container', children=[
                    html.P('''Par après, il est aussi pertinent de se poser la question si les saisons ont font une différence dans le taux de crimes à Montréal. En effet, on peut se demander si les mois d’été sont plus propices à la criminalité que les mois d’hiver. Le graphique ci-dessous permet de répondre à cette question en montrant le nombre total de crimes commis à Montréal par mois pour chaque année entre 2015 et 2024.'''),
                    vis_crimes_season.create_layout(df_monthly),
                    html.P('''Il y a une plus grande abondance des crimes que l’on peut observer en général entre les mois d’avril/mai jusqu’à octobre/novembre. Les périodes hivernales sont les périodes qui représentent le moins de criminalité. '''),
                    html.P('''Nous pouvons conclure que lorsqu’il commence à faire plus chaud, les gens sortent davantage et participent à plus d’événements. Par exemple, aller au parc, festivals, terrasses, etc. Il y a donc une augmentation des interactions sociales, alors il y a plus d’occasions de conflits, de vols, etc. Ce qui est contraire pour l’hiver où il risque que les gens aient plus tendance à rester à la maison et avoir moins d'interactions. '''),
                    html.P('''Selon une étude aussi, les températures plus chaudes peuvent représenter une agressivité plus grande et augmenter les conflits interpersonnels. Cela peut aussi expliquer l’augmentation des crimes violents durant les mois les plus chauds comme des pics en été où des vagues de chaleur sont plus propices. ''')
                ])
            ]),

            html.Section(id='crimes-district', className='graph-section', children=[
                html.Div(id='crimes-district-anchor', className='section-anchor'),
                html.H3('Crimes par Arrondissement'),
                html.Div(className='viz-container viz-container--map', children=[
                    html.P('''Au-delà des tendances temporelles, il est pertinent de se demander si les crimes sont répartis uniformément sur le territoire montréalais ou s'ils se concentrent dans certains quartiers. En examinant la distribution spatiale des infractions par Poste de Quartier (PDQ) du SPVM, on peut mieux comprendre quelles zones sont les plus touchées et si cette répartition varie selon le type de crime.'''),
                    vis_borough.create_layout(df_pdq),
                    html.P('''On constate que les crimes sont fortement concentrés dans les PDQ du centre-ville et des quartiers centraux, là où la densité de population et l'activité humaine sont les plus élevées. Ce phénomène rejoint l'observation du criminologue Rémi Boivin : « Les cartes du crime, ce sont des cartes de l'activité humaine. » En effet, les zones à forte fréquentation comme les commerces, transports et lieux de divertissement sont naturellement associées à une criminalité plus importante.'''),
                    html.P('''En revanche, les vols de véhicules à moteur présentent une distribution plus uniforme à travers l'île, sans se concentrer exclusivement au centre. Ce type d'infraction cible davantage les voitures stationnées dans les quartiers résidentiels, ce qui explique sa répartition plus homogène sur l'ensemble du territoire montréalais.'''),
                ])
            ]),

            html.Section(id='crimes-moment', className='graph-section', children=[
                html.Div(id='crimes-moment-anchor', className='section-anchor'),
                html.H3('Crimes par moment de la journée'),
                html.Div(className='viz-container', children=[
                    html.P('''Il est naturel d'associer la criminalité à la nuit, mais les données montréalaises révèlent une réalité différente. Le graphique ci-dessous présente le nombre total d'infractions par catégorie de crime, réparties selon trois moments de la journée: jour, soir et nuit. Les catégories sont ordonnées de la plus fréquente à la moins fréquente pour mettre en évidence les infractions les plus courantes.'''),
                    vis_time_of_day.create_layout(df_moment),
                    html.P('''On constate que la majorité des crimes surviennent pendant le jour, ce qui peut aller à l'encontre de l'intuition. Cela s'explique par le fait que les infractions les plus courantes, comme les vols dans ou sur véhicule à moteur, surviennent dans des espaces publics fréquentés pendant la journée. La seule grosse exception c'est les vols qualifiés, qui sont plus fréquents le soir.'''),
                    html.P('''Les crimes contre la propriété sont beaucoup plus nombreux que les crimes contre la personne, pour n'importe quel moment de la journée. Les vols dans ou sur véhicule à moteur représentent l'infraction la plus fréquente, tandis que les infractions entraînant la mort sont les moins nombreuses. Même en filtrant uniquement les crimes de nuit, les crimes contre la proprité restent les plus nombreux, avec les vols de voitures comme les plus nombreux.'''),
                ])
            ]),
            
            html.Section(id='crimes-tendances', className='graph-section', children=[
                html.Div(id='crimes-tendances-anchor', className='section-anchor'),
                html.H3('Tendances des crimes'),
                html.Div(className='viz-container', children=[
                    html.P('''Ensuite, il serait pertinent de voir si certains types de crimes sont plus populaires que les autres et si certains crimes suivent une tendance différente par rapport aux autres. Le graphique ci-dessous montre l'évolution de la proportion de chaque catégorie d'infraction par rapport au nombre total de crimes commis à Montréal pour chaque année. '''),
                    vis_trends.create_layout(df_tendances),
                    html.P('''Avec le graphique, on peut voir qu'en général, chaque type de crime a tendance à garder une proportion similaire à travers les années. Toutefois, nous pouvons voir que la proportion d'introduction par effraction monte considérablement entre les années 2019 et 2023 avant de redescendre durant les deux prochaines années. La hausse pourrait certainement être liée à la pandémie en raison d'une diminution de gens dans les commerces par exemple. Pour la baisse, le Gouvernement du Canada a annoncé des lois concernant les peines plus sévères sur plusieurs types de crime incluant les introductions par effraction.'''),
                    html.P('''Concernant la proportion de crimes violents comparé aux crimes contre les biens, nous pouvons voir que les crimes violents représentent une minorité de la totalité des crimes, ce qui est inférieur à la moyenne canadienne.'''),
                ])
            ]),

            html.Section(id='conclusion', className='graph-section', children=[
                html.Div(id='conclusion-anchor', className='section-anchor'),
                html.H3('Conclusion'),
                html.Div(className='conclusion-container', children=[
                    html.P("À travers les angles différents qui ont été explorés, un portrait nuancé de la criminalité montréalaise est représentée."),
                    html.P("Sur le plan temporel, la criminalité a suivi une trajectoire de baisse jusqu'en en 2020 et une forte remontée en 2023. Cela peut être attribué aux confinements lors de la pandémie. Cela nous rappelle que la criminalité est étroitement liée aux conditions sociales et économiques du moment. "),
                    html.P("Les données saisonnières confirment un effet estival assez constant. Les mois de mai à octobre concentrent systématiquement le plus grand nombre d'infractions, quelle que soit l'année. Ce phénomène s'explique par l'intensification des activités extérieures et des interactions sociales lorsque les températures montent. Une réalité récurrente à chaque année"),
                    html.P("La distribution géographique révèle quant à elle que la criminalité n'est pas uniforme sur le territoire. Elle se concentre là où l'activité humaine est la plus dense, notamment dans les PDQ centraux. Les vols de véhicules sont une exception et sont tout aussi concentré dans les milieux résidentiels."),
                    html.P("Enfin, contrairement à l'intuition populaire, la grande majorité des infractions surviennent le jour. Les crimes contre la propriété dominent à toutes les heures, tandis que les vols qualifiés sont la seule catégorie plus fréquente en soirée. Les crimes violents demeurent une minorité et restent inférieurs à la moyenne montréalaise."),
                    html.P(html.B("En somme, le crime à Montréal est un phénomène de la vie urbaine quotidienne. Il suit le rythme des saisons, se concentre où les gens se rassemblent, et évolue selon les bouleversements sociaux. Comprendre ces tendances est la première étape pour y répondre efficacement.")),
                ])
            ]),

            html.Section(id='Sources', className='graph-section', children=[
                html.Div(id='sources-anchor', className='section-anchor'),
                html.H3('Références'),
                html.Div(className='sources-container', children=[
                    html.P("[1] “How do Montreal’s top mayoral candidates compare on election issues?,” CBC News, 2025. https://newsinteractives.cbc.ca/features/2025/montreal-municipal-election/#montreal-municipal-2025-traffic"),

                    html.P("[2] “Baisse de la criminalité au Canada et à Montréal, légère hausse au Québec,” La Presse, 22 juill. 2025. https://www.lapresse.ca/actualites/national/2025-07-22/statistique-canada/baisse-de-la-criminalite-au-canada-et-a-montreal-legere-hausse-au-quebec.php"),
                ])
            ]),
        ])
    ])
])

vis_borough.register_callbacks(app, df_pdq)
vis_crimes_season.register_callbacks(app, df)
vis_time_of_day.register_callbacks(app, df_moment)
vis_trends.register_callbacks(app, df_tendances)
