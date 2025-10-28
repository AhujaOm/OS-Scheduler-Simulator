import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageStat
import math
from collections import deque
import random

class VisualSchedulingSimulator:
    
    def __init__(self, root):
        """
        Initializes the GUI for the Visual CPU Scheduling Simulator.
        """
        self.root = root
        self.root.title("Visual CPU Scheduling Simulator (Image Rendering)")
        self.root.geometry("1400x900") # Reduced from 1600x1000
        # self.root.state('zoomed') # Removed zoomed state to respect geometry
        self.root.configure(bg="#e8e8e8")

        # --- Style configuration ---
        style = ttk.Style(self.root)
        style.theme_use('clam')
        
        style.configure("TFrame", background="#fdfdff")
        style.configure("Background.TFrame", background="#e8e8e8")
        style.configure("TLabel", background="#fdfdff", font=("Helvetica", 11))
        style.configure("TButton", font=("Helvetica", 11, "bold"), padding=8)
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
        style.configure("Treeview", rowheight=25, font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), background="#fdfdff", foreground="#333")
        style.configure("Result.TLabel", font=("Helvetica", 12, "bold"), background="#fdfdff")
        style.configure("Time.TLabel", font=("Helvetica", 20, "bold"), background="#e8e8e8", foreground="#005f9e")
        style.map("TButton",
            background=[('active', '#005f9e')],
            foreground=[('active', 'white')])
        style.map("Run.TButton",
            background=[('!disabled', '#28a745'), ('active', '#218838')],
            foreground=[('!disabled', 'white')])
        style.map("Stop.TButton",
            background=[('!disabled', '#dc3545'), ('active', '#c82333')],
            foreground=[('!disabled', 'white')])
        
        # Style for selected treeview item (to override default)
        style.map('Treeview',
          background=[('selected', '#00FFFF')], # Cyan background when selected
          foreground=[('selected', '#000000')]) # Black text when selected


        # --- Process/Data Storage ---
        self.processes = []           # Master list of all generated processes
        self.ready_queue = deque()
        self.completed_processes = []
        self.current_process = None
        self.current_time = 0
        self.time_slice_remaining = 0
        self.total_idle_time = 0
        self.simulation_running = False
        self.simulation_delay = 5  # Default delay in ms
        self.gantt_colors = {}
        self.process_map = {}         # Stores {pid: process_object}
        self.base_image = None
        
        self.random_arrival_var = tk.BooleanVar(value=True) # Variable for the checkbox
        self.all_algorithms = ("FCFS", "SJF", "Priority", "Round Robin")
        self.no_fcfs_algorithms = ("SJF", "Priority", "Round Robin")


        # --- Main Layout Frames ---
        self.main_frame = ttk.Frame(self.root, style="Background.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left_panel = ttk.Frame(self.main_frame, style="Background.TFrame", width=400) # Reduced from 450
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.left_panel.pack_propagate(False) # Prevent resizing

        # --- Setup for scrollable left panel ---
        self.left_canvas = tk.Canvas(self.left_panel, bg="#e8e8e8", highlightthickness=0)
        self.left_scrollbar = ttk.Scrollbar(self.left_panel, orient="vertical", command=self.left_canvas.yview)
        self.left_canvas.configure(yscrollcommand=self.left_scrollbar.set)
        
        self.left_scrollable_frame = ttk.Frame(self.left_canvas, style="Background.TFrame")
        self.left_canvas_frame_id = self.left_canvas.create_window((0, 0), window=self.left_scrollable_frame, anchor="nw")
        
        self.left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.left_scrollable_frame.bind("<Configure>", self.on_left_frame_configure)
        self.left_canvas.bind("<Configure>", self.on_left_canvas_configure)
        # --- End scrollable setup ---

        self.right_panel = ttk.Frame(self.main_frame, style="Background.TFrame")
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Left Panel: Controls ---
        self.create_controls_ui(self.left_scrollable_frame) # Pass the scrollable frame
        
        # --- Right Panel: Visualization ---
        self.create_visualization_ui(self.right_panel)
        
    def on_left_frame_configure(self, event=None):
        """Updates the scrollregion of the left canvas when the frame size changes."""
        self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))

    def on_left_canvas_configure(self, event=None):
        """Ensures the frame inside the canvas fills the canvas width."""
        self.left_canvas.itemconfig(self.left_canvas_frame_id, width=event.width)

    def create_controls_ui(self, parent):
        """Creates the left-hand control panel."""
        
        # --- Image Frame ---
        img_frame = ttk.Frame(parent, padding="15", relief="solid", borderwidth=1)
        img_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(img_frame, text="1. Image & Grid Setup", style="Header.TLabel").pack(pady=5, anchor="w")
        
        self.load_image_button = ttk.Button(img_frame, text="Load Image", command=self.load_image)
        self.load_image_button.pack(fill=tk.X, pady=5, ipady=5)
        
        self.image_label = ttk.Label(img_frame, text="No image loaded.", anchor="center", background="#eee", relief="sunken")
        self.image_label.pack(fill=tk.X, pady=5, ipady=10) # Reduced ipady from 20
        
        grid_frame = ttk.Frame(img_frame)
        grid_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(grid_frame, text="Grid Size (e.g., 10 for 10x10):").pack(side=tk.LEFT, padx=5)
        self.grid_size_entry = ttk.Entry(grid_frame, width=5, font=("Helvetica", 11))
        self.grid_size_entry.pack(side=tk.LEFT, padx=5)
        self.grid_size_entry.insert(0, "10")

        # --- Moved Checkbutton here ---
        self.random_arrival_check = ttk.Checkbutton(img_frame, text="Random Arrival Time?", 
                                                    variable=self.random_arrival_var, 
                                                    onvalue=True, offvalue=False, 
                                                    command=self.on_random_arrival_toggle)
        self.random_arrival_check.pack(fill=tk.X, pady=8, padx=5) # Added a bit of padding

        self.generate_procs_button = ttk.Button(img_frame, text="Generate Processes from Image", command=self.generate_processes, state="disabled")
        self.generate_procs_button.pack(fill=tk.X, pady=10, ipady=5)
        
        # --- Algorithm Frame ---
        algo_frame = ttk.Frame(parent, padding="15", relief="solid", borderwidth=1)
        algo_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(algo_frame, text="2. Simulation Controls", style="Header.TLabel").pack(pady=5, anchor="w")

        # --- Removed Checkbutton from here ---

        algo_select_frame = ttk.Frame(algo_frame)
        algo_select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(algo_select_frame, text="Algorithm:").pack(side=tk.LEFT, padx=5)
        self.algorithm_var = tk.StringVar(value="FCFS")
        # --- Use Combobox instead of OptionMenu to allow dynamic updates ---
        self.algo_dropdown = ttk.Combobox(algo_select_frame, textvariable=self.algorithm_var, 
                                          values=self.all_algorithms, state="readonly")
        self.algo_dropdown.pack(fill=tk.X, expand=True)

        tq_frame = ttk.Frame(algo_frame)
        tq_frame.pack(fill=tk.X, pady=5)
        ttk.Label(tq_frame, text="Time Quantum (for RR):").pack(side=tk.LEFT, padx=5)
        self.time_quantum_entry = ttk.Entry(tq_frame, width=5, font=("Helvetica", 11))
        self.time_quantum_entry.pack(side=tk.LEFT, padx=5, expand=True)
        self.time_quantum_entry.insert(0, "4")
        
        delay_frame = ttk.Frame(algo_frame)
        delay_frame.pack(fill=tk.X, pady=5)
        ttk.Label(delay_frame, text="Delay (ms per tick):").pack(side=tk.LEFT, padx=5)
        self.delay_entry = ttk.Entry(delay_frame, width=5, font=("Helvetica", 11))
        self.delay_entry.pack(side=tk.LEFT, padx=5, expand=True)
        self.delay_entry.insert(0, "1000")
        
        self.run_button = ttk.Button(algo_frame, text="Run Simulation", style="Run.TButton", command=self.run_simulation, state="disabled")
        self.run_button.pack(fill=tk.X, pady=8, ipady=4) # Reduced ipady from 8, pady from 10
        
        self.stop_button = ttk.Button(algo_frame, text="Stop & Reset", style="Stop.TButton", command=self.reset_simulation, state="disabled")
        self.stop_button.pack(fill=tk.X, pady=4, ipady=4) # Reduced ipady from 8, pady from 5
        
        # --- Process Table Frame ---
        process_frame = ttk.Frame(parent, padding="15", relief="solid", borderwidth=1)
        process_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(process_frame, text="Generated Processes", style="Header.TLabel").pack(pady=5, anchor="w")
        
        tree_frame = ttk.Frame(process_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        self.process_tree = ttk.Treeview(tree_frame, columns=("ID", "Arrival", "Burst", "Priority"), show="headings", height=8, yscrollcommand=tree_scroll.set) # Reduced height from 10
        tree_scroll.config(command=self.process_tree.yview)
        
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.process_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add click binding for highlighting
        self.process_tree.bind("<<TreeviewSelect>>", self.on_process_select)
        
        self.process_tree.heading("ID", text="PID")
        self.process_tree.heading("Arrival", text="Arrival")
        self.process_tree.heading("Burst", text="Burst")
        self.process_tree.heading("Priority", text="Priority")
        self.process_tree.column("ID", width=40, anchor="center")
        self.process_tree.column("Arrival", width=60, anchor="center")
        self.process_tree.column("Burst", width=60, anchor="center")
        self.process_tree.column("Priority", width=60, anchor="center")
        
    def create_visualization_ui(self, parent):
        """Creates the right-hand visualization panel."""
        
        # --- Time & Stats Frame ---
        time_stats_frame = ttk.Frame(parent, style="Background.TFrame")
        time_stats_frame.pack(fill=tk.X, pady=5)

        self.time_label = ttk.Label(time_stats_frame, text="Current Time: 0", style="Time.TLabel")
        self.time_label.pack(side=tk.LEFT, padx=20)
        
        self.stats_label = ttk.Label(time_stats_frame, text="", style="Result.TLabel", background="#e8e8e8")
        self.stats_label.pack(side=tk.RIGHT, padx=20)
        
        # --- Main Viz Frame (Image + Ready Queue) ---
        viz_frame = ttk.Frame(parent, style="Background.TFrame")
        viz_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # --- Image Canvas ---
        img_canvas_frame = ttk.Frame(viz_frame, padding="15", relief="solid", borderwidth=1)
        img_canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(img_canvas_frame, text="Real-Time Image Rendering", style="Header.TLabel").pack(pady=5, anchor="n")
        
        # Canvas will be fixed size for simplicity
        self.image_canvas_size = 350 # Reduced from 400
        self.image_canvas = tk.Canvas(img_canvas_frame, width=self.image_canvas_size, height=self.image_canvas_size, bg="#000000", highlightthickness=0)
        self.image_canvas.pack(pady=10)
        self.image_canvas.bind("<Button-1>", self.clear_highlight) # Add click to clear highlight

        # --- Ready Queue ---
        queue_frame = ttk.Frame(viz_frame, padding="15", relief="solid", borderwidth=1, width=180) # Reduced from 200
        queue_frame.pack(side=tk.RIGHT, fill=tk.Y)
        queue_frame.pack_propagate(False)
        
        ttk.Label(queue_frame, text="Ready Queue", style="Header.TLabel").pack(pady=5, anchor="n")
        
        queue_list_frame = ttk.Frame(queue_frame)
        queue_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        queue_scroll = ttk.Scrollbar(queue_list_frame, orient="vertical")
        self.queue_listbox = tk.Listbox(queue_list_frame, yscrollcommand=queue_scroll.set, font=("Helvetica", 11), bg="#fdfdff")
        queue_scroll.config(command=self.queue_listbox.yview)
        
        queue_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.queue_listbox.pack(fill=tk.BOTH, expand=True)
        
        # --- Gantt Chart Canvas ---
        gantt_frame = ttk.Frame(parent, padding="15", relief="solid", borderwidth=1)
        gantt_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(gantt_frame, text="Live Gantt Chart", style="Header.TLabel").pack(pady=5, anchor="n")
        
        self.gantt_canvas = tk.Canvas(gantt_frame, width=1000, height=60, bg="#ffffff", highlightthickness=1, relief="sunken") # Reduced height from 80
        self.gantt_canvas.pack(fill=tk.X, expand=True, pady=10)
        self.gantt_canvas.bind("<Button-1>", self.clear_highlight) # Add click to clear highlight
        
    def load_image(self):
        """Opens a file dialog to load an image."""
        try:
            filepath = filedialog.askopenfilename(
                title="Select an Image",
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
            )
            if not filepath:
                return

            self.base_image = Image.open(filepath)
            
            # Create a thumbnail for the label
            thumb = self.base_image.copy()
            thumb.thumbnail((250, 60)) # (width, height) - Reduced height from 80
            self.tk_thumb = ImageTk.PhotoImage(thumb)
            
            self.image_label.config(image=self.tk_thumb, text="")
            self.generate_procs_button.config(state="normal")
            self.run_button.config(state="disabled") # Require re-generation
            self.reset_simulation()
            
        except Exception as e:
            messagebox.showerror("Image Load Error", f"Failed to load image: {e}")
            self.base_image = None
            self.generate_procs_button.config(state="disabled")

    def generate_processes(self):
        """Divides the loaded image into blocks and creates processes."""
        if not self.base_image:
            messagebox.showerror("Error", "Please load an image first.")
            return
            
        try:
            N = int(self.grid_size_entry.get())
            if N <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Grid Size must be a positive integer (e.g., 10).")
            return
            
        self.reset_simulation()
        
        # Resize image to fit the canvas for visualization
        img = self.base_image.resize((self.image_canvas_size, self.image_canvas_size), Image.Resampling.LANCZOS)
        
        block_w = self.image_canvas_size // N
        block_h = self.image_canvas_size // N
        center_x, center_y = N / 2, N / 2
        pid_counter = 1
        
        # --- Set arrival times based on checkbox ---
        if self.random_arrival_var.get():
            arrival_times = [i*2 for i in range(N*N)] # Stagger arrivals
            random.shuffle(arrival_times)
        else:
            arrival_times = [0] * (N*N) # All arrive at time 0

        for y in range(N):
            for x in range(N):
                # Define box coordinates
                left, top = x * block_w, y * block_h
                right, bottom = (x + 1) * block_w, (y + 1) * block_h
                
                # Crop the block from the image
                block_img = img.crop((left, top, right, bottom))
                
                # --- Calculate Burst Time (Complexity) ---
                # Convert to grayscale and get pixel value std deviation
                try:
                    stat = ImageStat.Stat(block_img.convert("L"))
                    stddev = stat.stddev[0]
                    burst_time = max(1, int(stddev / 5) + 1) # Ensure burst > 0
                except ZeroDivisionError:
                    burst_time = 1 # Solid color block
                
                # --- Calculate Priority ---
                # Lower number = higher priority
                # Priority based on distance from center
                dist = math.dist((x, y), (center_x, center_y))
                priority = int(dist * 2) # Scale it
                
                # --- Create Process Object ---
                process = {
                    "pid": pid_counter,
                    "arrival": arrival_times[pid_counter - 1], # Staggered or 0 arrival
                    "burst": burst_time,
                    "priority": priority,
                    "remaining_burst": burst_time,
                    "tk_image": ImageTk.PhotoImage(block_img), # Full color image
                    "coords": (left, top),
                    "block_size": (block_w, block_h),
                    "wait_time": 0,
                    "start_time": -1,
                    "completion_time": -1
                }
                
                self.processes.append(process)
                self.process_map[pid_counter] = process
                
                # Add to the Treeview with a unique tag for coloring
                self.process_tree.insert("", "end", 
                                        values=(process["pid"], process["arrival"], process["burst"], process["priority"]), 
                                        tags=(f"PID_{pid_counter}",))
                
                pid_counter += 1
                
        self.run_button.config(state="normal")
        self.stop_button.config(state="normal")
        self.draw_initial_image_canvas()
        self.generate_gantt_colors() # Generate colors AND apply them to tree

    def draw_initial_image_canvas(self):
        """Draws all image blocks as 'pending' (grayed out)."""
        self.image_canvas.delete("all")
        for p in self.processes:
            x, y = p['coords']
            w, h = p['block_size']
            # Draw a gray box as a placeholder
            self.image_canvas.create_rectangle(x, y, x + w, y + h, fill="#333", outline="#555", tags=f"block_{p['pid']}")
            
    def generate_gantt_colors(self):
        """Assigns a unique color to each process for the Gantt chart and Treeview."""
        self.gantt_colors = {}
        for p in self.processes:
            r = random.randint(50, 200)
            g = random.randint(50, 200)
            b = random.randint(50, 200)
            color = f'#{r:02x}{g:02x}{b:02x}'
            text_color = self.get_text_color(color)
            
            self.gantt_colors[p['pid']] = color
            # Configure the tag in the Treeview to have this background/foreground
            self.process_tree.tag_configure(f"PID_{p['pid']}", background=color, foreground=text_color)
            
        self.gantt_colors["Idle"] = "#e0e0e0"

    def run_simulation(self):
        """Starts the tick-based simulation."""
        if not self.processes:
            messagebox.showwarning("No Processes", "Please generate processes from an image first.")
            return
            
        if self.simulation_running:
            return

        # Get simulation parameters
        self.selected_algorithm = self.algorithm_var.get()
        try:
            self.time_quantum = int(self.time_quantum_entry.get())
            if self.time_quantum <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Time Quantum must be a positive integer.")
            return

        try:
            self.simulation_delay = int(self.delay_entry.get())
            if self.simulation_delay < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Delay must be a non-negative integer (e.g., 1000, 500, 0).")
            return
        
        # Clear any active highlight before running
        self.clear_highlight()
        
        self.simulation_running = True
        self.run_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.algo_dropdown.config(state="disabled")
        self.generate_procs_button.config(state="disabled")
        self.random_arrival_check.config(state="disabled") # Disable checkbox
        
        # Start the simulation loop
        self.simulation_tick()

    def simulation_tick(self):
        """The main simulation loop, runs once per time unit."""
        if not self.simulation_running:
            return
            
        # --- 1. Check for New Arrivals ---
        new_arrivals = [p for p in self.processes if p['arrival'] == self.current_time]
        for p in new_arrivals:
            self.ready_queue.append(p)
            
        # Sort ready queue based on algorithm (SJF/Priority)
        # FCFS/RR just append, so no sort needed here
        if self.selected_algorithm == "SJF":
            self.ready_queue = deque(sorted(self.ready_queue, key=lambda p: p['burst']))
        elif self.selected_algorithm == "Priority":
            self.ready_queue = deque(sorted(self.ready_queue, key=lambda p: p['priority']))
            
        self.update_ready_queue_listbox()
        
        # --- 2. Increment Wait Times ---
        for p in self.ready_queue:
            p['wait_time'] += 1

        # --- 3. CPU Scheduler Logic ---
        
        # If CPU is free, select a new process
        if self.current_process is None:
            if self.ready_queue:
                # Select process based on algorithm
                if self.selected_algorithm in ["FCFS", "Round Robin"]:
                    self.current_process = self.ready_queue.popleft()
                elif self.selected_algorithm == "SJF":
                    self.current_process = self.ready_queue.popleft() # Already sorted
                elif self.selected_algorithm == "Priority":
                    self.current_process = self.ready_queue.popleft() # Already sorted
                
                # Set start time if it's the first run
                if self.current_process['start_time'] == -1:
                    self.current_process['start_time'] = self.current_time
                
                # Reset time slice for RR
                if self.selected_algorithm == "Round Robin":
                    self.time_slice_remaining = self.time_quantum
            else:
                # CPU is Idle
                self.total_idle_time += 1
                self.draw_gantt_block("Idle")
        
        # --- 4. Process Execution ---
        if self.current_process:
            # Execute for one time unit
            self.current_process['remaining_burst'] -= 1
            if self.selected_algorithm == "Round Robin":
                self.time_slice_remaining -= 1
                
            # Update Visuals
            self.draw_image_block(self.current_process)
            self.draw_gantt_block(self.current_process['pid'])

            # --- 5. Check for Completion or Preemption ---
            
            # Process finished
            if self.current_process['remaining_burst'] == 0:
                self.current_process['completion_time'] = self.current_time + 1
                self.completed_processes.append(self.current_process)
                self.current_process = None
            
            # Round Robin quantum expired
            elif self.selected_algorithm == "Round Robin" and self.time_slice_remaining == 0:
                # Add back to queue (if not finished)
                self.ready_queue.append(self.current_process)
                self.current_process = None
        
        # --- 6. Update UI & Loop ---
        self.time_label.config(text=f"Current Time: {self.current_time}")
        
        if len(self.completed_processes) == len(self.processes):
            # Simulation Finished
            self.finish_simulation()
        else:
            # Continue to next tick
            self.current_time += 1
            self.root.after(self.simulation_delay, self.simulation_tick) # Use variable delay
            
    def finish_simulation(self):
        """Calculates final stats and resets the UI."""
        self.simulation_running = False
        
        total_wait = 0
        total_tat = 0
        n = len(self.completed_processes)
        
        if n > 0:
            for p in self.completed_processes:
                tat = p['completion_time'] - p['arrival']
                wait = tat - p['burst']
                total_wait += wait
                total_tat += tat
            
            avg_wait = total_wait / n
            avg_tat = total_tat / n
            
            stats_text = (
                f"Simulation Complete!\n"
                f"Avg. Waiting Time: {avg_wait:.2f}\n"
                f"Avg. Turnaround Time: {avg_tat:.2f}"
            )
            self.stats_label.config(text=stats_text)
            messagebox.showinfo("Simulation Complete", stats_text)
        
        self.run_button.config(state="normal")
        self.algo_dropdown.config(state="normal")
        self.generate_procs_button.config(state="normal")
        self.random_arrival_check.config(state="normal") # Re-enable checkbox

    def reset_simulation(self):
        """Stops and resets the entire simulation state."""
        self.simulation_running = False
        self.processes = []
        self.process_map = {}
        self.gantt_colors = {}
        self.ready_queue.clear()
        self.completed_processes = []
        self.current_process = None
        self.current_time = 0
        self.time_slice_remaining = 0
        self.total_idle_time = 0
        self.simulation_delay = 1000 # Reset delay to default
        
        self.process_tree.delete(*self.process_tree.get_children())
        self.image_canvas.delete("all")
        self.gantt_canvas.delete("all")
        self.queue_listbox.delete(0, tk.END)
        
        self.time_label.config(text="Current Time: 0")
        self.stats_label.config(text="")
        
        self.run_button.config(state="disabled" if self.base_image is None else "normal")
        self.stop_button.config(state="disabled")
        self.algo_dropdown.config(state="normal")
        self.generate_procs_button.config(state="disabled" if self.base_image is None else "normal")
        self.random_arrival_check.config(state="normal") # Re-enable checkbox
        
        # Reset algorithm dropdown based on checkbox state
        if self.random_arrival_var.get():
            self.algo_dropdown.config(values=self.all_algorithms)
        else:
            self.algo_dropdown.config(values=self.no_fcfs_algorithms)
            if self.algorithm_var.get() == "FCFS":
                self.algorithm_var.set("SJF")
        
        # Clear selection and highlight
        self.clear_highlight()

    def update_ready_queue_listbox(self):
        """Refreshes the ready queue visual."""
        self.queue_listbox.delete(0, tk.END)
        for p in self.ready_queue:
            self.queue_listbox.insert(tk.END, f" PID: {p['pid']} (Burst: {p['remaining_burst']})")
            
    def draw_image_block(self, process):
        """Draws the image block, including a 'loading bar' for progress."""
        pid = process['pid']
        x, y = process['coords']
        w, h = process['block_size']
        
        # Delete ALL items for this block (gray box, old image, old progress)
        self.image_canvas.delete(f"block_{pid}")
        
        # Draw the full-color image block
        # We re-tag it with block_{pid} so it can be deleted next tick
        self.image_canvas.create_image(x, y, image=process['tk_image'], anchor="nw", tags=(f"block_{pid}", f"img_{pid}"))
        
        # Calculate progress
        percent_done = 1.0 - (process['remaining_burst'] / process['burst'])
        
        # Draw a semi-transparent "loading" rectangle over the top
        if percent_done < 1.0:
            overlay_height = h * (1.0 - percent_done)
            self.image_canvas.create_rectangle(
                x, y, x + w, y + overlay_height, 
                fill="#000000", stipple="gray50", outline="", 
                tags=(f"block_{pid}", f"progress_{pid}") # Also tag with block_{pid}
            )

    def draw_gantt_block(self, pid):
        """Draws one time-unit block on the live Gantt chart."""
        
        # Scale: 4 pixels per time unit
        scale = 4 # Reduced from 5 to fit more
        bar_height = 30 # Reduced from 50
        y_offset = 10 # Reduced from 15
        
        x = self.current_time * scale
        color = self.gantt_colors.get(pid, "#333")
        
        self.gantt_canvas.create_rectangle(
            x, y_offset, x + scale, y_offset + bar_height, 
            fill=color, outline="#fff"
        )
        
        # Add timestamp label every 10 units
        if self.current_time % 10 == 0:
            self.gantt_canvas.create_text(
                x, y_offset + bar_height + 3, # Adjusted position
                text=str(self.current_time), anchor="n", 
                font=("Helvetica", 9)
            )
            
        # Move canvas view to follow the drawing
        # Add check for self.current_time > 0 to prevent ZeroDivisionError
        if self.current_time > 0 and x > self.gantt_canvas.winfo_width() - 50:
            fraction = (x - self.gantt_canvas.winfo_width() + 50) / (self.current_time * scale)
            # Ensure fraction is valid (0.0 to 1.0)
            if fraction < 0.0: fraction = 0.0
            if fraction > 1.0: fraction = 1.0
            self.gantt_canvas.xview_moveto(fraction)

    def on_process_select(self, event):
        """Highlights the corresponding image block when a process is selected in the tree."""
        self.image_canvas.delete("highlight") # Clear previous highlight
        
        selected_item = self.process_tree.focus()
        if not selected_item:
            return # User clicked off, highlight is cleared

        try:
            item_values = self.process_tree.item(selected_item, 'values')
            if not item_values:
                return
                
            pid = int(item_values[0])
            process = self.process_map[pid]
            x, y = process['coords']
            w, h = process['block_size']
            
            # Draw a bright, thick outline
            self.image_canvas.create_rectangle(
                x, y, x + w, y + h, 
                outline="#00FFFF", width=3, tags="highlight" # Bright cyan highlight
            )
        except (ValueError, KeyError, IndexError):
            print(f"Error selecting process, item: {selected_item}") # Gracefully handle errors

    def clear_highlight(self, event=None):
        """Clears the highlight box and deselects the treeview item."""
        self.image_canvas.delete("highlight")
        # De-select all items in the tree
        if self.process_tree.selection():
            self.process_tree.selection_set("") 
            
    def get_text_color(self, hex_color):
        """Determines if black or white text is more readable on a given hex color."""
        try:
            hex_color = hex_color.lstrip('#')
            if len(hex_color) != 6: return "#000000" # Default to black on error
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            # Calculate luminance (YIQ formula)
            luminance = ((r * 299) + (g * 587) + (b * 114)) / 1000
            return "#000000" if luminance > 128 else "#ffffff"
        except Exception:
            return "#000000" # Default to black on any error

    def on_random_arrival_toggle(self):
        """Disables/Enables FCFS algorithm based on random arrival selection."""
        if self.random_arrival_var.get():
            # Random arrivals: Enable FCFS
            self.algo_dropdown.config(values=self.all_algorithms)
        else:
            # All arrive at 0: Disable FCFS
            self.algo_dropdown.config(values=self.no_fcfs_algorithms)
            # If FCFS was selected, switch to a valid default
            if self.algorithm_var.get() == "FCFS":
                self.algorithm_var.set("SJF")


if __name__ == "__main__":
    root = tk.Tk()
    app = VisualSchedulingSimulator(root)
    root.mainloop()
