Tutorial for settings IDs with Feetech Software, and Serial bus driver : [https://www.robot-maker.com/forum/tutorials/article/168-brancher-et-controler-le-servomoteur-feetech-sts3032-360/]


Use Feetech software to set IDs : [https://github.com/Robot-Maker-SAS/FeetechServo/tree/main/feetech%20debug%20tool%20master/FD1.9.8.2)] 


## Rock, Paper, Scissors game

Install virtual environment
```bash
python3 -m venv myenv
source myenv/bin/activate
```

Install dependencies
```bash
python3 -m pip install -r PythonExample/requirements.txt
```

Run the game
```bash
python3 RockPaperScissors.py
```

### How to play

1. Keep your hands out of view of the camera to start. The game will start with a countdown from 3 to 1.
2. When the countdown reaches 1, show your hand in front of the camera. The game will recognize your hand gesture as either rock, paper, or scissors.
3. The game will then select its own gesture to attempt to win against you. The rules are as follows:
   - Rock beats scissors
   - Scissors beats paper
   - Paper beats rock
4. Remove your hand from view to start a new round.