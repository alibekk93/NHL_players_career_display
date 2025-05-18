# import libraries
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import os
import sys

# Function to parse the NHL standings table
def parse_hockey_standings(html_content, id):
    """Parse the HTML content of a hockey standings page and extract basic team statistics.

    Args:
        html_content (str): The HTML content of the page.
        id (str): The ID of the table to parse.
    
    Returns:
        list: A list of dictionaries containing team statistics.
    """

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    # Find the table
    table = soup.find('table', {'id': id})
    
    if not table:
        print("Table not found")
        return []
    
    # Find all rows in the table body with class "full_table"
    rows = table.select('tbody tr.full_table')
    
    # Initialize list to store the extracted data
    teams_data = []
    
    # Loop through each row and extract the data
    for row in rows:
        # Get team name (removing the asterisk if present)
        team_name_element = row.select_one('th[data-stat="team_name"] a')
        team_name = team_name_element.text.replace('*', '') if team_name_element else ''
        
        # Get Goals For (GF)
        goals_for_element = row.select_one('td[data-stat="goals"]')
        goals_for = int(goals_for_element.text) if goals_for_element else None
        
        # Get Goals Against (GA)
        goals_against_element = row.select_one('td[data-stat="opp_goals"]')
        goals_against = int(goals_against_element.text) if goals_against_element else None

        # Get number of games played
        games_played_element = row.select_one('td[data-stat="games"]')
        games_played = int(games_played_element.text) if games_played_element else None
        
        # Add to the list
        teams_data.append({
            'team': team_name,
            'GF': goals_for,
            'GA': goals_against,
            'GP': games_played
        })
    
    return teams_data

def main():
    # Get user input for start and end seasons
    try:
        start_season = int(input("Enter start season (e.g., 2000): "))
        end_season = int(input("Enter end season (e.g., 2025): "))
        
        # Validate input
        if start_season > end_season:
            print("Error: Start season cannot be greater than end season.")
            return
        
        if start_season < 1917 or end_season > 2026:  # NHL started in 1917
            print("Warning: Seasons should typically be between 1917 and 2026.")
    except ValueError:
        print("Error: Please enter valid years as integers.")
        return
    
    seasons_standings = {}

    for season in tqdm(range(start_season, end_season + 1)):
        # URL for the NHL standings page
        url = f"https://www.hockey-reference.com/leagues/NHL_{season}_standings.html"
        
        # Fetch the HTML content
        response = requests.get(url)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Parse the HTML content to extract standings
            standings_w = pd.DataFrame(parse_hockey_standings(html_content, 'standings_WES'))
            standings_e = pd.DataFrame(parse_hockey_standings(html_content, 'standings_EAS'))

            # Concatenate the two dataframes
            standings = pd.concat([standings_w, standings_e], ignore_index=True)
            standings['season'] = season
            
            # Store the standings in a dictionary
            seasons_standings[season] = standings     
        
        else:
            print(f"Failed to retrieve data for season {season}")

    if seasons_standings:
        teams_df = pd.concat(seasons_standings.values(), ignore_index=True)
        
        # Create path to data folder (relative to project root)
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate to project root (assuming script is in 'modules' folder)
        project_root = os.path.dirname(script_dir)
        # Create data directory path
        data_dir = os.path.join(project_root, 'data')
        
        # Create the data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Save to CSV in the data directory
        output_path = os.path.join(data_dir, 'nhl_standings.csv')
        teams_df.to_csv(output_path, index=False)
        print(f"Data successfully saved to {output_path}")
    else:
        print("No data was collected.")

if __name__ == "__main__":
    main()