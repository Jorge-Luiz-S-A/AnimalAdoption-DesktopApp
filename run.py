# run.py
from database import init_db
from login import login_screen
from main import MainApp

init_db()
login_screen() and MainApp().mainloop()
