# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'}
                                    ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                ),
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={i: f'{i} Kg' for i in range(0, 10001, 2500)},
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),

                                # TASK 5: Tarefa extra - definir payload ranges de maior e menor sucesso de lançamento
                                html.Div(id='success-rate-summary', style={'font-size': '20px', 'font-weight': 'bold', 'margin-top': '20px'}),

                                html.Div(id='booster-success-rate', style={'font-size': '20px', 'font-weight': 'bold', 'margin-top': '20px'}),


                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',
            title='Total Success Launches for All Sites'
        )
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(
            filtered_df,
            names='class',
            title=f"Total Success and Failure Launches for Site {entered_site}"
        )
        return fig                                

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]

    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for All Sites'
        )
    else:
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for Site {selected_site}'
        )
    
    return fig

# TASK 5: Tarefa extra - definir payload ranges de maior e menor sucesso de lançamento
@app.callback(
    Output(component_id='success-rate-summary', component_property='children'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def calculate_success_rate_summary(selected_site, payload_range):
    # Filtrar o DataFrame com base no intervalo de payload
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    # Se um site específico foi selecionado, filtrar os dados por site
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Criar grupos de faixas de payload
    bins = [0, 2000, 4000, 6000, 8000, 10000]  # Dividir em faixas de 2000 kg
    labels = ['0-2000 kg', '2000-4000 kg', '4000-6000 kg', '6000-8000 kg', '8000-10000 kg']
    filtered_df['Payload Range'] = pd.cut(filtered_df['Payload Mass (kg)'], bins=bins, labels=labels, include_lowest=True)
    
    # Calcular a taxa de sucesso por faixa de payload
    success_rates = filtered_df.groupby('Payload Range')['class'].mean()
    
    # Encontrar a faixa com a maior e menor taxa de sucesso
    highest_rate_range = success_rates.idxmax()  # Faixa com maior taxa de sucesso
    highest_rate = success_rates.max()          # Maior taxa de sucesso
    
    lowest_rate_range = success_rates.idxmin()  # Faixa com menor taxa de sucesso
    lowest_rate = success_rates.min()          # Menor taxa de sucesso
    
    # Retornar o resultado como texto
    return (
        f"The payload range with the highest success rate is {highest_rate_range} "
        f"with a success rate of {highest_rate:.2%}. "
        f"The payload range with the lowest success rate is {lowest_rate_range} "
        f"with a success rate of {lowest_rate:.2%}."
    )

# Task 6
@app.callback(
    Output(component_id='booster-success-rate', component_property='children'),
    [
        Input(component_id='site-dropdown', component_property='value')
    ]
)
def calculate_best_booster(selected_site):
    # Filtrar os dados pelo site selecionado, se aplicável
    if selected_site != 'ALL':
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
    else:
        filtered_df = spacex_df
    
    # Calcular a taxa de sucesso por Booster Version
    success_rates = filtered_df.groupby('Booster Version')['class'].mean()
    
    # Encontrar o Booster com a maior taxa de sucesso
    highest_rate_booster = success_rates.idxmax()  # Nome do Booster
    highest_rate = success_rates.max()            # Taxa de sucesso
    
    # Formatar e retornar o resultado
    return (
        f"The F9 Booster version with the highest success rate is {highest_rate_booster} "
        f"with a success rate of {highest_rate:.2%}."
    )


# Run the app
if __name__ == '__main__':
    app.run_server()
