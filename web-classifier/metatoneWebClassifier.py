import logging
# import metatoneClassifier
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
import OSC
from datetime import timedelta
from datetime import datetime
from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

#logger = logging.getLogger('gateway')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/classifier", ClassifierHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")
        # , messages=ChatSocketHandler.cache)

connections = set()
clients = dict()

def ProcessMetatoneMessageString(handler,time,packet):
    #something
    # ought to wrap this stuff in exception handling.
    message = OSC.decodeOSC(packet)
    #print ('Decoded Message: {}'.format(repr(message)))
    try:
        if "/metatone/touch/ended" in message[0]:
            # touch ended
            print("Got a touch ended message.")
        elif "/metatone/touch" in message[0]:
            print("Got a touch message.")
            # touch!
        elif "/metatone/switch" in message[0]:
            print("Got a switch message.")
            #switch
        elif "/metatone/online" in message[0]:
            print("Got an online message.")
            msg = OSC.OSCMessage("/metatone/classifier/hello")
            packet = msg.getBinary()
            handler.write_message(packet,binary=True)
            handler.deviceID = message[2]
            handler.app = message[3]
            # online! add to something.
        elif "/metatone/offline" in message[0]:
            print("Got an offline message.")
            # offline
        elif "/metatone/acceleration" in message[0]:
            print("Got an accel message.")
            # accel.
        elif "/metatone/app" in message[0]:
            print("Got an app message.")
            # app message.
        else:
            print("Got an unknown message! Address was: " + message[0])
            print u'Raw Message Data: {}'.format(packet)
    except():
        print("Message did not decode to a non-empty list.")
        


# # def classify():
# #     # calculate gestures
# #     # calculate performance state
# #     # performance evemt?
# #     for c in connections:
# #         # send gesture to c
# #         # send performance state to c
# #         if performanceEvent:
# #             #send performance event to c

class ClassifierHandler(tornado.websocket.WebSocketHandler):
    deviceID = ''
    app = ''

    def open(self):
        print("Client opened WebSocket")
        connections.add(self)
        logging.info(datetime.now().isoformat() + "Classifier Opened.")
        print("Connections" + repr(connections))

    def on_message(self,message):
        time = datetime.now()
        logging.info(time.isoformat() + " " + message)
        ProcessMetatoneMessageString(time,message)
        # self.write_message(message)
        #rint(message)
        # print("Attempting to return foo bar message.")
        msg = OSC.OSCMessage("/foo/bar")
        # msg.extend(['string argument',1,2,3.14])
        packet = msg.getBinary()
        print(u'Sending Message: {}'.format(packet))
        # # OSC.decodeOSC(packet)
        self.write_message(packet,binary=True)
        
    def on_close(self):
        print("Client closed WebSocket")
        logging.info(datetime.now().isoformat() + " Classifier Closed.")
        connections.remove(self)

    # waiters = set()
    # cache = []
    # cache_size = 200

    # def allow_draft76(self):
    #     # for iOS 5.0 Safari
    #     return True

    # def open(self):
    #     ChatSocketHandler.waiters.add(self)

    # def on_close(self):
    #     ChatSocketHandler.waiters.remove(self)

    # @classmethod
    # def update_cache(cls, chat):
    #     cls.cache.append(chat)
    #     if len(cls.cache) > cls.cache_size:
    #         cls.cache = cls.cache[-cls.cache_size:]

    # @classmethod
    # def send_updates(cls, chat):
    #     logging.info("sending message to %d waiters", len(cls.waiters))
    #     for waiter in cls.waiters:
    #         try:
    #             waiter.write_message(chat)
    #         except:
    #             logging.error("Error sending message", exc_info=True)

    # def on_message(self, message):
    #     logging.info("got message %r", message)
    #     parsed = tornado.escape.json_decode(message)
    #     chat = {
    #         "id": str(uuid.uuid4()),
    #         "body": parsed["body"],
    #         }
    #     chat["html"] = tornado.escape.to_basestring(
    #         self.render_string("message.html", message=chat))

    #     ChatSocketHandler.update_cache(chat)
    #     ChatSocketHandler.send_updates(chat)


def main():
    # Logging
    global logger
    logging_filename = datetime.now().isoformat().replace(":","-")[:19] + "-MetatoneOSCLog.log"
    logging.basicConfig(filename="logs/"+logging_filename,level=logging.DEBUG)
    logging.info("Logging started - " + logging_filename)
    print ("Classifier Server Started - logging to: " + logging_filename)

    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()