# social-media

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
