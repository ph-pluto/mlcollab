from mlcollab import init_application
import mlcollab.users 


app = init_application()

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host="172.20.10.4", debug=True)
