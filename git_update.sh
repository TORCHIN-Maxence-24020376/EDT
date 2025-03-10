#!/bin/bash


eval $(ssh-agent -s)
ssh-add /home/max/.ssh/id_ed25519

cd /home/max/SCRIPTS/EDT || exit

git add .

git commit -m "Mise à jour automatique des emplois du temps"

git push origin main
