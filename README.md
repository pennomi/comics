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

```
sudo apt-get update
sudo apt-get install docker docker-compose
git clone <project_url>

```