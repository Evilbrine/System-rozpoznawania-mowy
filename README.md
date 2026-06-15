# System-rozpoznawania-mowy
System rozpoznawania mowy do projektu inżynierskiego

Wymagania (instalacja):
- pip install vosk sounddevice

Model języka polskiego (pobierz i wypakuj):
- https://alphacephei.com/vosk/models/vosk-model-small-pl-0.22.zip
- Wypakuj obok skryptu do folderu "model". Oczekiwana struktura katalogów:

        projekt/
          robot_voice_control.py
          model/
            am/
            conf/
            graph/
            ivector/
            ...

Użycie:
- python robot_voice_control.py
- Lista dostępnych komend:
```python
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
```

Opcje:
- python robot_voice_control.py --model /ścieżka/do/modelu
- python robot_voice_control.py --device 1        # numer mikrofonu
- python robot_voice_control.py --list-devices    # lista mikrofonów
