import pandas as pd
import json

# For downloading data
import urllib

import visdcc

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State

# model
from .german_credit import init, score

# Load pre-trained model
init()

# Reading local files
training_data = pd.read_json(
    "/app/data/training_data.json", lines=True, orient="records"
)
testing_data = pd.read_json("/app/data/testing_data.json", lines=True, orient="records")
input_data = pd.concat([training_data, testing_data])

# Setting custom css stylesheet
external_stylesheets = ["assets/custom_template.css"]

# Initializing app
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    external_scripts=["assets/custom-script.js"],
)


server = app.server
app.config.suppress_callback_exceptions = True

# Odd row highlighting and conditional coloring for tables
var_color_options = [
    {"if": {"row_index": "odd"}, "backgroundColor": "rgb(247, 247, 247)"},
    {
        "if": {"column_id": "Gender", "filter_query": "{Gender} eq female"},
        "backgroundColor": "#F9B341",
    },
    {
        "if": {"column_id": "Gender", "filter_query": "{Gender} eq male"},
        "backgroundColor": "#68C3D8",
    },
    {
        "if": {
            "column_id": "Age Over Forty?",
            "filter_query": "{Age Over Forty?} eq True",
        },
        "backgroundColor": "#FE6666",
    },
    {
        "if": {
            "column_id": "Age Over Forty?",
            "filter_query": "{Age Over Forty?} eq False",
        },
        "backgroundColor": "#66FE9D",
    },
]

# CSS style for table cells
table_cell_style = {
    "textAlign": "left",
    "fontSize": 12,
    "paddingLeft": "1ch",
    "paddingRight": "1ch",
}

# Raw feature names as used in model
raw_feature_names = [
    "id",
    "age_over_forty",
    "gender",
    "duration_months",
    "credit_amount",
    "installment_rate",
    "present_residence_since",
    "number_existing_credits",
    "number_people_liable",
    "checking_status",
    "credit_history",
    "purpose",
    "savings_account",
    "present_employment_since",
    "debtors_guarantors",
    "property",
    "installment_plans",
    "housing",
    "job",
    "telephone",
    "foreign_worker",
]

# Corresponding legible feature names
features = [
    "ID",
    "Age Over Forty?",
    "Gender",
    "Duration (months)",
    "Credit Amount",
    "Installment Rate",
    "Present Residence Since",
    "Number of Existing Credits",
    "Number of People Liable",
    "Checking Status",
    "Credit History",
    "Purpose",
    "Savings Account",
    "Present Employment Since",
    "Debtors Guarantors",
    "Property",
    "Installment Plans",
    "Housing",
    "Job",
    "Telephone",
    "Foreign Worker",
]

numerical_features = [
    "duration_months",
    "credit_amount",
    "installment_rate",
    "present_residence_since",
    "number_existing_credits",
    "number_people_liable",
]

categorical_features = [
    "checking_status",
    "credit_history",
    "purpose",
    "savings_account",
    "present_employment_since",
    "debtors_guarantors",
    "property",
    "installment_plans",
    "housing",
    "job",
    "telephone",
    "foreign_worker",
    "gender",
    "age_over_forty",
]

# Map between raw and legible feature names
feature_name_map = {raw_feature_names[i]: features[i] for i in range(0, len(features))}

feature_name_map_reverse = {k: v for v, k in feature_name_map.items()}

# A message to be displayed when scoring is not applicable
not_applicable_message = html.P(
    children=[
        html.Strong("Logistic Regession Prediction: "),
        html.Span("N/A"),
        html.P("\u00A0"),
        html.Strong("Probability of Default: "),
        html.Span("N/A"),
    ]
)
# Dash app title (this can be different from the visible header below)
app.title = "A Dash Demo Model using German Credit Data"

# Layout of Dash app
app.layout = html.Div(
    [
        # Header
        html.H3(
            children=[
                html.Img(
                    src="assets/gauss.jpg",
                    height="16px",
                    style={"padding-top": 3, "margin-bottom": -2},
                ),
                "\u00A0\u00A0",
                "A Dash Demo Model using German Credit Data",
            ]
        ),
        html.Div(id="login_info", children="super_user", style={"display": "none"}),
        # A div to display username
        html.Div(
            [html.H4("Logged in as: GaussTheBoss")],
        ),
        html.Div(
            [  # Toolbar
                html.Div(
                    [
                        html.Img(
                            src="assets/gauss.jpg",
                            height="45px",
                            style={"margin-right": 20},
                        ),
                        html.Div(
                            [  # Input field for id
                                html.H6("ID"),
                                dcc.Input(
                                    id="id",
                                    type="number",
                                    placeholder="e.g. 123",
                                    value=1,  # Default value
                                ),
                            ],
                            style={"margin-right": 10},
                        ),
                        html.Div(
                            [
                                html.H6(" "),
                            ]
                        ),
                        html.Button(  # A button to trigger scoring in FastScore
                            "Submit for Scoring", id="scoring_button"
                        ),
                        html.P("\u00A0"),
                        html.A(  # A link to download data generated post scoring
                            html.H5("Save Data"),  # H5 will appear as a button
                            id="download_data_link",
                            download="",
                            href="",
                            target="_blank",
                        ),
                    ],
                    className="NoSpaceBetween",
                )
            ],
            className="Toolbar",
        ),  # End of Toolbar
        html.Div(
            [  # Components below Toolbar
                # Displaying record corresponding to input in a DataTable
                dash_table.DataTable(
                    id="input_record_visual",
                    columns=[{"name": feat, "id": feat} for feat in features],
                    data=[],  # No data to display on loading
                    style_table={
                        "minWidth": "100%",  # cover entire width of div
                        "overflowX": "auto",
                    },
                    style_header={
                        "backgroundColor": "#03331E",
                        "fontSize": 12,
                        "color": "white",
                    },
                    style_cell=table_cell_style,
                    # Row and cell highlighting rules
                    style_data_conditional=var_color_options,
                    style_as_list_view=True,  # Removes vertical lines from table
                ),
                # Displaying output from model:
                # Closest records ad their attributes
                # + summary
                # + feedback area
                html.Details(
                    [
                        html.Summary(
                            "Closest Records",
                            style={"margin-top": 10, "margin-bottom": 10},
                        ),
                        html.Div(
                            [  # Collapsible content
                                # A table showing (up tp) closest 5 matches
                                dash_table.DataTable(
                                    id="matches_table",
                                    columns=[
                                        {"name": feat, "id": feat} for feat in features
                                    ]
                                    + [{"name": "Status", "id": "status"}],
                                    data=[],
                                    style_table={"minWidth": "100%"},
                                    style_header={
                                        "backgroundColor": "#03331E",
                                        "fontSize": 12,
                                        "color": "white",
                                    },
                                    style_cell=table_cell_style,
                                    style_data_conditional=var_color_options,
                                    # fixing first column through scroll
                                    fixed_columns={"headers": True, "data": 1},
                                    style_as_list_view=True,
                                ),
                                html.P(" "),
                            ]
                        ),
                    ],
                    open=True,
                ),  # Details div will be open by default
            ],
            className="Tables",
        ),
        html.Div(
            [
                # Showing prediction after scoring
                html.Div(
                    [
                        html.Div(
                            id="messages",
                            children=not_applicable_message,
                        )
                    ],
                    style={"margin-right": 15, "width": "30%"},
                ),
                html.Div(
                    [  # A div for ratings
                        html.H6(
                            "Rate this prediction:",
                            style={"margin-bottom": 10},
                        ),
                        dcc.Slider(
                            id="prediction_rating",
                            min=1,
                            max=5,
                            value=3,
                            step=1,
                            marks={i: str(i) for i in range(1, 6)},
                        ),
                    ],
                    style={
                        "margin-top": 5,
                        "margin-bottom": 25,
                        "margin-left": 25,
                        "margin-right": 25,
                        "width": "30%",
                    },
                ),
                html.Div(
                    [  # A div for feedback textarea & feedback button
                        dcc.Textarea(
                            id="feedback",
                            placeholder="Feedback",
                            style={
                                "width": "100%",
                                "min-height": 80,
                                "margin": 0,
                            },
                        ),
                        html.Div(
                            [
                                html.Button(
                                    "Submit Feedback",
                                    id="submit_feedback",
                                    style={"margin": 0},
                                )
                            ]
                        ),
                    ],
                    style={"width": "40%"},
                ),
            ],
            className="feedbackArea",
        ),
        # divs to store model outputs
        html.Div(id="prediction", style={"display": "none"}),
        html.Div(id="probability_of_default", style={"display": "none"}),
        html.Div(id="recordIDs", style={"display": "none"}),
        html.Div(
            id="input_record",
            style={"display": "none"},
            children="[loading]",
        ),
        # scroll to top
        html.Div(
            [html.Button("Top", id="TopButton"), visdcc.Run_js(id="javascript")],
            style={"margin-right": "1.5%", "margin-bottom": 15, "float": "right"},
        ),
        # <button onclick="topFunction()" id="myBtn" title="Go to top">Top</button>
    ]
)


@app.callback(Output("javascript", "run"), [Input("TopButton", "n_clicks")])
def myfun(x):
    if x:
        return "topFunction()"
    return ""


@app.callback(
    [
        Output("input_record", "children"),
        Output("input_record_visual", "data"),
    ],
    [Input("id", "value")],
)
def update_id(id):
    """

    :param id: record id
    :return: a record of input_feature_A + attributes (actual + visual)
    """

    try:
        record_info = input_data[input_data["id"] == id]
    except:
        record_info = pd.DataFrame()

    record_info_visual = record_info.rename(columns=feature_name_map)

    print(record_info_visual.to_dict(orient="records"))
    return (
        json.dumps(record_info.to_dict(orient="records")),
        record_info_visual.to_dict(orient="records"),
    )


@app.callback(
    [
        Output("matches_table", "data"),
        Output("recordIDs", "children"),
        Output("messages", "children"),
        Output("prediction", "children"),
        Output("probability_of_default", "children"),
    ],
    [Input("scoring_button", "n_clicks")],
    [
        State("input_record", "children"),
        State("id", "value"),
    ],
)
def update_table(n_clicks, input_record, id):
    """
    A Function to send record to model and parse output

    :param n_clicks:
    :param input_record:
    :param id:
    :return:
    """

    if input_record == "[loading]":  # empty record on loading

        return (
            [],
            [],
            not_applicable_message,
            0.0,
            0.0,
        )

    elif input_record == "[]":  # Empty record corresponding to invalid id input

        return (
            [],
            [],
            html.P(
                children=[
                    html.P("\u00A0"),
                    html.P("\u00A0"),
                    html.Strong("Invalid ID input!"),
                    html.P("\u00A0"),
                    html.P("\u00A0"),
                ]
            ),
            0.0,
            0.0,
        )

    else:
        json_record = json.loads(input_record)[0]
        output = score(json_record)
        prediction = output["predicted_score"]

        if prediction == "Default":
            background_color = "red"
        else:
            background_color = "green"

        probability_of_default = output["probability_of_default"]

        row = input_data[input_data["id"] == id].reset_index(drop=True)
        input_data["matches"] = input_data.apply(
            lambda idx: sum(sum(idx.values == row.values)), axis=1
        )
        input_data.sort_values(by=["matches"], inplace=True, ascending=False)
        # Top 5 matches not including self
        matches = input_data.iloc[1:6].rename(columns=feature_name_map)

        text_output = html.P(
            children=[
                html.Strong("Logistic Regession Prediction: "),
                html.Span(
                    prediction,
                    style={
                        "color": "white",
                        "background-color": background_color,
                        "padding-left": "10px",
                        "padding-right": "10px",
                    },
                ),
                html.P("\u00A0"),
                html.Strong("Probability of Default: "),
                html.Span(probability_of_default),
            ]
        )

        print(matches.to_dict(orient="records"))

        return (
            matches.to_dict(orient="records"),
            matches.ID.values,
            text_output,
            prediction,
            probability_of_default,
        )


@app.callback(
    [Output("download_data_link", "href"), Output("download_data_link", "download")],
    [
        Input("input_record_visual", "data"),
        Input("matches_table", "data"),
        Input("id", "value"),
        Input("prediction", "children"),
        Input("probability_of_default", "children"),
    ],
)
def update_download_data_link(
    input_record,
    matches_table,
    id,
    prediction,
    probability_of_default,
):
    """
    A function to read generated data and download a corresponding CSV file

    :param input_record:
    :param matches_table:
    :param id:
    :param prediction:
    :param probability_of_default:
    :return: a link to download data in a CSV format
    """

    record_string = pd.DataFrame.from_records(input_record).to_csv(
        index=False, encoding="utf-8"
    )

    table_string = pd.DataFrame.from_records(matches_table).to_csv(
        index=False, encoding="utf-8"
    )

    summary_string = pd.DataFrame(
        [
            {
                "ID": id,
                "Logistic Regression Prediction": prediction,
                "Probability of Default": probability_of_default,
            }
        ]
    ).to_csv(index=False, encoding="utf-8")

    csv_string = (
        "data:text/csv;charset=utf-8,"
        + urllib.parse.quote(record_string)
        + "\n"
        + urllib.parse.quote(table_string)
        + "\n"
        + urllib.parse.quote(summary_string)
    )

    csv_filename = "model_results_appID_{}.csv".format(id)

    return (csv_string, csv_filename)


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8080, use_reloader=False)
