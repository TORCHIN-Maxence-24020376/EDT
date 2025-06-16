#!/bin/bash

eval $(ssh-agent -s)
ssh-add /home/max/.ssh/id_ed25519

cd /home/max/SCRIPTS/EDT || exit

/home/max/venv/bin/python3 /home/max/SCRIPTS/EDT/API.py

git add .

git commit -m "Mise à jour automatique des emplois du temps"

git push origin main
