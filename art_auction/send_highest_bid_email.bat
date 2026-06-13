@echo off
cd /d E:\ART-AUCTION PROJECTS\art-auction-project\art_auction  <-- Your project directory path
call E:\ART-AUCTION PROJECTS\virtualenv_art\Scripts\activate  <-- Your virtual environment path
python manage.py send_highest_bid_email
deactivate
