from website import create_app, setup_scheduler

app = create_app()
setup_scheduler(app)

if __name__ == '__main__':
    app.run(debug=True)

