from app import app,socketio

if __name__ =='__main__':
    #The Run file
    #- the file that runs the Flask APP
    socketio.run(app,debug=True,allow_unsafe_werkzeug=True)