# from strike_zone as strike_zone # Uncomment this line to run with `python main.py` from mlb_strikezone_app folder
from mlb_strikezone_app.strike_zone import tk, StrikeZone_Updates, windll  # comment this out if uncommenting above
import argparse
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


def run(api_key, access_level):
    root = tk.Tk()
    root.geometry("300x700")
    windll.shcore.SetProcessDpiAwareness(1)
    app = StrikeZone_Updates(root, api_key, access_level)
    app.update_live_data(True)
    root.mainloop()


def main():
    api_key_from_env = os.getenv("API_KEY")
    access_level_from_env = os.getenv("ACCESS_LEVEL", "trial")  # Default to 'trial' if not found

    # Welcome text
    welcome_text = """
        Welcome to the StrikeZone App!\n\n
        • Please get a free API key if you don't already have one.\n
        • Go to https://console.sportradar.com/signup\n
        • Create a free account → Add trial → choose MLB API.\n
        • Your API key will appear on your Sportradar console page.\n\n
        Note: The program refreshes every 20 seconds. The background flashes red letting you know the program has:\n\n
        • Refreshed data shown\n
        • Updated live games dropdown
        
        *** Can use API KEY on command line or .env file. See README.md.
        """
    parser = argparse.ArgumentParser(
        description=welcome_text,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--api_key", dest='api_key', type=str, help="Your Sportradar API key")
    parser.add_argument("--access_level", dest='access_level', type=str, default="trial",
                        help="API access level (e.g., trial, production)")

    args = parser.parse_args()

    print("Starting live MLB pitch stream...")
    print(f"Using access level: {args.access_level}")

    if api_key_from_env:
        api_key = api_key_from_env
        access_level = access_level_from_env
        run(api_key, access_level)

    elif args.api_key:
        api_key = args.api_key
        access_level = args.access_level
        run(api_key, access_level)

    else:
        print("Must have api_key. Will look in .env first then arguments. Access level 'trial' is default. \n"
              "Go to https://console.sportradar.com/signup .\n"
              "Create a free account > Add trial > choose MLB API.\n"
              "Once chosen a API key will seen in your SportsRadar console page.")


if __name__ == "__main__":
    main()
