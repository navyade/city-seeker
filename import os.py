import os
from tkinter import messagebox

# File to store leaderboard data
LEADERBOARD_FILE = "leaderboard.txt"

# Function to load the leaderboard from a file
def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []  # If the file does not exist, return an empty leaderboard

    leaderboard = []
    with open(LEADERBOARD_FILE, "r") as file:
        for line in file:
            name, score = line.strip().split(", ")
            leaderboard.append((name, int(score)))
    return leaderboard

# Function to save the leaderboard to a file
def save_leaderboard():
    with open(LEADERBOARD_FILE, "w") as file:
        for name, score in leaderboard:
            file.write(f"{name}, {score}\n")

# Function to update the leaderboard
def update_leaderboard(name, score):
    global leaderboard
    leaderboard.append((name, score))
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    save_leaderboard()  # Save the updated leaderboard to the file

# Function to show leaderboard
def show_leaderboard():
    leaderboard_text = "\n".join([f"{i+1}. {name} - {score} points" for i, (name, score) in enumerate(leaderboard)])
    messagebox.showinfo("Leaderboard", leaderboard_text if leaderboard_text else "No scores yet.")
