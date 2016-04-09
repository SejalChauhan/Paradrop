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
cd Paradrop
./pdbuild.sh setup
sudo -H pip install --upgrade ndg-httpsclient
sudo ./pdbuild.sh update-tools
git clone https://github.com/ParadropLabs/Example-Apps.git
paradrop register
paradrop chute install <ip of router> <port#, default is 14321> Example-Apps/hello-world/config.yaml
```
