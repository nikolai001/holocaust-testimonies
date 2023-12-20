import pandas as pd
import dash
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import plotly.express as px

app = dash.Dash(__name__)

data = pd.read_csv('volcanos.csv', encoding='utf-8')

types = data['primary_volcano_type'].unique()
type_options = [{'label': i, 'value': i} for i in types]
type_options.append({'label': 'All Volcano Types', 'value': 'all'})

mintime = data['last_eruption_year'].min()
#//500*500-500
maxtime = data['last_eruption_year'].max()
#//500*500+500

app.layout = html.Div([
                 html.H1(children="The World's Volcanos",
                         style = {'textAlign':'center', 'font-family' : 'Roboto'}),        
                 html.Div(dcc.Dropdown(
                        id='volcano_types',
                        options=type_options,
                        value='all'
                 )),
                 html.Div([
                     html.Div([
                         dcc.Graph(id='volcano-map')
                     ],style={'width':'46%','display':'inline-block','vertical-align':'top','margin':'2%'}),
                     html.Div([
                         html.Div(id='wiki-info')
                     ],style={'width':'46%','display':'inline-block','vertical-align':'top','margin':'2%'})
                 ]),
                 html.Div([
                     dcc.RangeSlider(
                       id='volcano-dates',
                       min=mintime,
                       max=maxtime,
                       step=100,
                       value=[mintime,maxtime],
                       marks={i: str(i) for i in range(mintime, maxtime, 500)})
                 ])
])

@app.callback(
    Output(component_id='volcano-map', component_property='figure'),
    [
        Input(component_id='volcano_types', component_property='value'),
        Input(component_id='volcano-dates', component_property='value')
    ]
)
def update_output(volcano_type, volcano_date):
    mydata = data
    if volcano_type != 'all':
        mydata = data[data['primary_volcano_type'] == volcano_type]
    if volcano_date != [mintime,maxtime]:
        mydata = mydata[mydata['last_eruption_year'] >= volcano_date[0]]
        mydata = mydata[mydata['last_eruption_year'] <= volcano_date[1]]
    fig = px.scatter_mapbox(data_frame=mydata, 
                        lat="latitude",
                        lon="longitude",
                        hover_name="volcano_name",
                        hover_data=["primary_volcano_type","tectonic_settings"],
                        size=[1 for i in mydata['volcano_number']],
                        size_max=10,
                        zoom=0,
                        height=700,
                        mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":20,"b":0})
    return fig

@app.callback(Output('wiki-info','children'),
              [Input('volcano-map','clickData')])
def update_wiki(click_data):
    url = "https://en.wikipedia.org/wiki/Volcano"
    if click_data != None:
        url = "https://en.wikipedia.org/wiki/"+click_data['points'][0]['hovertext'].replace(" ","_")
    return [
        html.Iframe(src=url,style={'width':'100%','height':'700px','display':'inline-block'})
    ]

if __name__ == '__main__':
    app.run_server(debug=False, port=8080)