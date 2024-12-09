from app.models import User

User.create(username="admin", email="admin@example.com", password_hash="hashedpassword")
print("Dummy user created!")
