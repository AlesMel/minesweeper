import tkinter as tk
import random
from tkinter import PhotoImage, messagebox
from PIL import Image, ImageTk
import sys 

def load_image(path, size=(30, 30)):  # Adjust to the size that looks good for your images
    img = Image.open(path)
    img = img.resize(size=size)
    return ImageTk.PhotoImage(img)

def create_transparent_image(size):
    # Create a transparent image
    transparent_image = Image.new('RGBA', size, (0, 0, 0, 0))
    return ImageTk.PhotoImage(transparent_image)
# In your Minesweeper class

can_continue = True

class Cell:
    number_colors = ["blue", "green", "red", "purple", "turquoise", "black", "gray"]

    def __init__(self, master, minesweeper, x, y, mine_image, flag_image, transparent_image):
        # Create a frame with a fixed size
        self.frame = tk.Frame(master, width=30, height=30)  # Set your desired size in pixels
        self.frame.pack_propagate(False)  # Prevent the frame from resizing to fit its contents
        self.frame.grid(row=x, column=y)
        self.minesweeper = minesweeper
        self.master = master
        self.mine_image = mine_image
        self.flag_image = flag_image
        self.transparent_image = transparent_image
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.x = x
        self.y = y
        self.neighbors = []
        self.neighbor_mines = 0
        # Create the button inside the frame
        self.button = tk.Button(self.frame, image=transparent_image, compound='center')
        self.button.pack(fill='both', expand=True)  # Make the button fill the frame
        self.button.bind("<Button-1>", self.reveal)  # Left click
        self.button.bind("<Button-3>", self.flag)    # Right click

    def reveal(self, event=None):
        global can_continue
        if can_continue:
            if not self.is_flagged:
                if self.is_mine:
                    self.button.config(image=self.mine_image)
                    self.is_revealed = True
                    messagebox.showinfo("Game Over", "Boom! You hit a mine.")
                    can_continue = False
                    # self.create_custom_messagebox("Game Over! You hit a mine.")
                else:
                    count = self.count_adjacent_mines()
                    self.button.config(image=self.transparent_image, text=str(count) if count > 0 else "", compound = 'center', fg=Cell.number_colors[count])
                    if count == 0:
                        to_reveal = self.reveal_neighbours()
                        for point in to_reveal:
                            p_count = point.count_adjacent_mines()
                            point.is_revealed = True
                            if p_count > 0:
                                point.button.config(image=self.transparent_image, text=str(p_count), compound = 'center', fg=Cell.number_colors[p_count])
                            else:
                                point.button.config(image=self.transparent_image, text="", compound = 'center', bg="white")
                    self.is_revealed = True
            if self.minesweeper.check_win():
                messagebox.showinfo("Congratulations!", "You have cleared all mines!")
    
    def reveal_neighbours(self):
        # flood-fill
        to_reveal = set()  # Using a set to avoid duplicates
        queue = [self]

        while queue:
            point = queue.pop(0)

            if point.is_revealed or point.is_mine:
                continue

            point.is_revealed = True  # Mark the point as revealed
            to_reveal.add(point)

            # Check if the current point has adjacent mines
            has_mine = any(n.is_mine for n in point.neighbors)

            # If the point has no adjacent mines, add its neighbors to the queue
            if not has_mine:
                for n in point.neighbors:
                    if not n.is_revealed and n not in queue:
                        queue.append(n)

        return list(to_reveal)
                        
    def set_neighbors(self, grid):
        rows, cols = len(grid), len(grid[0])
        directions = [-1, 0, 1]
        for dx in directions:
            for dy in directions:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    self.neighbors.append(grid[nx][ny])
        self.neighbor_mines = self.count_adjacent_mines()

    def count_adjacent_mines(self):
        mines = 0
        for neighbour in self.neighbors:
            if neighbour.is_mine:
                mines += 1
        return mines
    
    def flag(self, event=None):
        if not self.is_revealed:
            self.is_flagged = not self.is_flagged
            if self.is_flagged:
                self.button.config(image=self.flag_image)
            else:
                self.button.config(image='') 

    def create_custom_messagebox(self, message):
        # Create a top-level frame for the message box
        message_frame = tk.Frame(self.master, borderwidth=2, relief='raised')
        message_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')  # Adjust row and column as needed

        # Configure the grid for resizing
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # Add a label for the message
        message_label = tk.Label(message_frame, text=message)
        message_label.grid(row=0, column=0, padx=10, pady=10)

        # Add a close button
        close_button = tk.Button(message_frame, text='Close', command=message_frame.destroy)
        close_button.grid(row=1, column=0, pady=5)

        return message_frame

class Minesweeper:
    def __init__(self, master, rows=10, columns=10, mine_count=2):
        self.master = master
        self.rows = rows
        self.columns = columns
        self.mine_count = mine_count
        global mine_image, flag_image
        self.mine_image = load_image("Assets/mine.png")
        self.flag_image = load_image("Assets/flag.png")
        self.transparent_image = create_transparent_image((15, 15))
        self.setup_game()

    def setup_game(self):
        self.cells = [[Cell(self.master, self, x, y, self.mine_image, self.flag_image, self.transparent_image) for y in range(self.columns)] for x in range(self.rows)]
        for row in self.cells:
            for cell in row:
                cell.set_neighbors(self.cells)
        for i in range(self.mine_count):
            x_rand = random.randint(0, self.rows-1)
            y_rand = random.randint(0, self.columns-1)
            cell = self.cells[x_rand][y_rand]
            if cell.is_mine == False:
                cell.is_mine = True
            else:
                i-=1
       
    def reset_game(self):
        self.cells.clear()
        self.setup_game()
        global can_continue
        can_continue = True

    def check_win(self):
        # Check if all non-mine cells are revealed
        for row in self.cells:
            for cell in row:
                if not cell.is_mine and not cell.is_revealed:
                    return False  # Found a non-mine cell that is not revealed

        # Optional: Check if all mines are correctly flagged
        # for row in self.cells:
        #     for cell in row:
        #         if cell.is_mine != cell.is_flagged:
        #             return False  # Found a discrepancy in flagging

        # If all conditions are met
        return True  # Player wins
                


if __name__ == "__main__":
    root = tk.Tk()
    game_frame = tk.Frame(root)
    game_frame.pack(side='top')  # This frame will contain the Minesweeper grid
    game = Minesweeper(game_frame, mine_count=int(sys.argv[1]))  # Pass the frame to Minesweeper instead of root

    control_frame = tk.Frame(root)
    control_frame.pack(side='bottom')  # This frame will contain the control buttons

    reset_button = tk.Button(control_frame, text="Reset Game", command=game.reset_game)
    reset_button.pack()  # Use pack within the control frame

    root.mainloop()
