import os
import json
import requests
import tkinter as tk
from tkinter import font
from ctypes import windll
from PIL import Image, ImageTk

# Get the directory of the current script (strike_zone.py)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full paths to the JSON files
play_outcomes_file_path = os.path.join(script_dir, 'play_outcome_codes.json')
teams_file_path = os.path.join(script_dir, 'teams.json')
strike_zone_picture_path = os.path.join(script_dir, 'strike_zone.JPG')

# Now open the file using the absolute path
with open(play_outcomes_file_path, 'r') as file:
    play_outcome_codes = json.load(file)

with open(teams_file_path, 'r') as file:
    teams = json.load(file)


class MLB_API_Calls:
    """
      A class to interact with the Sportradar MLB API for fetching team data,
      today's live games, and pitch-by-pitch (PBP) data.

      Attributes:
          api_key (str): API key for authenticating requests to Sportradar.
          access_level (str): Access level for the API (e.g., 'trial', 'production').
          live_games_dict (dict): Dictionary mapping game matchups to game IDs.
          games_url (str): URL for fetching today's game schedule.
          teams_url (str): URL for fetching all MLB teams.
      """

    def __init__(self, api_key, access_level):
        from datetime import datetime
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")  # zero-padded month
        day = now.strftime("%d")  # zero-padded day
        self.live_games_dict = {}
        self.access_level = access_level
        self.api_key = api_key
        self.games_url = f"https://api.sportradar.com/mlb/{self.access_level}/v8/en/games/{year}/{month}/{day}/schedule.json?api_key={self.api_key}"
        self.teams_url = f"https://api.sportradar.com/mlb/{self.access_level}/v8/en/league/teams.json?api_key={self.api_key}"

    def get_teams(self):
        """
        Fetch all MLB teams and return a mapping of team IDs to full team names.

        Returns:
            dict: A dictionary with team IDs as keys and team names as values.

        Example:
            # api = MLB_API_Calls(api_key="your_api_key", access_level="trial")
            # teams = api.get_teams()
            # isinstance(teams, dict)
            True
        """
        all_teams_temp = {}
        with requests.get(self.teams_url, headers={"accept": "application/json"}) as r:
            for team in r.json()['teams']:
                all_teams_temp[team.get('id')] = team.get('market', ' ') + " " + team.get('name', ' ')
        return all_teams_temp

    def get_live_games(self, all_teams):
        """
       Update the live_games_dict with currently in-progress MLB games.

       Args:
           all_teams (dict): A dictionary of team IDs to team names.
       """
        with requests.get(self.games_url, headers={"accept": "application/json"}) as r:
            for game in r.json().get('games', []):
                if game.get('status') == 'inprogress':
                    game_id = game.get('id')
                    home_team = all_teams[game.get('home_team').strip()]
                    away_team = all_teams[game.get('away_team').strip()]
                    key = f"{away_team.strip()} vs(@) {home_team.strip()}"
                    self.live_games_dict[key] = game_id

    def get_pbp_data(self, game_id):
        """
        Fetch the pitch-by-pitch (PBP) data for a specific game.

        Args:
            game_id (str): The unique identifier of the game.

        Returns:
            dict: A dictionary containing the PBP data for the game.
        """
        url = f"https://api.sportradar.com/mlb/{self.access_level}/v8/en/games/{game_id}/pbp.json?api_key={self.api_key}"
        response = requests.get(url, headers={"accept": "application/json"})
        return response.json().get('game', {})


class StrikeZone:
    """
      A graphical user interface for displaying a strike zone and real-time pitch data
      using Tkinter. This class sets up the canvas, background image, and an informational
      display section for game details such as score, inning, and pitch outcomes.

      Attributes:
          root (tk.Tk): The main application window.
          canvas_width (int): Width of the canvas where the strike zone is drawn.
          canvas_height (int): Height of the canvas.
          container (tk.Frame): Parent frame holding the dropdown and canvas elements.
          itemChecked (tk.StringVar): Tracks the currently selected game in the dropdown.
          trace_id (str): Optional string identifier for the game or session.
          drop (tk.OptionMenu): Dropdown menu for selecting live MLB games.
          canvas (tk.Canvas): Area for rendering the strike zone image and pitch dots.
          background_image (PIL.Image): Loaded strike zone image before conversion.
          background_photo (ImageTk.PhotoImage): Tkinter-compatible image used in the canvas.
          last_pitch_dot (object): Reference to the last drawn pitch indicator on the canvas.
          center_x (int): X-coordinate for the center of the canvas.
          center_y (int): Y-coordinate for the center of the canvas.
          away_vs_home_label (tk.Label): Displays the team matchup (away vs home).
          score_label (tk.Label): Displays the current score of the game.
          inning_label (tk.Label): Displays the current inning and half.
          hitter_pitcher_label (tk.Label): Displays current hitter and pitcher matchup.
          count_label (tk.Label): Displays pitch count: balls, strikes, and outs.
          last_pitch_label (tk.Label): Displays information about the most recent pitch.
          pitch_outcome_label (tk.Label): Describes the outcome of the last pitch.
          play_outcome_label (tk.Label): Describes the outcome of the play, if applicable.
      """

    def __init__(self, root):
        """
        Initializes the StrikeZone GUI with a dropdown menu, canvas displaying
        a strike zone image, and an informational section showing game data.
        Also displays an instructional overlay on first load.

        Args:
            root (tk.Tk): The root window for the application.
        """
        self.root = root
        self.root.title("Strike Zone")
        self.canvas_width = 240
        self.canvas_height = 300

        #
        def close_overlay():
            overlay_frame.destroy()

        # Container frame to hold dropdown and canvas
        self.container = tk.Frame(self.root)
        self.defaultbg = root.cget('bg')
        self.container.pack()

        # StringVar to hold selected game
        self.itemChecked = tk.StringVar()
        self.itemChecked.set("No Live Games")
        self.trace_id = ''

        self.drop = tk.OptionMenu(self.container, self.itemChecked, *['No Live Games'])
        self.drop.pack(fill='x')

        self.canvas = tk.Canvas(self.container, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(pady=(10, 5))

        # Load and place the background image
        self.background_image = Image.open(strike_zone_picture_path)
        self.background_image = self.background_image.resize((self.canvas_width, self.canvas_height), Image.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.canvas.create_image(6, 6, anchor=tk.NW, image=self.background_photo)

        self.last_pitch_dot = None
        self.center_x = self.canvas_width // 2
        self.center_y = self.canvas_height // 2

        # --- Modern Styled Info Section ---
        info_frame = tk.Frame(self.container, bg="white", padx=12, pady=12, highlightbackground="#ccc",
                              highlightthickness=1)
        info_frame.pack(padx=10, pady=(10, 20), fill="both", expand=True)

        # Shared label styling (excluding font, so it's not duplicated)
        label_style = {
            "bg": "white",
            "fg": "black",
            "wraplength": 250,
            "justify": "left",
            "anchor": "w"
        }

        # Team matchup
        self.away_vs_home_label = tk.Label(info_frame, font=("Helvetica", 14, "bold"), justify="center", bg="white",
                                           wraplength=250)
        self.away_vs_home_label.pack(pady=(0, 6))

        # Score and inning
        self.score_label = tk.Label(info_frame, font=("Helvetica", 14), justify="center", bg="white", wraplength=250)
        self.score_label.pack(pady=(0, 4))

        self.inning_label = tk.Label(info_frame, font=("Helvetica", 12), justify="center", bg="white", wraplength=250)
        self.inning_label.pack(pady=(0, 8))

        # Hitter vs. pitcher (bold, so separate styling)
        self.hitter_pitcher_label = tk.Label(info_frame,
                                             font=("Helvetica", 12, "bold"),
                                             **label_style)
        self.hitter_pitcher_label.pack(pady=(0, 4))

        # Remaining labels
        self.count_label = tk.Label(info_frame, font=("Helvetica", 12), **label_style)
        self.count_label.pack(pady=(0, 4))

        self.last_pitch_label = tk.Label(info_frame, font=("Helvetica", 12), **label_style)
        self.last_pitch_label.pack(pady=(0, 4))

        self.pitch_outcome_label = tk.Label(info_frame, font=("Helvetica", 12), **label_style)
        self.pitch_outcome_label.pack(pady=(0, 4))

        self.play_outcome_label = tk.Label(info_frame, font=("Helvetica", 12), **label_style)
        self.play_outcome_label.pack(pady=(0, 4))

        # Overlay frame (centered)
        overlay_frame = tk.Frame(root, width=200, height=600, bg="#f0f0f0", bd=2, relief="raised")
        overlay_frame.place(relx=0.5, rely=0.4, anchor="center")

        # Close ("X") button styled smaller and placed top-right
        close_button = tk.Button(overlay_frame, text="✕", command=close_overlay, font=("Arial", 10), bd=0, bg="#f0f0f0",
                                 relief="flat", fg="black", activebackground="#d0d0d0")
        close_button.place(relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)

        # Welcome text
        welcome_text = (
            "Welcome to the StrikeZone App!\n\n"
            "• Please get a free API key if you don't already have one.\n"
            "• Go to https://console.sportradar.com/signup\n"
            "• Create a free account → Add trial → choose MLB API.\n"
            "• Your API key will appear on your Sportradar console page.\n\n"
            "Note: The program refreshes every 20 seconds. The background flashes red letting you know the program has:\n\n"
            "• Refreshed data shown\n"
            "• Updated live games dropdown"
        )

        # Custom font and text label
        custom_font = font.Font(family="Arial", size=12)
        welcome_label = tk.Label(overlay_frame, text=welcome_text, bg="#f0f0f0", justify="left", anchor="w",
                                 font=custom_font, wraplength=240)
        welcome_label.pack(padx=20, pady=20, fill="both")

        #


class StrikeZone_Updates(StrikeZone, MLB_API_Calls):
    """
       Extension of StrikeZone that integrates real-time MLB pitch tracking
       using the Sportradar API.

       Inherits:
           StrikeZone: Handles GUI rendering and layout.
           MLB_API_Calls: Manages API calls to fetch live game and pitch-by-pitch data.

       Attributes:
           currently_displayed_game_id (str): ID of the game currently shown in the UI.
           last_out (str): Keeps track of the last recorded out.
           last_inning (str): Keeps track of the last recorded inning.
       """

    def __init__(self, root, api_key, access_level):
        """
       Initializes the StrikeZone_Updates instance, connecting GUI elements with live data.

       Args:
           root (tk.Tk): The root window for the application.
           api_key (str): The user's Sportradar API key.
           access_level (str): The API access level (e.g., "trial" or "production").
       """
        MLB_API_Calls.__init__(self, api_key, access_level)
        StrikeZone.__init__(self, root)
        self.currently_displayed_game_id = 'No Live Games'
        # self.get_live_games(teams)
        # self.display_live_games()
        self.last_out = 'N/A'
        self.last_inning = 'N/A'

    def get_latest_inning(self, game_data):
        """
        Extracts the most recent inning and half-inning data from the full game object.

        Args:
            game_data (dict): A full play-by-play response from the API.

        Returns:
            tuple:
                - inning_dict (dict or None): The most recent inning's data.
                - half_dict (dict or None): The most recent half-inning's data.
                - error_msg (str or None): Error message if inning data is not found.
        """
        innings = game_data.get('innings', [])
        if not innings:
            return None, None, "No innings data found."

        last_inning = innings[-1]
        halfs = last_inning.get('halfs', [])
        if not halfs:
            return None, None, "Inning coming up."

        last_half = halfs[1] if halfs[-1].get("events") else halfs[0]
        #print("Last Inning:", last_inning.get('number', 'not here'), "Last Half:", last_half.get('half', 'not here'))
        return last_inning, last_half, None

    def stream_latest_pitch_and_info(self, game_id):
        """
        Fetches and summarizes the most recent pitch and game context data for a given game.

        Args:
            game_id (str): Unique identifier for the selected MLB game.

        Returns:
            dict: A dictionary summarizing the most recent pitch, including:
                - inning_number (str)
                - inning_half (str)
                - home_team_score (str)
                - away_team_score (str)
                - hitter (str)
                - pitcher (str)
                - balls (str)
                - strikes (str)
                - outs (str)
                - ball_strike_or_foul (str)
                - pitch_type (str)
                - pitch_speed (str)
                - pitch_zone (int)
                - pitch_x (float)
                - pitch_y (float)
                - pitch_outcome (str)
                - description (str)
                Or a message-only fallback if no pitch data is currently available.
        """
        #print(game_id)
        game_data = self.get_pbp_data(game_id)
        inning, half_data, error = self.get_latest_inning(game_data)
        if error:
            error_summary = {
                "inning_number": f"{error}",
                "inning_half": '',
                "home_team_score": "",
                "away_team_score": "",
                "hitter": '',
                "pitcher": '',
                "balls": '',
                "strikes": '',
                "outs": "",
                "ball_strike_or_foul": '',
                "pitch_type": "",
                "pitch_speed": "",
                "pitch_zone": -1,
                "pitch_x": 0,
                "pitch_y": 0,
                "pitch_outcome": '',
                "description": ''
            }
            #print(error)
            return error_summary

        events = half_data.get('events', [])
        half = "Top" if half_data.get('half', '') == 'T' else "Bottom"
        inning_number = inning.get('number', 'N/A')
        if not events:
            error_summary = {
                "inning_number": f"No events yet in the {half} of the {inning_number}.",
                "inning_half": '',
                "home_team_score": "",
                "away_team_score": "",
                "hitter": '',
                "pitcher": '',
                "balls": '',
                "strikes": '',
                "outs": "",
                "ball_strike_or_foul": '',
                "pitch_type": "",
                "pitch_speed": "",
                "pitch_zone": -1,
                "pitch_x": 0,
                "pitch_y": 0,
                "pitch_outcome": '',
                "description": ''
            }
            #print(f"No events yet in the {half} of the {inning_number}.")
            return error_summary

        at_bat = events[-1].get('at_bat', {})
        summary = self.summarize_at_bat(at_bat, inning_number, half)

        return summary

    def update_away_vs_home_text(self, text):
        """
        Update the away vs home team label.

        Args:
            text (str): Text to display.
        """
        text_var = tk.StringVar()
        text_var.set(text)
        self.away_vs_home_label.config(text=text)

    def update_score_text(self, text):
        """Update the score label."""
        text_var = tk.StringVar()
        text_var.set(text)
        self.score_label.config(text=text)

    def update_inning_text(self, text):
        """Update the inning label."""
        text_var = tk.StringVar()
        text_var.set(text)
        self.inning_label.config(text=text)

    def update_hitter_pitcher_text(self, text):
        """Update the hitter vs pitcher label."""
        text_var = tk.StringVar()
        text_var.set(text)
        self.hitter_pitcher_label.config(text=text)

    def update_count_text(self, text):
        """Update the balls-strikes-outs count label."""
        text_var = tk.StringVar()
        text_var.set(text)
        self.count_label.config(text=text)

    def update_last_pitch_text(self, text):
        """Update the last pitch information label."""
        text_var = tk.StringVar()
        text_var.set(text)
        self.last_pitch_label.config(text=text)

    def update_pitch_outcome_text(self, text):
        """Update the pitch outcome label."""
        text_var = tk.StringVar()
        text_var.set(text)
        self.pitch_outcome_label.config(text=text)

    def update_play_outcome_text(self, text):
        """Update the play outcome label."""
        text_var = tk.StringVar()
        text_var.set(text)
        self.play_outcome_label.config(text=text)

    def option_changed(self, *args):
        """
        Called when a new game is selected from the dropdown.
        Updates the currently displayed game and fetches new pitch data.
        """
        selected_game = self.itemChecked.get()

        if selected_game == 'No Live Games':
            return

        selected_game_id = self.live_games_dict.get(selected_game)
        if selected_game_id == self.currently_displayed_game_id:
            pitch_summary = self.stream_latest_pitch_and_info(self.currently_displayed_game_id)
            self.play_summary(pitch_summary)
        else:
            self.currently_displayed_game_id = selected_game_id
            pitch_summary = self.stream_latest_pitch_and_info(self.currently_displayed_game_id)
            self.play_summary(pitch_summary)

    def display_live_games(self):
        """
        Updates the dropdown menu with currently live MLB games. This method refreshes the list
        approximately every 20 seconds.

        If the application is run directly (e.g., via `strike_zone.py`) without setting an API key,
        a dummy list of games will be displayed. This allows developers to work on the UI or add features
        without consuming Sportradar API calls, which are rate-limited.

        Behavior:
        - If `self.api_key` is empty: populates dropdown with dummy games from `self.live_games_dict`.
        - If `self.api_key` is set: uses live data and updates the menu based on currently active games.
        - If no games are available: displays "No Live Games" in the dropdown.
        """
        if self.api_key == '':
            games = list(self.live_games_dict.keys())
            menu = self.drop["menu"]
            menu.delete(0, "end")
            for opt in games:
                menu.add_command(label=opt, command=lambda val=opt: self.itemChecked.set(val))
            self.itemChecked.set(games[0])
            return

        games = list(self.live_games_dict.keys())
        currently_displayed_game = self.itemChecked.get()

        if currently_displayed_game in games:
            menu = self.drop["menu"]
            menu.delete(0, "end")
            if self.trace_id:
                self.itemChecked.trace_remove('write', self.trace_id)

            for opt in games:
                menu.add_command(label=opt, command=lambda val=opt: self.itemChecked.set(val))

            self.itemChecked.set(currently_displayed_game)
            self.trace_id = self.itemChecked.trace_add("write", self.option_changed)

        elif currently_displayed_game == 'No Live Games' and games:
            menu = self.drop["menu"]
            menu.delete(0, "end")
            if self.trace_id:
                self.itemChecked.trace_remove('write', self.trace_id)

            for opt in games:
                menu.add_command(label=opt, command=lambda val=opt: self.itemChecked.set(val))

            self.itemChecked.set(games[0])
            self.trace_id = self.itemChecked.trace_add("write", self.option_changed)
        else:
            self.itemChecked.set('No Live Games')

    def add_pitch(self, pitch_x, pitch_y, ball_strike_foul):
        """
        Plot a pitch dot on the canvas using coordinates and pitch result.

        Args:
            pitch_x (float): Horizontal location of the pitch.
            pitch_y (float): Vertical location of the pitch.
            ball_strike_foul (str): Result of the pitch ('Ball', 'Strike', etc.).
        """
        x = self.center_x - (pitch_x / 300) * (self.canvas_width / 2)
        y = self.center_y - (pitch_y / 200) * (self.canvas_height / 2)

        # print(f"Placing dot at (x={x:.1f}, y={y:.1f})")

        if self.last_pitch_dot is not None:
            self.canvas.delete(self.last_pitch_dot)

        radius = 9.5
        red = "#E53935"
        green = "#43A047"
        if ball_strike_foul == 'Strike' or ball_strike_foul == 'Foul Ball':
            pitch_color = red
        elif ball_strike_foul == 'Ball':
            pitch_color = green
        else:
            pitch_color = red

        self.last_pitch_dot = self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius, fill=pitch_color, outline='black'
        )

    def play_summary(self, pitch_summary):
        """
        Update all GUI fields with the latest pitch summary.

        Args:
            pitch_summary (dict): Dictionary with pitch, score, and player info.
        """
        self.update_away_vs_home_text(f"{self.itemChecked.get()}")
        self.update_score_text(f"{pitch_summary['away_team_score']} - {pitch_summary['home_team_score']}")
        self.update_inning_text(f"{pitch_summary['inning_half']} - {pitch_summary['inning_number']}")
        self.update_hitter_pitcher_text(f"{pitch_summary['pitcher']} vs {pitch_summary['hitter']}")
        self.update_count_text(
            f"COUNT: {pitch_summary['balls']}-{pitch_summary['strikes']}, OUTS: {pitch_summary['outs']}")
        self.update_last_pitch_text(
            f"Last Pitch: {pitch_summary['pitch_type']} at {pitch_summary['pitch_speed']} mph")
        self.update_pitch_outcome_text(f"Pitch Outcome: {pitch_summary['pitch_outcome']}")
        self.update_play_outcome_text(f"Play Outcome: {pitch_summary['description']}")
        self.add_pitch(pitch_summary['pitch_x'], pitch_summary['pitch_y'], pitch_summary['ball_strike_or_foul'])

    def summarize_at_bat(self, at_bat, inning_number, half):
        """
        Parse and summarize at-bat data for GUI rendering.

        Args:
            at_bat (dict): Dictionary containing at-bat and pitch data.
            inning_number (int or str): Inning number of the event.
            half (str): 'Top' or 'Bottom' half of the inning.

        Returns:
            dict: Summary of batter, pitcher, pitch type, count, and scores.
        """
        events = at_bat.get('events', [])
        hitter = at_bat.get('hitter', {})
        pitcher = at_bat.get('pitcher', {})
        hitter_name = f"{hitter.get('preferred_name', '')} {hitter.get('last_name', '')}"
        pitcher_name = f"{pitcher.get('preferred_name', '')} {pitcher.get('last_name', '')}"
        home_team_score = at_bat.get('score', {}).get('home_team_runs', 'N/A')
        away_team_score = at_bat.get('score', {}).get('away_team_runs', 'N/A')
        if not events:
            return {
                "inning_number": inning_number,
                "inning_half": half,
                "home_team_score": home_team_score,
                "away_team_score": away_team_score,
                "hitter": hitter_name,
                "pitcher": pitcher_name,
                "balls": '',
                "strikes": '',
                "outs": self.last_out,
                "ball_strike_or_foul": '',
                "pitch_type": "",
                "pitch_speed": "",
                "pitch_zone": -1,
                "pitch_x": 0,
                "pitch_y": 0,
                "pitch_outcome": "",
                "description": at_bat.get('description', '')
            }

        last_event = events[-1]
        count = last_event.get('count', {})
        balls = count.get('balls', 0)
        strikes = count.get('strikes', 0)
        outs = count.get('outs', '')
        if outs == '':
            if self.last_inning == inning_number:
                outs = self.last_out
        else:
            self.last_out = outs

        mlb_pitch_data = last_event.get('mlb_pitch_data', {})
        pitch_type = mlb_pitch_data.get('description', 'Unknown')
        pitch_zone = mlb_pitch_data.get('zone', -1)
        pitch_speed = last_event.get('pitcher', {}).get('pitch_speed', 0)
        pitch_x = last_event.get('pitcher', {}).get('pitch_x', 0)
        pitch_y = last_event.get('pitcher', {}).get('pitch_y', 0)
        pitch_outcome = play_outcome_codes.get(last_event.get('outcome_id'), 'Unknown')

        if pitch_outcome in ['Strike', ' Foul Ball']:
            ball_strike_or_foul = 'Strike'
        elif "Ball" in pitch_outcome:
            ball_strike_or_foul = 'Ball'
        else:
            ball_strike_or_foul = 'N/A'

        return {
            "inning_number": inning_number,
            "inning_half": half,
            "home_team_score": home_team_score,
            "away_team_score": away_team_score,
            "hitter": hitter_name,
            "pitcher": pitcher_name,
            "balls": balls,
            "strikes": strikes,
            "outs": outs,
            "ball_strike_or_foul": ball_strike_or_foul,
            "pitch_type": pitch_type,
            "pitch_speed": pitch_speed,
            "pitch_zone": pitch_zone,
            "pitch_x": pitch_x,
            "pitch_y": pitch_y,
            "pitch_outcome": pitch_outcome,
            "description": at_bat.get('description', '')
        }

    def change_bg(self, color):
        """
        Change the background color of the container.

        Args:
            color (str): The color to change the background to.
        """
        self.container.configure(bg=color)

    def update_live_data(self, suppress_flash):
        """
        Refresh the GUI with the latest live games and schedule the next update.

        If `suppress_flash` is False, briefly change the background to red to show a refresh,
        then restore it after 4 seconds.

        Args:
            suppress_flash (bool): Skip red flash if True.

        Exceptions:
            Prints any errors during the update process.
        """
        try:
            if not suppress_flash:
                self.change_bg('red')
            self.container.after(4000, lambda: self.change_bg(self.defaultbg))  # Restore to white after 4 seconds
            self.get_live_games(teams)
            self.display_live_games()
            self.option_changed()
        except Exception as e:
            print("Error updating live data:", e)

        self.root.after(20000, lambda: self.update_live_data(False))


if __name__ == "__main__":

    root1 = tk.Tk()
    root1.geometry("300x700")
    access_level = 'trial'
    api_key = ''

    windll.shcore.SetProcessDpiAwareness(1) # Makes strike oval a little sharper visually.
    app = StrikeZone_Updates(root1, api_key, access_level)  # calls both classes

    # Dummy data that fills up the window for dev purposes if strike_zone.py is run alone.
    # Allows for changes to the window with data that isn't pulled from the api, which would waist a call.
    app.live_games_dict = {'New York Yankees vs(@) New York Mets': '1234567-6837-451e-9e10-adee8ac657cf',
                           'Miami Marlins vs(@) Los Angeles Dodgers': '12345678-2ce9-4bfb-a864-fdb9ca866213'}
    app.display_live_games()
    app.update_away_vs_home_text('New York Yankees vs(@) New York Mets')
    app.update_score_text('10 - 9')
    app.update_inning_text('Top 3')
    app.add_pitch(61, -100, 'Strike')
    app.update_hitter_pitcher_text('Carlos Carasco vs Pete Alonso')
    app.update_count_text('COUNT: 3-2, OUTS: 2')
    app.update_last_pitch_text('Last Pitch: FastBall - 98 mph')
    app.update_pitch_outcome_text('Pitch Outcome: Foul Ball')
    app.update_play_outcome_text('Play Outcome: Foul Ball caught by Paul Goldschmidt.')
    root1.mainloop()
