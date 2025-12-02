from app.models import db
from app import create_app

app = create_app('DevelopmentConfig')

with app.app_context():
  # db.drop_all()
  db.create_all() #Creating our database tables

# app.run()
# Finally, we run our Flask app





