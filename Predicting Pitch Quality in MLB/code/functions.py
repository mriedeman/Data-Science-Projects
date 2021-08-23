"""Collects data from baseball savant using the pybaseball library. Takes a time intervel and the player id to sucessfully get  scrape the baseball savant website."""

def get_data(start_date, end_date, file_number):  

    from pybaseball import playerid_lookup
    from pybaseball import statcast_pitcher
    import time
    import pandas as pd
    
    #report the time it takes for the function to execute
    print("This may take several minutes to run.")
    start_time = time.time()

    # creates a list of pitcher ids to loop through
    savant = pd.read_csv('../data/savant_data.csv')
    savant['player_name'] = savant['player_name'].str.lower()
    savant = savant.sort_values(by = 'player_name')
    pitcher_ids = [id for id in savant['player_id']]

    dictionary_list = []
    for i in pitcher_ids[:5]:   
        player_sabermetrics = statcast_pitcher(start_date, end_date, player_id = i)

        dictionary_list.append(player_sabermetrics)


    data_df = pd.concat(dictionary_list)

    data_df.to_csv(f'../data/pitching_masterfile{file_number}.csv',index = False)


    end_time = time.time()
    time_elapsed = end_time - start_time
    print(time_elapsed)
    return data_df

############################################################################################################################

"""filter dataframe to remove pitches with not enough data, and choose input features for models, and one-hot-encode categorical features"""

import pandas as pd
from sklearn.model_selection import cross_val_score, GridSearchCV, train_test_split

def preprocessing(remove_pitches = ['EP', 'KN', 'SC', 'PO', 'CS']):
    eda = pd.read_csv('../data/pitching_masterfile10.csv')
    print(f'{eda.shape[0]} pitches')
    print(f"{eda['player_name'].nunique()} unique pitchers")
    
    #filter dataframe to remove pitches with not enough data, and choose input features for models,
    #and one-hot-encode categorical features
    remove_pitches = ['EP', 'KN', 'SC', 'PO', 'CS']
    columns = ['stand','p_throws','pitch_type', 'release_speed', 'release_spin_rate','balls', 'strikes',
               'pfx_x', 'pfx_z', 'plate_x', 'plate_z', 'delta_run_exp' ]


    eda = eda.copy().loc[eda['pitch_type'].isin(remove_pitches) == False]

    input_df = eda[columns]

    input_df = pd.get_dummies(input_df, columns = ['pitch_type','p_throws','stand'], drop_first = True)

    input_df = input_df.dropna()
          
    X = input_df.drop(columns = 'delta_run_exp')
    y = input_df['delta_run_exp']

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state = 4)
          
    return input_df, X_train, X_test, y_train, y_test

############################################################################################################################
"""Gridsearches hyperparemters to find the optimal Random Forest regression model. Models are saved in the data folder. Be sure to change the 'trial_number' parameter to avoid overwriting previously saved models"""

from sklearn.ensemble import RandomForestRegressor
import time
import pickle
from sklearn.model_selection import GridSearchCV

def model(trial_number,
          train_features,
          train_target,
          estimators = [10],
          max_features = ['auto'],
          max_depth = [3],
          min_sample_split = [3],
          ccp_alpha = [0.01]):
    
    start_time = time.time()
    rf = RandomForestRegressor()
    
    params = {
        'n_estimators' : estimators,
        'max_features' : max_features,
        'max_depth'    : max_depth,
        'min_samples_split' : min_sample_split,
        'ccp_alpha'    : ccp_alpha
    }
    
    gs = GridSearchCV(rf, param_grid = params, cv = 5)

    gs.fit(train_features, train_target)

    with open(f'../data/rf{trial_number}.pkl', 'wb') as file:
        pickle.dump(gs, file)

    end_time = time.time() - start_time

    return print(f"The grid search took {end_time} seconds to complete. The model is saved as '../data/rf{trial_number}.pkl' in the data folder")


############################################################################################################################
"""Load model results and output to a dataframe. Add the model preditions to the features dataframe to be used in the plotting function below."""

import pickle
import pandas as pd

def evaluate_model(file_number, y_train, y_test, X_test):
    with open(f'../data/rf{file_number}.pkl', 'rb') as file:
        gs_rf = pickle.load(file)
    
    model_results_df = pd.DataFrame(gs_rf.cv_results_)
    

    y_preds = gs_rf.predict(X_test)
    
    final_results_df = X_test.copy()
    final_results_df['predictions'] = y_preds
    final_results_df['y_actual'] = y_test
    
    return model_results_df, final_results_df, y_preds

############################################################################################################################


"""Constructs a scatter plot heatmap for a given count and pitch type. The hue is the expected change in run expectancy after the pitch is thrown."""
import seaborn as sns
import matplotlib.pyplot as plt

def pitch_plots(predictions_df, balls, strikes, pitch_type):
    
    #filter the predictions results dataframe for the count and type of pitch
    filtered_df = predictions_df.copy().loc[(predictions_df['balls'] == balls) &
                                                   (predictions_df['strikes'] == strikes)  &
                                                   (predictions_df[f'{pitch_type}'] == 1)]
    

    #create plot from filtered dataframe
    sns.set(font_scale=2)
    sns.set_style("whitegrid")

    sns.relplot(
    data = filtered_df,
    x="plate_x", y= "plate_z",
    hue = filtered_df['predictions'],
    palette="Spectral",
    hue_norm=(filtered_df['predictions'].min(), filtered_df['predictions'].max()),
        sizes=(50, 250), size_norm=(-.2, .8),
    edgecolor=".7",
    height=10,
    alpha = .4
    ).set(title= f'Run Expectancy for {pitch_type[-2:]} in a {balls}-{strikes} Count', 
        xlabel='x pitch (feet)',
         ylabel='y pitch (feet)', );
    plt.savefig(f'../images/{balls}balls{strikes}strikes{pitch_type[-2:]}.png')
    

############################################################################################################################