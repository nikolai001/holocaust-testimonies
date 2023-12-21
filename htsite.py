import osimport reimport dashfrom dash import dcc, htmlfrom dash.dependencies import Input, Output  # Import Input and Output classesimport pandas as pdimport plotly.express as px# Read the data from the CSV file for the interactvie mapfreq_Cord_df = pd.read_csv('final_df.csv')protocol_df = pd.read_csv('testimonies_clean.csv')# Directory where testimonies are storedtestimonies_directory = r'testimonies/'# List all files in the directorytestimonies_files = [f for f in os.listdir(testimonies_directory) if f.endswith('.txt') and f.startswith('Protocol_Nr_')]# Create dfcolumns = ['protocol_number', 'content']testimonies_data = pd.DataFrame(columns=columns)# appendfor file_name in testimonies_files:    protocol_number = int(file_name.split('_')[2].split('.')[0])    file_path = os.path.join(testimonies_directory, file_name)    with open(file_path, 'r', encoding='utf-8') as file:        content = file.read()        testimonies_data = testimonies_data.append({'protocol_number': protocol_number, 'content': content},                                                   ignore_index=True)# Load stopwordswith open('stopwords.txt', 'r', encoding='utf-8') as stopword_file:    stopwords = stopword_file.read().split('\n')# Create a Dash app instanceapp = dash.Dash(__name__)# App Layoutapp.layout = html.Div(    children=[        html.H1(style={'background-color': '#121212', 'textAlign': 'center', 'font-family': 'Roboto', 'color': 'white'},                children='Holocaust Testimonies'),        # Parent div        html.Div([            # Search bar            html.Div([                dcc.Input(id='keyword-input', type='text', value=''),                html.Button('Search', id='search-button-sentences'),                html.Div(id='search-results-sentences'),            ], style={'width': '45%', 'height': '400px', 'display': 'block', 'margin': '5%', 'overflow': 'scroll'}),            # Scatter map            html.Div([                dcc.Graph(                    id='scatter-map',                    figure=px.scatter_mapbox(                        freq_Cord_df,                        lat='Latitude',                        lon='Longitude',                        size='total_freq',                        color='place_type',                        text='Place',                        color_discrete_map={'place_of_birth': 'blue', 'ghetto': 'green', 'camps': 'red'},                        zoom=4,                        center=dict(lat=48.4421119, lon=22.7185408),                        title='Map of Places',                        size_max=30                    ).update_layout(  # change map layout                        mapbox_style='open-street-map',                        title_font=dict(size=24, family='Arial', color='white'),                        title_x=0.5,                        title_y=0.95,                        paper_bgcolor='white'                    ).update_layout(  # change legend layout                        legend=dict(                            title=dict(text='Place Type', font=dict(size=24, color='darksalmon')),                            font=dict(size=20),                        )),                    style={'width': '100%', 'height': '800px', 'display': 'block', 'vertical-align': 'top',                           'margin': '2%'})            ], style={'width': '50%', 'display': 'flex', 'flex-direction': 'row'}),  # Adjust the width here            # Protocol summary from click_data            html.Div([                html.Div(id='protokol-output',                         style={'width': '45%', 'display': 'block', 'margin': '5%', 'overflow': 'scroll'}),            ], style={'width': '50%', 'display': 'flex', 'flex-direction': 'row'}),  # Parent container        ]),    ])@app.callback(    Output('search-results-sentences', 'children'),    [Input('search-button-sentences', 'n_clicks')],    [dash.dependencies.State('keyword-input', 'value')])def update_search_results_sentences(n_clicks, keyword):    if not keyword:        return html.Div("Please enter a keyword and click search to find the textual summary and testimonies.")    # Split the keyword into words, filter out stopwords, and convert to lowercase    keyword_words = [word.lower() for word in re.sub('[^a-z ]', '', keyword.lower()).split() if word.lower() not in stopwords]    # Check if the filtered keyword is empty after removing stopwords    if not keyword_words:        return html.Div("Please try a different keyword.")    result = []    for index, row in testimonies_data.iterrows():        content = row['content']        protocol_number = row['protocol_number']        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content)        matching_sentences = [            {'protocol_number': protocol_number, 'sentence': s}            for s in sentences            if any(word in s.lower() for word in keyword_words)        ]        if matching_sentences:            result.append(html.Div([                html.H3(f"Testimony {protocol_number}"),                *[html.P(f"Protocol {item['protocol_number']}: {item['sentence']}") for item in matching_sentences]            ]))    if not result:        return html.Div(f"No matching sentences found for '{keyword}'.")    return result# Your existing callback for scatter-map clickData@app.callback(Output('protokol-output', 'children'), [Input('scatter-map', 'clickData')])def display_protokols_on_click(click_data):   # Initialize an empty string for output_text   output_text = ""   print(f"Click Data: {click_data}")   if click_data == None:       Start_text = 'Press on a dot, to get protocols for that dot'       return Start_text   if click_data is not None:       # Extract the clicked place from the click_data       clicked_place = click_data['points'][0]['text']       # Initialize an empty list to store matching protocols       matching_protocols = []       # Iterate through each row in the protocol_df DataFrame       for index, row in protocol_df.iterrows():           # Check if the clicked place matches any of the columns           if pd.isna(row['place_of_birth']) or pd.isna(row['ghetto']) or pd.isna(row['camps']):               continue           places_of_birth = row['place_of_birth'].split(', ')           ghettos = row['ghetto'].split(', ')           camps = row['camps'].split(', ')           if clicked_place in places_of_birth or clicked_place in ghettos or clicked_place in camps:               matching_protocols.append(row['protocol'])       # Format the output text       if matching_protocols:           output_text = f"Protocols for {clicked_place}: {', '.join(map(str, matching_protocols))}"       else:           output_text = f"No specific protocols found for {clicked_place}."   return output_text# Run the app with host and port specifiedif __name__ == '__main__':    app.run_server(debug=True)