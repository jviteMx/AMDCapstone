import pandas as pd
import dash
import dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from databars_recipes import data_bars, data_bars_diverging
from dash_table.Format import Format, Align, Scheme

speedup_dataframe = pd.DataFrame()
def make_graph(dataframe, title, graph, versions, speedup_options):
    speedup_dataframe = pd.DataFrame()
    df = dataframe
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if graph == 'line':
        mode = 'lines'
    else:
        mode = 'lines+markers'    
    mask = df['collection'].unique()
    dfs = [df[df['collection']== collection] for collection in mask]    # gpu-server-1/rocfft/rocm3.9/r5-d3-ratio-1-1-c2c-op
    for df in dfs:
        name = df.iloc[0]['collection']
        name = rename(name)
        fig.add_trace(go.Scatter(x=df['xlength'], y=df['median'],
                    mode=mode,
                    name=name),
                    secondary_y=False)                            
    if len(list(set(speedup_options) & set(versions))) > 1:
        speedup_options = [value for value in speedup_options if value in versions]
        speedup_options.sort()
        options_collections = []
        for version in speedup_options:
            for collection in mask:
                if version in collection:
                    options_collections.append(collection) 
        firstelement = speedup_options[0] 
        # collections = mask
        collections = options_collections
        first_collections = [collection for collection in collections if firstelement in collection]
        first_collection = first_collections[0]
        del first_collections[0]
        reference_df =  dataframe[dataframe['collection']== first_collection]  
        ref_name = rename(first_collection) 
        speedup_dataframe['problem-size'] = reference_df['xlength']
        speedup_dataframe[f'median {ref_name}'] = reference_df['median']
        collections = [collection for collection in collections if collection != first_collection]  
         
        for option in collections:
            opt_name = rename(option)   
            option_df = dataframe[dataframe['collection']== option]
            speedup_dataframe[f'median {opt_name}'] = option_df['median']        
        for option in collections:
            opt_name = rename(option)   
            option_df = dataframe[dataframe['collection']== option]
            median_a = reference_df['median']
            median_b = option_df['median']
            speedup = median_a.subtract(median_b)
            speedup_dataframe[f'{opt_name} over {ref_name}'] = speedup
            ylist = speedup.tolist()

            fig.add_trace(
                go.Scatter(x=option_df['xlength'], y=ylist, name=opt_name + ' speedup over ' + 
                ref_name),
                secondary_y=True,
            )


    fig.update_layout(title=title, height=700, font=dict(
        family="Courier New, monospace",
        size=18,
        color="RebeccaPurple"
    ))
    fig.update_xaxes(title_text="Problem Size (logarithmic)", type="log") 
    fig.update_yaxes(title_text="Median Time (logarithmic)", type="log", secondary_y=False)
    fig.update_yaxes(title_text="Speedup", secondary_y=True)                                #rangemode="nonnegative"  range=[-2,2]
    
    table = make_table(speedup_dataframe)
    if len(list(set(speedup_options) & set(versions))) > 1:
        return fig, table
    else: 
        return fig, None   

def rename(collection):
    name = collection.split('/')
    rename_part1 = name[0].strip('gpu-')[0] + name[0].strip('gpu-')[-1] + '/' 
    rename_part2 = name[2].strip('rocm')
    rename_part3 = name[3].split('-')
    rename_part3 = ''.join([i[0] for i in rename_part3])
    renamed = rename_part1 + rename_part2 + rename_part3 
    return renamed.upper()    


def make_table(df):
    columns = list(df.columns)
    interest_cols = [i for i in columns if 'over' in i]
    style_data_conditional = [data_bars_diverging(df, a) for a in interest_cols]
    styles = [item for sublist in style_data_conditional for item in sublist]
    table = dash_table.DataTable(
        data=df.to_dict('records'),
        sort_action='native',
        columns=[{'name': i, 'id': i, "type": 'numeric', "format": Format(precision=6, scheme=Scheme.fixed)} for i in df.columns],
        # style_data_conditional=(
        #     styles
        # )
        style_data_conditional=([
                 {'if': { 'filter_query': '{S1/3.8RDCI over S1/3.6RDCI} >= 0','column_id': 'S1/3.8RDCI over S1/3.6RDCI'},
                     'color': 'green'},
                 {'if': {'filter_query': '{S1/3.8RDCI over S1/3.6RDCI} < 0','column_id': 'S1/3.8RDCI over S1/3.6RDCI'},
                     'color': 'red'},
                 {'if': {'filter_query': '{S1/3.9RDCI over S1/3.6RDCI} >= 0','column_id': 'S1/3.9RDCI over S1/3.6RDCI'},
                     'color': 'green' },
                 {'if': {'filter_query': '{S1/3.9RDCI over S1/3.6RDCI} < 0','column_id': 'S1/3.9RDCI over S1/3.6RDCI'},
                     'color': 'red' }
             ])
    )  

    return table    