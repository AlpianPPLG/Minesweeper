import tkinter as tk
from tkinter import messagebox
import random
import time
import json

class Minesweeper:
    def __init__(self, root, size=9, bombs=10, difficulty="easy", dark_mode=False, no_flags=False):
        self.root = root
        self.size = size
        self.bombs = bombs
        self.difficulty = difficulty  # Store difficulty level
        self.grid = []
        self.buttons = []
        self.bomb_locations = []
        self.is_game_over = False
        self.start_time = None
        self.dark_mode = dark_mode
        self.no_flags = no_flags
        self.timer_label = tk.Label(self.root, text="Time: 0")
        self.timer_label.grid(row=0, column=0, columnspan=self.size - 2, sticky="ew")
        self.mode_button = tk.Button(self.root, text="Dark Mode", command=self.toggle_mode)
        self.mode_button.grid(row=0, column=self.size - 2, columnspan=2, sticky="ew")
        self.quit_button = tk.Button(self.root, text="Quit", command=self.quit_game)
        self.quit_button.grid(row=0, column=self.size, columnspan=2, sticky="ew")  # Positioning Quit button
        self.create_widgets()
        self.place_bombs()
        self.calculate_numbers()
        self.update_timer()
        self.apply_mode()  # Apply the initial theme (light or dark)

    def toggle_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_mode()

    def apply_mode(self):
        bg_color = "black" if self.dark_mode else "white"
        fg_color = "white" if self.dark_mode else "black"
        button_bg = "grey" if self.dark_mode else "lightgrey"

        self.root.config(bg=bg_color)
        self.timer_label.config(bg=bg_color, fg=fg_color)
        self.mode_button.config(text="Light Mode" if self.dark_mode else "Dark Mode", bg=bg_color, fg=fg_color)
        self.quit_button.config(bg=bg_color, fg=fg_color)  # Update Quit button color

        for r in range(self.size):
            for c in range(self.size):
                self.buttons[r][c].config(bg=button_bg, fg=fg_color, highlightbackground=bg_color)

    def create_widgets(self):
        for r in range(self.size):
            row_buttons = []
            for c in range(self.size):
                button = tk.Button(self.root, width=2, height=1, command=lambda r=r, c=c: self.click(r, c))
                button.bind("<Button-3>", lambda e, r=r, c=c: self.right_click(r, c) if not self.no_flags else None)
                button.grid(row=r + 1, column=c)  # Adjust for the timer row
                row_buttons.append(button)
            self.buttons.append(row_buttons)

    def place_bombs(self):
        while len(self.bomb_locations) < self.bombs:
            r, c = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if (r, c) not in self.bomb_locations:
                self.bomb_locations.append((r, c))

    def calculate_numbers(self):
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        for r, c in self.bomb_locations:
            self.grid[r][c] = -1
            for i in range(r - 1, r + 2):
                for j in range(c - 1, c + 2):
                    if 0 <= i < self.size and 0 <= j < self.size and self.grid[i][j] != -1:
                        self.grid[i][j] += 1

    def click(self, r, c):
        if self.is_game_over:
            return

        # Start the timer when the first cell is clicked
        if self.start_time is None:
            self.start_time = time.time()

        if (r, c) in self.bomb_locations:
            self.buttons[r][c].config(text="*", bg="red")
            self.game_over()
        else:
            self.reveal(r, c)
            if self.check_win():
                self.win_game()

    def right_click(self, r, c):
        if self.is_game_over:
            return

        current_text = self.buttons[r][c].cget("text")
        if current_text == "":
            self.buttons[r][c].config(text="F", fg="blue", bg="yellow")  # Change color when flagged
            self.buttons[r][c].config(state="disabled")  # Disable button after flagging
        elif current_text == "F":
            self.buttons[r][c].config(text="", bg="SystemButtonFace")  # Reset to default background when unflagged
            self.buttons[r][c].config(state="normal")  # Re-enable button when unflagged

    def reveal(self, r, c):
        if self.grid[r][c] == -1 or self.buttons[r][c].cget("text") != "":
            return
        self.buttons[r][c].config(text=str(self.grid[r][c]), state="disabled", relief="sunken")
        if self.grid[r][c] == 0:
            self.buttons[r][c].config(text="")
            for i in range(r - 1, r + 2):
                for j in range(c - 1, c + 2):
                    if 0 <= i < self.size and 0 <= j < self.size and self.buttons[i][j].cget("state") != "disabled":
                        self.reveal(i, j)

    def check_win(self):
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] != -1 and self.buttons[r][c].cget("state") != "disabled":
                    return False
        return True

    def calculate_score(self, time_taken):
        # Base scores based on difficulty
        if self.difficulty == "easy":
            base_score = 100
        elif self.difficulty == "medium":
            base_score = 200
        elif self.difficulty == "hard":
            base_score = 300

        # Multiplier based on time (the faster, the higher the multiplier)
        if time_taken > 0:
            multiplier = 100 / time_taken
        else:
            multiplier = 0

        score = int(base_score * multiplier)
        return score

    def game_over(self):
        self.is_game_over = True
        time_taken = time.time() - self.start_time if self.start_time else 0
        score = self.calculate_score(time_taken)
        for r, c in self.bomb_locations:
            self.buttons[r][c].config(text="*", bg="red")
        messagebox.showinfo("Game Over", f"You hit a bomb! Game over!\nTime: {int(time_taken)} seconds\nScore: {score}")

    def win_game(self):
        self.is_game_over = True
        time_taken = time.time() - self.start_time
        score = self.calculate_score(time_taken)
        messagebox.showinfo("Congratulations", f"You win!\nTime: {int(time_taken)} seconds\nScore: {score}")

    def update_timer(self):
        if self.start_time is not None and not self.is_game_over:
            time_elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {time_elapsed} seconds")
        self.root.after(1000, self.update_timer)
        
    def save_game(self):
        # Save the game state to a file (for example, using JSON)
        game_state = {
            'size': self.size,
            'bombs': self.bombs,
            'grid': self.grid,
            'bomb_locations': self.bomb_locations,
            'buttons_state': [[self.buttons[r][c].cget("text") for c in range(self.size)] for r in range(self.size)]
        }
        with open("saved_game.json", "w") as file:
            json.dump(game_state, file)
        messagebox.showinfo("Save Game", "Game has been saved.")

    def quit_game(self):
        if messagebox.askyesno("Quit Game", "Do you want to save the game before quitting?"):
            self.save_game()
        if messagebox.askyesno("Quit Game", "Are you sure you want to quit?"):
            self.root.destroy()  # Close the game window
            
# Function to create the game with different difficulty levels
def start_game(difficulty, no_flags=False):
    if difficulty == "easy":
        size, bombs = 9, 10
    elif difficulty == "medium":
        size, bombs = 16, 40
    elif difficulty == "hard":
        size, bombs = 24, 99
    root = tk.Tk()
    root.title(f"Minesweeper - {difficulty.capitalize()} Mode")
    game = Minesweeper(root, size=size, bombs=bombs, difficulty=difficulty, no_flags=no_flags)
    root.mainloop()

# Main menu to select difficulty
def main_menu():
    root = tk.Tk()
    root.title("Minesweeper")

    tk.Label(root, text="Choose Difficulty").pack(pady=10)

    tk.Button(root, text="Easy", command=lambda: [root.destroy(), start_game("easy")]).pack(pady=5)
    tk.Button(root, text="Medium", command=lambda: [root.destroy(), start_game("medium")]).pack(pady=5)
    tk.Button(root, text="Hard", command=lambda: [root.destroy(), start_game("hard")]).pack(pady=5)
    tk.Button(root, text="No Flags", command=lambda: [root.destroy(), start_game("easy", no_flags=True)]).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main_menu()
