import tkinter as tk
from tkinter import ttk, messagebox
import random, os

# ------------------ Country Groups by Difficulty ------------------
easy_countries = {
    "USA": "Washington D.C.",
    "Germany": "Berlin",
    "France": "Paris",
    "India": "New Delhi",
    "Japan": "Tokyo"
}
medium_countries = {
    "Turkey": "Ankara",
    "Egypt": "Cairo",
    "Nigeria": "Abuja",
    "Morocco": "Rabat",
    "South Africa": "Pretoria"
}
hard_countries = {
    "Mongolia": "Ulaanbaatar",
    "Kyrgyzstan": "Bishkek",
    "Bhutan": "Thimphu",
    "Suriname": "Paramaribo",
    "Eswatini": "Mbabane"
}

# ----------------------- Global Variables -------------------------
leaderboard = []
asked_questions = set()
score = 0
lifelines_left = 3
current_question = None
correct_answer = None
options = []
player_name = ""
selected_answer_index = None
difficulty = None

# ---------------------- Leaderboard Functions ----------------------
def load_leaderboard():
    global leaderboard
    if os.path.exists("leaderboard.txt"):
        with open("leaderboard.txt", "r") as file:
            lines = file.readlines()
            temp = []
            for line in lines:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    name, s = parts
                    if name and s.isdigit():
                        temp.append((name, int(s)))
            leaderboard = temp

def save_leaderboard():
    global leaderboard
    leaderboard = [(name, s) for name, s in leaderboard if name and s > 0]
    with open("leaderboard.txt", "w") as file:
        for name, s in leaderboard:
            file.write(f"{name},{s}\n")

# ---------------------- Helper / Layout ---------------------------
def clear_content():
    """Remove all widgets from the content_frame."""
    for widget in content_frame.winfo_children():
        widget.destroy()

# ---------------------- Start / Name Entry ------------------------
def show_name_entry():
    clear_content()
    lbl_name = ttk.Label(content_frame, text="Enter Your Name:", style="TLabel")
    lbl_name.pack(pady=10)

    entry_name = ttk.Entry(content_frame, font=("Arial", 12), style="TEntry")
    entry_name.pack(pady=5)

    btn_start = ttk.Button(content_frame, text="Start Game",
                           style="Visible.TButton",
                           command=lambda: start_game(entry_name))
    btn_start.pack(pady=10)

def start_game(entry_widget):
    global player_name
    player_name = entry_widget.get().strip()
    if not player_name:
        messagebox.showwarning("Warning", "Please enter your name to start!")
        return
    show_difficulty_selection()

def show_difficulty_selection():
    clear_content()
    lbl_diff = ttk.Label(content_frame, text="Select Difficulty:", style="TLabel")
    lbl_diff.pack(pady=10)

    btn_easy = ttk.Button(content_frame, text="Easy",
                          style="Visible.TButton",
                          command=lambda: set_difficulty("Easy"))
    btn_easy.pack(pady=5, ipadx=10, ipady=5)

    btn_medium = ttk.Button(content_frame, text="Medium",
                            style="Visible.TButton",
                            command=lambda: set_difficulty("Medium"))
    btn_medium.pack(pady=5, ipadx=10, ipady=5)

    btn_hard = ttk.Button(content_frame, text="Hard",
                          style="Visible.TButton",
                          command=lambda: set_difficulty("Hard"))
    btn_hard.pack(pady=5, ipadx=10, ipady=5)

def set_difficulty(level):
    global difficulty
    difficulty = level
    reset_game()
    show_question_screen()

def reset_game():
    global score, lifelines_left, asked_questions, selected_answer_index
    score, lifelines_left = 0, 3
    asked_questions.clear()
    selected_answer_index = None

# ---------------------- Main Gameplay Screen ----------------------
def show_question_screen():
    """Build the layout frames & widgets, then call next_question()."""
    clear_content()

    # 1) Top frame: Score and Lifelines
    top_frame = ttk.Frame(content_frame, style="TFrame")
    top_frame.pack(pady=10)

    global lbl_score, lbl_lifelines
    lbl_score = ttk.Label(top_frame, text=f"Score: {score}", style="TLabel")
    lbl_score.grid(row=0, column=0, padx=20)

    lbl_lifelines = ttk.Label(top_frame, text=f"Lifelines Left: {lifelines_left}", style="TLabel")
    lbl_lifelines.grid(row=0, column=1, padx=20)

    # 2) Question Label
    global lbl_question
    lbl_question = ttk.Label(content_frame, text="", style="TLabel")
    lbl_question.pack(pady=20)

    # 3) Answers Frame (to hold the 4 buttons)
    global answers_frame
    answers_frame = ttk.Frame(content_frame, style="TFrame")
    answers_frame.pack()

    # Create the 4 buttons but do NOT pack them yet
    global answer_buttons
    answer_buttons = []
    for i in range(4):
        btn = ttk.Button(answers_frame,
                         text="",
                         style="Visible.TButton",
                         command=lambda i=i: select_answer(i))
        answer_buttons.append(btn)

    # 4) Confirm Answer button
    global btn_confirm
    btn_confirm = ttk.Button(content_frame, text="Confirm Answer",
                             style="Visible.TButton",
                             command=confirm_answer)
    btn_confirm.pack(pady=15, ipadx=10, ipady=5)

    # 5) Lifeline buttons in one row
    lifeline_frame = ttk.Frame(content_frame, style="TFrame")
    lifeline_frame.pack(pady=10)

    btn_skip = ttk.Button(lifeline_frame, text="Skip",
                          style="Visible.TButton",
                          command=lambda: use_lifeline("skip"))
    btn_skip.grid(row=0, column=0, padx=5)

    btn_50_50 = ttk.Button(lifeline_frame, text="50-50",
                           style="Visible.TButton",
                           command=lambda: use_lifeline("50-50"))
    btn_50_50.grid(row=0, column=1, padx=5)

    btn_ai = ttk.Button(lifeline_frame, text="Ask AI",
                        style="Visible.TButton",
                        command=lambda: use_lifeline("ai"))
    btn_ai.grid(row=0, column=2, padx=5)

    # 6) Leaderboard button
    btn_leaderboard = ttk.Button(content_frame, text="Leaderboard",
                                 style="Visible.TButton",
                                 command=show_leaderboard)
    btn_leaderboard.pack(pady=10, ipadx=10, ipady=5)

    # Finally, load the first question
    next_question()

# ---------------------- Next Question Logic -----------------------
def next_question():
    global current_question, correct_answer, options, selected_answer_index, score
    selected_answer_index = None
    lbl_score.config(text=f"Score: {score}")

    # 1) Make sure all 4 buttons are shown again (in answers_frame)
    for btn in answer_buttons:
        btn.pack_forget()  # in case they were removed by 50-50
        btn.config(state=tk.NORMAL)
        btn.configure(style="Visible.TButton")
        btn.pack(pady=5, ipadx=20, ipady=2, fill=tk.X)

    # 2) Check if we've asked all possible questions
    if difficulty == "Easy":
        country_pool = easy_countries
    elif difficulty == "Medium":
        country_pool = medium_countries
    else:
        country_pool = hard_countries

    if len(asked_questions) == len(country_pool):
        messagebox.showinfo("Game Over", f"Final Score: {score}")
        update_leaderboard()
        ask_to_restart_or_end()
        return

    # 3) Pick a question that hasn't been asked
    country, capital = random.choice(list(country_pool.items()))
    while country in asked_questions:
        country, capital = random.choice(list(country_pool.items()))
    asked_questions.add(country)
    correct_answer = capital

    lbl_question.config(text=f"What is the capital of {country}?")

    # 4) Shuffle answers and assign them to the 4 buttons
    all_capitals = list(country_pool.values())
    all_capitals.remove(correct_answer)
    choices = [correct_answer] + random.sample(all_capitals, 3)
    random.shuffle(choices)

    options.clear()
    options.extend(choices)

    for i, btn in enumerate(answer_buttons):
        btn.config(text=choices[i])

def select_answer(index):
    global selected_answer_index
    selected_answer_index = index
    # Highlight only the chosen one
    for i, btn in enumerate(answer_buttons):
        if i == index:
            btn.configure(style="Selected.Visible.TButton")
        else:
            btn.configure(style="Visible.TButton")

def show_custom_popup(is_correct, correct_answer=None):
    popup = tk.Toplevel()
    popup.title("Result")
    
    # Decide the size you want:
    popup.geometry("400x200")  # width x height in pixels
    
    # Make the popup appear on top of the main window
    popup.transient(root)
    popup.grab_set()

    # Decide which image and text to show
    if is_correct:
        icon_label = tk.Label(popup, image=tick_image)
        text_label = tk.Label(popup, text="You got it right!", font=("Arial", 14))
    else:
        icon_label = tk.Label(popup, image=cross_image)
        text_label = tk.Label(popup, text=f"Incorrect! Correct answer was: {correct_answer}",
                              font=("Arial", 14))

    icon_label.pack(pady=10)
    text_label.pack(pady=10)

    # Button to close the popup
    ok_button = tk.Button(
        popup,
        text="OK",
        fg="black",         # text color
        bg="white",          # background color
        font=("Arial", 14), # larger font
        command=popup.destroy
    )
    ok_button.pack(pady=10, ipadx=10, ipady=5)

def confirm_answer():
    global score
    if selected_answer_index is None:
        messagebox.showwarning("Warning", "Please select an answer!")
        return

    if options[selected_answer_index] == correct_answer:
        score += 10
        # Show the tick popup
        show_custom_popup(is_correct=True)
    else:
        # Show the cross popup
        show_custom_popup(is_correct=False, correct_answer=correct_answer)

    next_question()

# --------------------- Lifelines and Endgame ----------------------
def use_lifeline(lifeline_type):
    global lifelines_left
    if lifelines_left <= 0:
        messagebox.showwarning("Warning", "No lifelines left!")
        return

    lifelines_left -= 1
    lbl_lifelines.config(text=f"Lifelines Left: {lifelines_left}")

    if lifeline_type == "skip":
        next_question()

    elif lifeline_type == "50-50":
        incorrect_buttons = [btn for btn in answer_buttons
                             if btn.cget("text") != correct_answer]
        random.shuffle(incorrect_buttons)
        for btn in incorrect_buttons[:2]:
            btn.pack_forget()

    elif lifeline_type == "ai":
        messagebox.showinfo("AI Help", f"The AI suggests the answer is: {correct_answer}")

def ask_to_restart_or_end():
    result = messagebox.askquestion("Game Over", "Do you want to start over?")
    if result == "yes":
        reset_game()
        show_name_entry()
    else:
        root.quit()

# --------------------- Leaderboard Handling -----------------------
def update_leaderboard():
    global leaderboard
    player_found = False
    for i, (name, s) in enumerate(leaderboard):
        if name == player_name:
            leaderboard[i] = (name, score)
            player_found = True
            break

    if not player_found:
        leaderboard.append((player_name, score))

    leaderboard.sort(key=lambda x: x[1], reverse=True)
    save_leaderboard()
    show_leaderboard()

def show_leaderboard():
    if leaderboard:
        ranks = [f"{i+1}. {name} - {s} pts" for i, (name, s) in enumerate(leaderboard)]
        leaderboard_text = "\n".join(ranks)
    else:
        leaderboard_text = "No scores yet."
    messagebox.showinfo("Leaderboard", leaderboard_text)

# --------------------- (A) RESTART GAME HELPER --------------------
def restart_game():
    """Resets the quiz and returns to name entry screen."""
    reset_game()
    show_name_entry()

# --------------------- (B) CREATE AN IN-WINDOW MENUBAR ------------
def create_in_window_menubar(parent):
    """
    Creates a menubar INSIDE the window using Menubuttons,
    so it doesn't appear in the macOS global menubar.
    """
    menubar_frame = ttk.Frame(parent, style="TFrame")
    menubar_frame.pack(side=tk.TOP, fill=tk.X)

    # "File" Menubutton
    file_button = ttk.Menubutton(menubar_frame, text="File", style="TMenubutton")
    file_button.pack(side=tk.LEFT, padx=5)

    file_menu = tk.Menu(file_button, tearoff=0)
    file_menu.add_command(label="Restart", command=restart_game)
    file_menu.add_command(label="Quit", command=root.quit)
    file_button["menu"] = file_menu  # attach the menu to the Menubutton

    # "Help" Menubutton
    help_button = ttk.Menubutton(menubar_frame, text="Help", style="TMenubutton")
    help_button.pack(side=tk.LEFT, padx=5)

    help_menu = tk.Menu(help_button, tearoff=0)
    help_menu.add_command(label="About",
        command=lambda: messagebox.showinfo("About", "City Seeker Quiz v1.0"))
    help_button["menu"] = help_menu

# ---------------------- Main Window & Setup -----------------------
root = tk.Tk()
root.title("City Seeker Quiz")
root.geometry("500x600")
root.resizable(False, False)

# Load your images
tick_image = tk.PhotoImage(file="tick.png")
cross_image = tk.PhotoImage(file="cross.png")

# 1) Create a style for your frames, labels, buttons, etc.
style = ttk.Style()
style.theme_create("myCustomTheme", parent="clam", settings={
    "TFrame": {
        "configure": {
            "background": "#FFFFFF"
        }
    },
    "TLabel": {
        "configure": {
            "background": "#FFFFFF",
            "foreground": "#000000",
            "font": ("Arial", 14)
        }
    },
    "TEntry": {
        "configure": {
            "foreground": "#000000",
            "fieldbackground": "#FFFFFF",
            "borderwidth": 1,
            "relief": "solid",
            "font": ("Arial", 12),
            "padding": 3
        }
    },
    "Visible.TButton": {
        "configure": {
            "background": "#E0E0E0",
            "foreground": "#000000",
            "font": ("Arial", 14),
            "padding": 5,
            "borderwidth": 2,
            "relief": "raised"
        },
        "map": {
            "background": [("active", "#D0D0D0"), ("pressed", "#C0C0C0")],
            "relief": [("pressed", "sunken"), ("active", "raised")]
        }
    },
    "Selected.Visible.TButton": {
        "configure": {
            "background": "#FFCC66",
            "foreground": "#000000",
            "font": ("Arial", 14, "bold"),
            "borderwidth": 2,
            "relief": "groove"
        }
    },
    # Add a TMenubutton style so it doesn't blend into background
    "TMenubutton": {
        "configure": {
            "background": "#E0E0E0",
            "foreground": "#000000",
            "font": ("Arial", 12),
            "padding": 5,
            "borderwidth": 1,
            "relief": "raised"
        },
        "map": {
            "background": [("active", "#D0D0D0"), ("pressed", "#C0C0C0")],
            "relief": [("pressed", "sunken"), ("active", "raised")]
        }
    }
})
style.theme_use("myCustomTheme")

# 2) Optional header (like a title bar inside the app)
header_frame = tk.Frame(root, bg="#4A90E2", height=80)
header_frame.pack(fill=tk.X)

lbl_title = tk.Label(header_frame, text="City Seeker Quiz",
                     font=("Helvetica", 20, "bold"),
                     bg="#4A90E2", fg="white")
lbl_title.pack(pady=20)

# 3) Create the main content frame
content_frame = ttk.Frame(root, style="TFrame")
content_frame.pack(expand=True, fill=tk.BOTH)

# 4) Create your in-window menubar
create_in_window_menubar(root)

# 5) Load leaderboard and start
load_leaderboard()
show_name_entry()

root.mainloop()
