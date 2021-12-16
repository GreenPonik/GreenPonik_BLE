from gatt_server import BleApplication, JsonAdvertisement, JsonService

app = BleApplication()

# logging.basicConfig(level=logging.DEBUG,
#                    filename="ble_server.log")

app.add_service(JsonService(0))
app.register()

adv = JsonAdvertisement(0)
adv.register()

try:
    app.run()
except KeyboardInterrupt:
    app.quit()
