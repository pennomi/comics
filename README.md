# Project Setup

Want to run a comics server for yourself? Maybe you'd rather send us a bug fix or new feature? Get started here.

##Windows Setup

- Install [Python 3.7](https://www.python.org/downloads/)
- Install Requirements: `python -m pip install -r requirements.txt`
- Create the Database: `python manage.py migrate`
- Create a User: `python manage.py createsuperuser`
- Run the Development Server: `python manage.py runserver`
- Add Data into the [Django Admin](http://localhost:8000/admin/).
- Open [the Site](http://localhost:8000) in a Web Browser.


## Linux Setup (Ubuntu)

- To be added later. If you're a Linux person, you can probably figure it out.


# Roadmap

- [ ] Tag rendering
- [ ] Main Page
- [ ] Archive Page
- [ ] Domain-specific routing
- [ ] Tag Search Pages
- [ ] Links for Web Crawlers
- [ ] RSS Feed
- [ ] Translations


# AWS Ubuntu Setup

```bash
# Fix an annoying bug in AWS. This will be the last "unable to resolve host" error you see
sudo sh -c 'echo "127.0.0.1 $(hostname)" >> /etc/hosts'

# Get Docker
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install docker-ce
# OPTIONAL: if you don't want to use docker as sudo
# sudo groupadd docker
# sudo usermod -aG docker $USER
# sudo systemctl enable docker
# REBOOT HERE

# Get docker-compose
sudo curl -L https://github.com/docker/compose/releases/download/1.22.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod 777 /usr/local/bin/docker-compose

# Get the project
git clone https://github.com/pennomi/comics.git
cd comics
sudo docker-compose build
sudo docker-compose up -d

# Configure SSL Cert with Let's Encrypt
# First, set your DNS to the public IP address of the server
sudo docker exec -it <container_id> bash
certbot --nginx -d <your_domain_name>

# Create the database for administration
./manage.py migrate
./manage.py createsuperuser
./manage.py collectstatic
```