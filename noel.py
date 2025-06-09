import tkinter as tk
from tkinter import ttk, messagebox, font
import json
from datetime import datetime, timedelta, timezone
import requests

# --- Live API Configuration ---
# PASTE YOUR API KEY HERE
API_KEY = "69733272b3fece458e5ab58fdd91f7d5"
API_HOST = "v3.football.api-sports.io"
API_URL = f"https://{API_HOST}/"

def get_real_api_data(endpoint, params):
    """Fetches live data from the API-Football endpoint."""
    headers = {
        'x-rapidapi-host': API_HOST,
        'x-rapidapi-key': API_KEY
    }
    try:
        response = requests.get(API_URL + endpoint, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("API Error", f"Could not fetch data from API: {e}")
        return None
    except json.JSONDecodeError:
        messagebox.showerror("API Error", "Failed to parse API response.")
        return None

class SoccerAnalyserApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Soccer Bet Analyser v2.4")
        self.geometry("1000x700") # Wider window for new layout
        self.configure(bg="#2E2E2E")

        # --- Font Configuration ---
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Helvetica", size=10)
        self.title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.header_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.result_font = font.Font(family="Helvetica", size=36, weight="bold")
        self.info_font = font.Font(family="Helvetica", size=9)

        # --- App Data ---
        self.bet_types = [
            "3-Way Result (Home Win)", "3-Way Result (Draw)", "3-Way Result (Away Win)",
            "First Team to Score (Home)", "First Team to Score (Away)",
            "Both Teams to Score (Yes)", "Both Teams to Score (No)",
            "Over/Under 3.0 (Over)", "Over/Under 3.0 (Under)"
        ]
        self.history = self.load_history()
        self.current_fixture_data = {} # To store data of the selected match

        self._create_widgets()
        self.load_upcoming_fixtures()

    def _create_widgets(self):
        # Main container with two columns
        main_frame = tk.Frame(self, bg="#2E2E2E", padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1) # Fixtures list
        main_frame.columnconfigure(1, weight=2) # Analysis panel
        main_frame.rowconfigure(0, weight=1)

        # --- Fixtures Frame (Left Side) ---
        fixtures_frame = tk.Frame(main_frame, bg="#3C3C3C", padx=15, pady=15)
        fixtures_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        fixtures_frame.rowconfigure(1, weight=1)
        fixtures_frame.columnconfigure(0, weight=1)

        tk.Label(fixtures_frame, text="Upcoming Matches (3 Days)", font=self.title_font, bg="#3C3C3C", fg="white").grid(row=0, column=0, pady=(0,15), sticky="w")
        
        # Treeview for fixtures
        fixture_cols = ("time", "league", "match")
        self.fixture_tree = ttk.Treeview(fixtures_frame, columns=fixture_cols, show="headings")
        self.fixture_tree.grid(row=1, column=0, sticky="nsew")

        self.fixture_tree.heading("time", text="Date & Time (UTC)")
        self.fixture_tree.heading("league", text="League")
        self.fixture_tree.heading("match", text="Match")
        self.fixture_tree.column("time", width=120)
        self.fixture_tree.column("league", width=150)
        self.fixture_tree.column("match", width=200)

        # Bind the selection event
        self.fixture_tree.bind("<<TreeviewSelect>>", self.on_match_select)

        # --- Analysis Frame (Right Side) ---
        analysis_container = tk.Frame(main_frame, bg="#2E2E2E")
        analysis_container.grid(row=0, column=1, sticky="nsew")
        analysis_container.rowconfigure(2, weight=1)
        analysis_container.columnconfigure(0, weight=1)

        # --- Bet Setup Frame (Top Right) ---
        self.input_frame = tk.Frame(analysis_container, bg="#3C3C3C", padx=15, pady=15)
        self.input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.input_frame.columnconfigure(1, weight=1)
        
        self.selected_match_label = tk.Label(self.input_frame, text="Select a Match to Begin Analysis", font=self.title_font, bg="#3C3C3C", fg="#FFFFFF")
        self.selected_match_label.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="w")
        
        tk.Label(self.input_frame, text="Bet Type:", bg="#3C3C3C", fg="#CCCCCC").grid(row=1, column=0, sticky="w", padx=(0,10))
        self.bet_type_var = tk.StringVar()
        self.bet_type_menu = ttk.Combobox(self.input_frame, textvariable=self.bet_type_var, values=self.bet_types, state="readonly")
        self.bet_type_menu.grid(row=1, column=1, sticky="ew", pady=5)

        self.calculate_button = tk.Button(self.input_frame, text="Calculate Probability", bg="#4CAF50", fg="white", font=self.header_font, command=self.run_analysis, relief="flat", state="disabled")
        self.calculate_button.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(15,0))

        # --- Results & Info Frame (Middle Right) ---
        results_info_frame = tk.Frame(analysis_container, bg="#2E2E2E")
        results_info_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        results_info_frame.columnconfigure(0, weight=1)
        results_info_frame.columnconfigure(1, weight=1)

        result_frame = tk.Frame(results_info_frame, bg="#3C3C3C", padx=15, pady=15)
        result_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        result_frame.pack_propagate(False)

        tk.Label(result_frame, text="Probability", font=self.header_font, bg="#3C3C3C", fg="#FFFFFF").pack()
        self.result_label = tk.Label(result_frame, text="--%", font=self.result_font, bg="#3C3C3C", fg="#FFFFFF")
        self.result_label.pack(expand=True)
        
        info_frame = tk.Frame(results_info_frame, bg="#3C3C3C", padx=15, pady=15)
        info_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        info_frame.columnconfigure(0, weight=1)

        tk.Label(info_frame, text="Prediction Factors", font=self.header_font, bg="#3C3C3C", fg="#FFFFFF").grid(row=0, column=0, sticky="w", pady=(0,10))
        self.home_info_label = tk.Label(info_frame, text="Home Team Info:", bg="#3C3C3C", fg="#CCCCCC", justify="left", wraplength=250, font=self.info_font)
        self.home_info_label.grid(row=1, column=0, sticky="nw", pady=5)
        self.away_info_label = tk.Label(info_frame, text="Away Team Info:", bg="#3C3C3C", fg="#CCCCCC", justify="left", wraplength=250, font=self.info_font)
        self.away_info_label.grid(row=2, column=0, sticky="nw", pady=5)

        # --- History Frame (Bottom Right) ---
        history_frame = tk.Frame(analysis_container, bg="#3C3C3C", padx=15, pady=15)
        history_frame.grid(row=2, column=0, sticky="nsew")
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(1, weight=1)

        tk.Label(history_frame, text="Analysis History", font=self.header_font, bg="#3C3C3C", fg="#FFFFFF").grid(row=0, column=0, sticky="w")
        history_cols = ("date", "match", "bet", "prediction", "actual_result")
        self.history_tree = ttk.Treeview(history_frame, columns=history_cols, show="headings")
        self.history_tree.grid(row=1, column=0, sticky="nsew")
        for col in history_cols:
            self.history_tree.heading(col, text=col.replace("_", " ").title())
        self.populate_history_tree()

    def load_upcoming_fixtures(self):
        if API_KEY == "YOUR_API_KEY_HERE":
            self.fixture_tree.insert("", "end", values=("", "", "Add your API Key to load fixtures"))
            return

        self.fixture_tree.delete(*self.fixture_tree.get_children())
        all_fixtures = []
        for i in range(3):
            date_to_fetch = (datetime.now(timezone.utc) + timedelta(days=i)).strftime("%Y-%m-%d")
            data = get_real_api_data("fixtures", {"date": date_to_fetch})
            if data and data.get("response"):
                all_fixtures.extend(data["response"])

        if not all_fixtures:
            self.fixture_tree.insert("", "end", values=("", "", "No upcoming matches found in the next 3 days."))
            return
        
        self.fixture_map = {}
        for fixture in sorted(all_fixtures, key=lambda x: x['fixture']['date']):
            match_id = fixture['fixture']['id']
            self.fixture_map[match_id] = fixture

            display_time = datetime.fromisoformat(fixture['fixture']['date']).strftime('%m-%d %H:%M')
            league_name = fixture['league']['name']
            match_name = f"{fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']}"
            
            league_name_lower = fixture['league'].get('name', '').lower()
            country_name_lower = fixture['league'].get('country', '').lower()
            international_keywords = ['world cup', 'nations league', 'friendlies', 'afcon', 'copa america', 'euro']
            is_international = any(keyword in league_name_lower for keyword in international_keywords) or country_name_lower == 'world'
            
            tag = "international" if is_international else "club"
            self.fixture_tree.insert("", "end", iid=match_id, values=(display_time, league_name, match_name), tags=(tag,))

    def on_match_select(self, event=None):
        selected_item_id = self.fixture_tree.focus()
        if not selected_item_id:
            return
            
        fixture_data = self.fixture_map.get(int(selected_item_id))
        if not fixture_data:
            return

        self.current_fixture_data = {
            "league_id": fixture_data['league']['id'],
            "league_name": fixture_data['league']['name'],
            "home_team_id": fixture_data['teams']['home']['id'],
            "home_team_name": fixture_data['teams']['home']['name'],
            "away_team_id": fixture_data['teams']['away']['id'],
            "away_team_name": fixture_data['teams']['away']['name'],
            "is_international": "international" in self.fixture_tree.item(selected_item_id, "tags")
        }
        
        self.selected_match_label.config(text=f"{fixture_data['teams']['home']['name']} vs {fixture_data['teams']['away']['name']}")
        self.bet_type_var.set('')
        self.result_label.config(text="--%")
        self.home_info_label.config(text="Home Team Info:")
        self.away_info_label.config(text="Away Team Info:")
        self.calculate_button.config(state="normal")

    def run_analysis(self):
        bet_type = self.bet_type_var.get()
        if not bet_type:
            messagebox.showerror("Error", "Please select a bet type.")
            return

        if not self.current_fixture_data:
            messagebox.showerror("Error", "No match selected for analysis.")
            return
        
        try:
            home_team_id = self.current_fixture_data['home_team_id']
            away_team_id = self.current_fixture_data['away_team_id']
            
            now = datetime.now()
            season = now.year - 1 if now.month < 8 else now.year
            
            home_stats_params = {"season": season, "team": home_team_id}
            away_stats_params = {"season": season, "team": away_team_id}
            
            home_stats_data = get_real_api_data("teams/statistics", home_stats_params)
            away_stats_data = get_real_api_data("teams/statistics", away_stats_params)

            # --- Primary Analysis ---
            if home_stats_data.get("response") and away_stats_data.get("response"):
                self.analyze_with_stats(home_stats_data, away_stats_data)
            else:
                # --- Fallback to H2H ---
                self.analyze_with_h2h()

        except Exception as e:
            messagebox.showerror("Calculation Error", f"An unexpected error occurred: {e}")

    def analyze_with_stats(self, home_stats_data, away_stats_data):
        """Calculates probability based on detailed team statistics."""
        home_team_name = self.current_fixture_data['home_team_name']
        away_team_name = self.current_fixture_data['away_team_name']

        home_stats = home_stats_data["response"]
        away_stats = away_stats_data["response"]
        
        home_attack = home_stats.get("goals", {}).get("for", {}).get("average", {}).get("total", "0.0") or "0.0"
        home_defence = home_stats.get("goals", {}).get("against", {}).get("average", {}).get("total", "1.0") or "1.0"
        away_attack = away_stats.get("goals", {}).get("for", {}).get("average", {}).get("total", "0.0") or "0.0"
        away_defence = away_stats.get("goals", {}).get("against", {}).get("average", {}).get("total", "1.0") or "1.0"
        
        home_form_str = home_stats.get("form", "")[-4:] if home_stats.get("form") else ""
        away_form_str = away_stats.get("form", "")[-4:] if away_stats.get("form") else ""
        
        home_unavailable = [] # Simplified for this example, injuries require separate calls
        away_unavailable = []

        self.home_info_label.config(text=f"{home_team_name} Info:\n- Method: Season Stats\n- Form: {' '.join(home_form_str)}\n- Avg Gls For: {home_attack}")
        self.away_info_label.config(text=f"{away_team_name} Info:\n- Method: Season Stats\n- Form: {' '.join(away_form_str)}\n- Avg Gls For: {away_attack}")
        
        self.calculate_and_display_prob(float(home_attack), float(home_defence), float(away_attack), float(away_defence), home_unavailable, away_unavailable)

    def analyze_with_h2h(self):
        """Fallback: Calculates probability based on Head-to-Head history."""
        home_team_id = self.current_fixture_data['home_team_id']
        away_team_id = self.current_fixture_data['away_team_id']
        home_team_name = self.current_fixture_data['home_team_name']
        away_team_name = self.current_fixture_data['away_team_name']

        h2h_data = get_real_api_data("fixtures/headtohead", {"h2h": f"{home_team_id}-{away_team_id}", "last": "10"})
        
        if not h2h_data or not h2h_data.get("response"):
            messagebox.showerror("Error", "Could not fetch H2H data. No analysis possible.")
            return

        h2h_fixtures = h2h_data["response"]
        home_wins = 0
        away_wins = 0
        draws = 0

        for fixture in h2h_fixtures:
            if fixture["teams"]["home"]["winner"]:
                if fixture["teams"]["home"]["id"] == home_team_id:
                    home_wins += 1
                else:
                    away_wins += 1
            elif fixture["teams"]["away"]["winner"]:
                if fixture["teams"]["away"]["id"] == away_team_id:
                    away_wins += 1
                else:
                    home_wins += 1
            else:
                draws += 1
        
        total_matches = len(h2h_fixtures)
        if total_matches == 0:
            messagebox.showerror("Error", "No H2H history found. No analysis possible.")
            return

        self.home_info_label.config(text=f"{home_team_name} Info:\n- Method: H2H History\n- Last {total_matches} games:\n- Wins: {home_wins}")
        self.away_info_label.config(text=f"{away_team_name} Info:\n- Method: H2H History\n- Last {total_matches} games:\n- Wins: {away_wins}")

        # Simple H2H model: probability is the ratio of past results.
        # We assign a synthetic attack/defence strength based on this.
        home_attack = 1.0 + (home_wins / total_matches)
        away_attack = 1.0 + (away_wins / total_matches)
        home_defence = 1.0 + (away_wins / total_matches)
        away_defence = 1.0 + (home_wins / total_matches)

        self.calculate_and_display_prob(home_attack, home_defence, away_attack, away_defence, [], [])


    def calculate_and_display_prob(self, home_attack, home_defence, away_attack, away_defence, home_unavailable, away_unavailable):
        """Shared logic to calculate and display final probability."""
        bet_type = self.bet_type_var.get()
        home_team_name = self.current_fixture_data['home_team_name']
        away_team_name = self.current_fixture_data['away_team_name']

        home_attack_adj = home_attack * (1 - len(home_unavailable) * 0.05)
        away_attack_adj = away_attack * (1 - len(away_unavailable) * 0.05)
        
        prob = 0
        if "3-Way Result" in bet_type:
            total_strength = (home_attack_adj / away_defence) + (away_attack_adj / home_defence)
            home_chance = (home_attack_adj / away_defence) / total_strength if total_strength > 0 else 0
            away_chance = (away_attack_adj / home_defence) / total_strength if total_strength > 0 else 0
            draw_chance = 1 - home_chance - away_chance
            if draw_chance < 0.15:
                draw_chance = 0.15
                if (home_chance + away_chance) > 0:
                    scale = (1-draw_chance) / (home_chance + away_chance)
                    home_chance *= scale
                    away_chance *= scale
            if "Home Win" in bet_type: prob = home_chance
            if "Away Win" in bet_type: prob = away_chance
            if "Draw" in bet_type: prob = draw_chance
        elif "Both Teams to Score" in bet_type:
            btts_chance = (home_attack / 1.8) * (away_attack / 1.8)
            if "Yes" in bet_type: prob = btts_chance
            if "No" in bet_type: prob = 1 - btts_chance

        final_prob = min(max(prob, 0), 1) * 100
        self.result_label.config(text=f"{final_prob:.1f}%")

        self.save_to_history({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "match": f"{home_team_name} vs {away_team_name}",
            "bet": bet_type,
            "prediction": f"{final_prob:.1f}",
            "actual_result": "Pending"
        })
        self.populate_history_tree()

    def save_to_history(self, record):
        self.history.insert(0, record)
        with open("bet_analyser_history.json", "w") as f:
            json.dump(self.history, f, indent=4)

    def load_history(self):
        try:
            with open("bet_analyser_history.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def populate_history_tree(self):
        self.history_tree.delete(*self.history_tree.get_children())
        for record in self.history:
            self.history_tree.insert("", "end", values=(record.get("date"), record.get("match"), record.get("bet"), record.get("prediction"), record.get("actual_result")))

if __name__ == "__main__":
    app = SoccerAnalyserApp()
    app.mainloop()
