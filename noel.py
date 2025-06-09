import tkinter as tk
from tkinter import ttk, messagebox, font
import json
from datetime import datetime

# --- Mock Data Simulation ---
# In a real application, this data would be fetched from a live sports API.
# I've created a comprehensive mock data structure to simulate this.
def get_mock_api_data(league):
    """
    Simulates fetching data from a sports API based on the selected league.
    """
    all_leagues_data = {
        "Premier League": {
            "teams": ["Manchester City", "Arsenal", "Liverpool", "Aston Villa", "Tottenham Hotspur", "Chelsea", "Newcastle United", "Manchester United", "West Ham United", "Crystal Palace"],
            "data": {
                "Manchester City": {
                    "attack_strength": 2.8, "defence_strength": 0.8,
                    "last_4": ["W", "W", "W", "D"],
                    "unavailable": ["Ederson (Injury)", "Kevin De Bruyne (Suspended)"]
                },
                "Manchester United": {
                    "attack_strength": 1.5, "defence_strength": 1.4,
                    "last_4": ["L", "D", "W", "L"],
                    "unavailable": ["Lisandro Martinez (Injury)"]
                },
                # Add more teams as needed
            }
        },
        "La Liga": {
             "teams": ["Real Madrid", "Barcelona", "Girona", "Atletico Madrid", "Athletic Club", "Real Sociedad"],
             "data": {
                "Real Madrid": {
                    "attack_strength": 2.5, "defence_strength": 0.7,
                    "last_4": ["W", "W", "D", "W"],
                    "unavailable": ["Thibaut Courtois (Injury)"]
                },
                "Barcelona": {
                    "attack_strength": 2.2, "defence_strength": 1.1,
                    "last_4": ["W", "L", "W", "W"],
                    "unavailable": ["Gavi (Injury)", "Pedri (Doubtful)"]
                }
             }
        },
        "Premier Soccer League (South Africa)": {
            "teams": ["Mamelodi Sundowns", "Orlando Pirates", "Kaizer Chiefs", "SuperSport United"],
            "data": {
                "Mamelodi Sundowns": {"attack_strength": 2.1, "defence_strength": 0.5, "last_4": ["W", "D", "W", "W"], "unavailable": []},
                "Orlando Pirates": {"attack_strength": 1.6, "defence_strength": 0.9, "last_4": ["W", "L", "D", "W"], "unavailable": ["Thembinkosi Lorch (Suspended)"]},
                "Kaizer Chiefs": {"attack_strength": 1.1, "defence_strength": 1.2, "last_4": ["D", "L", "L", "W"], "unavailable": ["Itumeleng Khune (Injury)"]},
            }
        },
        # Add other leagues here...
        "Serie A": {"teams": [], "data": {}},
        "UEFA Champions League": {"teams": [], "data": {}},
        "UEFA Nations League": {"teams": [], "data": {}},
        "AFCON": {"teams": [], "data": {}},
        "CAF Champions League": {"teams": [], "data": {}},
    }
    return all_leagues_data.get(league, {"teams": [], "data": {}})


class SoccerAnalyserApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Soccer Bet Analyser")
        self.geometry("800x600")
        self.configure(bg="#2E2E2E")

        # --- Font Configuration ---
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Helvetica", size=10)
        self.title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.header_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.result_font = font.Font(family="Helvetica", size=36, weight="bold")
        self.info_font = font.Font(family="Helvetica", size=9)

        # --- App Data ---
        self.leagues = [
            "Premier League", "La Liga", "Serie A",
            "UEFA Champions League", "UEFA Nations League", "AFCON",
            "CAF Champions League", "Premier Soccer League (South Africa)"
        ]
        self.bet_types = [
            "3-Way Result (Home Win)", "3-Way Result (Draw)", "3-Way Result (Away Win)",
            "First Team to Score (Home)", "First Team to Score (Away)",
            "Both Teams to Score (Yes)", "Both Teams to Score (No)",
            "Over/Under 3.0 (Over)", "Over/Under 3.0 (Under)"
        ]

        self.history = self.load_history()

        # --- UI Creation ---
        self._create_widgets()

    def _create_widgets(self):
        # Main container
        main_frame = tk.Frame(self, bg="#2E2E2E", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # --- Input Frame ---
        input_frame = tk.Frame(main_frame, bg="#3C3C3C", padx=15, pady=15)
        input_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        input_frame.columnconfigure(1, weight=1)

        tk.Label(input_frame, text="Bet Analysis Setup", font=self.title_font, bg="#3C3C3C", fg="#FFFFFF").grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="w")

        # League Selection
        tk.Label(input_frame, text="League:", bg="#3C3C3C", fg="#CCCCCC").grid(row=1, column=0, sticky="w", padx=(0,10))
        self.league_var = tk.StringVar()
        self.league_menu = ttk.Combobox(input_frame, textvariable=self.league_var, values=self.leagues, state="readonly")
        self.league_menu.grid(row=1, column=1, sticky="ew", pady=5)
        self.league_menu.bind("<<ComboboxSelected>>", self.update_teams)

        # Team Selection
        tk.Label(input_frame, text="Home Team:", bg="#3C3C3C", fg="#CCCCCC").grid(row=2, column=0, sticky="w", padx=(0,10))
        self.home_team_var = tk.StringVar()
        self.home_team_menu = ttk.Combobox(input_frame, textvariable=self.home_team_var, state="readonly")
        self.home_team_menu.grid(row=2, column=1, sticky="ew", pady=5)

        tk.Label(input_frame, text="Away Team:", bg="#3C3C3C", fg="#CCCCCC").grid(row=3, column=0, sticky="w", padx=(0,10))
        self.away_team_var = tk.StringVar()
        self.away_team_menu = ttk.Combobox(input_frame, textvariable=self.away_team_var, state="readonly")
        self.away_team_menu.grid(row=3, column=1, sticky="ew", pady=5)

        # Bet Type Selection
        tk.Label(input_frame, text="Bet Type:", bg="#3C3C3C", fg="#CCCCCC").grid(row=4, column=0, sticky="w", padx=(0,10))
        self.bet_type_var = tk.StringVar()
        self.bet_type_menu = ttk.Combobox(input_frame, textvariable=self.bet_type_var, values=self.bet_types, state="readonly")
        self.bet_type_menu.grid(row=4, column=1, sticky="ew", pady=5)

        # Calculate Button
        calculate_button = tk.Button(input_frame, text="Calculate Probability", bg="#4CAF50", fg="white", font=self.header_font, command=self.run_analysis, relief="flat", borderwidth=0)
        calculate_button.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(15,0))

        # --- Result Frame ---
        result_frame = tk.Frame(main_frame, bg="#3C3C3C", padx=15, pady=15)
        result_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        result_frame.pack_propagate(False)

        tk.Label(result_frame, text="Probability", font=self.header_font, bg="#3C3C3C", fg="#FFFFFF").pack()
        self.result_label = tk.Label(result_frame, text="--%", font=self.result_font, bg="#3C3C3C", fg="#FFFFFF")
        self.result_label.pack(expand=True)

        # --- Info Frame ---
        info_frame = tk.Frame(main_frame, bg="#3C3C3C", padx=15, pady=15)
        info_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        info_frame.pack_propagate(False)
        info_frame.columnconfigure(0, weight=1)

        tk.Label(info_frame, text="Prediction Factors", font=self.header_font, bg="#3C3C3C", fg="#FFFFFF").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,10))
        
        self.home_info_label = tk.Label(info_frame, text="Home Team Info:", bg="#3C3C3C", fg="#CCCCCC", justify="left", wraplength=250, font=self.info_font)
        self.home_info_label.grid(row=1, column=0, sticky="nw", pady=5)
        
        self.away_info_label = tk.Label(info_frame, text="Away Team Info:", bg="#3C3C3C", fg="#CCCCCC", justify="left", wraplength=250, font=self.info_font)
        self.away_info_label.grid(row=2, column=0, sticky="nw", pady=5)

        # --- History Frame ---
        history_frame = tk.Frame(main_frame, bg="#3C3C3C", padx=15, pady=15)
        history_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(20, 0))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(1, weight=1)

        tk.Label(history_frame, text="Analysis History", font=self.header_font, bg="#3C3C3C", fg="#FFFFFF").grid(row=0, column=0, sticky="w")
        
        # Treeview for history
        columns = ("date", "match", "bet", "prediction", "actual_result")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        self.history_tree.grid(row=1, column=0, sticky="nsew")

        # Define headings
        self.history_tree.heading("date", text="Date")
        self.history_tree.heading("match", text="Match")
        self.history_tree.heading("bet", text="Bet")
        self.history_tree.heading("prediction", text="Prediction (%)")
        self.history_tree.heading("actual_result", text="Actual Result")

        # Configure column widths
        self.history_tree.column("date", width=120)
        self.history_tree.column("match", width=200)
        self.history_tree.column("bet", width=200)
        self.history_tree.column("prediction", width=100, anchor="center")
        self.history_tree.column("actual_result", width=120, anchor="center")

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        self.populate_history_tree()
        
        # Add a button to manually add the actual result
        result_button_frame = tk.Frame(history_frame, bg="#3C3C3C")
        result_button_frame.grid(row=2, column=0, sticky="ew", pady=(10,0))
        
        self.actual_result_entry = tk.Entry(result_button_frame, bg="#555555", fg="#FFFFFF", relief="flat")
        self.actual_result_entry.pack(side="left", fill="x", expand=True, padx=(0,10))
        self.actual_result_entry.insert(0, "e.g., Home Win")

        add_result_button = tk.Button(result_button_frame, text="Add Actual Result", command=self.add_actual_result, bg="#2196F3", fg="white", relief="flat")
        add_result_button.pack(side="left")

    def update_teams(self, event=None):
        """Populates team dropdowns based on selected league."""
        league = self.league_var.get()
        api_data = get_mock_api_data(league)
        teams = api_data.get("teams", [])
        
        self.home_team_menu['values'] = teams
        self.away_team_menu['values'] = teams
        
        self.home_team_var.set('')
        self.away_team_var.set('')

    def run_analysis(self):
        """Main function to run the probability calculation."""
        league = self.league_var.get()
        home_team_name = self.home_team_var.get()
        away_team_name = self.away_team_var.get()
        bet_type = self.bet_type_var.get()

        if not all([league, home_team_name, away_team_name, bet_type]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return
            
        if home_team_name == away_team_name:
            messagebox.showerror("Error", "Home and Away teams cannot be the same.")
            return

        api_data = get_mock_api_data(league)
        home_team = api_data["data"].get(home_team_name)
        away_team = api_data["data"].get(away_team_name)

        if not home_team or not away_team:
            messagebox.showerror("Error", "Could not find data for the selected teams. This league may not have mock data yet.")
            return
            
        # --- Update Info Panel ---
        self.home_info_label.config(text=f"{home_team_name} Info:\n- Recent Form: {' '.join(home_team['last_4'])}\n- Unavailable: {', '.join(home_team['unavailable']) or 'None'}")
        self.away_info_label.config(text=f"{away_team_name} Info:\n- Recent Form: {' '.join(away_team['last_4'])}\n- Unavailable: {', '.join(away_team['unavailable']) or 'None'}")

        # --- Model Calculation ---
        # Adjust strength based on unavailable players (simple heuristic)
        home_attack = home_team["attack_strength"] * (1 - len(home_team["unavailable"]) * 0.1)
        away_attack = away_team["attack_strength"] * (1 - len(away_team["unavailable"]) * 0.1)
        home_defence = home_team["defence_strength"]
        away_defence = away_team["defence_strength"]
        
        # Weighting for recent form
        form_weight = {"W": 1.1, "D": 1.0, "L": 0.9}
        home_form_mod = sum(form_weight.get(res, 1.0) for res in home_team['last_4']) / 4
        away_form_mod = sum(form_weight.get(res, 1.0) for res in away_team['last_4']) / 4

        home_attack *= home_form_mod
        away_attack *= away_form_mod

        # This is a simplified logic model. A real app would use more complex stats.
        prob = 0
        if "3-Way Result" in bet_type:
            # Simple strength comparison
            total_strength = home_attack / away_defence + away_attack / home_defence
            home_chance = (home_attack / away_defence) / total_strength
            away_chance = (away_attack / home_defence) / total_strength
            draw_chance = 1 - home_chance - away_chance
            # Normalize to prevent negative draw chance if teams are very unbalanced
            if draw_chance < 0.15: 
                draw_chance = 0.15
                scale = (1-draw_chance)/(home_chance+away_chance)
                home_chance *= scale
                away_chance *= scale
            
            if "Home Win" in bet_type: prob = home_chance
            if "Away Win" in bet_type: prob = away_chance
            if "Draw" in bet_type: prob = draw_chance

        elif "First Team to Score" in bet_type:
            # Based on who has higher attack strength
            if "Home" in bet_type: prob = home_attack / (home_attack + away_attack)
            if "Away" in bet_type: prob = away_attack / (home_attack + away_attack)
        
        elif "Both Teams to Score" in bet_type:
            # Heuristic based on combined attack and defence
            btts_chance = (home_attack / 2.0) * (away_attack / 2.0)
            if btts_chance > 0.95: btts_chance = 0.95
            if "Yes" in bet_type: prob = btts_chance
            if "No" in bet_type: prob = 1 - btts_chance
            
        elif "Over/Under 3.0" in bet_type:
            # Very simple model based on expected goals
            expected_goals = (home_attack + away_attack) * ((home_defence + away_defence)/2)
            if "Over" in bet_type: prob = expected_goals / 5.0 # Scaled
            if "Under" in bet_type: prob = 1 - (expected_goals / 5.0)

        final_prob = min(max(prob, 0), 1) * 100 # Clamp probability between 0 and 100
        self.result_label.config(text=f"{final_prob:.1f}%")

        # --- Save to History ---
        self.save_to_history({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "league": league,
            "match": f"{home_team_name} vs {away_team_name}",
            "bet": bet_type,
            "prediction": f"{final_prob:.1f}",
            "actual_result": "Pending"
        })
        self.populate_history_tree()


    def save_to_history(self, record):
        """Appends a new record to the history list and saves to file."""
        self.history.insert(0, record) # Add to the top
        with open("bet_analyser_history.json", "w") as f:
            json.dump(self.history, f, indent=4)

    def load_history(self):
        """Loads the history log from a JSON file."""
        try:
            with open("bet_analyser_history.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def populate_history_tree(self):
        """Clears and repopulates the history treeview with current data."""
        # Clear existing items
        for i in self.history_tree.get_children():
            self.history_tree.delete(i)
        
        # Add new items from history
        for record in self.history:
            self.history_tree.insert("", "end", values=(
                record.get("date"),
                record.get("match"),
                record.get("bet"),
                record.get("prediction"),
                record.get("actual_result")
            ))
            
    def add_actual_result(self):
        """Adds an actual result to the selected history item."""
        selected_item = self.history_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item from the history log first.")
            return
            
        result_text = self.actual_result_entry.get()
        if not result_text or result_text == "e.g., Home Win":
             messagebox.showerror("Error", "Please enter the actual result in the text box.")
             return

        # Find the index of the selected item in the treeview
        selected_index = self.history_tree.index(selected_item)
        
        # History is displayed in reverse, so we need to map the index correctly
        history_index = len(self.history) - 1 - selected_index

        # Update the history list and save
        self.history[history_index]["actual_result"] = result_text
        with open("bet_analyser_history.json", "w") as f:
            json.dump(self.history, f, indent=4)

        # Refresh the treeview
        self.populate_history_tree()
        messagebox.showinfo("Success", "Actual result has been updated.")


if __name__ == "__main__":
    app = SoccerAnalyserApp()
    app.mainloop()
