MLB Strikezone App

A Python application that polls the Sportradar MLB API and displays a real-time visual strike zone, including descriptions of each pitch and its outcome.


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
`python3 -m venv {venv}` # (name it anything you like)

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
>> `python -m mlb_strikezone_app.main.py --api_key YOUR_API_KEY [--access_level trial|production]`
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
***

🧠 Future Improvements
- Show runners on base (text or visual).

- Display batter stats (AVG, OPS+, plate appearances).

- Package for PyPI.

- Dockerize the application.
***

📝 License

This project is licensed under the [MIT License](LICENSE).