import tkinter as tk
from tkinter import ttk

class EnvelopeSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Envelope Segment Normalizer")
        self.root.geometry("500x500")  # Slightly larger window

        # Variables
        self.time_val = tk.DoubleVar(value=0)
        self.attack_val = tk.DoubleVar(value=20)  # Now represents %
        self.decay_val = tk.DoubleVar(value=100)   # Now represents %
        self.norm_attack = tk.StringVar(value="0.00")
        self.norm_decay = tk.StringVar(value="0.00")
        self.amplitude = tk.StringVar(value="0.00")  # Current amplitude value

        # Clock variables
        self.clock_running = False
        self.after_id = None
        self.updating_from_clock = False
        self.interval_sec = tk.DoubleVar(value=1.0)  # Default interval

        # Canvas for visualization
        self.canvas = tk.Canvas(root, width=400, height=200, bg='white',
                               relief='sunken', bd=2)
        self.canvas.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

        # Time Slider
        ttk.Label(root, text="Fake Time (0-100):").grid(row=1, column=0, padx=10, pady=5)
        self.time_slider = ttk.Scale(root, from_=0, to=100, variable=self.time_val,
                                    command=self.update_envelope)
        self.time_slider.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        ttk.Label(root, textvariable=self.time_val).grid(row=1, column=2, padx=5)

        # Attack Control (now ratio)
        ttk.Label(root, text="Attack Ratio (%):").grid(row=2, column=0, padx=10, pady=5)
        self.attack_spin = ttk.Spinbox(root, from_=0, to=100, width=8,
                                     textvariable=self.attack_val,
                                     command=self.update_envelope)
        self.attack_spin.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Decay Control (now ratio)
        ttk.Label(root, text="Decay Ratio (%):").grid(row=3, column=0, padx=10, pady=5)
        self.decay_spin = ttk.Spinbox(root, from_=0, to=100, width=8,
                                    textvariable=self.decay_val,
                                    command=self.update_envelope)
        self.decay_spin.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Normalized Values Display
        ttk.Label(root, text="Normalized Attack:").grid(row=4, column=0, padx=10, pady=5)
        ttk.Label(root, textvariable=self.norm_attack, width=8,
                 relief="solid").grid(row=4, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(root, text="Normalized Decay:").grid(row=5, column=0, padx=10, pady=5)
        ttk.Label(root, textvariable=self.norm_decay, width=8,
                 relief="solid").grid(row=5, column=1, padx=10, pady=5, sticky="w")

        # Amplitude Display
        ttk.Label(root, text="Current Amplitude:").grid(row=6, column=0, padx=10, pady=5)
        ttk.Label(root, textvariable=self.amplitude, width=8,
                 relief="solid").grid(row=6, column=1, padx=10, pady=5, sticky="w")

        # Clock Controls
        clock_frame = ttk.Frame(root)
        clock_frame.grid(row=7, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        ttk.Label(clock_frame, text="Clock Interval (sec):").pack(side=tk.LEFT, padx=(0, 5))
        self.interval_spin = ttk.Spinbox(clock_frame, from_=0.1, to=10, increment=0.1, width=8,
                                        textvariable=self.interval_sec)
        self.interval_spin.pack(side=tk.LEFT, padx=5)

        self.play_btn = ttk.Button(clock_frame, text="Play", command=self.toggle_clock)
        self.play_btn.pack(side=tk.LEFT, padx=5)

        # Time value change handler
        self.time_val.trace_add('write', self.on_time_val_changed)

        # Initialize
        self.update_envelope()

        # Bind canvas resize
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def on_canvas_resize(self, event):
        """Handle canvas resize event"""
        self.update_envelope()

    def on_time_val_changed(self, *args):
        """Stop clock if user manually changes time value"""
        if self.clock_running and not self.updating_from_clock:
            self.stop_clock()

    def toggle_clock(self):
        """Toggle play/stop state"""
        if self.clock_running:
            self.stop_clock()
        else:
            self.start_clock()

    def start_clock(self):
        """Start the clock timer"""
        if not self.clock_running:
            self.clock_running = True
            self.play_btn.config(text="Stop")
            # Reset to 0 if at end
            if self.time_val.get() >= 100:
                self.time_val.set(0)
            self.advance_clock()

    def stop_clock(self):
        """Stop the clock timer"""
        if self.clock_running:
            self.clock_running = False
            self.play_btn.config(text="Play")
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None

    def advance_clock(self):
        if not self.clock_running:
            return

        current_time = self.time_val.get()
        step = 1

        if current_time < 100:
            new_time = current_time + step
            if new_time > 100:
                new_time = 100
        else:
            new_time = 0

        self.updating_from_clock = True
        self.time_val.set(new_time)
        self.updating_from_clock = False

        # Explicitly update envelope after time change
        self.update_envelope()

        interval_ms = int(self.interval_sec.get() * 1000)
        self.after_id = self.root.after(interval_ms, self.advance_clock)

    def compute_amplitude(self, t, A, D):
        """Compute current amplitude based on time position"""
        if A > 0 and t <= A:
            return t / A
        elif D > A and t >= A and t <= D:
            return 1.0 - (t - A) / (D - A)
        else:
            return 0.0

    def draw_envelope(self, A, D, t):
        """Draw the envelope curve on canvas"""
        self.canvas.delete("all")  # Clear previous drawing

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        padding = 20

        # Calculate drawing area
        draw_width = width - 2 * padding
        draw_height = height - 2 * padding

        # Draw axes
        self.canvas.create_line(padding, height - padding, width - padding, height - padding, width=2)  # X-axis
        self.canvas.create_line(padding, padding, padding, height - padding, width=2)  # Y-axis

        # Add axis labels
        self.canvas.create_text(padding - 10, padding, text="1.0", anchor="e")
        self.canvas.create_text(padding - 10, height - padding, text="0.0", anchor="e")
        self.canvas.create_text(width - padding, height - padding + 15, text="Time", anchor="n")
        self.canvas.create_text(padding - 15, padding - 10, text="Ampl", anchor="e")

        # Draw grid
        for i in range(1, 10):
            # Vertical lines
            x = padding + i * draw_width / 10
            self.canvas.create_line(x, padding, x, height - padding, dash=(2, 2), fill="gray")
            # Horizontal lines
            y = padding + i * draw_height / 10
            self.canvas.create_line(padding, y, width - padding, y, dash=(2, 2), fill="gray")

        # Convert percentages to coordinates
        def t_to_x(t_val):
            return padding + (t_val / 100) * draw_width

        def a_to_y(amplitude):
            return padding + (1 - amplitude) * draw_height

        # Calculate points for envelope curve
        points = []

        # Start point
        points.append((padding, height - padding))

        # Attack segment
        attack_end_x = t_to_x(A)
        points.append((attack_end_x, padding))

        # Decay segment
        decay_end_x = t_to_x(D)
        points.append((decay_end_x, height - padding))

        # Draw envelope curve
        if len(points) > 1:
            self.canvas.create_line(points, fill="blue", width=2, smooth=True)

        # Draw control points
        self.canvas.create_oval(attack_end_x-5, padding-5, attack_end_x+5, padding+5, fill="red")
        self.canvas.create_oval(decay_end_x-5, height-padding-5, decay_end_x+5, height-padding+5, fill="green")

        # Draw current time marker
        if t >= 0:
            current_x = t_to_x(t)
            current_amp = self.compute_amplitude(t, A, D)
            current_y = a_to_y(current_amp)

            # Draw vertical position indicator
            self.canvas.create_line(current_x, padding, current_x, height - padding,
                                   dash=(2, 2), fill="purple")

            # Draw amplitude marker
            self.canvas.create_oval(current_x-6, current_y-6, current_x+6, current_y+6,
                                   fill="gold", outline="black")

            # Draw value labels
            self.canvas.create_text(current_x, current_y - 15,
                                  text=f"t={t:.1f}\na={current_amp:.2f}",
                                  anchor="s", fill="darkred")

    def update_envelope(self, *args):
        try:
            t = self.time_val.get()
            A = self.attack_val.get()
            D = self.decay_val.get()

            # Ensure decay doesn't start before attack finishes
            if D < A:
                D = A

            # Attack Segment (0-1 normalized)
            if A > 0 and t <= A:
                norm_a = t / A
                self.norm_attack.set(f"{norm_a:.2f}")
                self.norm_decay.set("0.00")
                current_amp = norm_a

            # Decay Segment (0-1 normalized)
            elif D > A and t >= A and t <= D:
                norm_d = (t - A) / (D - A)
                self.norm_attack.set("0.00")
                self.norm_decay.set(f"{norm_d:.2f}")
                current_amp = 1.0 - norm_d

            # Outside segments
            else:
                self.norm_attack.set("0.00")
                self.norm_decay.set("0.00")
                current_amp = 0.0

            # Update amplitude display
            self.amplitude.set(f"{current_amp:.2f}")

            # Update visualization
            self.draw_envelope(A, D, t)

        except (ValueError, ZeroDivisionError):
            pass  # Handle invalid input silently

if __name__ == "__main__":
    root = tk.Tk()
    app = EnvelopeSimulator(root)
    root.mainloop()