from website import create_app, setup_scheduler
from website.services.tasks import run_scheduler

app = create_app()
setup_scheduler(app)  # Ensure this is called to set up the scheduler

if __name__ == '__main__':
    run_scheduler(app)
    app.run(debug=True)
