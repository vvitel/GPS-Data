from dash import Dash
from folder_code.dash_code.callbacks import *
from folder_code.dash_code.layout import *
from folder_code.processing_code.dash_functions import *

#parcourir les dossiers
data_path = "./data"
date_dic, match_dic, joueur_dic, df_files = get_path_select(data_path)

#récupérer le front
front = create_layout(date_dic, match_dic, joueur_dic)

#code de l'application
app = Dash(__name__)
server = app.server
app.layout = front

if __name__ == '__main__':
    app.run(debug=True, dev_tools_hot_reload=False)

