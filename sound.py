import pygame
import random
pygame.mixer.init()
channel1 = pygame.mixer.Channel(1)
channel2 = pygame.mixer.Channel(2)
class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {
            'c': pygame.mixer.Sound('./sounds/c.wav'),
            'd': pygame.mixer.Sound('./sounds/d.wav'),
            'e': pygame.mixer.Sound('./sounds/e.wav'),
            'f': pygame.mixer.Sound('./sounds/f.wav'),
            'g': pygame.mixer.Sound('./sounds/g.wav'),
            'a': pygame.mixer.Sound('./sounds/a.wav'),
            'b': pygame.mixer.Sound('./sounds/b.wav'),
            'c2': pygame.mixer.Sound('./sounds/c2.wav'),
            'attack': pygame.mixer.Sound('./sounds/attack.wav'),
            'found_food': pygame.mixer.Sound('./sounds/found_food.wav'),
            'danger': pygame.mixer.Sound('./sounds/danger.wav'),
            'death': pygame.mixer.Sound('./sounds/death.wav'),
            'collision': pygame.mixer.Sound('./sounds/collision.wav'),
            'hungry': pygame.mixer.Sound('./sounds/hungry.wav'),
            'finished_eating': pygame.mixer.Sound('./sounds/finished_eating.wav'),
        }
        self.last_sound_played = None
    def play_random_piano_sound(self):
        piano_keys = ['c', 'd', 'e', 'f', 'g', 'a', 'b', 'c2']
        random_key = random.choice(piano_keys)

        self.play_sound(random_key)

    def play_sound(self, sound_key):
        if sound_key in self.sounds:
            self.sounds[sound_key].play()
            self.last_sound_played = sound_key

    def play_danger_on_channel1(self):
        if 'danger' in self.sounds:
            channel1.play(self.sounds['danger'])
            self.last_sound_played = 'danger'

    def play_death_on_channel2(self):
        if 'death' in self.sounds:
            channel2.play(self.sounds['death'])
            self.last_sound_played = 'death'
            
    def get_last_sound_played(self):
        return self.last_sound_played