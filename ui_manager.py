"""
UI Manager Module
Handles all Tkinter GUI components and camera preview
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
from config import *


class UIManager:
    """Manages the game's user interface"""
    
    def __init__(self, root, use_gpu=False):
        """
        Initialize the UI Manager
        
        Args:
            root: Tkinter root window
            use_gpu: Whether GPU is available
        """
        self.root = root
        self.use_gpu = use_gpu
        self.is_fullscreen = False
        
        # Widget references
        self.canvas = None
        self.camera_preview = None
        self.start_stop_button = None
        self.pause_button = None
        self.camera_status = None
        self.camera_indicator = None
        self.left_hand_status = None
        self.right_hand_status = None
        self.fps_display = None
        self.score_display = None
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the Tkinter UI"""
        self.root.title(WINDOW_TITLE)
        self.root.configure(bg=BG_PRIMARY)
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Allow resizing and set initial size
        self.root.resizable(True, True)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # Center window
        self.root.update_idletasks()
        x = (screen_width // 2) - (WINDOW_WIDTH // 2)
        y = (screen_height // 2) - (WINDOW_HEIGHT // 2)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        
        # Create main canvas with scrollbar
        self.main_canvas = tk.Canvas(self.root, bg=BG_PRIMARY, highlightthickness=0)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.main_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create frame inside canvas
        main_container = tk.Frame(self.main_canvas, bg=BG_PRIMARY, padx=25, pady=25)
        self.canvas_window = self.main_canvas.create_window((0, 0), window=main_container, anchor='nw')
        
        # Configure scroll region
        def configure_scroll_region(event=None):
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox('all'))
        
        main_container.bind('<Configure>', configure_scroll_region)
        
        # Mousewheel scrolling
        def on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.root.bind_all("<MouseWheel>", on_mousewheel)
        
        # Adjust canvas window width
        def on_canvas_configure(event):
            self.main_canvas.itemconfig(self.canvas_window, width=event.width)
        self.main_canvas.bind('<Configure>', on_canvas_configure)
        
        # Build UI sections
        self._create_header(main_container)
        self._create_status_bar(main_container)
        self._create_game_canvas(main_container)
        self._create_instructions(main_container)
        self._create_bottom_section(main_container)
    
    def _create_header(self, parent):
        """Create header section"""
        header_frame = tk.Frame(parent, bg=BG_SECONDARY, relief=tk.FLAT, bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_container = tk.Frame(header_frame, bg=BG_SECONDARY, pady=15)
        title_container.pack()
        
        title = tk.Label(title_container, text="🎮 HAND GESTURE PONG",
                        font=FONT_TITLE, fg=TEXT_PRIMARY, bg=BG_SECONDARY)
        title.pack()
        
        subtitle = tk.Label(title_container, text="AI-Powered Hand Tracking Game",
                           font=FONT_SUBTITLE, fg=TEXT_SECONDARY, bg=BG_SECONDARY)
        subtitle.pack(pady=(5, 0))
        
        # Badges
        badges_frame = tk.Frame(header_frame, bg=BG_SECONDARY, pady=5)
        badges_frame.pack()
        
        gpu_text = "🚀 GPU ACCELERATED" if self.use_gpu else "💻 CPU MODE"
        gpu_bg = "#065f46" if self.use_gpu else BG_TERTIARY
        gpu_fg = COLOR_SUCCESS if self.use_gpu else TEXT_SECONDARY
        
        gpu_badge = tk.Label(badges_frame, text=gpu_text, font=FONT_BADGE,
                            fg=gpu_fg, bg=gpu_bg, padx=12, pady=4, relief=tk.FLAT)
        gpu_badge.pack(side=tk.LEFT, padx=5)
        
        fullscreen_hint = tk.Label(badges_frame, text="🖥️ Press F11 for Fullscreen",
                                   font=FONT_BADGE_SMALL, fg=TEXT_DARK, bg=BG_TERTIARY,
                                   padx=12, pady=4, relief=tk.FLAT)
        fullscreen_hint.pack(side=tk.LEFT, padx=5)
    
    def _create_status_bar(self, parent):
        """Create status bar"""
        status_frame = tk.Frame(parent, bg=BG_TERTIARY, relief=tk.FLAT, bd=0)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Left section
        left_status = tk.Frame(status_frame, bg=BG_TERTIARY, padx=15, pady=12)
        left_status.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        cam_frame = tk.Frame(left_status, bg=BG_TERTIARY)
        cam_frame.pack(side=tk.LEFT)
        
        self.camera_status = tk.Label(cam_frame, text="📹 Camera: OFF",
                                      font=FONT_NORMAL_BOLD, fg=COLOR_DANGER, bg=BG_TERTIARY)
        self.camera_status.pack(side=tk.LEFT)
        
        hands_frame = tk.Frame(left_status, bg=BG_TERTIARY)
        hands_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        self.left_hand_status = tk.Label(hands_frame, text="👈 Left: ✗",
                                         font=FONT_NORMAL_BOLD, fg=TEXT_DARK, bg=BG_TERTIARY)
        self.left_hand_status.pack(side=tk.LEFT, padx=5)
        
        self.right_hand_status = tk.Label(hands_frame, text="👉 Right: ✗",
                                          font=FONT_NORMAL_BOLD, fg=TEXT_DARK, bg=BG_TERTIARY)
        self.right_hand_status.pack(side=tk.LEFT, padx=5)
        
        # Right section
        right_status = tk.Frame(status_frame, bg=BG_TERTIARY, padx=15, pady=12)
        right_status.pack(side=tk.RIGHT)
        
        self.fps_display = tk.Label(right_status, text="⚡ 0 FPS",
                                    font=FONT_NORMAL_BOLD, fg=COLOR_WARNING, bg=BG_TERTIARY)
        self.fps_display.pack(side=tk.LEFT, padx=(0, 15))
        
        self.score_display = tk.Label(right_status, text="🏆 0 - 0",
                                      font=FONT_SCORE, fg=COLOR_SUCCESS, bg=BG_TERTIARY)
        self.score_display.pack(side=tk.LEFT)
    
    def _create_game_canvas(self, parent):
        """Create game canvas"""
        canvas_container = tk.Frame(parent, bg=BG_SECONDARY, relief=tk.FLAT, bd=0)
        canvas_container.pack(pady=(0, 20))
        
        canvas_frame = tk.Frame(canvas_container, bg=BG_DARK, padx=8, pady=8)
        canvas_frame.pack()
        
        self.canvas = tk.Canvas(canvas_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                               bg=BG_CANVAS, highlightthickness=3,
                               highlightbackground=COLOR_INFO_DARK,
                               highlightcolor=COLOR_INFO)
        self.canvas.pack()
    
    def _create_instructions(self, parent):
        """Create instructions panel"""
        instructions_frame = tk.Frame(parent, bg=BG_TERTIARY, relief=tk.FLAT, bd=0)
        instructions_frame.pack(fill=tk.X, pady=(0, 20))
        
        instructions_inner = tk.Frame(instructions_frame, bg=BG_SECONDARY, padx=20, pady=12)
        instructions_inner.pack(fill=tk.X)
        
        instructions = tk.Label(instructions_inner,
                               text="🎯 CONTROLS: Move your hands UP/DOWN to control paddles  |  📍 Left hand → Left paddle  |  Right hand → Right paddle",
                               font=FONT_NORMAL, fg=TEXT_LIGHT, bg=BG_SECONDARY,
                               wraplength=800, justify=tk.CENTER)
        instructions.pack()
    
    def _create_bottom_section(self, parent):
        """Create bottom section with camera and controls"""
        bottom_frame = tk.Frame(parent, bg=BG_PRIMARY)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # Camera section
        camera_section = tk.Frame(bottom_frame, bg=BG_SECONDARY, relief=tk.FLAT, bd=0)
        camera_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        camera_header = tk.Frame(camera_section, bg=BG_SECONDARY, padx=20, pady=12)
        camera_header.pack(fill=tk.X)
        
        camera_title = tk.Label(camera_header, text="📹 LIVE CAMERA FEED",
                               font=FONT_HEADER, fg=TEXT_PRIMARY, bg=BG_SECONDARY)
        camera_title.pack(side=tk.LEFT)
        
        self.camera_indicator = tk.Label(camera_header, text="● OFF",
                                         font=FONT_NORMAL_BOLD, fg=COLOR_DANGER, bg=BG_SECONDARY)
        self.camera_indicator.pack(side=tk.RIGHT)
        
        camera_preview_frame = tk.Frame(camera_section, bg=BG_DARK, padx=15, pady=15)
        camera_preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.camera_preview = tk.Label(camera_preview_frame,
                                       text="📷 Camera Offline\n\n🎮 Click START GAME to activate\n\n✋ Position both hands in view\n👀 Hands will be detected automatically\n🟢 Green paddles = Hand control active",
                                       width=45, height=16, bg=BG_CANVAS, fg=TEXT_DARK,
                                       font=FONT_NORMAL, justify=tk.CENTER, relief=tk.FLAT,
                                       borderwidth=2, highlightthickness=2,
                                       highlightbackground=BG_TERTIARY,
                                       highlightcolor=COLOR_INFO_DARK)
        self.camera_preview.pack(fill=tk.BOTH, expand=True)
        
        tips_frame = tk.Frame(camera_section, bg=BG_SECONDARY, padx=15, pady=10)
        tips_frame.pack(fill=tk.X)
        
        tips_label = tk.Label(tips_frame,
                             text="💡 TIP: Good lighting improves hand detection accuracy",
                             font=FONT_BADGE_SMALL, fg=TEXT_SECONDARY, bg=BG_SECONDARY,
                             justify=tk.LEFT)
        tips_label.pack(anchor=tk.W)
        
        # Controls section
        self._create_controls_section(bottom_frame)
    
    def _create_controls_section(self, parent):
        """Create controls section"""
        controls_section = tk.Frame(parent, bg=BG_SECONDARY, relief=tk.FLAT, bd=0)
        controls_section.pack(side=tk.RIGHT, fill=tk.Y)
        
        controls_inner = tk.Frame(controls_section, bg=BG_SECONDARY, padx=20, pady=15)
        controls_inner.pack(fill=tk.BOTH, expand=True)
        
        # START/STOP button
        self.start_stop_button = tk.Button(controls_inner, text="▶️ START GAME",
                                          font=FONT_BUTTON_LARGE, bg=COLOR_SUCCESS,
                                          fg='white', padx=30, pady=20, relief=tk.FLAT, bd=0,
                                          cursor='hand2', activebackground=COLOR_SUCCESS_DARK,
                                          activeforeground='white')
        self.start_stop_button.pack(fill=tk.X, pady=(0, 10))
        
        # PAUSE button
        self.pause_button = tk.Button(controls_inner, text="⏸️ PAUSE",
                                     font=FONT_BUTTON_MEDIUM, bg=COLOR_WARNING,
                                     fg='white', padx=20, pady=10, relief=tk.FLAT, bd=0,
                                     cursor='hand2', state=tk.DISABLED,
                                     activebackground=COLOR_WARNING_DARK,
                                     activeforeground='white')
        self.pause_button.pack(fill=tk.X, pady=(0, 15))
        
        # Game modes card
        modes_card = tk.Frame(controls_inner, bg=BG_DARK, relief=tk.FLAT, bd=0)
        modes_card.pack(fill=tk.X, pady=(0, 10))
        
        modes_inner = tk.Frame(modes_card, bg=BG_DARK, padx=15, pady=12)
        modes_inner.pack(fill=tk.X)
        
        mode_title = tk.Label(modes_inner, text="🎮 GAME MODES", font=FONT_NORMAL_BOLD,
                             fg=TEXT_PRIMARY, bg=BG_DARK)
        mode_title.pack(anchor=tk.W, pady=(0, 8))
        
        mode_info = tk.Label(modes_inner,
                            text="👤 1 Hand: You vs AI\n👥 2 Hands: Full Manual Control\n🤖 0 Hands: AI Demo Mode",
                            font=FONT_BADGE_SMALL, fg=TEXT_SECONDARY, bg=BG_DARK,
                            justify=tk.LEFT)
        mode_info.pack(anchor=tk.W)
        
        # QUIT button
        self.quit_button = tk.Button(controls_inner, text="✖️ QUIT",
                                     font=FONT_BUTTON_SMALL, bg=COLOR_DANGER_DARK,
                                     fg='white', padx=20, pady=10, relief=tk.FLAT, bd=0,
                                     cursor='hand2', activebackground=COLOR_DANGER_DARKER,
                                     activeforeground='white')
        self.quit_button.pack(fill=tk.X, pady=(5, 0))
    
    def update_camera_status(self, is_active):
        """Update camera status indicators"""
        if is_active:
            self.camera_status.config(text="📹 Camera: ACTIVE", fg=COLOR_SUCCESS)
            self.camera_indicator.config(text="● LIVE", fg=COLOR_SUCCESS)
        else:
            self.camera_status.config(text="📹 Camera: OFF", fg=COLOR_DANGER)
            self.camera_indicator.config(text="● OFF", fg=COLOR_DANGER)
    
    def update_hand_status(self, left_detected, right_detected):
        """Update hand detection status"""
        if left_detected:
            self.left_hand_status.config(text="👈 Left: ✓", fg=COLOR_SUCCESS)
        else:
            self.left_hand_status.config(text="👈 Left: ✗", fg=TEXT_DARK)
        
        if right_detected:
            self.right_hand_status.config(text="👉 Right: ✓", fg=COLOR_SUCCESS)
        else:
            self.right_hand_status.config(text="👉 Right: ✗", fg=TEXT_DARK)
    
    def update_score(self, score):
        """Update score display"""
        self.score_display.config(text=f"🏆 {score['player1']} - {score['player2']}")
    
    def update_fps(self, fps):
        """Update FPS display with color coding"""
        fps_int = int(fps)
        fps_color = COLOR_SUCCESS if fps_int >= 50 else COLOR_WARNING if fps_int >= 30 else COLOR_DANGER
        self.fps_display.config(text=f"⚡ {fps_int} FPS", fg=fps_color)
    
    def update_start_stop_button(self, is_running):
        """Update start/stop button state"""
        if is_running:
            self.start_stop_button.config(text="⏹️ STOP GAME", bg=COLOR_DANGER_DARK,
                                         activebackground=COLOR_DANGER_DARKER)
            self.pause_button.config(state=tk.NORMAL)
        else:
            self.start_stop_button.config(text="▶️ START GAME", bg=COLOR_SUCCESS,
                                         activebackground=COLOR_SUCCESS_DARK)
            self.pause_button.config(state=tk.DISABLED)
    
    def update_pause_button(self, is_paused):
        """Update pause button state"""
        if is_paused:
            self.pause_button.config(text="▶️ RESUME", bg=COLOR_SUCCESS)
        else:
            self.pause_button.config(text="⏸️ PAUSE", bg=COLOR_WARNING)
    
    def update_camera_preview(self, frame, use_gpu=False, paused_overlay=False):
        """Update camera preview with frame"""
        try:
            # Resize frame for preview
            if use_gpu:
                try:
                    gpu_frame = cv2.cuda_GpuMat()
                    gpu_frame.upload(frame)
                    gpu_resized = cv2.cuda.resize(gpu_frame, (CAMERA_PREVIEW_WIDTH, CAMERA_PREVIEW_HEIGHT))
                    preview_frame = gpu_resized.download()
                except:
                    preview_frame = cv2.resize(frame, (CAMERA_PREVIEW_WIDTH, CAMERA_PREVIEW_HEIGHT),
                                             interpolation=cv2.INTER_LINEAR)
            else:
                preview_frame = cv2.resize(frame, (CAMERA_PREVIEW_WIDTH, CAMERA_PREVIEW_HEIGHT),
                                         interpolation=cv2.INTER_LINEAR)
            
            # Add paused overlay if needed
            if paused_overlay:
                h, w, _ = preview_frame.shape
                text = "GAME PAUSED"
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 3)[0]
                text_x = (w - text_size[0]) // 2
                text_y = h - 40
                
                cv2.rectangle(preview_frame, 
                            (text_x - 15, text_y - text_size[1] - 10),
                            (text_x + text_size[0] + 15, text_y + 10),
                            (10, 14, 39), -1)
                cv2.putText(preview_frame, text, (text_x, text_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (96, 165, 250), 3)
            
            preview_frame = cv2.cvtColor(preview_frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PhotoImage
            img = Image.fromarray(preview_frame)
            photo = ImageTk.PhotoImage(img)
            
            self.camera_preview.config(image=photo, text='')
            self.camera_preview.image = photo  # Keep reference
            
        except Exception as e:
            print(f"📹 Camera preview error: {e}")
    
    def clear_camera_preview(self):
        """Clear camera preview and show offline message"""
        self.camera_preview.config(
            text="📷 Camera Offline\n\n🎮 Click START GAME to activate\n\n✋ Position both hands in view\n👀 Hands will be detected automatically\n🟢 Green paddles = Hand control active",
            image='', fg=TEXT_DARK)
    
    def draw_game(self, game_state):
        """Draw game state on canvas"""
        self.canvas.delete("all")
        
        # Draw pause overlay if paused
        if game_state['paused']:
            self.canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT,
                                        fill=BG_CANVAS, stipple='gray50', outline='')
            self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2,
                                   text="⏸️ PAUSED", font=FONT_PAUSE_LARGE, fill=TEXT_PRIMARY)
            self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 + 60,
                                   text="Press RESUME to continue", font=FONT_PAUSE_SMALL,
                                   fill=TEXT_SECONDARY)
            return
        
        # Center line
        for i in range(0, CANVAS_HEIGHT, 20):
            self.canvas.create_rectangle(CANVAS_WIDTH//2 - 2, i, CANVAS_WIDTH//2 + 2, i + 10,
                                        fill=COLOR_CENTER_LINE, outline='')
        
        # Left paddle
        paddle1 = game_state['paddle1']
        left_color = COLOR_PADDLE_ACTIVE if paddle1['hand_controlled'] else COLOR_PADDLE_INACTIVE
        left_outline = COLOR_PADDLE_OUTLINE_ACTIVE if paddle1['hand_controlled'] else COLOR_PADDLE_OUTLINE_INACTIVE
        self.canvas.create_rectangle(paddle1['x'], paddle1['y'],
                                     paddle1['x'] + paddle1['width'],
                                     paddle1['y'] + paddle1['height'],
                                     fill=left_color, outline=left_outline, width=2)
        
        # Right paddle
        paddle2 = game_state['paddle2']
        right_color = COLOR_PADDLE_ACTIVE if paddle2['hand_controlled'] else COLOR_PADDLE_INACTIVE
        right_outline = COLOR_PADDLE_OUTLINE_ACTIVE if paddle2['hand_controlled'] else COLOR_PADDLE_OUTLINE_INACTIVE
        self.canvas.create_rectangle(paddle2['x'], paddle2['y'],
                                     paddle2['x'] + paddle2['width'],
                                     paddle2['y'] + paddle2['height'],
                                     fill=right_color, outline=right_outline, width=2)
        
        # Ball
        ball = game_state['ball']
        ball_active = paddle1['hand_controlled'] or paddle2['hand_controlled']
        ball_color = COLOR_BALL_ACTIVE if ball_active else COLOR_BALL_INACTIVE
        ball_outline = COLOR_BALL_OUTLINE_ACTIVE if ball_active else COLOR_BALL_OUTLINE_INACTIVE
        
        self.canvas.create_oval(ball['x'] - ball['radius'], ball['y'] - ball['radius'],
                               ball['x'] + ball['radius'], ball['y'] + ball['radius'],
                               fill=ball_color, outline=ball_outline, width=2)
    
    def show_welcome_message(self):
        """Show welcome message dialog"""
        messagebox.showinfo("🎮 Welcome to Hand Pong!", WELCOME_MESSAGE)
    
    def show_error(self, title, message):
        """Show error dialog"""
        messagebox.showerror(title, message)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        
        if self.is_fullscreen:
            print("🖥️ Fullscreen mode activated (Press ESC or F11 to exit)")
        else:
            print("🪟 Windowed mode activated")
    
    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes('-fullscreen', False)
            print("🪟 Exited fullscreen mode")
