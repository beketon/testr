import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate(
    'src/clients/b-express-8b7a5-firebase-adminsdk-3srns-08fd53169f.json')
firebase_admin.initialize_app(cred)


class FirebaseClient:
    def send_notification(self, device_token: str, title: str, body: str):
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=device_token
        )
        response = messaging.send(message)
        print('Successfully sent message:', response)
        return response


firebase_client = FirebaseClient()
