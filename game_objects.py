"""
Game Objects Module
Contains Ball and Paddle classes with their properties and behaviors
"""

import numpy as np
from config import *


class Ball:
    """Represents the game ball"""
    
    def __init__(self):
        """Initialize the ball"""
        self.radius = BALL_RADIUS
        self.max_speed = BALL_MAX_SPEED
        self.min_speed = BALL_MIN_SPEED
        self.reset()
    
    def reset(self):
        """Reset ball to center with random direction"""
        self.x = CANVAS_WIDTH // 2
        self.y = CANVAS_HEIGHT // 2
        
        # Random direction but normalized speed
        angle = np.random.uniform(-np.pi/4, np.pi/4)  # -45 to 45 degrees
        direction = 1 if np.random.random() > 0.5 else -1
        speed = BALL_INITIAL_SPEED
        
        self.dx = speed * np.cos(angle) * direction
        self.dy = speed * np.sin(angle)
    
    def move(self):
        """Update ball position"""
        self.x += self.dx
        self.y += self.dy
    
    def bounce_vertical(self):
        """Bounce off top or bottom wall"""
        self.dy = -self.dy
    
    def bounce_paddle(self, paddle, is_left=True):
        """
        Bounce off paddle with angle based on hit position
        
        Args:
            paddle: Paddle object that was hit
            is_left: True if left paddle, False if right paddle
        """
        # Calculate hit position on paddle (0 to 1)
        hit_pos = (self.y - paddle.y) / paddle.height
        
        # Angle based on hit position (-45 to 45 degrees)
        angle = (hit_pos - 0.5) * np.pi / 2
        
        # Increase speed slightly but cap it
        current_speed = np.sqrt(self.dx**2 + self.dy**2)
        new_speed = min(current_speed * BALL_SPEED_INCREASE, self.max_speed)
        
        # Set new velocity
        if is_left:
            self.dx = abs(new_speed * np.cos(angle))
        else:
            self.dx = -abs(new_speed * np.cos(angle))
        
        self.dy = new_speed * np.sin(angle)
    
    def constrain_to_bounds(self):
        """Keep ball within vertical bounds"""
        if self.y <= self.radius:
            self.y = self.radius
            self.bounce_vertical()
        elif self.y >= CANVAS_HEIGHT - self.radius:
            self.y = CANVAS_HEIGHT - self.radius
            self.bounce_vertical()
    
    def is_out_left(self):
        """Check if ball went out on left side"""
        return self.x < 0
    
    def is_out_right(self):
        """Check if ball went out on right side"""
        return self.x > CANVAS_WIDTH
    
    def get_speed(self):
        """Get current ball speed"""
        return np.sqrt(self.dx**2 + self.dy**2)
    
    def get_position(self):
        """Get ball position as tuple"""
        return (self.x, self.y)
    
    def get_velocity(self):
        """Get ball velocity as tuple"""
        return (self.dx, self.dy)
    
    def increase_speed(self, amount=BALL_SPEED_CHANGE_AMOUNT):
        """
        Increase ball speed by a fixed amount
        
        Args:
            amount: Speed increase amount
        """
        current_speed = self.get_speed()
        if current_speed < self.max_speed:
            # Calculate new speed
            new_speed = min(current_speed + amount, self.max_speed)
            # Maintain direction, update magnitude
            if current_speed > 0:
                scale = new_speed / current_speed
                self.dx *= scale
                self.dy *= scale
            print(f"⚡ Ball speed increased to {new_speed:.1f}")
    
    def decrease_speed(self, amount=BALL_SPEED_CHANGE_AMOUNT):
        """
        Decrease ball speed by a fixed amount
        
        Args:
            amount: Speed decrease amount
        """
        current_speed = self.get_speed()
        if current_speed > self.min_speed:
            # Calculate new speed
            new_speed = max(current_speed - amount, self.min_speed)
            # Maintain direction, update magnitude
            if current_speed > 0:
                scale = new_speed / current_speed
                self.dx *= scale
                self.dy *= scale
            print(f"🐌 Ball speed decreased to {new_speed:.1f}")


class Paddle:
    """Represents a game paddle"""
    
    def __init__(self, x, is_left=True):
        """
        Initialize the paddle
        
        Args:
            x: X position of paddle
            is_left: True for left paddle, False for right paddle
        """
        self.x = x
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.y = (CANVAS_HEIGHT - self.height) // 2  # Start in center
        self.is_left = is_left
        self.is_hand_controlled = False
        self._last_y = self.y  # For deadzone calculation
    
    def move_up(self, speed=PADDLE_SPEED):
        """Move paddle up"""
        self.y = max(0, self.y - speed)
    
    def move_down(self, speed=PADDLE_SPEED):
        """Move paddle down"""
        self.y = min(CANVAS_HEIGHT - self.height, self.y + speed)
    
    def set_position_normalized(self, y_normalized, use_deadzone=False):
        """
        Set paddle position using normalized y (0-1)
        
        Args:
            y_normalized: Y position normalized to 0-1 range
            use_deadzone: If True, apply deadzone to reduce small movements
        """
        target_y = y_normalized * CANVAS_HEIGHT
        new_y = max(0, min(target_y - self.height // 2, CANVAS_HEIGHT - self.height))
        
        # Apply deadzone to reduce jitter
        if use_deadzone and hasattr(self, '_last_y'):
            y_diff = abs(new_y - self._last_y)
            if y_diff < HAND_POSITION_DEADZONE * CANVAS_HEIGHT:
                return  # Movement too small, ignore
        
        self.y = new_y
        self._last_y = new_y
    
    def set_position(self, y):
        """Set absolute Y position (with bounds checking)"""
        self.y = max(0, min(y, CANVAS_HEIGHT - self.height))
    
    def get_center_y(self):
        """Get Y coordinate of paddle center"""
        return self.y + self.height // 2
    
    def move_toward_target(self, target_y, speed=AI_SPEED, error_margin=AI_ERROR_MARGIN):
        """
        Move paddle toward a target Y position (for AI)
        
        Args:
            target_y: Target Y position
            speed: Movement speed
            error_margin: Acceptable distance from target
        """
        center_y = self.get_center_y()
        
        if center_y < target_y - error_margin:
            self.move_down(speed)
        elif center_y > target_y + error_margin:
            self.move_up(speed)
    
    def collides_with_ball(self, ball):
        """
        Check if paddle collides with ball
        
        Args:
            ball: Ball object
            
        Returns:
            True if collision detected
        """
        if self.is_left:
            # Left paddle - check right edge
            x_collision = (ball.x - ball.radius <= self.x + self.width and 
                          ball.x >= self.x and 
                          ball.dx < 0)
        else:
            # Right paddle - check left edge
            x_collision = (ball.x + ball.radius >= self.x and 
                          ball.x <= self.x + self.width and 
                          ball.dx > 0)
        
        # Check Y collision
        y_collision = (ball.y >= self.y and 
                      ball.y <= self.y + self.height)
        
        return x_collision and y_collision
    
    def adjust_ball_position_after_collision(self, ball):
        """
        Adjust ball position after collision to prevent sticking
        
        Args:
            ball: Ball object
        """
        if self.is_left:
            ball.x = self.x + self.width + ball.radius
        else:
            ball.x = self.x - ball.radius
    
    def get_bounds(self):
        """Get paddle bounds as (x, y, width, height)"""
        return (self.x, self.y, self.width, self.height)
