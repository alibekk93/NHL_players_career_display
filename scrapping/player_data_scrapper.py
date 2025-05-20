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
    rows = table.select('tbody tr')
    
    # Initialize list to store the extracted data
    players_data = []

    for row in rows:
        try:
            # Get name
            name_element = row.select_one('td[data-stat="name_display"]')
            name = name_element.text if name_element else ''

            # Get age
            age_element = row.select_one('td[data-stat="age"]')
            age = int(age_element.text) if age_element else None

            # Get team
            team_element = row.select_one('td[data-stat="team_name_abbr"]')
            team = team_element.text if team_element else ''

            # Get position
            pos_element = row.select_one('td[data-stat="pos"]')
            pos = pos_element.text if pos_element else ''

            # Get TOI
            toi_element = row.select_one('td[data-stat="time_on_ice"]')
            toi_m, toi_s = toi_element.text.split(':') if toi_element else None
            toi = int(toi_m) + (int(toi_s)/60) if toi_element else None

            # Add to the list
            players_data.append({
                'name': name,
                'age': age,
                'team': team,
                'position': pos,
                'TOI': toi
                })        
        except:
            pass

    return players_data

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
    
    seasons_stats = {}

    for season in tqdm(range(start_season, end_season + 1)):
        # URL for the NHL stats page
        url = f"https://www.hockey-reference.com/leagues/NHL_{season}_skaters.html"
        
        # Fetch the HTML content
        response = requests.get(url)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Parse the HTML content to extract stats
            stats = pd.DataFrame(parse_hockey_standings(html_content, 'player_stats'))

            # Add the season to the DataFrame
            stats['season'] = season
            
            # Store the standings in a dictionary
            seasons_stats[season] = stats
        
        else:
            print(f"Failed to retrieve data for season {season}")

    if seasons_stats:
        players_df = pd.concat(seasons_stats.values(), ignore_index=True)
        
        # Create path to data folder (relative to project root)
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate to project root (assuming script is in 'modules' folder)
        project_root = os.path.dirname(script_dir)
        # Create data directory path
        data_dir = os.path.join(project_root, 'data')
        data_dir = os.path.join(project_root, 'data')
        
        # Create the data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Save to CSV in the data directory
        output_path = os.path.join(data_dir, 'nhl_stats.csv')
        players_df.to_csv(output_path, index=False)
        print(f"Data successfully saved to {output_path}")
    else:
        print("No data was collected.")

if __name__ == "__main__":
    main()