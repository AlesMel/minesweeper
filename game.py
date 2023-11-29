import tkinter as tk
import random
from tkinter import PhotoImage
from PIL import Image, ImageTk

def load_image(path, size=(15, 15)):  # Adjust to the size that looks good for your images
    img = Image.open(path)
    img = img.resize(size=size)
    return ImageTk.PhotoImage(img)

def create_transparent_image(size):
    # Create a transparent image
    transparent_image = Image.new('RGBA', size, (0, 0, 0, 0))
    return ImageTk.PhotoImage(transparent_image)
# In your Minesweeper class

class Cell:
    number_colors = ["blue", "green", "red", "purple", "turquoise", "black", "gray"]

    def __init__(self, master, x, y, mine_image, flag_image, transparent_image):
        # Create a frame with a fixed size
        self.frame = tk.Frame(master, width=15, height=15)  # Set your desired size in pixels
        self.frame.pack_propagate(False)  # Prevent the frame from resizing to fit its contents
        self.frame.grid(row=x, column=y)
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
        # self.button = tk.Button(master, image=create_transparent_image((15, 15)), compound='center')
        # self.button.image = create_transparent_image((15, 15))  # Keep a reference to the image
        # # self.button = tk.Button(master, image='')
        # # self.button.grid(row=x, column=y, sticky='nsew')  # Use 'nsew' to make the button expand
        # # master.grid_columnconfigure(y, weight=1)  # This makes the column expandable
        # # master.grid_rowconfigure(x, weight=1)  # This makes the row expandable
        # self.button.grid(row=x, column=y, padx=0, pady=0)
        # self.button.bind("<Button-1>", self.reveal)  # Left click
        # self.button.bind("<Button-3>", self.flag)    # Right click

    def reveal(self, event=None):
        if not self.is_flagged:
            if self.is_mine:
                self.button.config(image=self.mine_image)
                self.is_revealed = True
            else:
                count = self.count_adjacent_mines()
                self.button.config(image=self.transparent_image, text=str(count) if count > 0 else "", compound = 'center', fg=Cell.number_colors[count])
                if count == 0:
                    print("Count is 0")
                    to_reveal = self.reveal_neighbours()
                    for point in to_reveal:
                        p_count = point.count_adjacent_mines()
                        print(f"point: {point}")
                        if p_count > 0:
                            point.button.config(image=self.transparent_image, text=str(p_count), compound = 'center', fg=Cell.number_colors[p_count])
                        else:
                            point.button.config(image=self.transparent_image, text="", compound = 'center', bg="white")

    
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
            # Add logic for flagging a cell
            # For example, change button text to show a flagw

class Minesweeper:
    def __init__(self, master, rows=10, columns=10, mine_count=25):
        self.master = master
        self.rows = rows
        self.columns = columns
        global mine_image, flag_image
        self.mine_image = load_image("Assets/mine.png")
        self.flag_image = load_image("Assets/flag.png")
        self.transparent_image = create_transparent_image((15, 15))
        self.cells = [[Cell(master, x, y, self.mine_image, self.flag_image, self.transparent_image) for y in range(columns)] for x in range(rows)]
        for row in self.cells:
            for cell in row:
                cell.set_neighbors(self.cells)
        for i in range(mine_count):
            x_rand = random.randint(0, rows-1)
            y_rand = random.randint(0, columns-1)
            cell = self.cells[x_rand][y_rand]
            if cell.is_mine == False:
                cell.is_mine = True
            else:
                i-=1
                
        # Add any additional initialization here (e.g., placing mines)

    # Add additional methods here (e.g., for game logic)

def main():
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()

if __name__ == "__main__":
    main()
