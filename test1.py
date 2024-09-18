import cv2

# 카메라 장치를 OpenCV로 열기 (기본 카메라 장치 ID 0 사용)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("프레임을 읽을 수 없습니다.")
        break

    # 화면에 프레임 표시
    cv2.imshow('Camera Stream', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 사용 후 자원 해제
cap.release()
cv2.destroyAllWindows()
