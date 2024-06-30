from app import app,socketio

if __name__ =='__main__':
    socketio.run(app.run(host='192.116.98.97', port=5000, debug=True))
    