from pinder.campfire import Campfire
from twisted.application import service

from watson.chatbot import Chatbot

class Firebot(Chatbot):
    
    def __init__(self, name, commands, auth_token, subdomain, room_name):
        super(Firebot, self).__init__(name, commands)
        self.auth_token = auth_token
        self.subdomain = subdomain
        self.room_name = room_name
        self.room = None
        self.users = {}
    
    def speak(self, user, message):
        if not self.room:
            print "Must have a room before I can speak!"
            return
        
        self.room.speak(message)
    
    def connect(self):
        self.campfire = Campfire(self.subdomain, self.auth_token)
        self.room = self.campfire.find_room_by_name(self.room_name)
        self.room.join()
        
        def callback(message):
            text = message['body']
            user_id = message['user_id']
            user = self.users.get(user_id)
            
            if not user:
                user = self.campfire.user(user_id)['user']['name']
                self.users[user_id] = user
                
            self.perform_action(user, text)
        
        def err_callback(*args):
            self.error()
            
        self.room.join()
        self.room.listen(callback, err_callback, start_reactor = False)
        # self.room.speak(self.welcome_phrase)
        application = service.Application("firebot")
        return application

    def error(self):
        # self.room.speak("HAD AN ERROR")
        # self.room.speak(self.goodbye_phrase)
        self.room.leave()
    
    def disconnect(self):
        # self.room.speak(self.goodbye_phrase)
        self.room.leave()
    