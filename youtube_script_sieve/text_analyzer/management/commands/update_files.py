"""
We will run this command every 24
hours to update our CSV files.
"""
import os # to get environment variables
from django.core.management.base import BaseCommand
from django.conf import settings
import csv

# for working with the sheets api
from googleapiclient.discovery import build

import json # TBD


class Command(BaseCommand):
    help = 'Queries the twitter API for tweets'

    # this will be used for comparison with the cell background
    # colors returned
    background_colors = {
        "monetized": {
            "red": 0.7137255,
            "green": 0.84313726,
            "blue": 0.65882355
        },

        "demonetized": {
            "red": 1,
            "green": 0.8980392,
            "blue": 0.6
        }
    }

    def writeToCSV(self, rows, filename):
        with open(filename, 'w',  encoding='UTF8') as f:
            writer = csv.writer(f)
            for row in rows:
                columns = row.get("values")

                word = columns[0].get("formattedValue")
                word_background_color = columns[0].get("userEnteredFormat").get("backgroundColor")

                if word_background_color == self.background_colors.get("demonetized"):
                    color = "yellow"
                else:
                    color = "green"

                # Get seveity if present
                if len(columns) > 1:
                    try:
                        severity = len(columns[1].get("formattedValue"))
                    except:
                        severity = 0
                else:
                    severity = 0

                # write a row to the csv file
                writer.writerow([word, color, severity])
        return

    def handle(self, *args, **options):
        google_api_key = os.environ.get('GOOGLE_API_KEY')
        files_dir = f"{settings.BASE_DIR}/words"

        spreadsheet_id = '1ozg1Cnm6SdtM4M5rATkANAi07xAzYWaKL7HKxyvoHzk'
        ranges = ["All Words!A5:B"]

        with build('sheets', 'v4', developerKey=google_api_key) as service:
            spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id, ranges=ranges, includeGridData=True).execute()
            
            sheets = spreadsheet.get("sheets")

            for sheet in sheets:
                title = sheet.get("properties").get("title")
                grids = sheet.get("data")

                for grid in grids:
                    rows = grid.get("rowData")

                    if title == "All Words":
                        self.writeToCSV(rows, f'{files_dir}/all_words.csv')
                    elif title == "Demonetized Words":
                        self.writeToCSV(rows, f'{files_dir}/demonetized.csv')
                    else:
                        pass
