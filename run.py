from app import create_app

# Create and run the app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
