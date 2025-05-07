import dash_mantine_components as dmc
from dash import html

def create_layout(dic_date, dic_match, dic_joueur):
    return dmc.MantineProvider(
        forceColorScheme="dark",
        children=[
            dmc.Tabs(
                [
                    #création des panneaux
                    dmc.TabsList(
                        [
                            dmc.TabsTab("📈", value="tab_gps", style={"fontSize": "30px"}),
                            dmc.TabsTab("📽️", value="tab_video", style={"fontSize": "30px"}),
                        ]
                    ),
                    #panneau pour visualisation des données GPS
                    dmc.TabsPanel(
                        children=[
                            html.Br(),
                            dmc.Grid(
                                [
                                    #création des sélecteurs
                                    dmc.GridCol(
                                        children=[
                                            dmc.Badge("Choisir match", size="lg", radius="lg", color="blue"),
                                            dmc.Select(label="Date", id="select_date", data=dic_date, searchable=True, clearable=True, w=200),
                                            dmc.Select(label="Match", id="select_match", data=dic_match, searchable=True, clearable=True, w=200),
                                            html.Br(),
                                            dmc.Badge("Choisir joueur", size="lg", radius="lg", color="violet"),
                                            dmc.Select(label="Joueur", id="select_joueur", data=dic_joueur, searchable=True, clearable=True, w=200),
                                        ],
                                        span=2
                                    ),
                                    #visualisations graphiques
                                    dmc.GridCol(
                                        children=[
                                            dmc.Center(dmc.Title("Visualisation des données GPS", order=1, mt="lg")),
                                            #graphique en bar pour les distances parcourues
                                            dmc.Title("Distances parcourues par zone de vitesse", id="title_barplot", order=3, mt="lg", style={"display": "none"}),
                                            dmc.BarChart(id="barplot_dist", h=0, dataKey="", data=[], type="stacked", orientation="vertical", series=[], style={"display": "none"}),
                                            html.Br(),
                                            dmc.Group(children=[dmc.Title("Vitesses et accélérations maximales", id="title_scatterspeedaccel", order=3, mt="lg", style={"display": "none"}),
                                                                dmc.Title("Nombre d'accélération", id="title_nbaccel", order=3, mt="lg", style={"display": "none"})],
                                                      grow=True, justify="space-around"),
                                            dmc.Group(children=[dmc.ScatterChart(id="scatter_vitesse_accel", h=300, data=[], dataKey={"x": "vitesse", "y": "acceleration"}, xAxisLabel="Vitesse (km/h)", yAxisLabel="Accélération (m/s)", xAxisProps={"domain": [17, 30]}, yAxisProps={"domain": [2, 7]}, withLegend=True, legendProps={"verticalAlign": "bottom", "height": 10}, style={"display": "none"}),
                                                                dmc.BarChart(id="barplot_accel", h=400, dataKey="", data=[], type="stacked", orientation="vertical", series=[], withBarValueLabel=True, style={"display": "none"})],
                                                      grow=True),
                                            html.Br(),
                                            #donut pour repésenter note des joueuses
                                            dmc.Title("Comparaison niveau international", id="title_donut", order=3, mt="lg", style={"display": "none"}),
                                            html.Br(),
                                            dmc.Group(children=[dmc.DonutChart(id="donut_vmax", data=[], startAngle=180, endAngle=0, chartLabel="vitesse max.", style={"display": "none"}),
                                                                dmc.DonutChart(id="donut_amax", data=[], startAngle=180, endAngle=0, chartLabel="accélération max.", style={"display": "none"}),],
                                                      grow=False)],
                                        span=10
                                    ),
                                ]
                            ),
                        ],
                        value="tab_gps"
                    ),
                    #panneau pour visualisation des données vidéo
                    dmc.TabsPanel(
                        children=[
                            html.Br(),
                            dmc.Grid(
                                [
                                    #création des sélecteurs
                                    dmc.GridCol(
                                        children=[
                                            dmc.Badge("Choisir match", size="lg", radius="lg", color="blue"),
                                            dmc.Select(label="Date", id="select_date_video", data=dic_date, searchable=True, clearable=True, w=200),
                                            dmc.Select(label="Match", id="select_match_video", data=dic_match, searchable=True, clearable=True, w=200),
                                            html.Br(),
                                            dmc.Badge("Choisir joueur", size="lg", radius="lg", color="violet"),
                                            dmc.Select(label="Joueur", id="select_joueur_video", data=dic_joueur, searchable=True, clearable=True, w=200),
                                            html.Br(),
                                            dmc.Badge("Choisir métrique", size="lg", radius="lg", color="grape"),
                                            dmc.Select(label="Métrique", id="select_metrique_video", data=[{"value": "vitesse max.", "label": "vitesse max."}], searchable=True, clearable=True, w=200),
                                        ],
                                        span=2
                                    ),
                                    #ffichage de la vidéo
                                    dmc.GridCol(
                                        children=[
                                            dmc.Center(dmc.Title("Visualisation vidéo", order=1, mt="lg")),
                                            dmc.Center(html.Div([html.Video(id="html_video", src="", controls=True, width=960 , height=540, style={"display": "none"})]))
                                        ],
                                        span=10
                                    )
                                ]
                            ),
                        ],
                        value="tab_video"
                    ),
                ],
                color="blue",
                orientation="horizontal",
                variant="default",
                value="tab_gps"
            )
        ]
    )
