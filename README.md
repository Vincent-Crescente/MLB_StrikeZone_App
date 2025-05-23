MLB Strikezone App

![main_pic..JPG](images%2Fmain_pic..JPG)

A Python application that polls the Sportradar MLB API and displays a real-time visual strike zone, including descriptions of each pitch and its outcome. The app is designed to be lightweight and unobtrusive, so it can be placed in the corner of a monitor or alongside other windows, providing an easy, subtle way to keep track of your favorite baseball team's game in real-time. While this app is a concept built around the idea of integrating with a free API, it showcases how such a tool could be used to stay updated without interrupting your workflow.<br>

✨ Features
- Displays live daily MLB games
- Real-time pitch tracking
- Tkinter window for pitch visualizations
- Clean, extensible architecture

⚙️ Tech Stack
- Python

- tkinter – GUI framework for desktop windowing

- Pillow (pillow==11.2.1) – Image handling and rendering

- Requests (requests==2.32.3) – HTTP library for API communication

- python-dotenv (python-dotenv==1.0.0) – Environment variable management

- Sportradar MLB API – External data source

- setuptools – Packaging and entry point management


🛠️ Installation
## 1) Clone with:
### HTTPS
- git clone https://github.com/Vincent-Crescente/MLB_StrikeZone_App.git

### SSH
- git clone git@github.com:Vincent-Crescente/MLB_StrikeZone_App.git

***

## 2) `cd /MLB_StrikeZone_App` <br>

### (Optional) Create Virtual Environment:
`python -m venv {venv}` # (name it anything you like)

2.1) Activate the virtual environment <br>
- On macOS/Linux: <br>
`source {venv}/bin/activate` <br>
- On Windows: <br>
`.\{venv}\Scripts\activate` <br><br>

### 3) After activating download the required dependencies: <br>
`pip install -r requirements.txt`

### Without VENV 
Not RECOMMENDED - Download the required dependencies to your local packages with the
same command just without being in the active venv. <br>

🚀 Usage <br>

### Arguments

| Arg              | Required | Description                                      |
|------------------|----------|--------------------------------------------------|
| `--api_key`      | Yes      | Your Sportradar API key.                         |
| `--access_level` | No       | Set to `trial` (default) or `production`.        |

>> Run the program with: <br>
>> `python -m mlb_strikezone_app.main --api_key YOUR_API_KEY [--access_level trial|production]`
* Running it as a module allows for easier transition to a package.

## Alternatively, create a .env file to rid arguments:

1) Create file:
- `touch .env` or
`echo.>.env` for windows <br><br>
2) Open .env and add your credentials:: <br>
`API_KEY=your_api_key_here` <br>
`ACCESS_LEVEL=trial # or production` <br><br>
3) Once created run with: <br>
`python -m mlb_strikezone_app.main` <br><br>
***

💡 Developer Notes <br>

Modifying the StrikeZone display easily by avoiding API calls by adding dummy data to the
class calls at the bottom of strike_zone.py:<br>
Just call: `python mlb_strikezone_app/strike_zone.py` <br>

This project includes a setup.py file, 
which is used for packaging and distribution. 
While it’s not currently published to PyPI, 
it allows for easy local installation with `pip install -e .` and could be used to turn this into a PyPI package at a later time.

* Considering the entry point is 'strikezone' once `pip install -e .` is used with .env configured the program can be run with just the call `strikezone`

Feel free to explore or utilize the setup.py as you see fit!

* Red strike in the middle is the default for no data.

***

🧠 Future Improvements
- Show runners on base (text or visual).

- Display batter stats (AVG, OPS+, plate appearances).

- Package for PyPI.

- Dockerize the application.
***

## Nuances in the SportsRadar API

1) ### Rapid Play-by-Play Updates
   The play-by-play API uses a 2-second TTL, meaning data can update very frequently. Because of this, a play might still be in progress when the data is fetched—so the result (e.g., out, single, double) may not yet be finalized.

If the program refreshes during this time, you might see something like the image below:

![pending_info.png](images%2Fpending_info.png)

Yes, the metrics may appear off and the outcome unclear—but that’s expected behavior. This is what the API returns while the play is unfolding. After the program’s next refresh (every 20 seconds), the data should correct itself and reflect the finalized result.

* Yes the metrics look odd and the play outcome is quite ambiguous but this is what is sent
while a play is in play at the moment we request data. After the programs 20 second refresh the
data should update and make sense.

2) ### Downtime Moments
   If you select a game during a pause in action—such as the seventh-inning stretch or the national anthem—you might see something like this:

![inning_but_no_play_data.JPG](images%2Finning_but_no_play_data.JPG)

📝 License

This project is licensed under the [MIT License](LICENSE).