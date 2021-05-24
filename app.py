import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Output, Input
#need prod WSGI server settings, currently PythonAnywhere does this
#import gunicorn

# Read in new .CSV file, commenting out locations for remote platforms
#df = pd.read_csv("/home/SlappyWhite/homeless/data/Homeless_Pop.csv")
#df = pd.read_csv("data\Homeless_Pop.csv") #On Windows machine
df = pd.read_csv("data/homeless_Pop.csv") #On Mac machine

mark_values =  {2009: '2009', 2010: '2010',2011: '2011',2012: '2012',2013: '2013',2014: '2014',
				2015: '2015',2016: '2016',2017: '2017',2018: '2018'}

app = dash.Dash(__name__)

server = app.server
app.title = "Homelessness"

app.layout = html.Div(
    [
        html.Div(
            html.H1("Homeless Populations", className="header-title"),
            className="header"
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("State", className="menu-title"),
                        dcc.Dropdown(
                            id="state",
                            options=[{'label': m, 'value': m} for m in sorted(df.state.unique())],
                            placeholder="Search for a region",
							value="California",
                            multi=False,
                            clearable=True,
                            className="dropdown"
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("County", className="menu-title"),
                        dcc.Dropdown(id="filtered_counties",options=[],placeholder="Search counties",value=[],multi=False,className="dropdown"),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Population", className="menu-title"),
                        dcc.Dropdown(
                            id="type-filter",
                            options=[{"label": pop_type, "value": pop_type} for pop_type in df.pop_type.unique()],
                            value="Total Homeless",
                            multi=False,
                            clearable=True,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
            ],
            className="menu",
        ),
        html.Div(
            [
                html.Div(
					dcc.Graph(id="PIT-chart",config={"displayModeBar": True}),
					className="card",
				),
				html.Label("Date Range", className="menu-title"),
				dcc.RangeSlider(
				    id='year-slider',
				    min=2009,
				    max=2018,
				    step=1.0,
				    value=[2009, 2018],
				    allowCross=False,
				    marks=mark_values,
			 	),
			],
            className="wrapper",
        ),
    ]
)

#Populate the options of counties dropdown based on state dropdown
@app.callback(
    Output('filtered_counties','options'),
    Input('state','value')
)
def set_county_options(chosen_state):
	dff = df[df.state == chosen_state]
	return [{'label': c, 'value': c} for c in sorted(dff.county_name.unique())]

# Populate initial values of counties dropdown
@app.callback(
    Output('filtered_counties','value'),
    Input('filtered_counties','options')
)
def set_counties_value(county_options):
	return [x['value'] for x in county_options]

# Populate the graph with user input data
@app.callback(
    Output('PIT-chart', 'figure'),
	Input('state', 'value'),
	Input('filtered_counties', 'value'),
    Input('type-filter', 'value'),
	Input('year-slider',  'value')
)
def update_charts(selected_state, selected_counties, pop_type, year_range):
	if len(selected_counties) == 0:
		return dash.no_update
	else:
		dff = df[
			(df.state == selected_state)
			& (df.county_name.isin([selected_counties]))
			& (df.pop_type == pop_type)
			& (df.year >= year_range[0])
			& (df.year <= year_range[1])
		]

		PIT_count_figure = {
	        "data": [
	            {
	                "x": dff["year"],
	                "y": dff["pop_size"],
	                "type": "lines",
	                "hovertemplate": "%{y:.2f}<extra></extra>",
	            },
	        ],
	        "layout": {
	            "title": {
	                "text": "Point-in-Time Counts",
	                "x": 0.05,
	                "xanchor": "left",
	            },
	            "xaxis": {"fixedrange": True},
	            "yaxis": {"fixedrange": True},
	            "colorway": ["#17B897"],
	        }
	    }
		return PIT_count_figure #volume_chart_figure

if __name__ == "__main__":
    app.run_server(debug=True)
