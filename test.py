import time

import Leap, sys


class LeapEventListener(Leap.Listener):

    def on_connect(self, controller):
        print ("Connected")
        controller.enable_gesture(Leap.Gesture.Type.TYPE_SWIPE)
        controller.config.set("Gesture.Swipe.MinLength", 200.0)
        controller.config.save()

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print ("Disconnected")

    def on_frame(self, controller):
        print ("Frame available")
        frame = controller.frame()
        # Process frame data


# listener = LeapEventListener
# controller = Leap.Controller()
# controller.add_listener(listener)




if __name__ == '__main__':
    controller = Leap.Controller()

    while True:
        frame = controller.frame()
        hands = frame.hands
        # pointables = frame.pointables
        # fingers = frame.fingers
        # tools = frame.tools
        if not hands.is_empty:
            first_hand = hands[0]
            yaw = first_hand.direction.yaw
            print("----yaw-----")
            print(yaw * -90 + 90)
            time.sleep(1)
            # print(first_hand)
            # print(hands)
