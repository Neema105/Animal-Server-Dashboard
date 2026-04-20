# Neema Taghipour app.py
# admin account is user: admin password: password!
import dash_leaflet as dl
from dash import Dash, dcc, html, dash_table, ctx
import plotly.express as px
from dash.dependencies import Input, Output, State
import base64
import json
import os
import pandas as pd
from datetime import datetime
from time import perf_counter
from CRUD_Python_Module import CSVAnimalShelter, PostgresAnimalShelter, build_animal_shelter

#Read csv
DATA_FILE = os.path.join(os.path.dirname(__file__), 'dogs_dataset.csv')
animal_shelter = build_animal_shelter(DATA_FILE)
DEFAULT_FILTER = 'RESET'
df = animal_shelter.get_dashboard_data(DEFAULT_FILTER)
DATA_SOURCE_LABEL = 'PostgreSQL' if isinstance(animal_shelter, PostgresAnimalShelter) else 'CSV fallback'

#read user file
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')
LOGIN_LOG_FILE = os.path.join(os.path.dirname(__file__), 'login_data.txt')
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w', encoding='utf-8') as file:
        json.dump({"admin": {"password": "CS499Dash!", "question": "Favorite color?", "answer": "blue"}}, file, indent=2)

def load_users():
    with open(USERS_FILE, 'r', encoding='utf-8') as file:
        users = json.load(file)
    if users and isinstance(next(iter(users.values())), str):
        users = {name: {"password": pwd, "question": "Favorite color?", "answer": "blue"} for name, pwd in users.items()}
        with open(USERS_FILE, 'w', encoding='utf-8') as file:
            json.dump(users, file, indent=2)
    return users

#Quicksort Algorithm
def quicksort_records(records, key_name, reverse=False):
    if len(records) <= 1:
        return records

    pivot_value = records[len(records) // 2].get(key_name)
    lower = []
    equal = []
    higher = []

    for record in records:
        record_value = record.get(key_name)
        if record_value < pivot_value:
            lower.append(record)
        elif record_value > pivot_value:
            higher.append(record)
        else:
            equal.append(record)

    sorted_records = quicksort_records(lower, key_name) + equal + quicksort_records(higher, key_name)
    return list(reversed(sorted_records)) if reverse else sorted_records

#Merge Sort Algorithm
def merge_records(left, right, key_name):
    merged = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index].get(key_name) <= right[right_index].get(key_name):
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged


def mergesort_records(records, key_name, reverse=False):
    if len(records) <= 1:
        return records

    midpoint = len(records) // 2
    left_half = mergesort_records(records[:midpoint], key_name)
    right_half = mergesort_records(records[midpoint:], key_name)
    sorted_records = merge_records(left_half, right_half, key_name)
    return list(reversed(sorted_records)) if reverse else sorted_records


def heapify(records, heap_size, root_index, key_name):
    largest_index = root_index
    left_child = (2 * root_index) + 1
    right_child = (2 * root_index) + 2

    if left_child < heap_size and records[left_child].get(key_name) > records[largest_index].get(key_name):
        largest_index = left_child

    if right_child < heap_size and records[right_child].get(key_name) > records[largest_index].get(key_name):
        largest_index = right_child

    if largest_index != root_index:
        records[root_index], records[largest_index] = records[largest_index], records[root_index]
        heapify(records, heap_size, largest_index, key_name)

#Heapsort algorithm
def heapsort_records(records, key_name, reverse=False):
    sorted_records = records.copy()
    record_count = len(sorted_records)

    for index in range((record_count // 2) - 1, -1, -1):
        heapify(sorted_records, record_count, index, key_name)

    for index in range(record_count - 1, 0, -1):
        sorted_records[0], sorted_records[index] = sorted_records[index], sorted_records[0]
        heapify(sorted_records, index, 0, key_name)

    return list(reversed(sorted_records)) if reverse else sorted_records

#select sort algorithm
def selectionsort_records(records, key_name, reverse=False):
    sorted_records = records.copy()
    record_count = len(sorted_records)

    for left_index in range(record_count):
        min_index = left_index
        for right_index in range(left_index + 1, record_count):
            if sorted_records[right_index].get(key_name) < sorted_records[min_index].get(key_name):
                min_index = right_index
        sorted_records[left_index], sorted_records[min_index] = sorted_records[min_index], sorted_records[left_index]

    return list(reversed(sorted_records)) if reverse else sorted_records

#insertsort algorithm
def insertionsort_records(records, key_name, reverse=False):
    sorted_records = records.copy()

    for index in range(1, len(sorted_records)):
        current_record = sorted_records[index]
        current_value = current_record.get(key_name)
        compare_index = index - 1

        while compare_index >= 0 and sorted_records[compare_index].get(key_name) > current_value:
            sorted_records[compare_index + 1] = sorted_records[compare_index]
            compare_index -= 1

        sorted_records[compare_index + 1] = current_record

    return list(reversed(sorted_records)) if reverse else sorted_records

#bubble sort algortihm
def bubblesort_records(records, key_name, reverse=False):
    sorted_records = records.copy()
    record_count = len(sorted_records)

    for pass_index in range(record_count):
        swapped = False
        for compare_index in range(0, record_count - pass_index - 1):
            if sorted_records[compare_index].get(key_name) > sorted_records[compare_index + 1].get(key_name):
                sorted_records[compare_index], sorted_records[compare_index + 1] = (
                    sorted_records[compare_index + 1],
                    sorted_records[compare_index]
                )
                swapped = True
        if not swapped:
            break

    return list(reversed(sorted_records)) if reverse else sorted_records

def time_record_sort(sort_function, records, key_name, reverse=False):
    start_time = perf_counter()
    sorted_records = sort_function(records.copy(), key_name, reverse)
    elapsed_time = perf_counter() - start_time
    return sorted_records, elapsed_time


SORT_FUNCTIONS = {
    'quick': ('Quick Sort', quicksort_records, 'Best/Average: O(n log n), Worst: O(n^2)'),
    'merge': ('Merge Sort', mergesort_records, 'Best/Average/Worst: O(n log n)'),
    'heap': ('Heap Sort', heapsort_records, 'Best/Average/Worst: O(n log n)'),
    'selection': ('Selection Sort', selectionsort_records, 'Best/Average/Worst: O(n^2)'),
    'insertion': ('Insertion Sort', insertionsort_records, 'Best: O(n), Average/Worst: O(n^2)'),
    'bubble': ('Bubble Sort', bubblesort_records, 'Best: O(n), Average/Worst: O(n^2)'),
}

# Dashboard Layout

app = Dash(__name__)

# Add in Grazioso Salvare's logo
image_filename = os.path.join(os.path.dirname(__file__), 'Grazioso_Software_Logo.png')
try:
    with open(image_filename, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read())
    logo_src = 'data:image/png;base64,{}'.format(encoded_image.decode())
except FileNotFoundError:
    print(f"Warning: Logo file '{image_filename}' not found.")
    logo_src = ''

app.layout = html.Div([
    dcc.Store(id='auth-ok', data=False),
    #title
    html.Center(html.B(html.H1('CS-340 Dashboard'))),
    html.Center(html.Img(src=logo_src, style={'height': '100px'})),
    html.Center(html.B('Neema Taghipour')),
    html.Center(html.Div(f'Data source: {DATA_SOURCE_LABEL}', style={'marginTop': '8px'})),
    html.Hr(),
    #Buttons
    html.Div([
        dcc.Input(id='login-user', type='text', placeholder='Username'),
        dcc.Input(id='login-pass', type='password', placeholder='Password'),
        html.Button('Login', id='login-button', n_clicks=0),
        html.Div('Default login: admin / CS499Dash!', id='login-message', style={'marginTop': '10px'}),
        html.Hr(),
        dcc.Input(id='create-user', type='text', placeholder='New username'),
        dcc.Input(id='create-pass', type='password', placeholder='New password'),
        dcc.Input(id='security-question', type='text', placeholder='Security question'),
        dcc.Input(id='security-answer', type='text', placeholder='Security answer'),
        html.Button('Create User', id='create-button', n_clicks=0),
        html.Div(id='create-message', style={'marginTop': '10px'}),
        html.Hr(),
        dcc.Input(id='forgot-user', type='text', placeholder='Username for recovery'),
        dcc.Input(id='forgot-answer', type='text', placeholder='Security answer'),
        dcc.Input(id='forgot-pass', type='password', placeholder='New password'),
        html.Button('Forgot Password', id='forgot-button', n_clicks=0),
        html.Div(id='question-message', style={'marginTop': '10px'}),
        html.Div(id='forgot-message', style={'marginTop': '10px'})
    ], id='login-box'),
    html.Div([
        html.Div(
            dcc.RadioItems(
                id='filter-type',
                options=[
                    {'label': 'Reset', 'value': 'RESET'},
                    {'label': 'Water Rescue', 'value': 'WATER'},
                    {'label': 'Mountain or Wilderness Rescue', 'value': 'MOUNTAIN'},
                    {'label': 'Disaster or Individual Tracking', 'value': 'DISASTER'}
                ],
                value='RESET'
            )
        ),
        html.Hr(),
        dash_table.DataTable(
            id='datatable-id',
            columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns],
            data=df.to_dict('records'),
            page_size=10,
            row_selectable="single",
            selected_rows=[0]
        ),
        html.Br(),
        html.Div([
            html.Label('Sort column'),
            dcc.Dropdown(
                id='sort-column',
                options=[{'label': column, 'value': column} for column in df.columns],
                value='age_upon_outcome_in_weeks',
                clearable=False
            ),
            html.Br(),
            html.Label('Display sorted results with'),
            dcc.RadioItems(
                id='sort-algorithm',
                options=[
                    {'label': 'Quick Sort', 'value': 'quick'},
                    {'label': 'Merge Sort', 'value': 'merge'},
                    {'label': 'Heap Sort', 'value': 'heap'},
                    {'label': 'Selection Sort', 'value': 'selection'},
                    {'label': 'Insertion Sort', 'value': 'insertion'},
                    {'label': 'Bubble Sort', 'value': 'bubble'}
                ],
                value='quick',
                inline=False
            ),
            html.Br(),
            html.Label('Sort order'),
            dcc.RadioItems(
                id='sort-order',
                options=[
                    {'label': 'Ascending', 'value': 'asc'},
                    {'label': 'Descending', 'value': 'desc'}
                ],
                value='asc',
                inline=True
            ),
            html.Div(id='sort-timing-output', style={'marginTop': '10px', 'fontWeight': 'bold'})
        ]),
        html.Br(),
        html.Hr(),
        html.Div(
            className='row',
            style={'display': 'flex'},
            children=[
                html.Div(
                    id='graph-id',
                    className='col s12 m6'
                ),
                html.Div(
                    id='map-id',
                    className='col s12 m6'
                )
            ]
        )
    ], id='dashboard-box', style={'display': 'none'})
])

@app.callback(
    [Output('auth-ok', 'data'),
     Output('login-message', 'children'),
     Output('create-message', 'children'),
     Output('question-message', 'children'),
     Output('forgot-message', 'children')],
    [Input('login-button', 'n_clicks'),
     Input('create-button', 'n_clicks'),
     Input('forgot-button', 'n_clicks')],
    [State('login-user', 'value'),
     State('login-pass', 'value'),
     State('create-user', 'value'),
     State('create-pass', 'value'),
     State('security-question', 'value'),
     State('security-answer', 'value'),
     State('forgot-user', 'value'),
     State('forgot-answer', 'value'),
     State('forgot-pass', 'value')]
)
#Login
def login(_, __, ___, entered_user, entered_pass, create_user, create_pass, security_question, security_answer, forgot_user, forgot_answer, forgot_pass):
    users = load_users()
    action = ctx.triggered_id
    if action == 'create-button':
        create_user = (create_user or '').strip()
        if not all([create_user, create_pass, security_question, security_answer]):
            return False, '', 'Fill in all create-user fields.', '', ''
        if create_user in users:
            return False, '', 'Username already exists.', '', ''
        users[create_user] = {"password": create_pass, "question": security_question, "answer": security_answer}
        with open(USERS_FILE, 'w', encoding='utf-8') as file:
            json.dump(users, file, indent=2)
        return False, '', f'User {create_user} created.', '', ''
    #Forgotpassword
    if action == 'forgot-button':
        forgot_user = (forgot_user or '').strip()
        user = users.get(forgot_user)
        if not user:
            return False, '', '', 'User not found.', ''
        if not forgot_answer or not forgot_pass:
            return False, '', '', f"Question: {user['question']}", 'Enter the answer and a new password.'
        if forgot_answer != user['answer']:
            return False, '', '', f"Question: {user['question']}", 'Security answer is incorrect.'
        users[forgot_user]['password'] = forgot_pass
        with open(USERS_FILE, 'w', encoding='utf-8') as file:
            json.dump(users, file, indent=2)
        return False, '', '', f"Question: {user['question']}", 'Password updated.'
    ok = users.get((entered_user or '').strip(), {}).get('password') == (entered_pass or '')
    with open(LOGIN_LOG_FILE, 'a', encoding='utf-8') as file:
        file.write(f"{datetime.now().isoformat()} | user={entered_user} | success={ok}\n")
    return ok, '' if ok else 'Login failed.', '', '', ''

@app.callback(
    [Output('login-box', 'style'),
     Output('dashboard-box', 'style')],
    [Input('auth-ok', 'data')]
)
def toggle_login(auth_ok):
    return ({'display': 'none'}, {'display': 'block'}) if auth_ok else ({}, {'display': 'none'})

@app.callback(
    [Output('datatable-id', 'data'),
     Output('sort-timing-output', 'children')],
    [Input('filter-type', 'value'),
     Input('sort-column', 'value'),
     Input('sort-algorithm', 'value'),
     Input('sort-order', 'value')]
)
def update_dashboard(filter_type, sort_column, sort_algorithm, sort_order):
    data = animal_shelter.get_dashboard_data(filter_type)

    records = data.to_dict('records')
    if not records or not sort_column:
        return records, 'No rows available to sort.'

    reverse_sort = sort_order == 'desc'
    sort_label, sort_function, complexity = SORT_FUNCTIONS.get(sort_algorithm, SORT_FUNCTIONS['quick'])
    displayed_records, elapsed_time = time_record_sort(sort_function, records, sort_column, reverse_sort)
    timing_message = (
        f"{sort_label}: {elapsed_time:.6f} seconds | "
        f"Time Complexity: {complexity} | "
        f"Displaying results by '{sort_column}' ({'descending' if reverse_sort else 'ascending'})."
    )

    return displayed_records, timing_message

@app.callback(
    Output('graph-id', "children"),
    [Input('datatable-id', "derived_virtual_data")]
)
def update_graphs(viewData):
    if not viewData:
        return []
    dff = pd.DataFrame.from_dict(viewData)
    fig = px.histogram(dff, x='breed', title='Preferred Animals')
    return [dcc.Graph(figure=fig)]

@app.callback(
    Output('datatable-id', 'style_data_conditional'),
    [Input('datatable-id', 'selected_columns')]
)
def update_styles(selected_columns):
    if not selected_columns:
        return []
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]

@app.callback(
    Output('map-id', "children"),
    [Input('datatable-id', "derived_virtual_data"),
     Input('datatable-id', "derived_virtual_selected_rows")]
)
def update_map(viewData, index):
    if not viewData or not index:
        return []

    dff = pd.DataFrame.from_dict(viewData)

    if len(dff) == 0 or index[0] >= len(dff):
        return []

    row = index[0]

    return [
        dl.Map(style={'width': '1000px', 'height': '500px'}, center=[30.75, -97.48], zoom=10, children=[
            dl.TileLayer(id="base-layer-id"),
            dl.Marker(position=[dff.iloc[row]['location_lat'], dff.iloc[row]['location_long']], children=[
                dl.Tooltip(dff.iloc[row]['breed']),
                dl.Popup([
                    html.H1("Animal Name"),
                    html.P(dff.iloc[row]['name'])
                ])
            ])
        ])
    ]

# Execute the application
if __name__ == '__main__':
    app.run(debug=True, port=8050)
