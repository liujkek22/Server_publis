import websocket
import json
import threading
import time
import uuid

TOKEN = "dd299392b9a64e8abf98adac70d558e3"
APPKEY = "3VEMXP1dAB3qx5ns"
SAMPLE_RATE = 16000

task_id = None
ws = None
count = 0
WS_URL = f"wss://nls-gateway-cn-shanghai.aliyuncs.com/ws/v1?token={TOKEN}"

# 用于线程同步的事件
audio_sent_event = threading.Event()

def generate_uuid():
    return str(uuid.uuid4()).replace("-", "")

def start_transcription_message():
    global task_id
    task_id = generate_uuid()
    return {
        "header": {
            "message_id": generate_uuid(),
            "task_id": task_id,
            "namespace": "SpeechTranscriber",
            "name": "StartTranscription",
            "appkey": APPKEY
        },
        "payload": {
            "format": "pcm",
            "sample_rate": SAMPLE_RATE,
            "enable_intermediate_result": True,
            "enable_punctuation_prediction": True,
            "enable_inverse_text_normalization": True
        }
    }

def stop_transcription_message(task_id):
    return {
        "header": {
            "message_id": generate_uuid(),
            "task_id": task_id,
            "namespace": "SpeechTranscriber",
            "name": "StopTranscription",
            "appkey": APPKEY
        }
    }

def send_audio_data():
    global ws
    with open('tts_test.pcm', 'rb') as audio_file:
        while True:
            data = audio_file.read(3200)
            if not data:
                print("End of file reached")
                break
            if ws and ws.sock and ws.sock.connected:
                ws.send(data, websocket.ABNF.OPCODE_BINARY)
    # Signal音频数据已完全发送
    audio_sent_event.set()

def on_message(ws, message):
    global count
    response = json.loads(message)
    print(f"----------------------------------------------------------------------------------->{count}")
    print(response)
    if response["header"]["name"] == "SentenceEnd":
        # print("Task failed:", response["payload"]["message"])
        # ws.close()
        print("Task completed#########################################################################################")
        stop_message = stop_transcription_message(task_id)
        ws.send(json.dumps(stop_message))
        # wait for the audio to finish sending
        ws.close()
    count += 1
    print("------------------------------------------------------------------------------------")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed with code:", close_status_code, "and message:", close_msg)

def on_open(ws):
    global task_id
    start_message = start_transcription_message()
    ws.send(json.dumps(start_message))

    #发送音频数据
    send_audio_data()

    # print("Task completed#########################################################################################")
    # stop_message = stop_transcription_message(task_id)
    # ws.send(json.dumps(stop_message))

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(WS_URL,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()
