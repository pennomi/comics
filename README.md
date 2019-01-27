# License

This minimal webcomics platform is available under the terms of the permissive MIT license. While not required, if you 
do something interesting with the code, please drop us a line; we'd love to know what you're up to!

# Project Setup

Want to run a comics server for yourself? Maybe you'd rather send us a bug fix or new feature? Get started here.

## Docker Setup

If you're unfamiliar with Docker, this might be a little tricky for you. It's worth learning though; power through it until you understand!

- Install Docker and Docker Compose for your platform
- Run `python deploy/generate_env.py` to set up the docker environment configuration
- Run `docker-compose build`
- Run `docker-compose up -d`
- The site will now be running on `http://localhost`
- Enter a shell on the docker django machine `docker exec -it YOUR_CONTAINER_ID bash`
- Create the database `python3 manage.py migrate`
- Add a superuser `python3 manage.py createsuperuser`
- Collect static files `python3 manage.py collectstatic`
- Add Data into the [Django Admin](http://localhost/admin/).
- Open [the Site](http://localhost) in a Web Browser.


# Roadmap

- [x] Add a docker-generated secret key for Django
- [x] Full overhaul of Docker image (Alpine-based for faster builds)
- [ ] Social link previews & search engine metadata (use SEO checkers)
  - [x] Page
  - [ ] Archive
  - [ ] Tag
  - [ ] Tagtype
- [ ] robots.txt
- [ ] Scroll to top of comic upon navigating
- [ ] Error handling for failed AJAX requests
- [ ] Order by Chronological
- [ ] Favicons
- [ ] New Patreon banners (also consider ad space)
- [ ] Smooth out navigation so people don't get stuck in the tag pages ("Return to the Comic" button)
- [ ] Reveal hover-text button
- [ ] Extended Markdown for tag links; update transcripts and wiki pages
- [ ] Refine Tag, TagType, and Archive Pages
- [ ] Archive/Transcript/Tag Search
- [ ] Translations
- [ ] Fix Navigation on VERY old browsers and crawlers (anchor fallback for no js)
- [ ] Allow suggestions to transcripts, tags, wiki pages
- [ ] Add configuration for Google Analytics per-comic
- [ ] Opt-in to receive [browser push notifications](https://developers.google.com/web/updates/2016/07/web-push-interop-wins) on new posts
- [ ] Domain-specific routing
- [ ] Main Page (temporarily just redirecting to swords)
- [ ] OAuth client to auto-post to various social media

# Other ideas:

- [ ] Swords "panel bot" (request a comic id and panel number for a cropped version of the comic)

# AWS Ubuntu Setup

Here's a rough outline of what I did to get this server deployed on an Ubuntu AWS EC2 instance.

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

# OPTIONAL: if you don't want to use docker with sudo
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
python deploy/generate_env.py  # Generate env variables for the docker build
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