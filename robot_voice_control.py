"""
Robot Voice Control - sterowanie głosowe robotem mobilnym
Silnik: Vosk (offline AI, język polski)

Wymagania (instalacja):
    pip install vosk sounddevice

Model języka polskiego (pobierz i wypakuj):
    https://alphacephei.com/vosk/models/vosk-model-small-pl-0.22.zip
    Wypakuj do folderu "model" obok tego skryptu.

Użycie:
    python robot_voice_control.py

Opcje:
    python robot_voice_control.py --model /ścieżka/do/modelu
    python robot_voice_control.py --device 1        # numer mikrofonu
    python robot_voice_control.py --list-devices    # lista mikrofonów
"""

import argparse
import json
import queue
import sys
import os
import threading
import time
from datetime import datetime

import sounddevice as sd
from vosk import Model, KaldiRecognizer

# ─────────────────────────────────────────────
# KONFIGURACJA KOMEND
# ─────────────────────────────────────────────

COMMANDS = {
    "forward": [
        "do przodu", "naprzód", "jedź", "jedz", "jazda",
        "jedź do przodu", "ruszaj"
    ],
    "backward": [
        "do tyłu", "wstecz", "cofnij", "tył", "cofaj",
        "jedź do tyłu"
    ],
    "left": [
        "w lewo", "skręć w lewo", "lewo", "skręć lewo"
    ],
    "right": [
        "w prawo", "skręć w prawo", "prawo", "skręć prawo"
    ],
    "stop": [
        "stój", "stop", "zatrzymaj", "zatrzymaj się",
        "hamuj", "stoi", "koniec"
    ],
    "spin": [
        "obrót", "obróć się", "zawróć", "zawracaj", "spin"
    ],
    "speed_up": [
        "szybciej", "przyspiesz", "więcej gazu"
    ],
    "slow_down": [
        "wolniej", "zwolnij", "zwalniaj"
    ],
}

# Etykiety wyświetlane w konsoli
LABELS = {
    "forward":    "▲  DO PRZODU",
    "backward":   "▼  DO TYŁU",
    "left":       "◄  W LEWO",
    "right":      "►  W PRAWO",
    "stop":       "■  STOP",
    "spin":       "↻  OBRÓT 360°",
    "speed_up":   "⚡ SZYBCIEJ",
    "slow_down":  "🐢 WOLNIEJ",
}

# ─────────────────────────────────────────────
# OBSŁUGA ROBOTA
# (tutaj podpinasz Serial / Socket / Bluetooth)
# ─────────────────────────────────────────────

def send_command(action: str):
    """
    Wyślij komendę do robota.

    Na razie tylko print — zamień na np.:
        serial_port.write(f"{action}\\n".encode())   # Serial/USB
        sock.sendall(f"{action}\\n".encode())        # WiFi/Socket
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    label = LABELS.get(action, action.upper())
    print(f"  [{timestamp}]  KOMENDA → {label}")

# ─────────────────────────────────────────────
# ROZPOZNAWANIE KOMEND
# ─────────────────────────────────────────────

def match_command(text: str) -> str | None:
    """Dopasuj rozpoznany tekst do komendy. Zwraca nazwę akcji lub None."""
    text = text.lower().strip()
    for action, phrases in COMMANDS.items():
        for phrase in phrases:
            if phrase in text:
                return action
    return None

# ─────────────────────────────────────────────
# GŁÓWNA LOGIKA NAGRYWANIA
# ─────────────────────────────────────────────

audio_queue: queue.Queue = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    """Callback sounddevice — wrzuca surowe audio do kolejki."""
    if status:
        print(f"  [!] Audio status: {status}", file=sys.stderr)
    audio_queue.put(bytes(indata))

def run(model_path: str, device: int | None, samplerate: int = 16000):
    print()
    print("╔══════════════════════════════════════════╗")
    print("║      ROBOT VOICE CONTROL  v1.0           ║")
    print("║      Silnik: Vosk (offline AI, PL)       ║")
    print("╚══════════════════════════════════════════╝")
    print()

    # Załaduj model
    if not os.path.isdir(model_path):
        print(f"[BŁĄD] Nie znaleziono modelu w: {model_path}")
        print()
        print("  Pobierz model polski:")
        print("  https://alphacephei.com/vosk/models/vosk-model-small-pl-0.22.zip")
        print("  Wypakuj jako folder 'model' obok skryptu.")
        print()
        sys.exit(1)

    print(f"[OK] Ładowanie modelu: {model_path} ...")
    model = Model(model_path)
    rec = KaldiRecognizer(model, samplerate)
    rec.SetWords(True)
    print("[OK] Model załadowany.")
    print()

    # Pokaż wybrany mikrofon
    if device is not None:
        print(f"[OK] Mikrofon: urządzenie #{device}")
    else:
        print("[OK] Mikrofon: domyślny")
    print()
    print("─" * 46)
    print("  Mów komendy. Naciśnij Ctrl+C aby zakończyć.")
    print("─" * 46)
    print()

    last_action = None
    last_time = 0
    DEBOUNCE = 1.5  # sekundy — minimalna przerwa między tą samą komendą

    with sd.RawInputStream(
        samplerate=samplerate,
        blocksize=8000,
        device=device,
        dtype="int16",
        channels=1,
        callback=audio_callback,
    ):
        while True:
            data = audio_queue.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()

                if not text:
                    continue

                print(f"  [słyszę] \"{text}\"")

                action = match_command(text)
                now = time.time()

                if action:
                    # Debounce: ignoruj tę samą komendę powtórzoną za szybko
                    if action == last_action and (now - last_time) < DEBOUNCE:
                        continue
                    last_action = action
                    last_time = now
                    send_command(action)
                else:
                    print("  [?] Nie rozpoznano komendy.")

                print()

# ─────────────────────────────────────────────
# ARGUMENTY CLI
# ─────────────────────────────────────────────

def list_devices():
    print("\nDostępne urządzenia audio:\n")
    print(sd.query_devices())
    print()

def parse_args():
    parser = argparse.ArgumentParser(
        description="Sterowanie robotem głosem (Vosk, offline)"
    )
    parser.add_argument(
        "--model", default="model",
        help="Ścieżka do folderu z modelem Vosk (domyślnie: ./model)"
    )
    parser.add_argument(
        "--device", type=int, default=None,
        help="Numer urządzenia audio (mikrofonu). Domyślnie: systemowy."
    )
    parser.add_argument(
        "--list-devices", action="store_true",
        help="Wypisz dostępne urządzenia audio i wyjdź."
    )
    return parser.parse_args()

# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    args = parse_args()

    if args.list_devices:
        list_devices()
        sys.exit(0)

    try:
        run(model_path=args.model, device=args.device)
    except KeyboardInterrupt:
        print("\n\n[OK] Program zakończony.\n")
    except Exception as e:
        print(f"\n[BŁĄD] {e}\n")
        sys.exit(1)
