## CLIENT ##
import socket
from _thread import *
import os
import random
import cv2
import serial
import time
from PIL import Image
import os
import requests

py_serial = serial.Serial(
    
    # Window
    port='COM19',
    # 보드 레이트 (통신 속도)
    baudrate=9600,
)

HOST = '13.125.175.70' ## server에 출력되는 ip를 입력해주세요 ##
PORT = 9999
IdentityKey="\"C:/Users/richa/OneDrive/문서/ssh_security_key/glados_key.pem\""
DNS="ec2-user@ec2-13-125-175-70.ap-northeast-2.compute.amazonaws.com"
recieve_addr=["1011","1012","1021","1022","2011","2012","2021","2022","3011","3012","3021","3022"]
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
cnt=0
data=""
decoded_response=""
def optimize_image(input_path, output_path, quality=60):
    try:
        # 이미지 열기
        image = Image.open(input_path)
        
        # 이미지 최적화 및 저장
        image.save(output_path, optimize=True, quality=quality)
        
        print(f"이미지 최적화 완료: {output_path}")
    except Exception as e:
        print(f"이미지 최적화 중 오류 발생: {e}")
def image_process():
    global decoded_response,recieve_addr,cnt,data,DNS,IdentityKey
    input_image_path = "C:\\Users\\richa\\OneDrive\\바탕 화면\\geekble\\data2\\{}.jpg".format(recieve_addr[cnt])  # 최적화할 이미지 파일 경로
    output_image_path = "C:\\Users\\richa\\OneDrive\\바탕 화면\\geekble\\data2\\{}.jpg".format(recieve_addr[cnt])  # 최적화된 이미지를 저장할 경로
    quality_level = 60  # 이미지 품질 설정 (0-100 범위)
    optimize_image(input_image_path, output_image_path, quality_level)
    SendFile="\"C:/Users/richa/OneDrive/바탕 화면/geekble/data2/{}.jpg\"".format(recieve_addr[cnt])
    RecieveFile="/home/ec2-user/po-glos/public/data/id_{}/{}.JPG".format(data[2],recieve_addr[cnt])
    command="scp -i {} {} {}:{}".format(IdentityKey,SendFile,DNS,RecieveFile)
    os.system(command)
    url = 'http://po-glos.com:3000/person_recog/{}/{}'.format(data[2],recieve_addr[cnt])  # 요청을 보낼 웹 페이지의 URL을 지정합니다.

    # GET 요청 보내기
    response = requests.get(url, timeout=10)

    # 응답 확인
    if response.status_code == 200:  # HTTP 상태 코드가 200이면 성공적인 요청입니다.
        print('요청 성공!')
        print('응답 내용:', response.text)  # 웹 페이지의 내용을 출력합니다.
        if cnt==12:
            cnt==0
        else:
            cnt=cnt+1
    else:
        print('요청 실패. 상태 코드:', response.status_code)
    decoded_response=""
def read_serial_data():
    global data_sign,cnt,data,client_socket,decoded_response
    while True:
        if py_serial.readable():
            response = py_serial.readline()
            decoded_response = response[:len(response) - 1].decode().strip()
            print("시리얼 데이터:", decoded_response)
            if (decoded_response=='0'):
                message="촬영:{}".format(recieve_addr[cnt])
                client_socket.send(message.encode())
            
                
def recv_data(client_socket):
    global data_sign,data
    while True:
        temp = client_socket.recv(1024)
        temp = temp.decode()
        print("recive : ", temp)
        if temp=="촬영완료":
            image_process()
        else:
            data=temp.split(":")
            if data[1]=="2층" or data[1]=="1층" or data[1]=="3층":
                command="2"
                py_serial.write(command.encode())

start_new_thread(recv_data, (client_socket,))
start_new_thread(read_serial_data, ())

print('>> Connect Server')

while True:
    message = input()
    if message == 'quit':
        close_data = message
        break

    client_socket.send(message.encode())

client_socket.close()