"""Configuration commune aux vues."""
import os

# Pygame ne doit pas ajouter sa bannière aux mouvements du terminal.
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
