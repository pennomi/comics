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

You now have a server running. Unfortunately it doesn't do much - we need to initialize the data or restore from a backup.


## Initialize Data From Scratch

- Enter a shell on the docker django machine `docker-compose exec comics_django bash`
- Create the database `python3 manage.py migrate`
- Add a superuser `python3 manage.py createsuperuser`. Follow the prompts.
- Collect static files `python3 manage.py collectstatic`
- The site will now be running on `http://localhost`. (Note that this is running on port 80 unlike many development servers.)
- Add Data into the [Django Admin](http://localhost/admin/). Set up at least one Comic and then give it at least one Page. The Comic should use `localhost` as its "domain" so the URL router knows where to find it.
- Open [the Site](http://localhost) in a Web Browser.


## Backing Up and Restoring Data

To back up your database, run `docker-compose exec comics python manage.py backup dump <your filename here>.zip`.

To restore your database from a backup zip:
 - Clear your database by moving it to a backup location.  `mv deploy/db/comics.sqlite3 deploy/db/comics.sqlite3.bak`
 - Create a fresh database `docker-compose exec comics python manage.py migrate`
 - Then load the backup zip `docker-compose exec comics python manage.py backup load <your filename here>.zip`.
 - Log into your admin and make sure to change any Comics or Alias URLs so they work on your new IPs/Domains.
 - If you're not seeing the CSS, make sure to run `docker-compose exec comics python manage.py collectstatic`.

# Setting up SSL certs

To create SSL certs for use in production, you need to run certbot from within the comics container

 - `sudo certbot certonly --cert-name <project name> --standalone --staple-ocsp -m <your email> --non-interactive --agree-tos -d <example.com> -d <another.example.com>`

# Configuring Ads

This section is a work in progress, so it may not be entirely accurate!

Ads should currently be configured globally for the entire server, NOT per domain. In order to set up an ad network, you need to do a couple things.

1. Configure your `ads.txt` URL in your server's `django.env` file. It should look like: `DJANGO_ADS_TXT_URL=https://example.com/ads.txt`
2. Inject the ad network code into the global comic header using the "Code Snippets" function in the Django admin. (Don't specify a comic so it shows up everywhere.)
3. Inject the ad tags into the appropriate site areas using the "Code Snippets" function. Currently the supported areas are hardcoded. You can add more by editing the `apps/comics/templatetags/snippet_extras.py` file.
4. You may find it helpful to use the "testing" flag before a snippet to the whole site. When this is true it only exists on the `example.com/test/` URL.


# Roadmap

- [ ] Bug Fixes
  - [ ] Alt text doesn't dynamically change with page switch on Chrome
  - [ ] Replace the forum with a built-in system for comments. Leave the forum-y stuff to Reddit or something.
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
- [ ] RSS Upgrade
  - [ ] Only show items created within 1 week ago with no count limit (some RSS readers delete their cache after some time)
- [ ] Cache invalidation
  - [ ] Configure CloudFlare per-domain
  - [ ] Split first/last AJAX into a separate request
  - [ ] Ensure JSON XHR is cached by CloudFlare
  - [ ] On-save Comic/Page trigger that invalidates related URLs (namespace for easier invalidation)
  - [ ] CTA ad should load using API and invalidate on model change
- [ ] Support WebP file format
  - [ ] Request the best image file format (PNG, JPEG, WEBP).
  - [ ] Encode many different image permutations (size, format). 
  - [ ] Request the best file size for the comic view area.
  - [ ] Create a way to view the highest resolution version of the file.
- [ ] New URL-based Router
  - [x] Google Analytics per domain
  - [ ] Remove comic slug field
  - [ ] Blacklisted page slugs ("feed", "data")
  - [ ] Restricted admin permissions for artists
  - [ ] Automate NGINX configuration as a management command
  - [ ] Automate SSL certs through LetsEncrypt as a management command
  - [ ] Autorenew certs where applicable
- [x] Comments System
  - [x] Style the comments section using the page styles
  - [ ] Have an auto-generator for Discourse comment embed styles
- [ ] Code Cleanliness & Data Integrity
  - [ ] Ensure RSS feed has no issues. Validate with http://www.feedvalidator.org/
  - [ ] Make the CSS variables load into the template and move the main css file out to a static file
  - [ ] Load any JS variables into the template and move the main js file out to a static file
  - [ ] Inject admin edit button ONLY if the cookie is detected (instead of hiding it)
  - [ ] Migrate media files to namespaced paths. Randomize comic page image names so they're not guessable.
  - [ ] Periodically clean out orphaned media. Make sure the forum stuff still links properly.
  - [ ] Consider making slugs case-insensitive, and have restricted slugs, for pages, tags, and tag types
  - [ ] Reduce code duplication in nginx configs
  - [x] Remove fontawesome
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
python3 generate_env.py  # Select "n" because this is a production environment
docker compose build

# Configure SSL Cert with Let's Encrypt
# HEADS UP! First remember to set your DNS to the public IP address of the server
sudo apt install certbot
sudo certbot certonly --cert-name <project name> --standalone --staple-ocsp -m <your email> --non-interactive --agree-tos -d <example.com> -d <another.example.com>

# HEAD UP! You don't need this yet, but to renew do this.
certbot renew --post-hook "docker compose restart"

# You have the certs, so you can finally start the server
docker compose up -d

# Create the database and initialize the static files
python manage.py migrate
python manage.py collectstatic

# EITHER initialize the data
python manage.py createsuperuser
# OR load from a data dump
python manage.py backup load <dumpfile.zip>

# Exit out of the shell
<ctrl-d>

# Restart the server
docker-compose restart
```

# Notes on comfortable reading

The theory behind the design on the site is that it should be a perfectly comfortable reading experience for all of
the following screen sizes:

- [ ] 1024x768 (iPad landscape. This also covers smallish laptops, which are typically wider with the same height.
 In this case, the vertical height is the limitation.)
- [ ] 329x568 (iPhone 5 portrait. This also covers most Android phones)
- [ ] (Very large screens. This covers the case where neither the height nor width are bounded.)

These need to have the comic fill the majority of the screen, while still exposing the navigation buttons.
