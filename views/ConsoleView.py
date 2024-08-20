import flask


class ConsoleView:
    @staticmethod
    def index():
        return flask.redirect('/apidocs')

    @staticmethod
    def display_data(data):
        print('[DATA FROM SENSOR]', data)
        return data

    @staticmethod
    def display_info(message):
        print('[INFO]', message)
        return message

    @staticmethod
    def send_message_to_udpserver(message):
        print('[SENDING UDP]', message)
        return message

    @staticmethod
    def receive_message_from_udpserver(message):
        print('[RECEIVING UDP]', message)
        return message
