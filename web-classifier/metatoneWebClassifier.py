import logging
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

def ProcessMetatoneMessageString(time,packet):
    #something
    # ought to wrap this stuff in exception handling.
    message = OSC.decodeOSC(packet)
    try:
        if "/metatone/touch/ended" in message.address:
            # touch ended
            print("Got a touch ended message.")
        elif "/metatone/touch" in message.address:
            # touch! Go ahead and parse and add to the messages.
            print("Got a touch message.")
        elif "/metatone/switch" in message.address:
            print("Got a switch message.")
            #switch
        elif "/metatone/online" in message.address:
            print("Got an online message.")
            # online! add to something.
        elif "/metatone/offline" in message.address:
            print("Got an offline message.")
            # offline
        elif "/metatone/acceleration" in message.address:
            print("Got an accel message.")
            # accel.
        elif "/metatone/app" in message.address:
            print("Got an app message.")
            # app message.
        else:
            print("Got an unknown message")
    except:
        print("Exception Parsing Message: uh oh- the message couldn\'t be parsed.")
        print u'GOT MESSAGE: {}'.format(packet)
        print ('GOT MESSAGE: {}'.format(repr(message)))
        # print("Message: " + str(packet))


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
    def open(self):
        print("Client opened WebSocket")
        connections.add(self)
        logging.info(datetime.now().isoformat() + "Classifier Opened.")

    def on_message(self,message):
        time = datetime.now()
        logging.info(time.isoformat() + " " + message)
        ProcessMetatoneMessageString(time,message)
        print(message)
        
    def on_close(self):
        print("Client closed WebSocket")
        logging.info(datetime.now().isoformat() + " Classifier Closed.")

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