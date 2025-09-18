import time
import sys
from pyfirmata2 import Arduino
from pyfirmata2.util import Iterator

# ==================== 포트 설정 ====================
PORT = 'COM4'
# ==================================================

board = None  # board 변수를 전역 스코프에서 초기화
try:
    # 보드 연결
    print(f"'{PORT}' 포트로 Arduino 연결을 시도합니다...")
    board = Arduino(PORT)
    print("연결 성공! Firmata 통신을 시작합니다.")

    it = Iterator(board)
    it.start()
    
    # 핀 번호 설정
    LED_PINS = [2, 3, 4, 5, 6]
    BUZZER_PIN = 8
    BUTTON_PINS_NUM = [9, 10, 11, 12, 13]

    # LED 핀 객체 (출력)
    led_pins = [board.get_pin(f'd:{pin}:o') for pin in LED_PINS]

    # [핵심 수정] 버튼 핀을 한 번에 하나씩 순차적으로 설정합니다.
    print("버튼 핀을 INPUT_PULLUP 모드로 설정합니다...")
    button_pins = []
    for pin_num in BUTTON_PINS_NUM:
        # 핀 모드를 설정하고 리스트에 추가합니다. 'p'는 INPUT_PULLUP을 의미합니다.
        button_pins.append(board.get_pin(f'd:{pin_num}:p'))
        print(f" - 디지털 핀 {pin_num} 설정 완료.")
        # [수정] 통신 안정성을 위해 딜레이를 0.3초로 늘립니다.
        time.sleep(0.3) 
    
    # 각 버튼 핀의 데이터 보고를 명시적으로 활성화합니다.
    print("각 버튼 핀의 데이터 보고를 활성화합니다...")
    for i, button in enumerate(button_pins):
        button.enable_reporting()
        print(f" - 버튼 {BUTTON_PINS_NUM[i]} (핀 D{button.pin_number}) 보고 활성화 완료.")
    
    time.sleep(1) # 안정화 시간
    print("핀 설정 및 초기화 완료.")

    def play_melody():
        melody = [(262, 0.2), (294, 0.2), (330, 0.2), (349, 0.2)]
        for note, duration_sec in melody:
            board.play_tone(BUZZER_PIN, note, duration_sec)
            time.sleep(0.05)

    last_button_states = [None] * len(BUTTON_PINS_NUM)

    print("="*20)
    print("게임 시작! 5개의 버튼 중 하나를 눌러보세요.")
    print("종료하려면 Ctrl+C를 누르세요.")
    print("="*20)
    
    loop_count = 0
    while True:
        if loop_count % 1000 == 0:
             sys.stdout.write(f"\r메인 루프 실행 중... (카운트: {loop_count})")
             sys.stdout.flush()

        for i, button in enumerate(button_pins):
            current_state = button.read()

            if last_button_states[i] is None and current_state is not None:
                last_button_states[i] = current_state
                continue

            # 버튼이 눌리는 '순간'을 감지 (풀업 모드에서는 눌리면 False가 됩니다)
            if current_state is False and last_button_states[i] is True:
                time.sleep(0.05) # 디바운싱
                
                print(f"\n>> 버튼 {BUTTON_PINS_NUM[i]} (index {i}) 눌림 감지! <<")
                
                led_pins[i].write(1)
                play_melody()
                led_pins[i].write(0)

            last_button_states[i] = current_state
        
        loop_count += 1
        time.sleep(0.001)

except KeyboardInterrupt:
    print("\n\n사용자에 의해 프로그램이 중단되었습니다.")

except Exception as e:
    print(f"\n\n[오류 발생] 프로그램이 예기치 않게 종료되었습니다: {e}")
    print("-" * 40)
    print("1. 아두이노 보드에 'ToneFirmata' 스케치를 다시 한번 업로드해보세요.")
    print("2. 버튼 회로 배선을 다시 확인해주세요. [버튼 한쪽 -> 디지털 핀, 다른 쪽 -> GND]")
    print("-" * 40)

finally:
    if board is not None:
        print("연결을 종료하고 모든 핀의 출력을 끕니다.")
        if 'led_pins' in locals():
            for pin in led_pins:
                pin.write(0)
        board.exit()
    else:
        print("프로그램을 종료합니다.")

