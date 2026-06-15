# System-rozpoznawania-mowy
System rozpoznawania mowy do projektu inżynierskiego

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
