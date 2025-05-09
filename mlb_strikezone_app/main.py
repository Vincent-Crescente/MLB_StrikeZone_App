import strike_zone


if __name__ == "__main__":
    print("Starting live MLB pitch stream...")

    access_level = 'trial'
    api_key = ''

    root = strike_zone.tk.Tk()
    strike_zone.windll.shcore.SetProcessDpiAwareness(1)
    app = strike_zone.StrikeZone_Updates(root, api_key, access_level)
    app.update_live_data()
    root.mainloop()

