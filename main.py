from website import create_app
from website.services.tasks import run_scheduler

app = create_app()

if __name__ == '__main__':
    run_scheduler(app)
    app.run(debug=True)
