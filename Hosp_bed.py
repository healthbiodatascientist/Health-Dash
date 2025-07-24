from dash import Dash, html, dcc, Input, Output  # pip install dash
import plotly.express as px
import dash_ag_grid as dag
import dash_bootstrap_components as dbc   # pip install dash-bootstrap-components
import pandas as pd     # pip install pandas
import matplotlib      # pip install matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import gunicorn
year = input('Please enter the year that you want to view between 2014 and 2023') # input the year that you want to display
specialism = input('Please enter the specialism that you are interested in from the following list: Accident & Emergency, All Specialties, Allergy, Anaesthetics, Cardiology, Clinical Neurophysiology, Clinical Oncology, Clinical Radiology, Community Grouping, Dental Grouping, Dermatology, Diagnostics Grouping, Learning Disability Grouping, Medical Grouping, Medical Oncology, Mental Health Grouping, Midwifery, Neurology, Obstetrics Grouping, Paediattrics Grouping, Rehabilitation Medicine, Renal Medicine, Respiratory Medicine, Surgery Grouping, Women and Newborn Grouping')
df_hosp_beds = pd.read_csv('https://raw.githubusercontent.com/healthbiodatascientist/Health-Dash/refs/heads/main/beds_by_nhs_board-of-treatment_specialty.csv')
df_region = pd.read_csv('https://raw.githubusercontent.com/healthbiodatascientist/Health-Dash/refs/heads/main/Health_Boards_(Dec_2020)_Names_and_Codes_in_Scotland.csv')
df_filter = df_hosp_beds.loc[df_hosp_beds['SpecialtyName'] == specialism] # filter for A&E beds
df_filter_year = df_filter.loc[df_filter['FinancialYear'].str.startswith(year, na=False)] # filter for year
df_filternumber = df_filter_year.filter(items=['HB', 'AverageAvailableStaffedBeds', 'PercentageOccupancy', 'AllStaffedBeds', 'AverageOccupiedBeds', 'TotalOccupiedBeds']) # filter for values
df_filternumber = df_filternumber.set_index('HB')
df_hb_beds = df_filternumber.join(df_region.set_index('HB20CD'), on='HB') # join health board region names
df_hb_beds = df_hb_beds.dropna()
df_hb_beds = df_hb_beds.filter(items=['HB20NM', 'PercentageOccupancy', 'AverageAvailableStaffedBeds', 'AllStaffedBeds'])
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    html.H1([specialism, " Beds Available in Scottish Health Boards ", year], className='mb-2', style={'textAlign':'center'}),
    dbc.Row([dbc.Col([dcc.Dropdown(id='category', value='PercentageOccupancy', clearable=False, options=df_hb_beds.columns[1:]) ], width=4)]),
    dbc.Row([dbc.Col([html.Img(id='bar-graph-matplotlib')], width=12)]),
    dbc.Row([dbc.Col([dcc.Graph(id='bar-graph-plotly', figure={})], width=12, md=6),
             dbc.Col([dag.AgGrid(id='grid', rowData=df_hb_beds.to_dict("records"), columnDefs=[{"field": i} for i in df_hb_beds.columns], columnSize="sizeToFit",)], width=12, md=6),
             ], className='mt-4'),])
@app.callback(
    Output(component_id='bar-graph-matplotlib', component_property='src'),
    Output('bar-graph-plotly', 'figure'),
    Output('grid', 'defaultColDef'),
    Input('category', 'value'),
)

def plot_data(selected_yaxis):

    # Build the matplotlib figure
    fig = plt.figure(figsize=(14, 6), constrained_layout=True)
    plt.bar(df_hb_beds['HB20NM'], df_hb_beds[selected_yaxis], color='blue')
    plt.ylabel(selected_yaxis)
    plt.xticks(rotation=90)
    bar_container = plt.bar(df_hb_beds['HB20NM'], df_hb_beds[selected_yaxis])
    plt.bar_label(bar_container, fmt='{:,.0f}')

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig_bar_matplotlib = f'data:image/png;base64,{fig_data}'

    # Build the Plotly figure
    fig_bar_plotly = px.bar(df_hb_beds, x='HB20NM', y=selected_yaxis).update_xaxes(tickangle=330)

    my_cellStyle = {
        "styleConditions": [
            {
                "condition": f"params.colDef.field == '{selected_yaxis}'",
                "style": {"backgroundColor": "#d3d3d3"},
            },
            {   "condition": f"params.colDef.field != '{selected_yaxis}'",
                "style": {"color": "black"}
            },
        ]
    }

    return fig_bar_matplotlib, fig_bar_plotly, {'cellStyle': my_cellStyle}  
if __name__ == '__main__':
    app.run()