# License

This minimal webcomics platform is available under the terms of the permissive MIT license. While not required, if you 
do something interesting with the code, please drop us a line; we'd love to know what you're up to!


# Project Setup

Want to run a comics server for yourself? Maybe you'd rather send us a bug fix or new feature? Get started here.


## Docker Setup

If you're unfamiliar with Docker, this might be a little tricky for you. It's worth learning though; power through it until you understand!

- Install Docker and Docker Compose for your platform
- Run `python generate_env.py` to set up the docker environment configuration. Answer `y` to the prompt if you're doing development work, or `n` if you're deploying a server.
- Run `docker compose up --build -d`

You now have a server running. Unfortunately it doesn't do much - we need to initialize the data or restore from a backup.


## Initialize Data From Scratch

- Enter a shell on the docker django machine `docker compose exec django bash`
- Create the database `python manage.py migrate`
- Add a superuser `python manage.py createsuperuser`. Follow the prompts.
- Collect static files `python manage.py collectstatic`
- The site will now be running on `http://localhost`. (Note that this is running on port 80 unlike many development servers.)
- Add Data into the [Django Admin](http://localhost/admin/). Set up at least one Comic and then give it at least one Page. The Comic should use `localhost` as its "domain" so the URL router knows where to find it.
- Open [the Site](http://localhost) in a Web Browser.


## Backing Up and Restoring Data

To back up your database, run `docker compose exec django python manage.py backup dump <your filename here>.zip`.

To restore your database from a backup zip:
 - Ensure you have an empty database to start. It should be migrated.
 - Then load the backup zip `docker-compose exec django python manage.py backup load <your filename here>.zip`.
 - Log into your admin and make sure to change any Comics or Alias URLs so they work on your new IPs/Domains.

# Setting up SSL certs

The caddy server will automatically generate certs for the domain set in project.env

# Roadmap

- [ ] Bug Fixes
  - [ ] Alt text doesn't dynamically change with page switch on Chrome
  - [ ] nginx access and error logs don't ever cycle, so they might fill up the disk.
  - [ ] Migrate to a slightly larger server for the extra RAM
- [ ] Nice New Features
  - [ ] Community Page: a quick link to all social pages
    - [ ] LD+JSON for author and all community links
  - [ ] Extended Markdown for tag links; update transcripts and wiki pages
    - [ ] Auto-migrate tags when they are renamed.
  - [ ] Global search functionality for archive (returns tags and pages)
- [ ] Comments Overhaul
  - [ ] The forum isn't working out well for comments, is hard to set up, and embedding has gotten harder. What can we do instead?
- [ ] Support WebP file format
  - [ ] Request the best image file format (PNG, JPEG, WEBP).
  - [ ] Encode many different image permutations (size, format). 
  - [ ] Request the best file size for the comic view area.
  - [ ] Create a way to view the highest resolution version of the file.
- [ ] New URL-based Router
  - [ ] Blacklisted page slugs ("feed", "data")
  - [ ] Restricted admin permissions for artists
  - [ ] Automate SSL certs through LetsEncrypt as a management command
  - [ ] Autorenew certs where applicable
- [ ] Code Cleanliness & Data Integrity
  - [ ] Ensure RSS feed has no issues. Validate with https://validator.w3.org/feed/check.cgi
  - [ ] Make the CSS variables load into the template and move the main css file out to a static file
  - [ ] Load any JS variables into the template and move the main js file out to a static file
  - [ ] Migrate media files to namespaced paths. Randomize comic page image names so they're not guessable.
  - [ ] Periodically clean out orphaned media. Make sure the comments still link properly.
  - [ ] Use proper HTML template elements for dynamic sections
- [ ] Optimization
  - [ ] Run everything through an SEO checker
  - [ ] Google PageSpeed Insights
  - [ ] User Timing API for real user data
- [ ] Onboarding
  - [ ] Add a "no content" placeholder template for comics that have no pages yet
- [ ] Font update
  - [ ] Adjust certain punctuation to be lower (apostrophe, quotation, exclamation, question)
  - [ ] Make left margin slightly smaller on O
  - [ ] Slightly smaller space
  - [ ] Russian characters and о̄ñ
  - [ ] Adjust everything down a pixel or so
- [ ] New Reader "Quests" Section
  - [ ] Subscribe to RSS feed
  - [ ] Social Share Functionality
  - [ ] Vote for me on TopWebComics
  - [ ] Patreon integration
    - [ ] Become a Patron
    - [ ] Remove Ads if user is authed
    - [ ] Google Analytics tracking for conversion
  - [ ] Browser Push Notifications
    - [ ] Only present the modal if requested
    - [ ] Take them to a dedicated page that explains what to expect and then present modal
    - [ ] Look here: [browser push notifications](https://developers.google.com/web/updates/2016/07/web-push-interop-wins)
  - [ ] Join the Conversation on Discord
  - [ ] Tip me on Ko-Fi
  - [ ] GA event tracking
- [ ] Host static media through a better server than gunicorn
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
- [ ] QoL improvements
  - [ ] Error handling for failed AJAX requests
  - [ ] Reveal Hover Text button
  - [ ] Smooth out navigation so people don't get stuck in the tag pages ("Return to the Comic" button)
  - [ ] Search
  - [ ] Translations
  - [ ] Transcript/Tag suggestions
  - [ ] Better reading experience for people with 1366x768 laptop screens
  - [ ] Nice 404 page. Maybe make it configurable per comic. (404 Sword Not Found)
- [ ] Search Engine Optimization
  - [ ] Metadata
    - [x] Page
    - [ ] Archive
    - [ ] Tag
    - [ ] TagType
  - [ ] robots.txt & sitemap (These are stubbed out. Please finish.)
  - [ ] Schema.org tagging for our pages, tags
    - [ ] About the author section
    - [ ] Character section
    - [ ] Distinguish between cover art, etc
    - [ ] Javascript changing of values where appropriate
    - [ ] Tags might want a nullable "schema type"
- [ ] Other Wishlist
  - [ ] Translations
  - [ ] Order by Chronological vs Release vs whatever
  - [ ] Make a simpler install process. Maybe avoid docker-compose?

# Other ideas:

- [ ] Swords "panel bot" (request a comic id and panel number for a cropped version of the comic)

# AWS Ubuntu Setup

Here's a rough outline of what I did to get this server deployed on a fresh Ubuntu AWS EC2 instance.

```bash
# Apply security updates
sudo apt update
sudo apt upgrade

# Get Docker
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install docker-ce

# Get Docker Compose
mkdir -p ~/.docker/cli-plugins/
curl -SL https://github.com/docker/compose/releases/download/v2.3.3/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose

# Make it so we don't have to use docker with sudo
sudo usermod -aG docker ${USER}
newgrp docker

# Get the project
git clone https://github.com/pennomi/comics.git
cd comics

# HEADS UP! First remember to set your DNS to the public IP address of the server
python3 generate_env.py  # Select "n" because this is a production environment
docker compose build

# Start the server
docker compose up --build -d

# Create the database and initialize the static files
docker compose exec django python manage.py migrate
docker compose exec django python manage.py collectstatic

# EITHER initialize the data
docker compose exec django python manage.py createsuperuser
# OR load from a data dump
docker compose exec django python manage.py backup load <dumpfile.zip>

# Restart the server
docker compose restart
```
