import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# Load the data
df = pd.read_csv('apple_products.csv')

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Apple Products Analysis Dashboard"),
    
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='product-dropdown',
                options=[{'label': product, 'value': product} for product in df['Product Name'].unique()],
                value=df['Product Name'].iloc[0],
                multi=False,
                style={'width': '100%'}
            ),
            dcc.Graph(id='price-comparison-graph')
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.RadioItems(
                id='chart-type',
                options=[{'label': i, 'value': i} for i in ['Scatter', 'Bar']],
                value='Scatter',
                labelStyle={'display': 'inline-block', 'marginRight': 10}
            ),
            dcc.Graph(id='ram-vs-price-graph')
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ]),
    
    html.Div([
        dcc.RangeSlider(
            id='price-range-slider',
            min=df['Sale Price'].min(),
            max=df['Sale Price'].max(),
            step=1000,
            marks={i: f'₹{i:,}' for i in range(int(df['Sale Price'].min()), int(df['Sale Price'].max()), 20000)},
            value=[df['Sale Price'].min(), df['Sale Price'].max()]
        ),
        dcc.Graph(id='product-distribution-graph')
    ]),
    
    html.Div(id='summary', style={'marginTop': 20})
])

# Callback for price comparison graph
@app.callback(
    Output('price-comparison-graph', 'figure'),
    Input('product-dropdown', 'value')
)
def update_price_comparison(selected_product):
    product_data = df[df['Product Name'] == selected_product].iloc[0]
    
    fig = go.Figure(data=[
        go.Bar(name='Sale Price', x=['Sale Price'], y=[product_data['Sale Price']]),
        go.Bar(name='MRP', x=['MRP'], y=[product_data['Mrp']])
    ])
    
    fig.update_layout(title=f'Price Comparison for {selected_product}',
                      yaxis_title='Price (₹)')
    
    return fig

# Callback for RAM vs Price graph
@app.callback(
    Output('ram-vs-price-graph', 'figure'),
    Input('chart-type', 'value')
)
def update_ram_vs_price(chart_type):
    if chart_type == 'Scatter':
        fig = px.scatter(df, x='Ram', y='Sale Price', hover_data=['Product Name'])
    else:
        fig = px.bar(df, x='Ram', y='Sale Price', hover_data=['Product Name'])
    
    fig.update_layout(title='RAM vs Price',
                      xaxis_title='RAM (GB)',
                      yaxis_title='Price (₹)')
    
    return fig

# Callback for product distribution graph
@app.callback(
    Output('product-distribution-graph', 'figure'),
    Input('price-range-slider', 'value')
)
def update_product_distribution(price_range):
    filtered_df = df[(df['Sale Price'] >= price_range[0]) & (df['Sale Price'] <= price_range[1])]
    
    fig = px.pie(filtered_df, names='Brand', title='Product Distribution by Brand')
    
    return fig

# Callback for summary
@app.callback(
    Output('summary', 'children'),
    Input('price-range-slider', 'value')
)
def update_summary(price_range):
    filtered_df = df[(df['Sale Price'] >= price_range[0]) & (df['Sale Price'] <= price_range[1])]
    
    avg_price = filtered_df['Sale Price'].mean()
    avg_discount = filtered_df['Discount Percentage'].mean()
    avg_rating = filtered_df['Star Rating'].mean()
    
    summary = f"""
    Summary for selected price range (₹{price_range[0]:,} - ₹{price_range[1]:,}):
    - Average Price: ₹{avg_price:,.2f}
    - Average Discount: {avg_discount:.2f}%
    - Average Rating: {avg_rating:.2f} stars
    """
    
    return summary

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
