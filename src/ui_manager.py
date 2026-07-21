"""
UI Manager Module
Handles all CustomTkinter GUI components and camera preview
OPTIMIZED: Side-by-Side Dashboard Layout
"""

import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
from config import *
import tkinter.messagebox as messagebox

class UIManager:
    """Manages the game's user interface using CustomTkinter"""
    
    def __init__(self, root):
        self.root = root
        self.is_fullscreen = False
        
        # Icon references
        self.load_icons()
        
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
        
        self.setup_ui()

    def load_icons(self):
        """Load premium PNG icons from assets/icons"""
        try:
            icon_dir = os.path.join("assets", "icons")
            get_icon = lambda name, size=(20, 20): ctk.CTkImage(
                light_image=Image.open(os.path.join(icon_dir, f"{name}.png")),
                dark_image=Image.open(os.path.join(icon_dir, f"{name}.png")),
                size=size
            )
            self.icon_play = get_icon("play", (20, 20))
            self.icon_stop = get_icon("stop", (20, 20))
            self.icon_pause = get_icon("pause", (18, 18))
            self.icon_quit = get_icon("quit", (18, 18))
            self.icon_camera = get_icon("camera", (16, 16))
            self.icon_lightning = get_icon("lightning", (16, 16))
        except Exception as e:
            print(f"⚠️ Icon loading notice: {e}")
            self.icon_play = None
            self.icon_stop = None
            self.icon_pause = None
            self.icon_quit = None
            self.icon_camera = None
            self.icon_lightning = None
    
    def setup_ui(self):
        self.root.title(WINDOW_TITLE)
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.root.resizable(True, True)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        self.root.update_idletasks()
        x = (screen_width // 2) - (WINDOW_WIDTH // 2)
        y = (screen_height // 2) - (WINDOW_HEIGHT // 2)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        
        # Main layout container
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ---------------------------------------------------------
        # LEFT COLUMN (Game Area)
        # ---------------------------------------------------------
        self.game_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.game_area.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self._create_header(self.game_area)
        self._create_game_canvas(self.game_area)
        self._create_instructions(self.game_area)
        
        # ---------------------------------------------------------
        # RIGHT COLUMN (Sidebar Dashboard)
        # ---------------------------------------------------------
        self.sidebar = ctk.CTkFrame(self.main_container, width=380)
        self.sidebar.pack(side="right", fill="y", padx=(10, 0))
        self.sidebar.pack_propagate(False)  # Fix width
        
        self._create_sidebar_content(self.sidebar)
    
    def _create_header(self, parent):
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(header_frame, text="🎮 HAND GESTURE PONG", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(header_frame, text="AI-Powered Hand Tracking Game", font=ctk.CTkFont(size=14), text_color="gray")
        subtitle.pack(anchor="w", pady=(2, 10))
        
        badges_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        badges_frame.pack(anchor="w")
        
        cpu_badge = ctk.CTkLabel(badges_frame, text="💻 OPTIMIZED CPU MODE", font=ctk.CTkFont(size=12, weight="bold"),
                                 fg_color="#2b2b2b", corner_radius=6, padx=10, pady=4)
        cpu_badge.pack(side="left", padx=(0, 10))
        
        fullscreen_hint = ctk.CTkLabel(badges_frame, text="🖥️ Press F11 for Fullscreen", font=ctk.CTkFont(size=12),
                                       fg_color="#2b2b2b", corner_radius=6, padx=10, pady=4)
        fullscreen_hint.pack(side="left")
    
    def _create_game_canvas(self, parent):
        canvas_container = ctk.CTkFrame(parent, corner_radius=10, fg_color="transparent")
        canvas_container.pack(fill="both", expand=True, pady=(0, 20))
        
        # We must use standard tk.Canvas for fast shape drawing inside the CTkFrame
        self.canvas = tk.Canvas(canvas_container, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                               bg=BG_CANVAS, highlightthickness=0)
        self.canvas.pack(padx=20, pady=20, expand=True)
    
    def _create_instructions(self, parent):
        instructions_frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        instructions_frame.pack(fill="x")
        
        instructions = ctk.CTkLabel(instructions_frame,
                               text="🎯 Move your hands UP/DOWN to control paddles.   👈 Left hand → Left paddle   👉 Right hand → Right paddle",
                               font=ctk.CTkFont(size=13))
        instructions.pack(pady=12)
        
    def _create_sidebar_content(self, parent):
        # Add a scrollable frame inside the sidebar in case the window is too short
        scrollable_sidebar = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scrollable_sidebar.pack(fill="both", expand=True, padx=10, pady=10)
        
        # SCORE & FPS STATUS
        status_frame = ctk.CTkFrame(scrollable_sidebar, fg_color="#1a1a1a")
        status_frame.pack(fill="x", pady=(0, 15))
        
        score_label = ctk.CTkLabel(status_frame, text="SCORE", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
        score_label.pack(pady=(10, 0))
        self.score_display = ctk.CTkLabel(status_frame, text="0 - 0", text_color="#10b981", font=ctk.CTkFont(size=36, weight="bold"))
        self.score_display.pack(pady=(0, 10))
        
        metrics_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.fps_display = ctk.CTkLabel(metrics_frame, text="⚡ 0 FPS", text_color="#f59e0b", font=ctk.CTkFont(weight="bold"))
        self.fps_display.pack(side="left")
        
        self.camera_status = ctk.CTkLabel(metrics_frame, text="📹 OFF", text_color="#ef4444", font=ctk.CTkFont(weight="bold"))
        self.camera_status.pack(side="right")
        
        # CAMERA PREVIEW
        camera_section = ctk.CTkFrame(scrollable_sidebar, fg_color="#1a1a1a")
        camera_section.pack(fill="x", pady=(0, 15))
        
        cam_header = ctk.CTkFrame(camera_section, fg_color="transparent")
        cam_header.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(cam_header, text="LIVE CAMERA", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.camera_indicator = ctk.CTkLabel(cam_header, text="● OFF", text_color="#ef4444", font=ctk.CTkFont(weight="bold"))
        self.camera_indicator.pack(side="right")
        
        self.camera_preview = ctk.CTkLabel(camera_section, text="📷 Offline\nClick START GAME",
                                           width=CAMERA_PREVIEW_WIDTH, height=CAMERA_PREVIEW_HEIGHT,
                                           fg_color="#0f0f0f", corner_radius=6)
        self.camera_preview.pack(padx=10, pady=(0, 10))
        
        hand_status_frame = ctk.CTkFrame(camera_section, fg_color="transparent")
        hand_status_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.left_hand_status = ctk.CTkLabel(hand_status_frame, text="👈 Left: ✗", text_color="gray")
        self.left_hand_status.pack(side="left")
        self.right_hand_status = ctk.CTkLabel(hand_status_frame, text="👉 Right: ✗", text_color="gray")
        self.right_hand_status.pack(side="right")
        
        # MODE SELECTOR CARD
        mode_card = ctk.CTkFrame(scrollable_sidebar, fg_color="#1a1a1a")
        mode_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(mode_card, text="🎯 GAME MODE", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.mode_selector = ctk.CTkSegmentedButton(mode_card, values=["🤖 1-Player", "👥 2-Player"],
                                                    font=ctk.CTkFont(size=12, weight="bold"),
                                                    selected_color="#10b981", selected_hover_color="#059669")
        self.mode_selector.set("🤖 1-Player")
        self.mode_selector.pack(fill="x", padx=10, pady=(0, 10))

        # GESTURES CARD
        modes_card = ctk.CTkFrame(scrollable_sidebar, fg_color="#1a1a1a")
        modes_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(modes_card, text="🎮 GESTURES", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        gestures_text = "✊ Closed Fist: Pause\n👐 Open Palm: Resume\n👍 Thumbs Up: Speed Up\n👎 Thumbs Down: Slow Down"
        ctk.CTkLabel(modes_card, text=gestures_text, font=ctk.CTkFont(size=13), text_color="#cbd5e1", justify="left").pack(anchor="w", padx=10, pady=(0, 10))
        
        # CONTROLS
        self.start_stop_button = ctk.CTkButton(scrollable_sidebar, text=" START MATCH",
                                               image=self.icon_play, compound="left",
                                               font=ctk.CTkFont(size=16, weight="bold"),
                                               fg_color="#10b981", hover_color="#059669", height=50)
        self.start_stop_button.pack(fill="x", pady=(0, 10))
        
        self.pause_button = ctk.CTkButton(scrollable_sidebar, text=" PAUSE",
                                          image=self.icon_pause, compound="left",
                                          font=ctk.CTkFont(size=14, weight="bold"),
                                          fg_color="#f59e0b", hover_color="#d97706",
                                          state="disabled", height=40)
        self.pause_button.pack(fill="x", pady=(0, 10))
        
        self.quit_button = ctk.CTkButton(scrollable_sidebar, text=" QUIT",
                                         image=self.icon_quit, compound="left",
                                         fg_color="#ef4444", hover_color="#dc2626", height=40)
        self.quit_button.pack(fill="x", pady=(10, 0))
    
    def update_camera_status(self, is_active):
        if is_active:
            self.camera_status.configure(text="ACTIVE", text_color="#10b981")
            self.camera_indicator.configure(text="● LIVE", text_color="#10b981")
        else:
            self.camera_status.configure(text="OFF", text_color="#ef4444")
            self.camera_indicator.configure(text="● OFF", text_color="#ef4444")
    
    def update_hand_status(self, left_detected, right_detected):
        if left_detected:
            self.left_hand_status.configure(text="Left: ✓", text_color="#10b981")
        else:
            self.left_hand_status.configure(text="Left: ✗", text_color="gray")
        
        if right_detected:
            self.right_hand_status.configure(text="Right: ✓", text_color="#10b981")
        else:
            self.right_hand_status.configure(text="Right: ✗", text_color="gray")
    
    def update_score(self, score):
        self.score_display.configure(text=f"{score['player1']} - {score['player2']}")
    
    def update_fps(self, fps):
        fps_int = int(fps)
        fps_color = "#10b981" if fps_int >= 50 else "#f59e0b" if fps_int >= 30 else "#ef4444"
        self.fps_display.configure(text=f"{fps_int} FPS", text_color=fps_color)
    
    def update_start_stop_button(self, is_running):
        if is_running:
            self.start_stop_button.configure(text=" STOP MATCH", image=self.icon_stop, fg_color="#ef4444", hover_color="#dc2626")
            self.pause_button.configure(state="normal")
        else:
            self.start_stop_button.configure(text=" START MATCH", image=self.icon_play, fg_color="#10b981", hover_color="#059669")
            self.pause_button.configure(state="disabled")
    
    def update_pause_button(self, is_paused):
        if is_paused:
            self.pause_button.configure(text=" RESUME", image=self.icon_play, fg_color="#10b981", hover_color="#059669")
        else:
            self.pause_button.configure(text=" PAUSE", image=self.icon_pause, fg_color="#f59e0b", hover_color="#d97706")
    
    def update_camera_preview(self, frame, paused_overlay=False):
        try:
            preview_frame = cv2.resize(frame, (CAMERA_PREVIEW_WIDTH, CAMERA_PREVIEW_HEIGHT), interpolation=cv2.INTER_LINEAR)
            if paused_overlay:
                h, w, _ = preview_frame.shape
                text = "GAME PAUSED"
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                text_x = (w - text_size[0]) // 2
                text_y = h - 30
                cv2.rectangle(preview_frame, (text_x - 10, text_y - text_size[1] - 8), (text_x + text_size[0] + 10, text_y + 8), (10, 14, 39), -1)
                cv2.putText(preview_frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (250, 165, 96), 2)
            
            preview_frame = cv2.cvtColor(preview_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(preview_frame)
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(CAMERA_PREVIEW_WIDTH, CAMERA_PREVIEW_HEIGHT))
            self.camera_preview.configure(image=photo, text="")
        except Exception as e:
            print(f"📹 Camera preview error: {e}")
    
    def clear_camera_preview(self):
        self.camera_preview.configure(image="", text="📷 Offline\nClick START GAME")
    
    def draw_game(self, game_state):
        self.canvas.delete("all")
        if game_state['paused']:
            self.canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill=BG_CANVAS, stipple='gray50', outline='')
            self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2, text="⏸️ PAUSED", font=FONT_PAUSE_LARGE, fill=TEXT_PRIMARY)
            self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 + 60, text="Press RESUME to continue", font=FONT_PAUSE_SMALL, fill=TEXT_SECONDARY)
            return
        
        # Draw pitch boundary
        self.canvas.create_rectangle(2, 2, CANVAS_WIDTH-2, CANVAS_HEIGHT-2, outline=COLOR_CENTER_LINE, width=4)
        
        for i in range(0, CANVAS_HEIGHT, 20):
            self.canvas.create_rectangle(CANVAS_WIDTH//2 - 2, i, CANVAS_WIDTH//2 + 2, i + 10, fill=COLOR_CENTER_LINE, outline='')
        
        paddle1 = game_state['paddle1']
        left_color = COLOR_PADDLE_ACTIVE if paddle1['hand_controlled'] else COLOR_PADDLE_INACTIVE
        left_outline = COLOR_PADDLE_OUTLINE_ACTIVE if paddle1['hand_controlled'] else COLOR_PADDLE_OUTLINE_INACTIVE
        self.canvas.create_rectangle(paddle1['x'], paddle1['y'], paddle1['x'] + paddle1['width'], paddle1['y'] + paddle1['height'], fill=left_color, outline=left_outline, width=2)
        
        paddle2 = game_state['paddle2']
        right_color = COLOR_PADDLE_ACTIVE if paddle2['hand_controlled'] else COLOR_PADDLE_INACTIVE
        right_outline = COLOR_PADDLE_OUTLINE_ACTIVE if paddle2['hand_controlled'] else COLOR_PADDLE_OUTLINE_INACTIVE
        self.canvas.create_rectangle(paddle2['x'], paddle2['y'], paddle2['x'] + paddle2['width'], paddle2['y'] + paddle2['height'], fill=right_color, outline=right_outline, width=2)
        
        ball = game_state['ball']
        ball_active = paddle1['hand_controlled'] or paddle2['hand_controlled']
        ball_color = COLOR_BALL_ACTIVE if ball_active else COLOR_BALL_INACTIVE
        ball_outline = COLOR_BALL_OUTLINE_ACTIVE if ball_active else COLOR_BALL_OUTLINE_INACTIVE
        self.canvas.create_oval(ball['x'] - ball['radius'], ball['y'] - ball['radius'], ball['x'] + ball['radius'], ball['y'] + ball['radius'], fill=ball_color, outline=ball_outline, width=2)
    
    def draw_main_menu(self, selected_mode=MODE_1PLAYER):
        """Draw sleek Main Menu view on the game canvas"""
        self.canvas.delete("all")
        
        # Draw background and pitch outlines
        self.canvas.create_rectangle(2, 2, CANVAS_WIDTH-2, CANVAS_HEIGHT-2, outline=COLOR_CENTER_LINE, width=4)
        for i in range(0, CANVAS_HEIGHT, 20):
            self.canvas.create_rectangle(CANVAS_WIDTH//2 - 2, i, CANVAS_WIDTH//2 + 2, i + 10, fill=COLOR_CENTER_LINE, outline='')
            
        # Title
        self.canvas.create_text(CANVAS_WIDTH // 2, 80, text="🏓 HAND GESTURE PONG", font=(FONT_FAMILY, 32, "bold"), fill=COLOR_INFO)
        self.canvas.create_text(CANVAS_WIDTH // 2, 120, text="Select Game Mode & Click START MATCH to Play", font=(FONT_FAMILY, 14), fill=TEXT_SECONDARY)
        
        # 1-Player Card Box
        is_1p = (selected_mode == MODE_1PLAYER)
        box1_bg = "#1e293b" if is_1p else "#0f172a"
        box1_outline = "#10b981" if is_1p else "#334155"
        self.canvas.create_rectangle(80, 160, 330, 360, fill=box1_bg, outline=box1_outline, width=3 if is_1p else 1)
        self.canvas.create_text(205, 195, text="🤖 1-PLAYER MODE", font=(FONT_FAMILY, 16, "bold"), fill="#10b981" if is_1p else TEXT_LIGHT)
        self.canvas.create_text(205, 230, text="• You vs Smart AI", font=(FONT_FAMILY, 12), fill=TEXT_SECONDARY)
        self.canvas.create_text(205, 255, text="• Left Hand: Controls Paddle", font=(FONT_FAMILY, 12), fill=TEXT_SECONDARY)
        self.canvas.create_text(205, 280, text="• Right Paddle: Auto AI", font=(FONT_FAMILY, 12), fill=TEXT_SECONDARY)
        if is_1p:
            self.canvas.create_text(205, 325, text="✓ SELECTED", font=(FONT_FAMILY, 12, "bold"), fill="#10b981")
            
        # 2-Player Card Box
        is_2p = (selected_mode == MODE_2PLAYER)
        box2_bg = "#1e293b" if is_2p else "#0f172a"
        box2_outline = "#10b981" if is_2p else "#334155"
        self.canvas.create_rectangle(390, 160, 640, 360, fill=box2_bg, outline=box2_outline, width=3 if is_2p else 1)
        self.canvas.create_text(515, 195, text="👥 2-PLAYER MODE", font=(FONT_FAMILY, 16, "bold"), fill="#10b981" if is_2p else TEXT_LIGHT)
        self.canvas.create_text(515, 230, text="• Local Multiplayer", font=(FONT_FAMILY, 12), fill=TEXT_SECONDARY)
        self.canvas.create_text(515, 255, text="• Left Hand: Left Paddle", font=(FONT_FAMILY, 12), fill=TEXT_SECONDARY)
        self.canvas.create_text(515, 280, text="• Right Hand: Right Paddle", font=(FONT_FAMILY, 12), fill=TEXT_SECONDARY)
        if is_2p:
            self.canvas.create_text(515, 325, text="✓ SELECTED", font=(FONT_FAMILY, 12, "bold"), fill="#10b981")

        # Bottom Hint
        self.canvas.create_text(CANVAS_WIDTH // 2, 420, text="💡 Tip: Toggle mode on sidebar panel anytime!", font=(FONT_FAMILY, 12, "italic"), fill=TEXT_DARK)

    def draw_calibration_overlay(self, countdown_seconds, left_detected=False, right_detected=False, mode=MODE_1PLAYER):
        """Draw 3-second camera calibration and countdown phase on canvas"""
        self.canvas.delete("all")
        
        # Draw background pitch
        self.canvas.create_rectangle(2, 2, CANVAS_WIDTH-2, CANVAS_HEIGHT-2, outline=COLOR_CENTER_LINE, width=4)
        for i in range(0, CANVAS_HEIGHT, 20):
            self.canvas.create_rectangle(CANVAS_WIDTH//2 - 2, i, CANVAS_WIDTH//2 + 2, i + 10, fill=COLOR_CENTER_LINE, outline='')

        # Card Overlay
        self.canvas.create_rectangle(110, 80, CANVAS_WIDTH - 110, CANVAS_HEIGHT - 80, fill="#0f172a", outline="#3b82f6", width=2)
        
        # Heading
        self.canvas.create_text(CANVAS_WIDTH // 2, 120, text="📹 CAMERA CALIBRATION & COUNTDOWN", font=(FONT_FAMILY, 18, "bold"), fill=COLOR_INFO)
        
        # Hand Tracking Feedback Status
        if mode == MODE_1PLAYER:
            status_text = "👈 Left Hand: TRACKED ✓" if left_detected else "👈 Left Hand: Show hand to camera..."
            status_color = "#10b981" if left_detected else "#f59e0b"
            self.canvas.create_text(CANVAS_WIDTH // 2, 165, text=status_text, font=(FONT_FAMILY, 14, "bold"), fill=status_color)
        else:
            left_str = "Left: ✓" if left_detected else "Left: ✗"
            right_str = "Right: ✓" if right_detected else "Right: ✗"
            self.canvas.create_text(CANVAS_WIDTH // 2, 165, text=f"👈 {left_str}  |  👉 {right_str}", font=(FONT_FAMILY, 14, "bold"), fill="#10b981" if (left_detected or right_detected) else "#f59e0b")

        # Countdown Display
        if countdown_seconds > 0:
            count_str = str(countdown_seconds)
            self.canvas.create_text(CANVAS_WIDTH // 2, 250, text=count_str, font=(FONT_FAMILY, 64, "bold"), fill="#10b981")
            self.canvas.create_text(CANVAS_WIDTH // 2, 320, text="Get Ready! Match starts in...", font=(FONT_FAMILY, 13), fill=TEXT_SECONDARY)
        else:
            self.canvas.create_text(CANVAS_WIDTH // 2, 250, text="🚀 GO!", font=(FONT_FAMILY, 64, "bold"), fill="#3b82f6")
            self.canvas.create_text(CANVAS_WIDTH // 2, 320, text="Game On!", font=(FONT_FAMILY, 14, "bold"), fill="#10b981")
    
    def show_welcome_message(self):
        # Create a modern CustomTkinter Toplevel window instead of standard messagebox
        welcome_window = ctk.CTkToplevel(self.root)
        welcome_window.title("Welcome to Hand Pong")
        welcome_window.geometry("450x550")
        welcome_window.resizable(False, False)
        welcome_window.attributes('-topmost', True)
        
        # Center it on the screen
        welcome_window.update_idletasks()
        screen_width = welcome_window.winfo_screenwidth()
        screen_height = welcome_window.winfo_screenheight()
        x = (screen_width // 2) - (450 // 2)
        y = (screen_height // 2) - (550 // 2)
        welcome_window.geometry(f"450x550+{x}+{y}")
        
        # Title
        title = ctk.CTkLabel(welcome_window, text="🎮 WELCOME TO HAND PONG", font=ctk.CTkFont(size=22, weight="bold"), text_color="#10b981")
        title.pack(pady=(30, 10))
        
        # Message (Scrollable in case it's long)
        msg_frame = ctk.CTkScrollableFrame(welcome_window, fg_color="transparent")
        msg_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Content from config.py but skipping the first title line since we have a nice header
        lines = WELCOME_MESSAGE.split('\n')
        cleaned_msg = '\n'.join(lines[2:]) if len(lines) > 2 else WELCOME_MESSAGE
        
        content = ctk.CTkLabel(msg_frame, text=cleaned_msg, font=ctk.CTkFont(size=14), justify="left", text_color="#cbd5e1")
        content.pack(anchor="w", padx=10, pady=10)
        
        # Button
        btn = ctk.CTkButton(welcome_window, text="LET'S PLAY! 🚀", font=ctk.CTkFont(size=16, weight="bold"), 
                            fg_color="#10b981", hover_color="#059669", height=50,
                            command=welcome_window.destroy)
        btn.pack(pady=(10, 30), padx=30, fill="x")
        
        # Make the window modal and wait for it to close
        welcome_window.grab_set()
        self.root.wait_window(welcome_window)
    
    def show_error(self, title, message):
        messagebox.showerror(title, message)
    
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
    
    def exit_fullscreen(self):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes('-fullscreen', False)
