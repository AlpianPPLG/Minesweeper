import tkinter as tk
from tkinter import messagebox
import random
import time

class Minesweeper:
    def __init__(self, root, size=9, bombs=10, difficulty="easy", dark_mode=False, no_flags=False, zen_mode=False, hints_available=3):
        self.root = root
        self.size = size
        self.bombs = bombs
        self.difficulty = difficulty
        self.grid = []
        self.buttons = []
        self.bomb_locations = []
        self.is_game_over = False
        self.start_time = None
        self.dark_mode = dark_mode
        self.no_flags = no_flags
        self.zen_mode = zen_mode  # Mode Zen tanpa waktu
        self.hints_available = hints_available  # Jumlah hints yang tersedia
        self.timer_label = tk.Label(self.root, text="Time: 0")
        self.timer_label.grid(row=0, column=0, columnspan=self.size - 2, sticky="ew")
        self.hint_button = tk.Button(self.root, text=f"Hints ({self.hints_available})", command=self.use_hint)
        self.hint_button.grid(row=0, column=self.size - 4, sticky="ew")
        self.mode_button = tk.Button(self.root, text="Dark Mode", command=self.toggle_mode)
        self.mode_button.grid(row=0, column=self.size - 2, columnspan=2, sticky="ew")
        self.quit_button = tk.Button(self.root, text="Quit", command=self.quit_game)
        self.quit_button.grid(row=0, column=self.size, columnspan=2, sticky="ew")
        self.create_widgets()
        self.place_bombs()
        self.calculate_numbers()
        self.update_timer()
        self.apply_mode()

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
        self.quit_button.config(bg=bg_color, fg=fg_color)
        self.hint_button.config(bg=bg_color, fg=fg_color)

        for r in range(self.size):
            for c in range(self.size):
                self.buttons[r][c].config(bg=button_bg, fg=fg_color, highlightbackground=bg_color)

    def create_widgets(self):
        for r in range(self.size):
            row_buttons = []
            for c in range(self.size):
                button = tk.Button(self.root, width=2, height=1, command=lambda r=r, c=c: self.click(r, c))
                button.bind("<Button-3>", lambda e, r=r, c=c: self.right_click(r, c) if not self.no_flags else None)
                button.grid(row=r + 1, column=c)
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

        if self.start_time is None and not self.zen_mode:  # Timer only starts if not in Zen mode
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
            self.buttons[r][c].config(text="F", fg="blue", bg="yellow")
            self.buttons[r][c].config(state="disabled")
        elif current_text == "F":
            self.buttons[r][c].config(text="", bg="SystemButtonFace")
            self.buttons[r][c].config(state="normal")

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
        if self.difficulty == "easy":
            base_score = 100
        elif self.difficulty == "medium":
            base_score = 200
        elif self.difficulty == "hard":
            base_score = 300

        if time_taken > 0:
            multiplier = 100 / time_taken
        else:
            multiplier = 0

        return int(base_score * multiplier)

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
        if self.start_time is not None and not self.is_game_over and not self.zen_mode:
            time_elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {time_elapsed} seconds")
        self.root.after(1000, self.update_timer)

    def use_hint(self):
        if self.hints_available > 0:
            safe_cells = [(r, c) for r in range(self.size) for c in range(self.size)
                          if self.grid[r][c] != -1 and self.buttons[r][c].cget("state") == "normal"]
            if safe_cells:
                r, c = random.choice(safe_cells)
                self.reveal(r, c)
                self.hints_available -= 1
                self.hint_button.config(text=f"Hints ({self.hints_available})")
        else:
            messagebox.showinfo("No Hints", "No hints left!")

    def quit_game(self):
        if messagebox.askyesno("Quit Game", "Are you sure you want to quit?"):
            self.root.destroy()

# Main menu to select difficulty and custom modes
def start_game(difficulty, no_flags=False, zen_mode=False, custom=False, custom_size=9, custom_bombs=10):
    if custom:
        size, bombs = custom_size, custom_bombs
    elif difficulty == "easy":
        size, bombs = 9, 10
    elif difficulty == "medium":
        size, bombs = 16, 40
    elif difficulty == "medium":
        size, bombs = 16, 40
    elif difficulty == "hard":
        size, bombs = 24, 99

    root = tk.Tk()
    root.title("Minesweeper")

    # Inisialisasi permainan Minesweeper dengan mode yang dipilih
    game = Minesweeper(root, size=size, bombs=bombs, difficulty=difficulty, no_flags=no_flags, zen_mode=zen_mode)

    root.mainloop()

# Fungsi untuk memilih mode permainan dari menu utama
def main_menu():
    root = tk.Tk()
    root.title("Minesweeper Menu")

    def start_easy():
        root.destroy()
        start_game("easy")

    def start_medium():
        root.destroy()
        start_game("medium")

    def start_hard():
        root.destroy()
        start_game("hard")

    def start_zen_mode():
        root.destroy()
        start_game("easy", zen_mode=True)

    def start_custom_mode():
        root.destroy()
        # Di sini kita bisa meminta ukuran grid dan jumlah bom secara dinamis
        custom_size = int(input("Enter grid size (e.g., 9 for 9x9): "))
        custom_bombs = int(input(f"Enter number of bombs (max {custom_size * custom_size - 1}): "))
        start_game("custom", custom=True, custom_size=custom_size, custom_bombs=custom_bombs)

    def start_no_flags_mode():
        root.destroy()
        start_game("easy", no_flags=True)

    # Tombol di menu utama
    tk.Button(root, text="Easy", command=start_easy).grid(row=0, column=0)
    tk.Button(root, text="Medium", command=start_medium).grid(row=1, column=0)
    tk.Button(root, text="Hard", command=start_hard).grid(row=2, column=0)
    tk.Button(root, text="Zen Mode (No Timer)", command=start_zen_mode).grid(row=3, column=0)
    tk.Button(root, text="Custom Mode", command=start_custom_mode).grid(row=4, column=0)
    tk.Button(root, text="No Flags Mode", command=start_no_flags_mode).grid(row=5, column=0)

    root.mainloop()

if __name__ == "__main__":
    main_menu()
