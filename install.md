#Instructions to install Paradrop tools

```
sudo apt-get update
sudo apt-get install python2.7 python-pip python-dev libffi-dev libssl-dev
sudo -H pip install -U pip
sudo -H pip install pex
sudo pip install pypubsub --allow-external pypubsub
sudo -H pip install pdtools
sudo apt-get install git
git clone https://github.com/SejalChauhan/Paradrop.git
./pdbuild.sh setup
sudo ./pdbuild.sh update-tools
sudo -H pip install --upgrade ndg-httpsclient
git clone https://github.com/ParadropLabs/Example-Apps.git
paradrop register /paradrop login
```
