import cv2
import os
import django
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_MENTAL_HEALTH.settings")
django.setup()

from deepface import DeepFace
from monitoring.models import FacialExpression
from django.contrib.auth.models import User

camera = cv2.VideoCapture(0)

user = User.objects.first()
last_saved = time.time()

while True:
    ret, frame = camera.read()

    if not ret:
        break

    try:
        result = DeepFace.analyze(
            frame,
            actions=['emotion'],
            enforce_detection=False
        )

        emotion = result[0]['dominant_emotion']

        face = result[0]['region']

        x = face['x']
        y = face['y']
        w = face['w']
        h = face['h']

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (255, 0, 0),
            2
        )

        cv2.putText(
            frame,
            "Expression: " + emotion,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        if user and time.time() - last_saved >= 10:
            FacialExpression.objects.create(
                user=user,
                expression=emotion
            )

            last_saved = time.time()
            print("Saved:", emotion)

    except:
        pass

    cv2.imshow("MindCare AI", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()

