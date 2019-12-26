# License

This minimal webcomics platform is available under the terms of the permissive MIT license. While not required, if you 
do something interesting with the code, please drop us a line; we'd love to know what you're up to!

# Project Setup

Want to run a comics server for yourself? Maybe you'd rather send us a bug fix or new feature? Get started here.

## Docker Setup

If you're unfamiliar with Docker, this might be a little tricky for you. It's worth learning though; power through it until you understand!

- Install Docker and Docker Compose for your platform
- Run `python deploy/generate_env.py` to set up the docker environment configuration. Answer `y` to the prompt if you're doing development work, or `n` if you're deploying a server.
- Run `docker-compose build`
- Run `docker-compose up -d`
- Enter a shell on the docker django machine `docker-compose exec comics_django bash`
- Create the database `python3 manage.py migrate`
- Add a superuser `python3 manage.py createsuperuser`. Follow the prompts.
- Collect static files `python3 manage.py collectstatic`
- The site will now be running on `http://localhost`
- Add Data into the [Django Admin](http://localhost/admin/). Set up at least one Comic and then give it at least one Page.
- Open [the Site](http://localhost) in a Web Browser.

Sometimes we change this process and forget to update the readme. If it's not working for you, open an issue and we'll get it fixed.


# Roadmap

- [ ] Fix static files in development
- [ ] New URL-based Router
  - [ ] Google Analytics per domain
  - [ ] AliasUrl model that redirects to the primary
  - [ ] Blacklisted comic slugs
  - [ ] Blacklisted page slugs
  - [ ] Admin filters
  - [ ] Catch unconfigured domains and redirect
  - [ ] Index page for exploring comics
  - [ ] Automate NGINX configuration as a management command
  - [ ] Automate SSL certs through LetsEncrypt as a management command
  - [ ] Autorenew certs where applicable
  - [ ] Change URL scheme from /{slug}/ to /comic/
- [ ] Comments embed via Discourse topics
  - [ ] Only if discourse URL is configured at the comic level
  - [ ] Procedurally style based on the main stylesheet
- [ ] Management Convenience
  - [ ] Easy backup and restore management commands
- [ ] Cache invalidation
  - [ ] Configure CloudFlare per-domain
  - [ ] Split first/last AJAX into a separate request
  - [ ] Ensure JSON XHR is cached by cloudflare
  - [ ] On-save Comic/Page trigger that invalidates related URLs (namespace for easier invalidation)
  - [ ] CTA ad should load using API and invalidate on model change
- [ ] Font update
  - [ ] Adjust certain punctuation to be lower (apostrophe, quotation, exclamation, question)
  - [ ] Make left margin slightly smaller on O
  - [ ] Slightly smaller space
  - [ ] Russian characters
- [ ] Social Share Functionality
- [ ] Browser Push Notifications
  - [ ] Only present the modal if requested
  - [ ] Take them to a dedicated page that explains what to expect and then present modal
  - [ ] Look here: [browser push notifications](https://developers.google.com/web/updates/2016/07/web-push-interop-wins)
- [ ] Data integrity
  - [ ] Consider making slugs case-insensitive, and have restricted slugs, for pages, tags, and tag types
- [ ] Auto-post to various social media
  - [ ] General OAuth login
  - [ ] Reddit
  - [ ] Instagram
  - [ ] Discord
  - [ ] Patreon
  - [ ] Webtoons
  - [ ] Tumblr
- [ ] Merch Shop
  - [ ] Identify partner
  - [ ] One product beta
  - [ ] Upload image with strict specifications
  - [ ] Google Analytics tracking for conversion
- [ ] Patreon integration
  - [ ] Adjust UI if user is authed
  - [ ] Google Analytics tracking for conversion
- [ ] Floating Banner Ad
  - [ ] Hide for Patrons
- [ ] Call to Action section of the site
  - [ ] Become a Patron
  - [ ] Join the Conversation on Discord
  - [ ] Get notified when a new comic is posted
  - [ ] Subscribe to RSS feed
  - [ ] Tip me on Ko-Fi
  - [ ] Vote for me on TopWebComics
  - [ ] GA event tracking
  - [ ] How are these presented. Rotate through or show all?
- [ ] QoL improvements
  - [x] Scroll to top of page when navigating
  - [ ] Error handling for failed AJAX requests
  - [ ] Reveal Hover Text button
  - [ ] Smooth out navigation so people don't get stuck in the tag pages ("Return to the Comic" button)
  - [ ] Search
  - [ ] Translations
  - [x] No Javascript fallback
  - [ ] Transcript/Tag suggestions
  - [ ] Better reading experience for people with 1366x768 laptop screens
- [ ] Search Engine Optimization
  - [ ] Metadata
    - [x] Page
    - [ ] Archive
    - [ ] Tag
    - [ ] TagType
  - [ ] robots.txt
  - [ ] sitemap
  - [ ] Schema.org tagging for our pages, tags
    - [ ] About the author section
    - [ ] Character section
    - [ ] Distinguish between cover art, etc
    - [ ] Javascript changing of values where appropriate
- [ ] Other Wishlist
  - [ ] Order by Chronological vs Release vs whatever
  - [ ] Extended Markdown for tag links; update transcripts and wiki pages
  - [ ] Translations

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

# Notes on comfortable reading

The theory behind the design on the site is that it should be a perfectly comfortable reading experience for all of
the following screen sizes:

- [ ] 1024x768 (iPad landscape. This also covers smallish laptops, which are typically just wider with the same height.
 In this case, the vertical height is the limitation.)
- [ ] 329x568 (iPhone 5 portrait. This also covers )
- [ ] (Large screens. This covers the case where neither the height nor width are bounded.)

These need to have the comic fill the majority of the screen, while still exposing the navigation buttons.
