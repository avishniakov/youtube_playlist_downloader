# Download YouTube Playlists

python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt 
python3 dl.py -d <SAVE_DIR> -p <PLAYLIST_URL(s)> -mp <PARALLEL_PROCESSES_COUNT>