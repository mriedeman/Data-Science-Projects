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

#########################################################################################################