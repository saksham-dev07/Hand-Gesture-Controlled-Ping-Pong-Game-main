"""
Game Engine Module
Handles game logic, physics, collision detection, scoring, and AI
"""

import numpy as np
from game_objects import Ball, Paddle
from config import *


class GameEngine:
    """Manages game state, physics, and AI"""
    
    def __init__(self):
        """Initialize the game engine"""
        # Create game objects
        self.ball = Ball()
        self.paddle1 = Paddle(PADDLE1_X, is_left=True)   # Left paddle
        self.paddle2 = Paddle(PADDLE2_X, is_left=False)  # Right paddle
        
        # Game state
        self.score = {'player1': 0, 'player2': 0}
        self.paused = False
        
        # AI settings
        self.ai_difficulty = AI_DIFFICULTY
    
    def reset(self):
        """Reset the entire game"""
        self.score = {'player1': 0, 'player2': 0}
        self.ball.reset()
        self.paused = False
    
    def reset_ball(self):
        """Reset only the ball"""
        self.ball.reset()
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        return self.paused
    
    def set_pause(self, paused):
        """Set pause state"""
        self.paused = paused
    
    def update_paddle_from_hand(self, paddle_num, y_normalized):
        """
        Update paddle position from hand tracking
        
        Args:
            paddle_num: 1 for left paddle, 2 for right paddle
            y_normalized: Normalized Y position (0-1)
        """
        if paddle_num == 1:
            self.paddle1.set_position_normalized(y_normalized)
            self.paddle1.is_hand_controlled = True
        elif paddle_num == 2:
            self.paddle2.set_position_normalized(y_normalized)
            self.paddle2.is_hand_controlled = True
    
    def update_ai_paddle(self, paddle):
        """
        Update paddle using AI logic
        
        Args:
            paddle: Paddle object to control
        """
        target_y = self.ball.y
        
        # AI reaction based on difficulty (random chance to react)
        if np.random.random() < self.ai_difficulty:
            paddle.move_toward_target(target_y, speed=AI_SPEED, error_margin=AI_ERROR_MARGIN)
    
    def update(self, left_hand_data=None, right_hand_data=None):
        """
        Update game state for one frame
        
        Args:
            left_hand_data: Dict with 'detected' and 'paddle_y' keys
            right_hand_data: Dict with 'detected' and 'paddle_y' keys
            
        Returns:
            Dict with scoring events
        """
        if self.paused:
            return {'scored': False}
        
        # Reset hand control flags
        self.paddle1.is_hand_controlled = False
        self.paddle2.is_hand_controlled = False
        
        # Update left paddle
        if left_hand_data and left_hand_data.get('detected') and left_hand_data.get('paddle_y') is not None:
            self.update_paddle_from_hand(1, left_hand_data['paddle_y'])
        else:
            # AI control
            self.update_ai_paddle(self.paddle1)
        
        # Update right paddle
        if right_hand_data and right_hand_data.get('detected') and right_hand_data.get('paddle_y') is not None:
            self.update_paddle_from_hand(2, right_hand_data['paddle_y'])
        else:
            # AI control
            self.update_ai_paddle(self.paddle2)
        
        # Move ball
        self.ball.move()
        
        # Ball collision with walls
        self.ball.constrain_to_bounds()
        
        # Ball collision with paddles
        if self.paddle1.collides_with_ball(self.ball):
            self.paddle1.adjust_ball_position_after_collision(self.ball)
            self.ball.bounce_paddle(self.paddle1, is_left=True)
        
        if self.paddle2.collides_with_ball(self.ball):
            self.paddle2.adjust_ball_position_after_collision(self.ball)
            self.ball.bounce_paddle(self.paddle2, is_left=False)
        
        # Check for scoring
        scored = False
        scorer = None
        
        if self.ball.is_out_left():
            self.score['player2'] += 1
            scored = True
            scorer = 'player2'
            print(f"🎯 Right player scores! Score: {self.score['player1']} - {self.score['player2']}")
            self.reset_ball()
        elif self.ball.is_out_right():
            self.score['player1'] += 1
            scored = True
            scorer = 'player1'
            print(f"🎯 Left player scores! Score: {self.score['player1']} - {self.score['player2']}")
            self.reset_ball()
        
        return {
            'scored': scored,
            'scorer': scorer,
            'score': self.score.copy()
        }
    
    def get_game_state(self):
        """
        Get current game state for rendering
        
        Returns:
            Dict with all game object positions and states
        """
        return {
            'ball': {
                'x': self.ball.x,
                'y': self.ball.y,
                'radius': self.ball.radius,
                'speed': self.ball.get_speed()
            },
            'paddle1': {
                'x': self.paddle1.x,
                'y': self.paddle1.y,
                'width': self.paddle1.width,
                'height': self.paddle1.height,
                'hand_controlled': self.paddle1.is_hand_controlled
            },
            'paddle2': {
                'x': self.paddle2.x,
                'y': self.paddle2.y,
                'width': self.paddle2.width,
                'height': self.paddle2.height,
                'hand_controlled': self.paddle2.is_hand_controlled
            },
            'score': self.score.copy(),
            'paused': self.paused
        }
    
    def get_score(self):
        """Get current score"""
        return self.score.copy()
    
    def is_paused(self):
        """Check if game is paused"""
        return self.paused
