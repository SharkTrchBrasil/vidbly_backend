from sqlalchemy.orm import Session
from ..models.notification import Notification
from ..models.user import User
import uuid

def send_notification(db: Session, user_id: uuid.UUID, title: str, body: str, type: str, data: dict = None):
    """
    Creates an in-app notification and optionally sends a push notification via Firebase.
    """
    # 1. Save to Database
    notification = Notification(
        user_id=user_id,
        title=title,
        body=body,
        type=type,
        data=data
    )
    db.add(notification)
    db.commit()
    
    # 2. Trigger Push Notification (Firebase FCM)
    # user = db.query(User).filter(User.id == user_id).first()
    # if user and user.fcm_token:
    #     try:
    #         # from firebase_admin import messaging
    #         # message = messaging.Message(
    #         #     notification=messaging.Notification(title=title, body=body),
    #         #     data=data,
    #         #     token=user.fcm_token,
    #         # )
    #         # messaging.send(message)
    #         pass
    #     except Exception as e:
    #         print(f"Error sending push notification: {e}")
            
    return notification
