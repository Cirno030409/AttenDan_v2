import binascii

import nfc


class CardReader:
    def connect_reader(self):
        try:
            self.clf = nfc.ContactlessFrontend("usb")
        except Exception as e:
            print("[NFC] reader not found.: ", e)
            return e
        print("[NFC] reader connected.")
        return 0

    def wait_for_card_touched(
        self,
    ):  # This func blocks called thread until card is touched.
        try:
            tag = self.clf.connect(rdwr={"on-connect": lambda tag: False})
        except Exception as e:
            print("[NFC] an error has occured.: ", e)
            return -1
        return binascii.hexlify(tag.identifier).decode()

    def disconnect_reader(self):
        print("[NFC] reader disconnected.")
        self.clf.close()
