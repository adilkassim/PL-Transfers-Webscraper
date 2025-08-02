import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

url = 'https://www.transfermarkt.us/premier-league/transfers/wettbewerb/GB1/plus/?saison_id=2024&s_w=s&leihe=1&intern=0&intern=1'
headers = {
    "User-Agent": "Mozilla/5.0"
}
page = requests.get(url, headers=headers)

soup = BeautifulSoup(page.content, "html.parser")

import pandas as pd
from bs4 import BeautifulSoup

# This script assumes 'soup' is your BeautifulSoup object for the entire HTML page.
# For example: soup = BeautifulSoup(html_content, 'html.parser')

# Lists to store data from all teams
all_incoming_data = []
all_outgoing_data = []

def scrape_transfer_table(table_container, team_name, transfer_type):
    """
    Scrapes a single transfer table (incoming or outgoing) and returns the data as a list of dictionaries.
    
    Args:
        table_container: The BeautifulSoup object for the 'responsive-table' div.
        team_name: The name of the team being scraped.
        transfer_type: A string, either 'incoming' or 'outgoing'.
        
    Returns:
        A list of dictionaries, with each dictionary representing a row of data.
    """
    transfer_data = []
    
    table_body = table_container.find('tbody')
    if not table_body:
        return transfer_data

    rows = table_body.find_all('tr')
    for j, row in enumerate(rows):
        try:
            # Direct extraction without checks, assuming most fields exist
            name = row.find('td').find('a')['title']
            age = row.find('td', class_='zentriert alter-transfer-cell').text
            country_td = row.find('td', class_='zentriert nat-transfer-cell')
            countries_list = [img['title'] for img in country_td.find_all('img')]
            countries = ', '.join(countries_list)
            pos_td = row.find('td', class_='pos-transfer-cell')
            kurzpos_td = row.find('td', class_='kurzpos-transfer-cell zentriert')
            positions = f"{pos_td.text}/ {kurzpos_td.text}"
            market_value = row.find('td', class_='rechts mw-transfer-cell').text
            
            # Keeping the specified checks for the fee
            fee_cell = row.select_one('td.rechts:not(.mw-transfer-cell)')
            fee = fee_cell.find('a').get_text(separator=" ").strip() if fee_cell and fee_cell.find('a') else "N/A"

            # The logic for 'former_team' vs 'new_team' is the only difference
            if transfer_type == 'incoming':
                transfer_team_td = row.find('td', class_='no-border-rechts')
                transfer_team = transfer_team_td.find('a')['title'] if transfer_team_td and transfer_team_td.find('a') else "N/A"
                transfer_league_td = row.find('td', class_='no-border-links verein-flagge-transfer-cell')
                transfer_league = transfer_league_td.find('img')['title'] if transfer_league_td and transfer_league_td.find('img') else "N/A"

                transfer_data.append({
                    "Team": team_name,
                    "Transfer Type": transfer_type,
                    "Name": name, "Age": age, "Countries": countries, "Positions": positions,
                    "Market Value": market_value, "Transfer Team": transfer_team, 
                    "Transfer League": transfer_league, "Transfer Fee": fee
                })
            
            else: # transfer_type == 'outgoing'
                transfer_team_td = row.find('td', class_='no-border-links verein-flagge-transfer-cell')
                transfer_team = transfer_team_td.find('a')['title'] if transfer_team_td and transfer_team_td.find('a') else "N/A"
                transfer_league_td = row.find('td', class_='no-border-rechts')
                transfer_league = transfer_league_td.find('a')['title'] if transfer_league_td and transfer_league_td.find('a') else "N/A"
                
                transfer_data.append({
                    "Team": team_name,
                    "Transfer Type": transfer_type,
                    "Name": name, "Age": age, "Countries": countries, "Positions": positions,
                    "Market Value": market_value, "Transfer Team": transfer_team,
                    "Transfer League": transfer_league, "Transfer Fee": fee
                })

        except Exception as e:
            print(f"  Error processing {transfer_type} row {j + 1} for team '{team_name}': {e}")
            print(f"  Problematic row HTML: {row}")

    return transfer_data


# Find all the team name headings on the page
team_headings = soup.find_all('h2', class_='content-box-headline')


# Loop through each team heading
for heading in team_headings:
    # Safely get the team name from the 'title' attribute of the <a> tag
    team_link = heading.find('a')
    if team_link and 'title' in team_link.attrs:
        team_name = team_link['title'].replace('Array', '').strip()
    else:
        # Skip this heading if no valid team name can be found
        continue
    
    # Find the two tables that follow the heading
    tables = heading.find_next_siblings('div', class_='responsive-table', limit=2)
    
    if len(tables) == 2:
        incoming_table_container = tables[0]
        outgoing_table_container = tables[1]
        
        print(f"\nScraping data for team: {team_name}...")

        # --- Scrape Incoming Transfers using the new function ---
        incoming_data_for_team = scrape_transfer_table(incoming_table_container, team_name, 'incoming')
        all_incoming_data.extend(incoming_data_for_team)
        
        # --- Scrape Outgoing Transfers using the new function ---
        outgoing_data_for_team = scrape_transfer_table(outgoing_table_container, team_name, 'outgoing')
        all_outgoing_data.extend(outgoing_data_for_team)

            
# Create the final, combined DataFrames
incoming_df = pd.DataFrame(all_incoming_data)
outgoing_df = pd.DataFrame(all_outgoing_data)


print("\n--- Summary of Scraped Data ---")
print(f"\nCombined Incoming Transfers (Total Rows: {len(incoming_df)}):\n{incoming_df.head()}")
print(f"\nCombined Outgoing Transfers (Total Rows: {len(outgoing_df)}):\n{outgoing_df.head()}")

print("\nAll incoming transfer data is in the 'incoming_df' DataFrame.")
print("All outgoing transfer data is in the 'outgoing_df' DataFrame.")