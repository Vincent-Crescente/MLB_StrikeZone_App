import json
import requests
import tkinter as tk
from ctypes import windll
from PIL import Image, ImageTk


with open('./play_outcome_codes.json', 'r') as file:
    play_outcome_codes = json.load(file)

with open('./teams.json', 'r') as file:
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
    Draws and initializes components of the tkinter window, including the strike zone image
    and an informational display section below it.

       Attributes:
        root (tk.Tk): The main tkinter window.
        canvas_width (int): Width of the canvas for strike zone display.
        canvas_height (int): Height of the canvas for strike zone display.
        container (tk.Frame): A frame to hold the dropdown and canvas.
        itemChecked (tk.StringVar): Stores the selected game from the dropdown menu.
        trace_id (str): A string to optionally store a game identifier.
        drop (tk.OptionMenu): Dropdown menu for selecting a live game.
        canvas (tk.Canvas): Canvas widget where the strike zone image and pitch dots are drawn.
        background_image (PIL.Image): The loaded background image before conversion to PhotoImage.
        background_photo (ImageTk.PhotoImage): Converted image for display in tkinter.
        last_pitch_dot (object): Reference to the last pitch drawn on the canvas.
        center_x (int): X-coordinate of the center of the canvas.
        center_y (int): Y-coordinate of the center of the canvas.
        away_vs_home_label (tk.Label): Label showing the current match (away vs home).
        score_label (tk.Label): Label displaying the current score.
        inning_label (tk.Label): Label showing the current inning.
        hitter_pitcher_label (tk.Label): Label for current hitter vs. pitcher info.
        count_label (tk.Label): Label displaying the pitch count (balls/strikes/outs).
        last_pitch_label (tk.Label): Label for details about the last pitch.
        pitch_outcome_label (tk.Label): Label showing the result of the last pitch.
        play_outcome_label (tk.Label): Label describing the result of the play (if applicable).

    """
    def __init__(self, root):
        """
        Info
        :param root:
        """
        self.root = root
        self.root.title("Strike Zone")
        self.canvas_width = 235
        self.canvas_height = 300

        # Container frame to hold dropdown and canvas
        self.container = tk.Frame(self.root)
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
        self.background_image = Image.open("./strike_zone.JPG")
        self.background_image = self.background_image.resize((self.canvas_width, self.canvas_height), Image.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.canvas.create_image(6, 6, anchor=tk.NW, image=self.background_photo)

        self.last_pitch_dot = None
        self.center_x = self.canvas_width // 2
        self.center_y = self.canvas_height // 2

        # --- Modern Styled Info Section ---
        info_frame = tk.Frame(self.container, bg="white", padx=12, pady=12, highlightbackground="#ccc", highlightthickness=1)
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
        self.away_vs_home_label = tk.Label(info_frame, font=("Helvetica", 14, "bold"), justify="center", bg="white", wraplength=250)
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


class StrikeZone_Updates(StrikeZone, MLB_API_Calls):
    """
    A GUI class for displaying real-time MLB pitch data using the StrikeZone canvas and Sportradar API.

    Inherits from:
        StrikeZone: GUI rendering of the strike zone.
        MLB_API_Calls: API interface for fetching MLB game and pitch data.
    """

    def __init__(self, root, api_key, access_level):
        """
        Initialize the StrikeZone_Updates class.

        Args:
            root (tk.Tk): The root tkinter window.
            api_key (str): API key for Sportradar access.
            access_level (str): Access level for the API (e.g., 'trial' or 'production').
        """
        MLB_API_Calls.__init__(self, api_key, access_level)
        StrikeZone.__init__(self, root)
        self.last_out = 'N/A'
        self.currently_displayed_game_id = 'No Live Games'
        self.get_live_games(teams)
        self.display_live_games()

    def get_latest_inning(self, game_data):
        """
        Get the latest inning and half from game data.

        Args:
            game_data (dict): The full play-by-play game data from the API.

        Returns:
            tuple: (inning_dict, half_dict, error_msg or None)
        """
        innings = game_data.get('innings', [])
        if not innings:
            return None, None, "No innings data found."

        last_inning = innings[-1]
        halfs = last_inning.get('halfs', [])
        if not halfs:
            return None, None, "Next inning coming up."

        last_half = halfs[1] if halfs[-1].get("events") else halfs[0]
        return last_inning, last_half, None

    def stream_latest_pitch_and_info(self, game_id):
        """
        Stream the most recent pitch data from a given game.

        Args:
            game_id (str): The ID of the selected game.

        Returns:
            dict or None: A dictionary of summarized pitch and game information.
        """
        game_data = self.get_pbp_data(game_id)
        inning, half_data, error = self.get_latest_inning(game_data)
        if error:
            print(error)
            return

        events = half_data.get('events', [])
        half = "Top" if half_data.get('half', '') == 'T' else "Bottom"
        inning_number = inning.get('number', 'N/A')

        if not events:
            print(f"No events yet in the {half} of the {inning_number}.")
            return

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
            print("refreshed current game.")
        else:
            self.currently_displayed_game_id = selected_game_id
            pitch_summary = self.stream_latest_pitch_and_info(self.currently_displayed_game_id)
            self.play_summary(pitch_summary)
            print("changed game.")

    def display_live_games(self):
        """
        Displays games in a dropdown menu above the strike zone, refreshing every 20 seconds.
        """
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

        print(f"Placing dot at (x={x:.1f}, y={y:.1f})")

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
        if not events:
            return {
                "inning_number": "N/A",
                "inning_half": '',
                "home_team_score": "N/A",
                "away_team_score": "N/A",
                "hitter": '',
                "pitcher": '',
                "balls": self.last_out,
                "strikes": 0,
                "outs": "N/A",
                "ball_strike_or_foul": 'N/A',
                "pitch_type": "N/A",
                "pitch_speed": "N/A",
                "pitch_zone": -1,
                "pitch_x": 0,
                "pitch_y": 0,
                "pitch_outcome": "N/A",
                "description": at_bat.get('description', '')
            }

        hitter = at_bat.get('hitter', {})
        pitcher = at_bat.get('pitcher', {})
        hitter_name = f"{hitter.get('preferred_name', '')} {hitter.get('last_name', '')}"
        pitcher_name = f"{pitcher.get('preferred_name', '')} {pitcher.get('last_name', '')}"
        home_team_score = at_bat.get('score', {}).get('home_team_runs', 'N/A')
        away_team_score = at_bat.get('score', {}).get('away_team_runs', 'N/A')

        last_event = events[-1]
        count = last_event.get('count', {})
        balls = count.get('balls', 0)
        strikes = count.get('strikes', 0)
        outs = count.get('outs', '')
        if outs == '':
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

    def update_live_data(self):
        """
        Fetch the latest list of live games and update the GUI every 20 seconds.
        """
        try:
            self.get_live_games(teams)
            self.display_live_games()
            self.option_changed()
        except Exception as e:
            print("Error updating live data:", e)

        self.root.after(20000, self.update_live_data)


if __name__ == "__main__":
    root1 = tk.Tk()
    access_level = 'trial'
    api_key = ''

    windll.shcore.SetProcessDpiAwareness(1)
    app = StrikeZone_Updates(root1, api_key, access_level) # calls both classes
    # # Example - Making Sure UI looks good.
    app.live_games_dict = {'Detroit Tigers vs(@) Houston Astros': '862d312c-6837-451e-9e10-adee8ac657cf', 'Miami Marlins vs(@) Los Angeles Dodgers': '098a00b4-2ce9-4bfb-a864-fdb9ca866213'}
    #app.display_live_games()
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
