"""
Galactic Adventure

A small, inclusive, interactive sci-fi terminal game.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import time


# -----------------------------
# Data Models
# -----------------------------

@dataclass
class PlayerPrefs:
    text_size: str = "normal"      # normal | large
    high_contrast: bool = False
    reduced_motion: bool = False
    confirm_actions: bool = True


@dataclass
class GameState:
    ship_name: str = "Vanguard"
    callsign: str = "Pilot"
    chapter: int = 1
    power_cells: int = 3
    distress_packets_sent: int = 0
    last_choice: Optional[str] = None


# -----------------------------
# UI Helper
# -----------------------------

class UI:
    def __init__(self, prefs: PlayerPrefs):
        self.prefs = prefs

    def _style(self, text: str) -> str:
        if self.prefs.high_contrast:
            return f"=== {text.upper()} ==="
        return text

    def header(self, title: str) -> None:
        print()
        print(self._style(title))
        print("-" * max(10, min(70, len(title) + 6)))

    def body(self, text: str) -> None:
        if self.prefs.text_size == "large":
            for line in text.splitlines():
                print(line)
                print()
        else:
            print(text)

    def wait(self, seconds: float) -> None:
        if not self.prefs.reduced_motion:
            time.sleep(seconds)

    def ask(self, prompt: str) -> str:
        return input(self._style(prompt) + " ").strip()

    def confirm(self, prompt: str) -> bool:
        if not self.prefs.confirm_actions:
            return True
        ans = self.ask(f"{prompt} (y/n):").lower()
        return ans in ("y", "yes")

    def error(self, text: str) -> None:
        self.body(f"[Notice] {text}")

    def success(self, text: str) -> None:
        self.body(f"[OK] {text}")


# -----------------------------
# Validation Helpers
# -----------------------------

def validate_name(name: str) -> Tuple[bool, str]:
    if not name:
        return False, "Value cannot be empty."
    if len(name) > 24:
        return False, "Must be 24 characters or fewer."
    if any(ord(c) < 32 for c in name):
        return False, "Contains invalid characters."
    return True, ""


def safe_int_choice(raw: str, valid: Dict[int, str]) -> Optional[int]:
    try:
        value = int(raw)
    except ValueError:
        return None
    return value if value in valid else None


# -----------------------------
# Informational Screens
# -----------------------------

def show_user_stories(ui: UI) -> None:
    ui.header("User Stories")
    ui.body(
        "1) Adjust accessibility settings for comfortable reading.\n"
        "2) Make mission choices that affect resources.\n"
        "3) Recover safely from invalid input.\n"
    )


def show_inclusivity(ui: UI) -> None:
    ui.header("Inclusivity Heuristics")
    ui.body(
        "1) User control via settings\n"
        "2) Support for varied abilities\n"
        "3) Clear and consistent language\n"
        "4) Error prevention and recovery\n"
        "5) Respectful, neutral tone\n"
        "6) Transparent system feedback\n"
        "7) Privacy (no accounts or tracking)\n"
        "8) Predictable consequences\n"
    )


def show_quality(ui: UI) -> None:
    ui.header("Quality Attributes")
    ui.body(
        "Accessibility / Usability: Readability and motion options\n"
        "Reliability: Graceful handling of invalid input\n"
        "Maintainability: Clear separation of UI, logic, and data\n"
    )


# -----------------------------
# Menus
# -----------------------------

def settings_menu(ui: UI, prefs: PlayerPrefs) -> None:
    while True:
        ui.header("Settings")
        ui.body(f"1) Text size: {prefs.text_size}")
        ui.body(f"2) High contrast: {prefs.high_contrast}")
        ui.body(f"3) Reduced motion: {prefs.reduced_motion}")
        ui.body(f"4) Confirm actions: {prefs.confirm_actions}")
        ui.body("5) Back")

        valid = {1: "text", 2: "contrast", 3: "motion", 4: "confirm", 5: "back"}
        choice = safe_int_choice(ui.ask("Choose (1–5):"), valid)

        if choice is None:
            ui.error("Invalid selection.")
            continue

        if choice == 1:
            prefs.text_size = "large" if prefs.text_size == "normal" else "normal"
        elif choice == 2:
            prefs.high_contrast = not prefs.high_contrast
        elif choice == 3:
            prefs.reduced_motion = not prefs.reduced_motion
        elif choice == 4:
            prefs.confirm_actions = not prefs.confirm_actions
        else:
            return


def profile_menu(ui: UI, state: GameState) -> None:
    while True:
        ui.header("Profile")
        ui.body(f"Ship Name: {state.ship_name}")
        ui.body(f"Callsign: {state.callsign}")
        ui.body("1) Edit ship name")
        ui.body("2) Edit callsign")
        ui.body("3) Back")

        valid = {1: "ship", 2: "call", 3: "back"}
        choice = safe_int_choice(ui.ask("Choose (1–3):"), valid)

        if choice is None:
            ui.error("Invalid selection.")
            continue

        if choice == 1:
            name = ui.ask("New ship name:")
            ok, msg = validate_name(name)
            if ok:
                state.ship_name = name
            else:
                ui.error(msg)
        elif choice == 2:
            call = ui.ask("New callsign:")
            ok, msg = validate_name(call)
            if ok:
                state.callsign = call
            else:
                ui.error(msg)
        else:
            return


def mission(ui: UI, state: GameState) -> None:
    ui.header("Mission: Relay Crisis")
    ui.body(
        "A deep-space relay is failing.\n"
        "You may boost the system or attempt a manual reroute.\n"
    )

    while True:
        ui.body(f"Power Cells: {state.power_cells}")
        ui.body("1) Boost relay (costs 1 power cell)")
        ui.body("2) Manual reroute")
        ui.body("3) Back")

        valid = {1: "boost", 2: "manual", 3: "back"}
        choice = safe_int_choice(ui.ask("Choose (1–3):"), valid)

        if choice is None:
            ui.error("Invalid option.")
            continue

        if choice == 3:
            return

        if choice == 1:
            if state.power_cells <= 0:
                ui.error("No power cells available.")
                continue
            if ui.confirm("Spend 1 power cell?"):
                state.power_cells -= 1
                state.distress_packets_sent += 1
                state.last_choice = "boost"
                ui.success("Relay boosted successfully.")
                return

        if choice == 2:
            if ui.confirm("Attempt manual reroute?"):
                state.last_choice = "manual"
                ui.success("Manual reroute completed.")
                return


def status(ui: UI, state: GameState) -> None:
    ui.header("Status")
    ui.body(
        f"Ship: {state.ship_name}\n"
        f"Callsign: {state.callsign}\n"
        f"Power Cells: {state.power_cells}\n"
        f"Distress Packets Sent: {state.distress_packets_sent}\n"
        f"Last Choice: {state.last_choice}\n"
    )


# -----------------------------
# Main Menu
# -----------------------------

def main_menu(ui: UI, prefs: PlayerPrefs, state: GameState) -> None:
    while True:
        ui.header("Galactic Adventure")
        ui.body(
            "1) User Stories\n"
            "2) Inclusivity Heuristics\n"
            "3) Quality Attributes\n"
            "4) Start Mission\n"
            "5) Status\n"
            "6) Profile\n"
            "7) Settings\n"
            "8) Exit\n"
        )

        valid = {1: "stories", 2: "incl", 3: "qa", 4: "mission",
                 5: "status", 6: "profile", 7: "settings", 8: "exit"}

        choice = safe_int_choice(ui.ask("Choose (1–8):"), valid)

        if choice is None:
            ui.error("Invalid input.")
            continue

        if choice == 1:
            show_user_stories(ui)
        elif choice == 2:
            show_inclusivity(ui)
        elif choice == 3:
            show_quality(ui)
        elif choice == 4:
            mission(ui, state)
        elif choice == 5:
            status(ui, state)
        elif choice == 6:
            profile_menu(ui, state)
        elif choice == 7:
            settings_menu(ui, prefs)
        else:
            ui.header("Exit")
            return


def main() -> None:
    prefs = PlayerPrefs()
    state = GameState()
    ui = UI(prefs)

    ui.header("Welcome to Galactic Adventure")
    ui.body("An interactive sci-fi experience.\n")

    main_menu(ui, prefs, state)


if __name__ == "__main__":
    main()



