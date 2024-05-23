# social-media

### About project
This social media API allows users to follow/unfollow other users, like, write and see posts with images and comment those posts. Also you can add hashtags to your post and use them to search content.

User profile has bio and profile picture.

## How to install
### Using Docker

Follow these steps:

```bash
git clone https://github.com/SysoevDmitro/social-media.git
cd social-media/social_media
docker-compose build
docker-compose up
```
### Using GitHub

Clone the repository and set up the environment:

```bash
git clone https://github.com/SysoevDmitro/social-media.git
cd social-media/social_media
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Apply migrations and run the server
python manage.py migrate
python manage.py runserver


