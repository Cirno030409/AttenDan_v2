import Use_NFC

rd = Use_NFC.CardReader()

rd.connect_reader()
while True:
    print(rd.wait_for_card_touched())
