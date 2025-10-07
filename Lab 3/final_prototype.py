#!/usr/bin/env python3
"""
ideaBox Enhanced - AI-Powered Party Game Assistant with Touch Control
Combines creative AI suggestions, score tracking, and MPR121 touch sensor input
Features from both IdeaBox and Monopoly Voice Assistant
"""

import subprocess
import time
import os
import sys
import random
import re
from pathlib import Path
import threading
import board
import busio
import adafruit_mpr121

class IdeaBoxEnhanced:
    def __init__(self):
        self.piper_model = "en_US-lessac-medium"
        self.whisper_model = "tiny"
        self.current_game = None
        self.audio_dir = "audio"
        self.intro_sound = "intro.mp3"
        self.spinner_active = False
        self.spinner_thread = None
        
        # Score tracking state (from Zoe's script)
        self.player_scores = {}
        self.score_initialized = False
        
        # MPR121 Touch Sensor Setup
        self.touch_sensor = None
        self.setup_touch_sensor()
        
        # Touch sensor mappings
        # Pads 0-4: Select punishment (1-5)
        # Pads 5-11: Select duration
        self.touch_punishment_map = {
            0: 1,  # Pad 0 = Punishment option 1
            1: 2,  # Pad 1 = Punishment option 2
            2: 3,  # Pad 2 = Punishment option 3
            3: 4,  # Pad 3 = Punishment option 4
            4: 5   # Pad 4 = Punishment option 5
        }
        
        self.touch_duration_map = {
            5: 5,   # Pad 5 = 5 seconds
            6: 10,  # Pad 6 = 10 seconds
            7: 15,  # Pad 7 = 15 seconds
            8: 20,  # Pad 8 = 20 seconds
            9: 30,  # Pad 9 = 30 seconds
            10: 45, # Pad 10 = 45 seconds
            11: 60  # Pad 11 = 60 seconds
        }
        
        # Create audio directory if it doesn't exist
        os.makedirs(self.audio_dir, exist_ok=True)
        
        # Detect available Piper voices
        self.detect_piper_voice()
    
    def setup_touch_sensor(self):
        """Initialize MPR121 touch sensor"""
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.touch_sensor = adafruit_mpr121.MPR121(i2c)
            print("✓ MPR121 Touch Sensor initialized successfully!")
            print("Touch pads 0-11 are mapped to punishment durations:")
            for pad, duration in self.touch_duration_map.items():
                print(f"  Pad {pad}: {duration} seconds")
        except Exception as e:
            print(f"Warning: Could not initialize MPR121 touch sensor: {e}")
            print("Touch sensor features will be disabled.")
            self.touch_sensor = None
    
[pad]
                    print(f"\n✓ Pad {pad} touched! Selected duration: {duration} seconds")
                    time.sleep(0.3)  # Debounce
                    return duration
            
            time.sleep(0.1)
        
        print("\nTimeout - using default 10 seconds")
        return 10
    
    def __del__(self):
        """Cleanup on exit"""
        self.stop_spinner()
    
    def detect_piper_voice(self):
        """Detect available Piper voices and use the first available one"""
        try:
            result = subprocess.run(['piper', '--list-voices'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                voices = []
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('Available'):
                        voice_name = line.strip().split()[0]
                        voices.append(voice_name)
                
                if voices:
                    if self.piper_model in voices:
                        print(f"Using Piper voice: {self.piper_model}")
                    else:
                        self.piper_model = voices[0]
                        print(f"Voice en_US-lessac-medium not found. Using: {self.piper_model}")
        except Exception as e:
            print(f"Error detecting Piper voices: {e}")
    
    def play_intro_sound(self):
        """Play the intro sound using mpg123 or aplay"""
        try:
            intro_path = os.path.join(self.audio_dir, self.intro_sound)
            
            if not os.path.exists(intro_path):
                print(f"Warning: Intro sound not found at {intro_path}")
                return False
            
            print("Playing intro sound...")
            
            try:
                subprocess.run(['mpg123', intro_path], capture_output=True)
                return True
            except FileNotFoundError:
                try:
                    subprocess.run(['ffplay', '-nodisp', '-autoexit', intro_path], 
                                 capture_output=True)
                    return True
                except FileNotFoundError:
                    print("No suitable audio player found for MP3.")
                    return False
                    
        except Exception as e:
            print("Intro sound error:", e)
            return False
    
    def spinner_animation(self, message="Processing"):
        """Display spinning wheel animation"""
        spinner_chars = ['|', '/', '-', '\\']
        idx = 0
        
        while self.spinner_active:
            sys.stdout.write(f'\r{message}... {spinner_chars[idx % len(spinner_chars)]} ')
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)
        
        sys.stdout.write('\r' + ' ' * (len(message) + 10) + '\r')
        sys.stdout.flush()
    
    def start_spinner(self, message="Processing"):
        """Start the spinner animation in a separate thread"""
        if self.spinner_thread and self.spinner_thread.is_alive():
            self.stop_spinner()
        
        self.spinner_active = True
        self.spinner_thread = threading.Thread(target=self.spinner_animation, args=(message,))
        self.spinner_thread.daemon = True
        self.spinner_thread.start()
    
    def stop_spinner(self):
        """Stop the spinner animation"""
        self.spinner_active = False
        if self.spinner_thread:
            self.spinner_thread.join(timeout=0.5)
    
    def display_punishment_name(self, player_name, countdown_seconds=10, punishment=""):
        """Display player name during punishment countdown with synced audio"""
        try:
            for i in range(countdown_seconds, 0, -1):
                os.system('clear')
                
                print("\n" * 3)
                print("=" * 60)
                print(f"{'PUNISHMENT TIME!':^60}")
                print("=" * 60)
                print()
                print(f"{player_name:^60}")
                print()
                if punishment:
                    import textwrap
                    wrapped = textwrap.fill(punishment, width=58)
                    for line in wrapped.split('\n'):
                        print(f"{line:^60}")
                    print()
                
                if i <= 5:
                    print(f"{f'>>> {i} <<<':^60}")
                else:
                    print(f"{str(i):^60}")
                
                print()
                print("=" * 60)
                
                if i <= 5:
                    countdown_text = str(i)
                    self.text_to_speech(countdown_text, f"countdown_{i}.wav")
                else:
                    time.sleep(1)
            
            os.system('clear')
            print("\n" * 8)
            print("=" * 60)
            print(f"{'TIME UP!':^60}")
            print("=" * 60)
            print()
            
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print("Display error:", e)
            return False
    
    def text_to_speech(self, text, filename="output.wav"):
        """Convert text to speech using Piper or espeak as fallback"""
        try:
            print("ASSISTANT:", text)
            
            self.start_spinner("Generating speech")
            
            audio_path = os.path.join(self.audio_dir, filename)
            
            try:
                process = subprocess.run(
                    ['piper', '--model', self.piper_model, '--output_file', audio_path],
                    input=text,
                    text=True,
                    capture_output=True,
                    timeout=10
                )
                
                self.stop_spinner()
                
                if process.returncode == 0:
                    subprocess.run([
                        'aplay', 
                        '--buffer-size=8192',
                        audio_path
                    ], capture_output=True)
                    return True
                else:
                    raise Exception("Piper failed, trying fallback")
                    
            except Exception as piper_error:
                print("Piper unavailable, using espeak fallback...")
                try:
                    subprocess.run([
                        'espeak',
                        '-w', audio_path,
                        '-s', '150',
                        '-a', '200',
                        text
                    ], check=True, capture_output=True)
                    
                    self.stop_spinner()
                    
                    subprocess.run([
                        'aplay',
                        '--buffer-size=8192',
                        audio_path
                    ], capture_output=True)
                    return True
                    
                except FileNotFoundError:
                    self.stop_spinner()
                    print("No TTS available - printing only")
                    return True
                
        except Exception as e:
            self.stop_spinner()
            print("TTS ERROR:", e)
            return False
    
    def record_audio(self, duration=5, filename="user_input.wav"):
        """Record audio from microphone"""
        try:
            print(f"RECORDING for {duration} seconds...")
            
            audio_path = os.path.join(self.audio_dir, filename)
            
            result = subprocess.run([
                'arecord', 
                '-d', str(duration),
                '-f', 'cd',
                '-t', 'wav',
                audio_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Recording completed successfully")
                return True
            else:
                print("Recording failed:", result.stderr)
                return False
                
        except Exception as e:
            print("Recording error:", e)
            return False
    
    def speech_to_text(self, audio_file):
        """Convert speech to text using Whisper"""
        try:
            self.start_spinner("Converting speech to text")
            
            audio_path = os.path.join(self.audio_dir, audio_file)
            
            result = subprocess.run([
                'whisper', audio_path,
                '--model', self.whisper_model,
                '--output_format', 'txt',
                '--output_dir', self.audio_dir,
                '--verbose', 'False'
            ], capture_output=True, text=True)
            
            self.stop_spinner()
            
            if result.returncode == 0:
                text_file = os.path.join(self.audio_dir, audio_file.replace('.wav', '.txt'))
                if os.path.exists(text_file):
                    with open(text_file, 'r') as f:
                        text = f.read().strip()
                    print("You said:", text)
                    return text
                else:
                    print("Text file not generated")
                    return None
            else:
                print("Speech-to-text failed:", result.stderr)
                return None
                
        except Exception as e:
            self.stop_spinner()
            print("Speech-to-text error:", e)
            return None

    def get_ai_creative_suggestions(self, game_type, request_type, additional_context=""):
        """Get AI-powered creative suggestions using Ollama"""
        try:
            ack_messages = [
                "Let me think of some creative ideas for you...",
                "Give me a moment to come up with something fun...",
                "I'm brewing up some creative suggestions...",
                "Working on some fresh ideas for your game...",
                "Let me put on my creative thinking cap..."
            ]
            ack_message = random.choice(ack_messages)
            self.text_to_speech(ack_message, "thinking.wav")
            
            self.start_spinner("AI is thinking")
            
            if request_type == "punishments":
                prompt = f"""You're helping friends playing {game_type} who need creative consequences for losing. 

Give me exactly 5 fun, lighthearted punishment ideas. Be creative and think outside the box! They should be:
- Quick and entertaining
- Safe and appropriate for everyone
- Something that makes people laugh

Context: {additional_context}

IMPORTANT: Format your response as a numbered list with each punishment on a separate line. Start each line with the number and a period. Do not use emojis, asterisks, or special characters. Keep each punishment to one short sentence."""
            
            elif request_type == "themes":
                prompt = f"""Players are enjoying {game_type} and want fresh theme ideas to keep it interesting.

Suggest exactly 5 creative themes or categories. Think of unexpected, fun angles that would make the game more exciting. 

Context: {additional_context}

IMPORTANT: Format your response as a numbered list with each theme on a separate line. Start each line with the number and a period. Do not use emojis, asterisks, or special characters. Keep each theme to one short phrase."""
            
            elif request_type == "variations":
                prompt = f"""Friends playing {game_type} want to shake things up with some rule variations.

Give me exactly 5 creative ways to modify the game. Think of fun twists that change the dynamic while keeping it enjoyable.

Context: {additional_context}

IMPORTANT: Format your response as a numbered list with each variation on a separate line. Start each line with the number and a period. Do not use emojis, asterisks, or special characters. Keep each variation to one short sentence."""
            
            else:
                prompt = f"""Players of {game_type} are asking: "{additional_context}"

Help them make their game more fun and memorable. Give exactly 5 creative and practical suggestions they can use right now.

IMPORTANT: Format your response as a numbered list with each suggestion on a separate line. Start each line with the number and a period. Do not use emojis, asterisks, or special characters. Keep each suggestion to one short sentence."""
            
            result = subprocess.run([
                'ollama', 'run', 'llama3.2',
                prompt
            ], capture_output=True, text=True, timeout=60)
            
            self.stop_spinner()
            
            if result.returncode == 0:
                response = result.stdout.strip()
                print("AI generated creative suggestions successfully")
                suggestions = self.parse_numbered_list(response)
                return suggestions
            else:
                print("Ollama error:", result.stderr)
                return self.get_fallback_suggestion(request_type, game_type)
                
        except subprocess.TimeoutExpired:
            self.stop_spinner()
            print("Ollama timeout - using fallback")
            return self.get_fallback_suggestion(request_type, game_type)
        except Exception as e:
            self.stop_spinner()
            print("Ollama error:", e)
            return self.get_fallback_suggestion(request_type, game_type)
    
    def parse_numbered_list(self, text):
        """Parse AI response into a list of suggestions"""
        suggestions = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if re.match(r'^\d+\.', line):
                suggestion = re.sub(r'^\d+\.\s*', '', line)
                if suggestion:
                    suggestions.append(suggestion)
        
        if not suggestions:
            suggestions = [line.strip() for line in lines if line.strip()]
        
        return suggestions[:5]

    def get_fallback_suggestion(self, request_type, game_type):
        """Fallback suggestions if AI isn't available"""
        fallbacks = {
            "punishments": [
                "Do a 30 second victory dance for the winning team",
                "Tell a joke or funny story to make everyone laugh",
                "Give genuine compliments to each other player",
                "Act out their favorite animal for 1 minute",
                "Share an embarrassing but harmless childhood memory"
            ],
            "themes": [
                "90s nostalgia with movies music and trends",
                "Childhood favorites like cartoons games and snacks",
                "Around the world featuring countries landmarks and foods",
                "Superheroes and villains",
                "Time travel to past decades or future predictions"
            ],
            "variations": [
                "Speed rounds where you cut time limits in half",
                "Silent mode with no talking except for answers",
                "Team swap where you switch teams halfway through",
                "Prop challenge using random objects as hints",
                "Reverse rules where you play with opposite rules for one round"
            ]
        }
        return fallbacks.get(request_type, [])

    # --- Score Tracking Methods (from Zoe's script) ---
    def initialize_scores(self, initial_amount=10000, players=None):
        """Initialize player scores"""
        if players is None:
            players = ['Player1', 'Player2', 'Player3']
        self.player_scores = {player.lower(): initial_amount for player in players}
        self.score_initialized = True
        player_list = ", ".join([p.capitalize() for p in self.player_scores.keys()])
        return f"Game started! {player_list} all begin with ${initial_amount}. Let the game begin!"

    def update_score(self, player_name, amount, operation):
        """Update a player's score"""
        player_name = player_name.lower()
        if player_name not in self.player_scores:
            return f"Sorry, I don't see a player named {player_name}."

        try:
            amount = int(amount)
            if amount < 0:
                return "Please state a positive amount."

            if operation == 'subtract':
                self.player_scores[player_name] -= amount
                action_word = "paid"
            elif operation == 'add':
                self.player_scores[player_name] += amount
                action_word = "received"
            else:
                return "Internal error: Invalid operation."

            new_balance = self.player_scores[player_name]
            return f"{player_name.capitalize()} {action_word} ${amount}. New balance: ${new_balance}."
        except ValueError:
            return "I couldn't understand the amount."

    def display_scores(self):
        """Display all current scores"""
        if not self.player_scores:
            return "No game in progress. Say 'start game' to begin."
        score_lines = [f"{name.capitalize()}: ${score:,.0f}" for name, score in self.player_scores.items()]
        return "Current scores: " + " | ".join(score_lines)
    # ---------------------------------------------------

    def simulate_user_input(self, prompt_type="general"):
        """Simulate user input for testing without microphone"""
        if prompt_type == "game":
            test_games = [
                "charades", "pictionary", "trivia",
                "cards against humanity", "monopoly",
                "two truths and a lie", "never have I ever"
            ]
            
            print("\nSIMULATION MODE - Choose a game:")
            for i, game in enumerate(test_games, 1):
                print(f"{i}. {game}")
            
            try:
                choice = int(input("Enter number (1-7): ")) - 1
                if 0 <= choice < len(test_games):
                    return test_games[choice]
                else:
                    return test_games[0]
            except:
                return test_games[0]
        
        elif prompt_type == "confirmation":
            options = ["yes please", "sure", "no thanks", "yes"]
            print("\nConfirmation options:")
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            
            try:
                choice = int(input("Enter number (1-4): ")) - 1
                if 0 <= choice < len(options):
                    return options[choice]
                else:
                    return options[0]
            except:
                return options[0]
        
        elif prompt_type == "player_name":
            print("\nEnter player name for punishment:")
            player_name = input("Player name: ").strip()
            return player_name if player_name else "Player 1"
        
        elif prompt_type == "punishment_choice":
            print("\nEnter the number of the punishment you want to use:")
            try:
                choice = int(input("Punishment #: "))
                return str(choice)
            except:
                return "1"
        
        else:
            requests = [
                "punishment ideas for losers",
                "new themes to try",
                "fun variations to mix things up", 
                "creative scoring ideas",
                "help make it more interesting"
            ]
            
            print("\nWhat creative help do you want?")
            for i, request in enumerate(requests, 1):
                print(f"{i}. {request}")
            
            try:
                choice = int(input("Enter number (1-5): ")) - 1
                if 0 <= choice < len(requests):
                    return requests[choice]
                else:
                    return requests[0]
            except:
                return requests[0]

    def get_user_input(self, use_microphone, prompt_type="general", duration=6):
        """Get user input either from microphone or simulation"""
        if use_microphone:
            filename = f"{prompt_type}_response.wav"
            if self.record_audio(duration=duration, filename=filename):
                return self.speech_to_text(filename)
            return None
        else:
            user_input = self.simulate_user_input(prompt_type)
            print(f"Simulated input: {user_input}")
            return user_input

    def parse_confirmation(self, response):
        """Check if user wants help"""
        if not response:
            return True
        
        positive = ["yes", "yeah", "sure", "please", "ok", "sounds good"]
        negative = ["no", "nah", "not really", "skip"]
        
        response_lower = response.lower()
        
        for word in positive:
            if word in response_lower:
                return True
        
        for word in negative:
            if word in response_lower:
                return False
        
        return True

    def determine_request_type(self, user_request):
        """Determine what type of creative help the user wants"""
        if not user_request:
            return "general"
        
        request_lower = user_request.lower()
        
        if any(word in request_lower for word in ["punishment", "penalty", "consequence", "loser", "lose"]):
            return "punishments"
        elif any(word in request_lower for word in ["theme", "topic", "category", "subject"]):
            return "themes"
        elif any(word in request_lower for word in ["variation", "twist", "change", "different", "mix", "spice"]):
            return "variations"
        else:
            return "general"

    def handle_punishment_countdown(self, use_microphone, punishment_suggestions):
        """Handle punishment flow with touch sensor for selection and duration"""
        try:
            print("\n" + "="*60)
            print("PUNISHMENT OPTIONS:")
            print("="*60)
            
            if isinstance(punishment_suggestions, list):
                for i, punishment in enumerate(punishment_suggestions, 1):
                    print(f"{i}. {punishment}")
            else:
                punishments = self.parse_numbered_list(str(punishment_suggestions))
                for i, punishment in enumerate(punishments, 1):
                    print(f"{i}. {punishment}")
                punishment_suggestions = punishments
            
            print("="*60 + "\n")
            
            intro = "Here are your punishment options."
            self.text_to_speech(intro, "punishment_intro.wav")
            
            for i, punishment in enumerate(punishment_suggestions, 1):
                punishment_text = f"Option {i}. {punishment}"
                self.text_to_speech(punishment_text, f"punishment_option_{i}.wav")
                time.sleep(0.5)
            
            # USE TOUCH SENSOR TO SELECT PUNISHMENT
            selected_index = 0
            if self.touch_sensor:
                choice_question = "Touch pad 0 through 4 to select which punishment to use."
                self.text_to_speech(choice_question, "ask_punishment_choice.wav")
                
                selected_option = self.wait_for_touch_punishment(
                    max_options=len(punishment_suggestions), 
                    timeout=30
                )
                selected_index = selected_option - 1
            else:
                # Fallback to voice/text input
                choice_question = "Which punishment would you like to use? Say the number."
                self.text_to_speech(choice_question, "ask_punishment_choice.wav")
                
                choice_response = self.get_user_input(use_microphone, "punishment_choice", duration=5)
                
                if choice_response:
                    numbers = re.findall(r'\d+', choice_response)
                    if numbers:
                        try:
                            selected_index = int(numbers[0]) - 1
                            if selected_index < 0 or selected_index >= len(punishment_suggestions):
                                selected_index = 0
                        except:
                            selected_index = 0
            
            selected_punishment = punishment_suggestions[selected_index]
            
            confirm_msg = f"You selected punishment number {selected_index + 1}. {selected_punishment}"
            self.text_to_speech(confirm_msg, "confirm_selection.wav")
            print(f"\nSELECTED: {selected_punishment}\n")
            
            name_question = "What is the name of the player who will face this punishment?"
            self.text_to_speech(name_question, "ask_player_name.wav")
            
            player_name = self.get_user_input(use_microphone, "player_name", duration=8)
            if not player_name or len(player_name.strip()) == 0:
                player_name = "Player"
            
            # USE TOUCH SENSOR FOR DURATION
            if self.touch_sensor:
                duration_msg = "Touch pad 5 through 11 to select the punishment duration."
                self.text_to_speech(duration_msg, "touch_duration.wav")
                countdown_seconds = self.wait_for_touch_input(timeout=30)
            else:
                duration_question = "How many seconds should the punishment countdown last? Say a number between 5 and 90."
                self.text_to_speech(duration_question, "ask_duration.wav")
                
                duration_response = self.get_user_input(use_microphone, "countdown_time", duration=5)
                
                countdown_seconds = 10
                if duration_response:
                    numbers = re.findall(r'\d+', duration_response)
                    if numbers:
                        try:
                            countdown_seconds = int(numbers[0])
                            countdown_seconds = max(5, min(90, countdown_seconds))
                        except:
                            countdown_seconds = 10
            
            confirm_msg = f"Alright! {player_name} will have {countdown_seconds} seconds to complete. {selected_punishment}. Get ready!"
            self.text_to_speech(confirm_msg, "start_countdown.wav")
            
            time.sleep(1)
            
            self.display_punishment_name(player_name, countdown_seconds, selected_punishment)
            
            done_msg = f"Time up! {player_name} has completed the punishment. Great job everyone!"
            self.text_to_speech(done_msg, "punishment_complete.wav")
            
            return True
            
        except Exception as e:
            print(f"Error in punishment countdown: {e}")
            error_msg = "Sorry, there was an issue with the punishment countdown."
            self.text_to_speech(error_msg, "punishment_error.wav")
            return False

    def run_ideabox_assistant(self, use_microphone=False):
        """Run the enhanced ideaBox assistant with separate feature modes"""
        print("Welcome to ideaBox Enhanced!")
        print("AI Creative Assistant + Score Tracking + Touch Control")
        print("="*60)
        
        self.play_intro_sound()
        time.sleep(1)
        
        # MODE SELECTION - Touch Sensor or Voice
        if self.touch_sensor:
            mode_question = "Hi! I'm ideaBox Enhanced. Touch pad 0 for Punishment Mode, or pad 1 for Score Tracking Mode."
            self.text_to_speech(mode_question, "mode_question.wav")
            
            selected_mode = self.wait_for_mode_selection(timeout=30)
            score_mode = (selected_mode == "score")
            mode = "Score Tracking" if score_mode else "Punishment"
        else:
            # Fallback to voice/text input
            mode_question = "Hi! I'm ideaBox Enhanced. Would you like to use Punishment Mode with creative ideas, or Score Tracking Mode?"
            self.text_to_speech(mode_question, "mode_question.wav")
            
            mode_response = self.get_user_input(use_microphone, "general", duration=8)
            
            # Determine mode based on response
            score_mode = False
            if mode_response and any(word in mode_response.lower() for word in ["score", "track", "money", "points", "monopoly"]):
                score_mode = True
                mode = "Score Tracking"
            else:
                mode = "Punishment"
        
        print(f"\n>>> MODE SELECTED: {mode} <<<\n")
        
        # Ask what game they're playing
        game_question = f"Great! What game are you playing?"
        self.text_to_speech(game_question, "game_question.wav")
        
        game_response = self.get_user_input(use_microphone, "game", duration=8)
        
        if not game_response:
            game_response = "party game"
        
        self.current_game = game_response
        print(f"Game: {self.current_game}")
        
        # ========== PUNISHMENT MODE ==========
        if not score_mode:
            # Get AI-powered punishment suggestions
            punishment_suggestions = self.get_ai_creative_suggestions(
                self.current_game, 
                "punishments"
            )
            
            # Handle punishment countdown with touch sensor
            self.handle_punishment_countdown(use_microphone, punishment_suggestions)
            
            # Ask for other creative help
            other_help_question = "Would you like more creative ideas? I can suggest themes or game variations!"
            self.text_to_speech(other_help_question, "other_help.wav")
            
            help_response = self.get_user_input(use_microphone, "confirmation", duration=6)
            
            if self.parse_confirmation(help_response):
                help_request_question = "What would you like help with? Themes, variations, or something else?"
                self.text_to_speech(help_request_question, "help_request.wav")
                
                help_request = self.get_user_input(use_microphone, "general", duration=10)
                
                if help_request:
                    request_type = self.determine_request_type(help_request)
                    
                    ai_suggestions = self.get_ai_creative_suggestions(
                        self.current_game, 
                        request_type, 
                        help_request
                    )
                    
                    # Read out the suggestions
                    if isinstance(ai_suggestions, list):
                        for i, suggestion in enumerate(ai_suggestions, 1):
                            suggestion_text = f"Suggestion {i}. {suggestion}"
                            self.text_to_speech(suggestion_text, f"suggestion_{i}.wav")
                            time.sleep(0.5)
                    else:
                        self.text_to_speech(str(ai_suggestions), "ai_suggestions.wav")
                    
                    time.sleep(2)
        
        # ========== SCORE TRACKING MODE ==========
        else:
            # Initialize scores
            init_msg = self.initialize_scores()
            self.text_to_speech(init_msg, "score_init.wav")
            
            # Score tracking loop
            while True:
                # Display current scores
                scores = self.display_scores()
                self.text_to_speech(scores, "current_scores.wav")
                
                # Ask if they want to update scores
                update_question = "Would you like to update a player's score?"
                self.text_to_speech(update_question, "update_question.wav")
                
                update_response = self.get_user_input(use_microphone, "confirmation", duration=6)
                
                if not self.parse_confirmation(update_response):
                    break
                
                # Get score update details
                update_instruction = "Please say the player name, then the amount, then whether to add or subtract. For example: Player one, 500, add."
                self.text_to_speech(update_instruction, "update_instruction.wav")
                
                update_input = self.get_user_input(use_microphone, "general", duration=10)
                
                if update_input:
                    # Parse the update (simple parsing - can be enhanced)
                    # Look for player names
                    player = None
                    for p in self.player_scores.keys():
                        if p in update_input.lower():
                            player = p
                            break
                    
                    # Look for amount
                    numbers = re.findall(r'\d+', update_input)
                    amount = numbers[0] if numbers else "0"
                    
                    # Look for operation
                    operation = "add"
                    if any(word in update_input.lower() for word in ["subtract", "minus", "paid", "lost", "owes"]):
                        operation = "subtract"
                    
                    if player:
                        result = self.update_score(player, amount, operation)
                        self.text_to_speech(result, "score_update_result.wav")
                    else:
                        error_msg = "Sorry, I couldn't identify the player. Please try again."
                        self.text_to_speech(error_msg, "score_error.wav")
        
        # Farewell
        farewell = f"Have an amazing time with your {self.current_game}! This is ideaBox Enhanced signing off!"
        self.text_to_speech(farewell, "farewell.wav")
        
        print("\nideaBox Enhanced session complete!")
        return {
            "game": self.current_game,
            "mode": mode,
            "ai_powered": not score_mode,
            "score_tracking": score_mode,
            "touch_sensor": self.touch_sensor is not None,
            "session_complete": True
        }


def main():
    """Main function to run the enhanced assistant"""
    print("Starting ideaBox Enhanced...")
    print("Features: AI Suggestions + Score Tracking + Touch Sensor Control")
    print("="*60)
    
    ideabox = IdeaBoxEnhanced()
    
    # Check microphone availability
    mic_available = False
    try:
        result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
        mic_available = len(result.stdout.strip()) > 0
    except:
        pass
    
    if mic_available:
        print("✓ Microphone detected!")
        use_mic = input("Use microphone? (y/n): ").lower().startswith('y')
    else:
        print("! No microphone detected - using simulation mode")
        use_mic = False
    
    # Run ideaBox Enhanced
    result = ideabox.run_ideabox_assistant(use_microphone=use_mic)
    
    # Log results
    print("\n" + "="*60)
    print("ideaBox ENHANCED SESSION LOG:")
    print("="*60)
    print(f"Game: {result.get('game', 'Unknown')}")
    print(f"Mode: {result.get('mode', 'Unknown')}")
    print(f"AI-powered suggestions: {'✓' if result.get('ai_powered') else '✗'}")
    print(f"Score tracking enabled: {'✓' if result.get('score_tracking') else '✗'}")
    print(f"Touch sensor active: {'✓' if result.get('touch_sensor') else '✗'}")
    print(f"Session completed: {'✓' if result.get('session_complete') else '✗'}")
    print("="*60)


if __name__ == "__main__":
    main()
